"""
editor: Workflow integrating settings while allowing runtime editing.
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
import copy
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
    
    # def __str__(self) -> str:
    #     return pprint.pformat(self.contents, sort_dicts = False, compact = True)


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
        print('test suffixes', suffixes)
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
        return tuple([item + 's' for item in project.components.keys()])
    
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
            structure = 'pipeline'
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
        deliverable = self._create_structure(
            name = root_key,
            project = project)
        print('test deliverable', deliverable)
        project.results['deliverable'] = deliverable
        return project     

    """ Private Methods """

    def _create_unknown(self, name: str,
                        project: sourdough.Project) -> sourdough.Structure:        
        try:
            return self._create_structure(name = name, project = project)
        except KeyError:
            try:
                return self._instance_component(name = name, project = project)
            except KeyError:
                raise KeyError(f'{name} component does not exist')   

    def _create_structure(self, name: str,
                          project: sourdough.Project) -> sourdough.Structure:
        structure = self._instance_structure(name = name, project = project)
        print('test structure', name, structure)
        new_structure_contents = []
        for item in structure:
            print('test item structure contents', name, item)
            new_structure_contents = self._create_unknown(
                name = item, 
                project = project)
        structure.conents = new_structure_contents
        return structure
    
    def _instance_structure(self, name: str, 
                            project: sourdough.Project) -> sourdough.Structure:
        details = project.results['outline'][name]
        kwargs = {'name': name, 'contents': details.contents}
        print('test kwargs', kwargs)
        try:
            instance = project.bases[details.base].registry[name](kwargs)
        except KeyError:
            try:
                instance = project.bases[details.base].registry[details.design](kwargs)
            except KeyError:
                raise KeyError(f'{name} structure cannot be found')
        print('test instance.contents', instance)
        return instance

    def _instance_component(self, name: str, 
                            project: sourdough.Project) -> sourdough.Structure:
        details = project.results['outline'][name]
        kwargs = {'name': name}
        try:
            instance = project.bases[details.base].registry[name](kwargs)
        except KeyError:
            try:
                instance = project.bases[details.base].registry[details.design](kwargs)
            except KeyError:
                try:
                    instance = copy.deepcopy(
                        project.bases['components'].library[name])
                    instance.name = name
                    instance.contents = details.contents
                except KeyError:
                    raise KeyError(f'{name} component cannot be found')
        return instance            

    def _add_attributes(self, 
            component: sourdough.Component,
            project: sourdough.Project,
            attributes: Mapping[str, Any]) -> sourdough.Component:
        """[summary]

        Returns:
            [type]: [description]
            
        """
        for key, value in attributes.items():
            if (project.settings['general']['settings_priority']
                    or not hasattr(component, key)):
                setattr(component, key, value)
        return component  


    # def _create_component(self, name: str, outline: Outline,
    #                       project: sourdough.Project) -> sourdough.Structure:
    #     """[summary]

    #     Args:
    #         name (str): [description]
    #         details (Details): [description]
    #         outline (Outline): [description]
    #         project (sourdough.Project): [description]

    #     Returns:
    #         sourdough.Structure: [description]
            
    #     """
    #     base = self._instance_component(
    #         name = name,
    #         base = outline[name].base,
    #         design = outline[name].design,
    #         contents = copy.deepcopy(outline[name].contents),
    #         project = project)
    #     base = self._add_attributes(
    #         component = base, 
    #         attributes = outline[name].attributes,
    #         project = project)
    #     if issubclass(base.__class__, sourdough.Structure):
    #         print('test yes substructure')
    #         print('test outline', outline)
    #         for item in base.contents:
    #             print('test outline', outline)
    #             # print('test base', name, base)
    #             # print('test outline[name]', outline[name])
    #             # print('test item', item)
    #             instance = self._create_component(
    #                 name = item,
    #                 outline = outline,
    #                 project = project)
    #             base.add(instance)
    #     else:
    #         print('test not structure')
    #         # print('test yes instance component', base)
    #         # print('test outline[name].base', outline[name].base)
    #         # print('test outline[name].contents', outline[name].contents)
    #         instance = self._instance_component(
    #             name = name,
    #             base = outline[name].base,
    #             design = outline[name].design,
    #             contents = copy.deepcopy(outline[name].contents),
    #             project = project)
    #         base.contents = instance
    #     return base

    # def _instance_component(self,
    #         name: str, 
    #         base: str,
    #         design: str,
    #         contents: Sequence[str],
    #         project: sourdough.Project) -> sourdough.Component:
    #     """[summary]

    #     Args:
    #         name (str): [description]
    #         details (sourdough.project.containers.Details): [description]
    #         project (sourdough.Project): [description]

    #     Raises:
    #         KeyError: [description]

    #     Returns:
    #         sourdough.Component: [description]
            
    #     """
    #     try:
    #         print('project.base', project.bases[base].registry)
    #         print('test easy lookup', base, name)
    #         instance = project.bases[base].instance(key = name)
    #     except KeyError:
    #         try:
    #             print('test instance lookup', base, name)
    #             instance = project.bases['component'].borrow(key = name)
    #         except KeyError:
    #             try:
    #                 print('test design lookup', base, name)
    #                 instance = project.bases[base].instance(
    #                     key = design, 
    #                     name = name)
    #             except KeyError:
    #                 raise KeyError('this class is screwed')
    #     if contents:
    #         instance.contents = contents
    #     return instance  
 
       
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
