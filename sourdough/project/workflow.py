"""
workflow: sourdough workflow for project creation and iteration
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Draft (Action): creates a Hybrid instance from passed arguments and/or a 
        Settings instance.
    Publish (Action): finalizes a Hybrid instance based upon the initial
        construction by an Draft instance and/or runtime user editing.
    Apply (Action): executes a Hybrid instance, storing changes and results
        in the Apply instance and/or passed data object.

"""

import abc
import dataclasses
import inspect
from typing import Any, ClassVar, Iterable, Mapping, Sequence, Tuple, Union

import sourdough


@dataclasses.dataclass
class Workflow(sourdough.RegistryMixin, abc.ABC):
    """Base class for sourdough object creators.
    
    Args:
        project (sourdough.Project): the related Project instance.
        
    """
    project: 'sourdough.Project' = None
    name: str = None
    registry: ClassVar['sourdough.Inventory'] = sourdough.Inventory(
        defaults = ['draft', 'publish', 'apply'], 
        stored_types = ('Workflow'))
    roles: ClassVar['sourdough.Inventory'] = sourdough.Inventory()
    
    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def create(self, item: object = None, **kwargs) -> object:
        """Performs some action related to passed 'item'.
        
        Subclasses must provide their own methods.
        
        """
        pass

    """ Private Class Methods """
    
    @classmethod
    def _get_role(cls, role: str) -> 'sourdough.Role':
        """[summary]

        Args:
            role (str): [description]

        Returns:
            [type]: [description]
        """
        try:
            return cls.roles[role]
        except KeyError:
            cls.roles[role] = cls.project.roles.build(role)
            return cls.roles[role]


@dataclasses.dataclass
class Draft(Workflow):
    """Constructs composite objects from user settings.
    
    Args:
        project (sourdough.Project): the related Project instance.
    
    """
    project: 'sourdough.Project' = None  
    
    """ Public Methods """
    
    def create(self, worker: 'sourdough.Worker') -> 'sourdough.Worker':
        """Drafts a Manager of a sourdough Project.
        
        Args:
            worker (sourdough.Worker): Manager instance to create and organize
                based on the information in 'settings'.

        Raises:
            ValueError: if a section in 'project.settings' contains workers and
                other types of components.

        Returns:
            sourdough.Worker: an instance with contents organized.
                
        """
        # Creates an empty dict of attributes to add to 'worker'.
        attributes = {}
        # Divides settings into different subsections.
        worker_settings, component_settings, attributes = self._divide_settings(
            settings = self.project.settings[worker.name]) 
        # Adds extra settings as attributes to worker.
        worker = self._add_attributes(
            component = worker, 
            attributes = attributes)
        # Recursively calls method if other 'workers' are listed.
        if len(worker_settings) == 1: 
            new_workers = list(worker_settings.values())[0]
            for new_worker in new_workers:
                instance = self._create_component(
                    name = new_worker, 
                    base = 'worker')
                
                # Checks if special prebuilt class exists.
                try:
                    component = self.project.components.build(key = new_worker)
                # Otherwise uses the appropriate generic type.
                except KeyError:
                    key = self.project.components._get_keys_by_type(
                        sourdough.Worker)[0]
                    component = self.project.components.build(key = key)
                worker.add(self.create(worker = component))
        elif len(component_settings) > 0:
            # Finds and sets the 'role' of 'worker'.
            worker = self._validate_role(worker = worker)
            # Organizes 'contents' of 'worker' according to its 'role'.
            worker.role.organize(
                settings = component_settings, 
                project = self.project)
        elif len(worker_settings) > 1:
            raise ValueError(
                'A section in settings cannot contain two different sets of '
                'workers')            
        else:
            raise ValueError(
                'A section in settings can either contain workers or other' 
                'components, but not both')
        return worker          

    """ Private Methods """

    def _divide_settings(self,
            settings: Mapping[Any, Any]) -> Tuple[
                Mapping[Any, Any],
                Mapping[Any, Any]]:
        """Divides 'settings' into component and attribute related settings.

        Args:
            settings (Mapping[Any, Any]):
            
        Returns:
            Tuple[Mapping[Any, Any], Mapping[Any, Any]]:
        
        """
        worker_settings = {}
        component_settings = {}
        attributes = {}
        component_suffixes = tuple(self.project.components._suffixify().keys())
        for key, value in settings.items():
            if key.endswith(self._get_suffixes(component = sourdough.Worker)):
                worker_settings[key] = sourdough.utilities.listify(value)
            elif any(key.endswith(component_suffixes)):
                component_settings[key] = sourdough.utilities.listify(value)       
            elif not key.endswith('_role'):
                attributes[key] = value
        return worker_settings, component_settings, attributes

    def _add_attributes(self, 
            component: 'sourdough.Component',
            attributes: Mapping[str, Any]) -> 'sourdough.Component':
        """[summary]

        Returns:
            [type]: [description]
            
        """
        for key, value in attributes.items():
            setattr(component, key, value)
        return component   

    def _create_component(self, 
            name: str, 
            base: str,
            **kwargs) -> 'sourdough.Component':
        """[summary]

        Returns:
            [type]: [description]
            
        """
        # Checks if special prebuilt class exists.
        try:
            component = self.project.components.build(key = name, **kwargs)
        # Otherwise uses the appropriate generic type.
        except KeyError:
            generic = self.project.components.registry[base]
            kwargs.update({'name': name})
            component = generic(**kwargs)
        return component
     
    def _get_suffixes(self, component: 'sourdough.Component') -> Sequence[str]:
        """[summary]

        Args:
            component (sourdough.Component): [description]

        Returns:
            Sequence[str]: [description]
            
        """
        components = self.project.components._get_keys_by_type(component)
        components = sourdough.utilities.add_suffix(components, 's')
        return tuple(sourdough.utilities.add_prefix(components, '_'))
    
    def _add_role(self, worker: 'sourdough.Worker') -> 'sourdough.Worker':
        """
        """ 
        key = f'{worker.name}_role'
        try:    
            worker.role = self.project.settings[worker.name][key]
        except KeyError:
            pass
        worker.role = self._get_role(role = worker.role)
        return worker
                
        
@dataclasses.dataclass
class Publish(Workflow):
    """Finalizes a composite object from user settings.
    
    Args:
        project (sourdough.Project): the related Project instance.
    
    """    
    project: 'sourdough.Project' = None  

    """ Public Methods """
 
    def create(self, worker: 'sourdough.Worker') -> 'sourdough.Worker':
        """Finalizes a worker with 'parameters' added.
        
        Args:
            worker (sourdough.Worker): instance to finalize the objects in
                its 'contents'.

        Returns:
            sourdough.Worker: an instance with its 'contents' finalized and
                ready for application.
                
        """
        worker.apply(tool = self._get_techniques)
        worker.apply(tool = self._set_parameters)
        return worker

    """ Private Methods """
    
    def _get_techniques(self, 
            component: 'sourdough.Component',
            **kwargs) -> 'sourdough.Component':
        """
        
        """
        if isinstance(component, sourdough.Technique):
            component = self._get_technique(technique = component, **kwargs)
        elif isinstance(component, sourdough.Task):
            component.technique = self._get_technique(
                technique = component.technique,
                **kwargs)
        return component   

    def _get_technique(self, 
            technique: 'sourdough.Technique',
            **kwargs) -> 'sourdough.Technique':
        """
        
        """
        return self.project.component.build(technique, **kwargs)
       
    def _set_parameters(self, 
            component: 'sourdough.Component') -> 'sourdough.Component':
        """
        
        """
        if isinstance(component, sourdough.Technique):
            return self._set_technique_parameters(technique = component)
        elif isinstance(component, sourdough.Task):
            return self._set_task_parameters(task = component)
        else:
            return component
    
    def _set_technique_parameters(self, 
            technique: 'sourdough.Technique') -> 'sourdough.Technique':
        """
        
        """
        if technique.name not in ['none', None, 'None']:
            technique = self._get_settings(technique = technique)
        return technique
    
    def _set_task_parameters(self, task: 'sourdough.Task') -> 'sourdough.Task':
        """
        
        """
        if task.technique.name not in ['none', None, 'None']:
            task = self._get_settings(technique = task)
            try:
                task.set_conditional_parameters()
            except AttributeError:
                pass
            task.technique = self._set_technique_parameters(
                technique = task.technique)
        return task  
            
    def _get_settings(self,
            technique: Union[
                'sourdough.Technique', 
                'sourdough.Task']) -> Union[
                    'sourdough.Technique', 
                    'sourdough.Task']:
        """Acquires parameters from 'settings' of 'project'.

        Args:
            technique (technique): an instance for parameters to be added to.

        Returns:
            technique: instance with parameters added.

        """
        key = f'{technique.name}_parameters'
        try: 
            technique.parameters.update(self.project.settings[key])
        except KeyError:
            pass
        return technique


@dataclasses.dataclass
class Apply(Workflow):
    
    project: 'sourdough.Project' = None  
    
    def create(self, worker: 'sourdough.Worker') -> 'sourdough.Worker':
        """[summary]

        Returns:
            [type] -- [description]
            
        """
        new_contents = []
        for item in worker:
            if isinstance(item, sourdough.Worker):
                instance = self.create(worker = item)
            else:
                instance = item.perform(data = self.project.data)
            instance.role.finalize()
            new_contents.append(instance)
        worker.contents = new_contents
        return worker

    """ Private Methods """
        
    def _get_algorithms(self, 
            component: 'sourdough.Component') -> 'sourdough.Component':
        """
        
        """
        if isinstance(component, sourdough.Technique):
            component.algorithm = self.project.component.registry[
                component.algorithm]
        elif isinstance(component, sourdough.Task):
            component.technique.algorithm = self.project.component.registry[
                component.technique.algorithm]
        return component   
        