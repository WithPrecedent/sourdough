"""
workflows: classes used for project process and object creation and application
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)


Draft: Settings => Outline
Publish: Outline => Structure
Apply: Structure + Data => Structure + Data

Contents:
    Draft (Stage): creates a Hybrid instance from passed arguments and/or a 
        Settings instance.
    Publish (Stage): finalizes a Hybrid instance based upon the initial
        construction by an Draft instance and/or runtime user editing.
    Apply (Stage): executes a Hybrid instance, storing changes and results
        in the Apply instance and/or passed data object.

"""
from __future__ import annotations
import abc
import dataclasses
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Union)

import sourdough


@dataclasses.dataclass
class Details(sourdough.Slate):
    """Basic characteristics of a group of sourdough Components.
    
    Args:
        contents (Mapping[Any, Any]]): stored dictionary. Defaults to an empty 
            dict.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Element is called, 'name' is set based upon
            the 'get_name' method in Element. If that method is not overridden 
            by a subclass instance, 'name' will be assigned to the snake case 
            version of the class name ('__class__.__name__'). 
        
    """
    contents: Sequence[str] = dataclasses.field(default_factory = list)
    generic: str = None
    structure: str = None
    attributes: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    name: str = None
    
    """ Public Methods """
    
    def validate(self, contents: Union[str, Sequence[str]]) -> Sequence[str]:
        """Validates 'contents' or converts 'contents' to a list.
        
        Args:
            contents (Sequence[str]): variable to validate as compatible with 
                an instance.
            
        Raises:
            TypeError: if 'contents' argument is not of a supported datatype.
            
        Returns:
            Sequence[str]: validated or converted argument that is compatible 
                with an instance.
        
        """
        if isinstance(contents, str):
            return sourdough.tools.listify(contents)
        elif (isinstance(contents, Sequence) 
                and all(isinstance(c, str) for c in contents)):
            return contents
        else:
            raise TypeError('contents must be a str of list of str types')

 
@dataclasses.dataclass
class Overview(sourdough.Lexicon):
    """Dictionary of different Element types in a Structure instance.
    
    Args:
        contents (Mapping[Any, Any]]): stored dictionary. Defaults to an empty 
            dict.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Element is called, 'name' is set based upon
            the 'get_name' method in Element. If that method is not overridden 
            by a subclass instance, 'name' will be assigned to the snake case 
            version of the class name ('__class__.__name__').
              
    """
    contents: Mapping[Any, Any] = dataclasses.field(default_factory = dict)
    name: str = None
    
    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent initialization method(s).
        super().__post_init__()
        if self.structure.structure is not None:
            self.add({
                'name': self.structure.name, 
                'structure': self.structure.structure.name})
            for key, value in self.structure.structure.options.items():
                matches = self.structure.find(
                    self._get_type, 
                    element = value)
                if len(matches) > 0:
                    self.contents[f'{key}s'] = matches
        else:
            raise ValueError(
                'structure must be a Role for an overview to be created.')
        return self          
    
    """ Dunder Methods """
    
    def __str__(self) -> str:
        """Returns pretty string representation of an instance.
        
        Returns:
            str: pretty string representation of an instance.
            
        """
        new_line = '\n'
        representation = [f'sourdough {self.get_name}']
        for key, value in self.contents.items():
            if isinstance(value, Sequence):
                names = [v.name for v in value]
                representation.append(f'{key}: {", ".join(names)}')
            else:
                representation.append(f'{key}: {value}')
        return new_line.join(representation)    

    """ Private Methods """

    def _get_type(self, 
            item: sourdough.Element, 
            element: sourdough.Element) -> Sequence[sourdough.Element]: 
        """[summary]

        Args:
            item (self.stored_types): [description]
            self.stored_types (self.stored_types): [description]

        Returns:
            Sequence[self.stored_types]:
            
        """
        if isinstance(item, element):
            return [item]
        else:
            return []


@dataclasses.dataclass
class Outline(sourdough.Lexicon):
    """Base class for pieces of sourdough composite objects.
    
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Element is called, 'name' is set based upon
            the 'get_name' method in Element. If that method is not overridden 
            by a subclass instance, 'name' will be assigned to the snake case 
            version of the class name ('__class__.__name__'). 
        library (ClassVar[sourdough.Catalog]): the instance which 
            automatically stores any subclass of Component.
              
    """
    contents: Mapping[str, Details] = dataclasses.field(default_factory = dict)
    generic: str = None
    name: str = None
        
    """ Public Methods """
    
    def validate(self, 
            contents: Mapping[str, Details]) -> Mapping[str, Details]:
        """Validates 'contents' or converts 'contents' to a dict.
        
        Args:
            contents (Mapping[str, Details]): variable to validate as compatible 
                with an instance.
            
        Raises:
            TypeError: if 'contents' argument is not of a supported datatype.
            
        Returns:
            Mapping[str, Details]: validated or converted argument that is 
                compatible with an instance.
        
        """
        if (isinstance(contents, Mapping) 
                and all(isinstance(c, Details) for c in contents.values())):
            return contents
        else:
            raise TypeError(
                'contents must be a dict type with Details type values')


@dataclasses.dataclass
class Draft(sourdough.Stage):
    """Constructs an Outline instance from a project's settings.
    
    Args:
        project (sourdough.Project): the related Project instance.
    
    """
    name: str = None
    
    """ Public Methods """
    
    def perform(self, project: sourdough.Project) -> sourdough.Project:
        """Drafts an Outline instance based on 'settings'.

        Args:
            settings (sourdough.Settings): [description]

        Returns:
            sourdough.Outline: [description]
            
        """       
        components = self._get_all_components(project = project)
        project.results['outline']  = self._create_outline(
            components = components, 
            project = project)
        return project
        
    """ Private Methods """

    def _get_all_components(self, project: sourdough.Project) -> Dict[str, Sequence[str]]:
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
                    component_names[key] = sourdough.tools.listify(value)
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
    
    def _divide_key(self, key: str) -> Sequence[str, str]:
        """[summary]

        Args:
            key (str): [description]

        Returns:
            
            Sequence[str, str]: [description]
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
class Publish(sourdough.Stage):
    """Finalizes a composite object from user settings.
    
    Args:
        project (sourdough.Project): the related Project instance.
    
    """    
    name: str = None 

    
    """ Public Methods """
 
    def perform(self, project: sourdough.Project) -> sourdough.Project:
        """Drafts an Outline instance based on 'settings'.

        Args:
            settings (sourdough.Settings): [description]

        Returns:
            sourdough.Outline: [description]
            
        """
        root_key = project.results['outline'].keys()[0]
        root_value = project.results['outline'][root_key]
        project.results['deliverable'] = self. self._create_composite(
            name = root_key,
            details = root_value,
            project = project)
        return project     

    """ Private Methods """

    def _create_composite(self,
            name: str, 
            details: sourdough.project.containers.Details,
            project: sourdough.Project) -> sourdough.Component:
        """[summary]

        Args:
            name (str): [description]
            details (sourdough.project.containers.Details): [description]
            outline (sourdough.Outline): [description]
            project (sourdough.Project): [description]

        Returns:
            sourdough.Component: [description]
        """
        base = self._create_component(
            name = name,
            generic = details.generic,
            project = project)
        base = self._add_attributes(
            component = base, 
            attributes = details.attributes)
        base.organize()
        for item in details:
            if item in project.outline:
                value = project.outline[item]
                generic = project.components.library[value.generic]
                if issubclass(generic, sourdough.project.structures.Structure):
                    instance = self._create_composite(
                        name = item,
                        details = value,
                        project = project)
                else:
                    instance = self._create_clones(
                        name = item,
                        details = value,
                        project = project)
            else:
                instance = self._create_component(
                    name = item,
                    generic = details.generic,
                    project = project)
            base.add(instance)
        return base

    def _create_component(self,
            name: str, 
            generic: str,
            project: sourdough.Project) -> sourdough.Component:
        """[summary]

        Args:
            name (str): [description]
            details (sourdough.project.containers.Details): [description]
            project (sourdough.Project): [description]

        Raises:
            KeyError: [description]

        Returns:
            sourdough.Component: [description]
            
        """
        try:
            instance = project.components.instance(key = name)
        except KeyError:
            try:
                instance = project.structures.instance(
                    key = generic, 
                    name = name)
            except KeyError:
                raise KeyError(
                    f'No Component or Structure was found matching {name}')
        return instance  
    
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
        elif isinstance(component, sourdough.Step):
            component.technique = self._get_technique(
                technique = component.technique,
                **kwargs)
        return component   

    def _get_technique(self, 
            technique: sourdough.Technique,
            **kwargs) -> sourdough.Technique:
        """
        
        """
        return self.project.component.instance(technique, **kwargs)
       
    def _set_parameters(self, 
            component: sourdough.Component) -> sourdough.Component:
        """
        
        """
        if isinstance(component, sourdough.Technique):
            return self._set_technique_parameters(technique = component)
        elif isinstance(component, sourdough.Step):
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
    
    def _set_task_parameters(self, task: sourdough.Step) -> sourdough.Step:
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
                sourdough.Step]) -> Union[
                    sourdough.Technique, 
                    sourdough.Step]:
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

    def _create_Structures(self, 
            Structures: Sequence[str],
            suffix: str,
            **kwargs) -> Sequence[sourdough.Structure]:
        """[summary]

        Returns:
            [type]: [description]
        """
        new_Structures = []
        for Structure in Structures:
            # Checks if special prebuilt class exists.
            try:
                component = self.project.components.instance(
                    key = Structure, 
                    **kwargs)
            # Otherwise uses the appropriate generic type.
            except KeyError:
                generic = self.project.components._suffixify()[suffix]
                kwargs.update({'name': Structure})
                component = generic(**kwargs)
            component = self.create(Structure = component)
            new_Structures.append(component)
        return new_Structures
        

    def _get_Structure_suffixes(self) -> Sequence[str]:
        """[summary]

        Args:
            component (sourdough.Component): [description]

        Returns:
            Sequence[str]: [description]
            
        """
        components = self.project.components._suffixify()
        return [
            k for k, v in components.items() if isinstance(v, sourdough.Structure)]

    def _create_composite(self, 
            settings: Mapping[str, Sequence[str]]) -> Mapping[
                Sequence[str, str], 
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

    def _get_algorithms(self, 
            component: sourdough.Component) -> sourdough.Component:
        """
        
        """
        if isinstance(component, sourdough.Technique):
            component.algorithm = self.project.component.library[
                component.algorithm]
        elif isinstance(component, sourdough.Step):
            component.technique.algorithm = self.project.component.library[
                component.technique.algorithm]
        return component   
     
                
@dataclasses.dataclass
class Apply(sourdough.Stage):
    
    workflow: sourdough.Workflow = None
    name: str = None 
    
    def perform(self, project: sourdough.Project) -> sourdough.Project:
        """[summary]

        Returns:
            [type] -- [description]
            
        """
        kwargs = {}
        if project.data is not None:
            kwargs['data'] = project.data
        for component in project.results['deliverable']:
            component.apply(**kwargs)
        return project


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
    contents: Sequence[sourdough.Element] = dataclasses.field(
        default_factory = lambda: [Draft, Publish, Apply])
    results: Mapping[str, Any] = dataclasses.field(
        default_factory = sourdough.Catalog)
    name: str = None
