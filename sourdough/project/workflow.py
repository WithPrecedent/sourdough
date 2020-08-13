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
from __future__ import annotations
import dataclasses
from typing import (Any, Callable, ClassVar, Container, Generic, Iterable, 
                    Iterator, Mapping, Sequence, Tuple, TypeVar, Union)

import sourdough


@dataclasses.dataclass
class Workflow(sourdough.RegistryMixin, sourdough.Hybrid):
    """Base class for sourdough object creators.
    
    Args:
        project (sourdough.Project): the related Project instance.
        
    """
    contents: Sequence[sourdough.Action] = dataclasses.field(
        default_factory = list)
    project: sourdough.Project = None
    name: str = None
    registry: ClassVar[sourdough.Inventory] = sourdough.Inventory()

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent initialization method(s).
        super().__post_init__()
        # Validates 'roles'.
        self._validate_roles()
    
    """ Public Methods """
    
    def validate(self, contents: Any) -> Any:
        """
        """
        if isinstance(contents, self.contains):
            return contents
        else:
            raise TypeError(f'contents must be {str(self.contains)} types') 
    
    """ Private Methods """

    def _create_component(self, 
            name: str, 
            base: str,
            **kwargs) -> sourdough.Component:
        """[summary]

        Returns:
            [type]: [description]
            
        """
        # Checks if special prebuilt class exists.
        try:
            component = self.project.components.build(key = name, **kwargs)
        # Otherwise uses the appropriate generic type.
        except KeyError:
            kwargs.update({'name': name})
            component = self.project.components.build(key = base, **kwargs)
        return component
        

@dataclasses.dataclass
class Draft(sourdough.Action):
    """Constructs composite objects from user settings.
    
    Args:
        project (sourdough.Project): the related Project instance.
    
    """
    workflow: Workflow = None
    name: str = None 
    
    """ Public Methods """
    
    def perform(self, 
            worker: sourdough.Worker,
            settings: sourdough.Settings) -> sourdough.Worker:
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
        role, settings, attributes = self._divide_settings(
            settings = self.project.settings[worker.name]) 
        # If 'role' is found in the relevant settings, it is added to 'worker'.
        if role:
            worker.role = role
        # Adds extra settings as attributes to worker.
        worker = self._add_attributes(
            component = worker, 
            attributes = attributes)
        # # Gets a dict of all components identified in 'settings'.
        # components = self._get_components(settings = settings)
        # Organizes the 'components' and adds them to 'worker' based on 
        # 'worker.role'.
        # role = self._get_role(name = worker.role)
        worker = self._add_outline(
            worker = worker,
            settings = settings)
        first_suffix = settings.keys()[0]
        first_components = settings[first_suffix]
        if first_suffix.split('_')[-1] in self._get_worker_suffixes():
            self._create_workers(workers = settings[first_suffix])
            
        # worker = role.organize(worker = worker, components = components)
        return worker          

    """ Private Methods """

    def _divide_settings(self,
            settings: Mapping[Any, Any]) -> Tuple[
                str,
                Mapping[Any, Any],
                Mapping[Any, Any]]:
        """Divides 'settings' into component and attribute related settings.

        Args:
            settings (Mapping[Any, Any]):
            
        Returns:
            Tuple[Mapping[Any, Any], Mapping[Any, Any]]:
        
        """
        role = None
        component_settings = {}
        attributes = {}
        # Gets names of suffixes for available Component subclasses.
        suffixes = tuple(self._get_container_suffixes())
        for key, value in settings.items():
            if key.endswith('_role'):
                role = value
            elif key.endswith(suffixes):
                component_settings[key] = sourdough.utilities.listify(value)       
            else:
                attributes[key] = value
        return role, component_settings, attributes
     
    def _get_container_suffixes(self) -> Sequence[str]:
        """[summary]

        Args:
            component (sourdough.Component): [description]

        Returns:
            Sequence[str]: [description]
            
        """
        components = self.project.components._suffixify()
        return [k for k, v in components.items() if v.contains]
    
    def _add_attributes(self, 
            component: sourdough.Component,
            attributes: Mapping[str, Any]) -> sourdough.Component:
        """[summary]

        Returns:
            [type]: [description]
            
        """
        for key, value in attributes.items():
            setattr(component, key, value)
        return component   

    # def _add_outline(self, 
    #         worker: sourdough.Worker,
    #         settings: Mapping[str, Sequence[str]]) -> sourdough.Worker:
    #     """[summary]

    #     Returns:
    #         [type]: [description]
    #     """
    #     outline = sourdough.Outline(name = name)
    #     for key, value in settings.items():
    #         prefix, base = self._divide_key(key = key)
    #         for item in value:
    #             bases[prefix] = base
    #             components[prefix] = self._create_component(
    #                 name = item, 
    #                 base = base)
    #     return components  

    def _create_workers(self, 
            workers: Sequence[str],
            suffix: str,
            **kwargs) -> Sequence[sourdough.Worker]:
        """[summary]

        Returns:
            [type]: [description]
        """
        new_workers = []
        for worker in workers:
            # Checks if special prebuilt class exists.
            try:
                component = self.project.components.build(
                    key = worker, 
                    **kwargs)
            # Otherwise uses the appropriate generic type.
            except KeyError:
                generic = self.project.components._suffixify()[suffix]
                kwargs.update({'name': worker})
                component = generic(**kwargs)
            component = self.create(worker = component)
            new_workers.append(component)
        return new_workers
        

    def _get_worker_suffixes(self) -> Sequence[str]:
        """[summary]

        Args:
            component (sourdough.Component): [description]

        Returns:
            Sequence[str]: [description]
            
        """
        components = self.project.components._suffixify()
        return [
            k for k, v in components.items() if isinstance(v, sourdough.Worker)]

    def _get_components(self, 
            settings: Mapping[str, Sequence[str]]) -> Mapping[
                Tuple[str, str], 
                Sequence[sourdough.Component]]:
        """[summary]

        Returns:
            [type]: [description]
        """
        components = {}
        bases = {}
        for key, value in settings.items():
            prefix, base = self._divide_key(key = key)
            for item in value:
                bases[prefix] = base
                components[prefix] = self._create_component(
                    name = item, 
                    base = base)
        return components   

    def _divide_key(self, key: str) -> Tuple[str, str]:
        """[summary]

        Args:
            key (str): [description]

        Returns:
            Tuple[str, str]: [description]
        """
        suffix = key.split('_')[-1][:-1]
        prefix = key[:-len(suffix) - 2]
        return prefix, suffix
                
        
@dataclasses.dataclass
class Publish(sourdough.Action):
    """Finalizes a composite object from user settings.
    
    Args:
        project (sourdough.Project): the related Project instance.
    
    """    
    workflow: Workflow = None
    name: str = None 

    """ Public Methods """
 
    def perform(self, worker: sourdough.Worker) -> sourdough.Worker:
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
            component: sourdough.Component,
            **kwargs) -> sourdough.Component:
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
            technique: sourdough.Technique,
            **kwargs) -> sourdough.Technique:
        """
        
        """
        return self.project.component.build(technique, **kwargs)
       
    def _set_parameters(self, 
            component: sourdough.Component) -> sourdough.Component:
        """
        
        """
        if isinstance(component, sourdough.Technique):
            return self._set_technique_parameters(technique = component)
        elif isinstance(component, sourdough.Task):
            return self._set_task_parameters(task = component)
        else:
            return component
    
    def _set_technique_parameters(self, 
            technique: sourdough.Technique) -> sourdough.Technique:
        """
        
        """
        if technique.name not in ['none', None, 'None']:
            technique = self._get_settings(technique = technique)
        return technique
    
    def _set_task_parameters(self, task: sourdough.Task) -> sourdough.Task:
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
                sourdough.Technique, 
                sourdough.Task]) -> Union[
                    sourdough.Technique, 
                    sourdough.Task]:
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
class Apply(sourdough.Action):
    
    workflow: Workflow = None
    name: str = None 
    
    def perform(self, worker: sourdough.Worker) -> sourdough.Worker:
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
            component: sourdough.Component) -> sourdough.Component:
        """
        
        """
        if isinstance(component, sourdough.Technique):
            component.algorithm = self.project.component.registry[
                component.algorithm]
        elif isinstance(component, sourdough.Task):
            component.technique.algorithm = self.project.component.registry[
                component.technique.algorithm]
        return component   


@dataclasses.dataclass
class Editor(Workflow):
    """Three-step workflow that allows user editing and easy serialization.
    
    Args:
        contents (Union[Element, Mapping[Any, Element], 
            Sequence[Element]]): Element subclasses or Element subclass 
            instances to store in a list. If a dict is passed, the keys will be 
            ignored and only the values will be added to 'contents'. Defaults to 
            an empty list.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Element is called, 'name' is set based upon
            the '_get_name' method in Element. If that method is not 
            overridden by a subclass instance, 'name' will be assigned to the 
            snake case version of the class name ('__class__.__name__').
        
    """
    contents: Sequence[sourdough.Action] = dataclasses.field(
        default_factory = lambda: [Draft, Publish, Apply])
    project: sourdough.Project = None 
    name: str = None
     
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent initialization method(s).
        super().__post_init__()
        # Validates 'roles'.
        self._validate_roles()

    """ Public Methods """
    
    def perform(self, item: object = None, **kwargs) -> object:
        """Performs some action related to passed 'item'.
        
        Subclasses must provide their own methods.
        
        """
        pass
  
    """ Private Methods """
    