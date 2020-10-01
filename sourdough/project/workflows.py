"""
workflows: classes used for project process and object creation and application
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Details (Slate):
    Outline (Lexicon):
    Draft (Stage): creates a Hybrid instance from passed arguments and/or a 
        Settings instance.
    Publish (Stage): finalizes a Hybrid instance based upon the initial
        construction by an Draft instance and/or runtime user editing.
    Apply (Stage): executes a Hybrid instance, storing changes and results
        in the Apply instance and/or passed data object.
    Editor (Workflow):

"""
from __future__ import annotations
import abc
import dataclasses
import pprint
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
    name: str = None
    contents: Sequence[str] = dataclasses.field(default_factory = list)
    base: str = None
    contains: str = None
    design: str = None
    attributes: Mapping[str, Any] = dataclasses.field(default_factory = dict)

    """ Dunder Methods """

    def __str__(self) -> str:
        return pprint.pformat(self, sort_dicts = False, compact = True)


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
    name: str = None
    project: sourdough.Project = dataclasses.field(repr = False, default = None) 

    """ Dunder Methods """

    def __str__(self) -> str:
        return pprint.pformat(self.contents, sort_dicts = False, compact = True)


@dataclasses.dataclass
class Draft(sourdough.Stage):
    """Constructs an Outline instance from a project's settings.
    
    Args:
        project (sourdough.Project): the related Project instance.
    
    """
    action: str = 'drafting'
    
    """ Public Methods """
    
    def perform(self, project: sourdough.Project) -> sourdough.Project:
        """Drafts an Outline instance based on 'settings'.

        Args:
            settings (sourdough.Settings): [description]

        Returns:
            sourdough.Outline: [description]
            
        """       
        suffixes = self._get_component_suffixes(project = project)
        outline  = self._create_outline(project = project, suffixes = suffixes)
        self._set_product(name = 'outline', project = project, product = outline)
        print('test project outline', project.results['outline'])
        return project
        
    """ Private Methods """

    def _get_component_suffixes(self, project: sourdough.Project) -> Tuple[str]:
        """[summary]

        Args:
            key (str): [description]
            settings (sourdough.Settings): [description]

        Returns:
            sourdough.Outline: [description]
            
        """
        return tuple([item + 's' for item in project.bases.keys()])
    
    def _create_outline(self, project: sourdough.Project, 
                        suffixes: Tuple[str]) -> Outline:
        """[summary]

        Args:
            project (sourdough.Project): [description]
            suffixes (Tuple[str]): [description]

        Returns:
            Outline: [description]
            
        """
        outline = Outline(
            project = project,
            name = f'{project.name}_outline')
        for section in project.settings.values():
            for key, value in section.items():
                if key.endswith(suffixes):
                    name, suffix = self._divide_key(key = key)
                    contains = suffix.rstrip('s')
                    attributes = self._get_attributes(
                        name = name, 
                        project = project,
                        suffixes = suffixes)
                    outline[name] = Details(
                        name = name,
                        base = self._get_base(name = name, outline = outline),
                        contains = contains,
                        design = self._get_design(name = name, project = project),
                        contents = sourdough.tools.listify(value),
                        attributes = attributes)
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

    def _get_design(self, name: str, project: sourdough.Project) -> str:
        """[summary]

        Args:
            name (str): [description]
            project (sourdough.Project): [description]

        Returns:
            str: [description]
            
        """
        try:
            structure = project.settings[name][f'{name}_design']
        except KeyError:
            structure = None
        return structure

    def _get_attributes(self, name: str, project: sourdough.Project,
                        suffixes: Tuple[str]) -> Mapping[str, Any]:
        """[summary]

        Args:
            name (str): [description]
            project (sourdough.Project): [description]
            suffixes (Tuple[str]):

        Returns:
            Mapping[str, Any]: [description]
            
        """
        attributes = {}
        try:
            for key, value in project.settings[name].items():
                if not (key.endswith(suffixes) 
                        or key.endswith('_design')
                        or key.endswith('workflow')):
                    attributes[key] = value
        except KeyError:
            pass
        return attributes

    def _get_base(self, name: str, outline: Outline) -> str:
        """[summary]

        Args:
            name (str): [description]
            outline (Outline): [description]

        Returns:
            str: [description]
        """
        base = 'design'
        for key, details in outline.items():
            if name in details:
                base = details.contains
        return base
       
    
@dataclasses.dataclass
class Publish(sourdough.Stage):
    """Finalizes a composite object from user settings.
    
    Args:
        project (sourdough.Project): the related Project instance.
    
    """    
    action: str = 'publishing' 
    
    """ Public Methods """
 
    def perform(self, project: sourdough.Project) -> sourdough.Project:
        """Drafts an Outline instance based on 'settings'.

        Args:
            settings (sourdough.Settings): [description]

        Returns:
            sourdough.Outline: [description]
            
        """
        outline = project.results['outline']
        root_key = list(outline.keys())[0]
        root_details = outline[root_key]        
        project.results['deliverable'] = self._create_deliverable(
            name = root_key,
            details = root_details,
            outline = outline,
            project = project)
        print('test deliverable', project.results['deliverable'])
        return project     

    """ Private Methods """

    def _create_deliverable(self, name: str, details: Details, outline: Outline,
                            project: sourdough.Project) -> sourdough.Structure:
        """[summary]

        Args:
            name (str): [description]
            details (Details): [description]
            outline (Outline): [description]
            project (sourdough.Project): [description]

        Returns:
            sourdough.Structure: [description]
            
        """
        
        base = self._create_component(
            name = name,
            base = details.base,
            contents = details.contents,
            project = project)
        print('test base', name, base)
        base = self._add_attributes(
            component = base, 
            attributes = details.attributes)
        for item in details:
            if item in outline:
                inner_details = outline[item]
                inner_base = project.bases[inner_details.base]
                instance = self._create_deliverable(
                    name = item,
                    details = inner_details,
                    outline = outline,
                    project = project)
                base.add(instance)
                # if issubclass(base, sourdough.Structure):
                #     instance = self._create_composite(
                #         name = item,
                #         details = inner_details,
                #         project = project)
                # else:
                #     instance = self._create_clones(
                #         name = item,
                #         details = value,
                #         project = project)
            else:
                instance = self._create_component(
                    name = item,
                    base = details.base,
                    contents = details.contents,
                    project = project)
                base.contents = instance
        return base

    def _create_component(self,
            name: str, 
            base: str,
            contents: Sequence[str],
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
            instance = project.bases[base].instance(
                key = name, 
                contents = contents)
        except (AttributeError, KeyError):
            try:
                instance = project.bases['component'].borrow(key = name)
                if contents:
                    instance.contents = contents
            except KeyError:
                instance = project.bases[base](name = name, contents = contents)
                
                # raise KeyError(
                #     f'No Component or Structure was found matching {name}')
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
       
    # def _set_parameters(self, 
    #         component: sourdough.Component) -> sourdough.Component:
    #     """
        
    #     """
    #     if isinstance(component, sourdough.Technique):
    #         return self._set_technique_parameters(technique = component)
    #     elif isinstance(component, sourdough.Step):
    #         return self._set_task_parameters(task = component)
    #     else:
    #         return component
    
    # def _set_technique_parameters(self, 
    #         technique: sourdough.Technique) -> sourdough.Technique:
    #     """
        
    #     """
    #     if technique.name not in ['none', None, 'None']:
    #         technique = self._get_settings(technique = technique)
    #     return technique
    
    # def _set_task_parameters(self, task: sourdough.Step) -> sourdough.Step:
    #     """
        
    #     """
    #     if task.technique.name not in ['none', None, 'None']:
    #         task = self._get_settings(technique = task)
    #         try:
    #             task.set_conditional_parameters()
    #         except AttributeError:
    #             pass
    #         task.technique = self._set_technique_parameters(
    #             technique = task.technique)
    #     return task  
     
                
@dataclasses.dataclass
class Apply(sourdough.Stage):
    
    action: str = 'application' 

    """ Public Methods """
        
    def perform(self, project: sourdough.Project) -> sourdough.Project:
        """[summary]

        Returns:
            [type] -- [description]
            
        """
        kwargs = {}
        if project.data is not None:
            kwargs['data'] = project.data
        for component in project.results['deliverable']:
            component.perform(**kwargs)
        return project


@dataclasses.dataclass
class Editor(sourdough.Workflow):
    """Three-step workflow that allows user editing and easy serialization.
    
    Args:
        contents (Sequence[Union[str, Stage]]): a list of str or Stages. 
            Defaults to an empty list.
        project (sourdough.Project): related project instance.
        
    """
    contents: Sequence[Union[str, sourdough.Stage]] = dataclasses.field(
        default_factory = lambda: [Draft, Publish, Apply])
    project: sourdough.Project = None
    name: str = None
