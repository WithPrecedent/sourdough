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
class Workflow(sourdough.RegistryMixin, sourdough.Element, abc.ABC):
    """Base class for sourdough object creators.
    
    Args:
        project (sourdough.Project): the related Project instance.
    
    """
    name: str = None
    registry: ClassVar['sourdough.Inventory'] = sourdough.Inventory(
        defaults = ['draft', 'publish', 'apply'], 
        stored_types = ('Workflow'))
    
    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def create(self, item: object = None, **kwargs) -> object:
        """Performs some action related to passed 'item'.
        
        Subclasses must provide their own methods.
        
        """
        pass


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

        Returns:
            sourdough.Worker: an instance with contents organized.
                
        """
        # Creates an empty dict of attributes to add to 'worker'.
        attributes = {}
        # Finds and sets the 'role' of 'worker'.
        worker = self._add_role(worker = worker)
        # Divides settings into different subsections.
        settings, attributes = self._divide_settings(
            settings = self.project.settings[worker.name],
            role = worker.role) 
        # Organizes 'contents' of 'worker' according to its 'role'.
        worker.role.organize(settings = settings, project = self.project)
        # Adds an extra settings as attributes to worker.
        for key, value in attributes.items():
            setattr(worker, key, value)
        # Recursively calls method if other 'workers' are listed.
        new_workers = {
            k: v for k, v in settings.items() if k.endswith('_workers')}
        if len(new_workers) > 0: 
            new_workers = sourdough.utilities.listify(new_workers.values())[0]
            for new_worker in new_workers:
                # Checks if special prebuilt class exists.
                try:
                    component = self.project.component.build(key = new_worker)
                # Otherwise uses the appropriate generic type.
                except KeyError:
                    component = self.project.structures['worker'](
                        name = new_worker)
                worker.add(self.create(worker = component))
        return worker          

    """ Private Methods """

    def _add_role(self, worker: 'sourdough.Worker') -> 'sourdough.Worker':
        """
        """ 
        key = f'{worker.name}_role'
        try:    
            worker.role = self.project.settings[worker.name][key]
        except KeyError:
            pass
        return self.project.role.validate(worker = worker)

    def _divide_settings(self,
            settings: Mapping[Any, Any],
            role: 'sourdough.Role') -> Tuple[
                Mapping[Any, Any],
                Mapping[Any, Any]]:
        """

        Args:

        Returns:
            Tuple
        
        """
        component_settings = {}
        attributes = {}
        structures = self.project.structures.keys()
        for key, value in settings.items():
            # Stores settings related to available Element 'options' according
            # to 'role'.
            if any(key.endswith(f'_{s}s') for s in structures):
                component_settings[key] = sourdough.utilities.listify(value)
            # Stores other settings in 'attributes'.        
            elif not key.endswith('_role'):
                attributes[key] = value
        return component_settings, attributes
                
        
@dataclasses.dataclass
class Publish(Workflow):
    """Finalizes a composite object from user settings.
    
    Args:
        project (sourdough.Project): the related Project instance.
    
    """    
    project: 'sourdough.Project' = None  

    """ Public Methods """
 
    def create(self, worker: 'sourdough.Hybrid') -> 'sourdough.Hybrid':
        """Finalizes a worker with 'parameters' added.
        
        Args:
            worker (sourdough.Hybrid): Hybrid instance to finalize the objects in
                its 'contents'.

        Returns:
            sourdough.Hybrid: an instance with its 'contents' finalized and
                ready for application.
                
        """
        worker.apply(tool = self._set_parameters)
        return worker

    """ Private Methods """

    def _set_parameters(self, 
            element: 'sourdough.Element') -> 'sourdough.Element':
        """
        
        """
        if isinstance(element, sourdough.Technique):
            return self._set_technique_parameters(technique = element)
        elif isinstance(element, sourdough.Task):
            return self._set_task_parameters(task = element)
        else:
            return element
    
    def _set_technique_parameters(self, 
            technique: 'sourdough.Technique') -> 'sourdough.Technique':
        """
        
        """
        if technique.name not in ['none', None, 'None']:
            parameter_types = ['settings', 'selected', 'required', 'runtime']
            # Iterates through types of 'parameter_types'.
            for parameter_type in parameter_types:
                technique = getattr(self, f'_get_{parameter_type}')(
                    technique = technique)
        return technique
    
    def _set_task_parameters(self, task: 'sourdough.Task') -> 'sourdough.Task':
        """
        
        """
        if task.technique.name not in ['none', None, 'None']:
            task = self._get_settings(technique = task)
            try:
                task._set_conditional_parameters()
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

    def _get_selected(self,
            technique: 'sourdough.Technique') -> 'sourdough.Technique':
        """Limits parameters to those appropriate to the technique.

        Args:
            technique (technique): an instance for parameters to be selected.

        Returns:
            technique: instance with parameters selected.

        """
        if technique.selected:
            new_parameters = {}
            for key, value in technique.parameters.items():
                if key in technique.selected:
                    new_parameters[key] = value
            technique.parameters = new_parameters
        return technique

    def _get_required(self,
            technique: 'sourdough.Technique') -> 'sourdough.Technique':
        """Adds required parameters (mandatory additions) to 'parameters'.

        Args:
            technique (technique): an instance for parameters to be added to.

        Returns:
            technique: instance with parameters added.

        """
        try:
            technique.parameters.update(technique.required)
        except TypeError:
            pass
        return technique

    def _get_runtime(self,
            technique: 'sourdough.Technique') -> 'sourdough.Technique':
        """Adds parameters that are determined at runtime.

        The primary example of a runtime parameter throughout sourdough is the
        addition of a random seed for a consistent, replicable state.

        Args:
            technique (technique): an instance for parameters to be added to.

        Returns:
            technique: instance with parameters added.

        """
        try:
            for key, value in technique.runtime.items():
                try:
                    technique.parameters.update(
                        {key: getattr(self.project.settings['general'], value)})
                except AttributeError:
                    raise AttributeError(' '.join(
                        ['no matching runtime parameter', key, 'found']))
        except (AttributeError, TypeError):
            pass
        return technique


@dataclasses.dataclass
class Apply(Workflow):
    
    project: 'sourdough.Project' = None  
    
    def create(self, worker: 'sourdough.Hybrid') -> 'sourdough.Hybrid':
        """[summary]

        Returns:
            [type] -- [description]
            
        """
        # worker.apply(tool = self._add_data_dependent)
        # if self.project.data is None:
        #     worker.perform()
        # else:
        #     self.project.data = worker.perform(item = self.project.data)
        return worker

    """ Private Methods """
        
    def _get_data_dependent(self,
            element: 'sourdough.Element') -> 'sourdough.Element':
        """Gets parameters that are derived from data.

        Args:
            technique (technique): an instance for parameters to be added to.

        Returns:
            technique: instance with parameters added.

        """
        if isinstance(element, sourdough.Task):
            element.technique = self._add_data_dependent(
                technique = element.technique)
        elif isinstance(element, sourdough.Technique):
            element = self._add_data_dependent(technique = element)
        return element

    def _add_data_dependent(self,
            technique: 'sourdough.Technique') -> 'sourdough.Technique':
        """Adds parameters that are derived from data.

        Args:
            technique (technique): an instance for parameters to be added to.

        Returns:
            technique: instance with parameters added.

        """
        try:
            for key, value in technique.data_dependent.items():
                try:
                    technique.parameters.update(
                        {key: getattr(self.project.data, value)})
                except KeyError:
                    print('no matching parameter found for', key, 'in data')
        except (AttributeError, TypeError):
            pass
        return technique
    