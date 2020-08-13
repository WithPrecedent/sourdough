"""
editor: sourdough editor workflow for project creation and iteration
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
class Draft(sourdough.Flow):
    """Constructs an Outline instance from a project's settings.
    
    Args:
        project (sourdough.Project): the related Project instance.
    
    """
    name: str = None
    needs: Sequence[str] = dataclasses.field(
        default_factory = lambda: ['project']) 
    
    """ Public Methods """
    
    def perform(self, project: sourdough.Project) -> sourdough.Outline:
        """Drafts an Outline instance based on 'settings'.

        Args:
            settings (sourdough.Settings): [description]

        Returns:
            sourdough.Outline: [description]
            
        """       
        components = self._get_all_components(project = project)
        return self._create_outline(components = components, project = project)        

    """ Private Methods """

    def _get_all_components(self, 
            project: sourdough.Project) -> Mapping[str, Sequence[str]]:
        """[summary]

        Args:
            key (str): [description]
            settings (sourdough.Settings): [description]

        Returns:
            sourdough.Outline: [description]
            
        """
        suffixes = project.components._suffixify().keys()
        component_names = {}
        for section in project.settings.values():
            for key, value in section.items():
                if key.startswith(key) and key.endswith(suffixes):
                    component_names[key] = sourdough.utilities.listify(value)
        return component_names
        
    def _create_outline(self, 
            components: Mapping[str, Sequence[str]], 
            project: sourdough.Project) -> sourdough.Outline:
        """[summary]

        Args:
            key (str): [description]
            settings (sourdough.Settings): [description]

        Returns:
            sourdough.Outline: [description]
            
        """
        outline = sourdough.project.containers.Outline()  
        for key, value in components.items():
            name, generic = self._divide_key(key = key)
            structure = self._get_structure(
                name = name, 
                settings = project.settings)
            attributes = self._get_attributes(name = name, project = project) 
            details = sourdough.project.containers.Details(
                    contents = value,
                    generic = generic, 
                    structure = structure,
                    attributes = attributes)
            outline.add({name: details})
        return outline
    
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

    def _get_structure(self, name: str, settings: sourdough.Settings) -> str:
        """[summary]

        Args:
            name (str): [description]
            settings (sourdough.Settings): [description]

        Returns:
            str: [description]
            
        """
        try:
            structure = settings[name][f'{name}_structure']
        except KeyError:
            structure = 'pipeline'
        return structure

    def _get_attributes(self, 
            name: str, 
            project: sourdough.Project) -> Mapping[str, Any]:
        """[summary]

        Args:
            name (str): [description]
            settings (sourdough.Settings): [description]

        Returns:
            Mapping[str, Any]: [description]
            
        """
        suffixes = project.components._suffixify().keys()
        attributes = {}
        for key, value in project.settings[name].items():
            if not key.endswith('_structure') and not key.endswith(suffixes):
                attributes[key] = value
        return attributes

        
@dataclasses.dataclass
class Publish(sourdough.project.workflow.Flow)):
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

                

@dataclasses.dataclass
class Apply(sourdough.project.workflow.Flow)):
    
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
            instance.structure.finalize()
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
class Editor(sourdough.Workflow):
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
    results: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    name: str = None
