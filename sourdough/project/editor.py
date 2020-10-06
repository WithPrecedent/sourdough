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
    contents: Sequence[str] = dataclasses.field(default_factory = list)
    name: str = None
    base: str = None
    contains: str = None
    design: str = None
    parameters: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    attributes: Mapping[str, Any] = dataclasses.field(default_factory = dict)

    """ Dunder Methods """

    def __str__(self) -> str:
        return pprint.pformat(self, sort_dicts = False, compact = True)


@dataclasses.dataclass
class Outline(sourdough.Lexicon):
    """Output of the the drafting process.

    Outline is a dictionary representation of the overall project design. All
    Components are listed by key names and the information needed for Component
    construction are stored in Details instances.
    
    Args:
              
    """
    contents: Mapping[str, Details] = dataclasses.field(default_factory = dict)
    project: sourdough.Project = dataclasses.field(repr = False, default = None) 
    _bases: Mapping[str, str] = dataclasses.field(
        repr = False, 
        default_factory = dict)

    """ Dunder Methods """
    
    def __str__(self) -> str:
        return pprint.pformat(self, sort_dicts = False, compact = True)


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
        outline = Outline(project = project)
        for name in project.settings.key():     
            outline = self._process_section(
                name = name,
                outline = outline,
                project = project)
        project.design = outline
        print('test project outline', project.design)
        return project
        
    """ Private Methods """
    
    def _process_section(self, name: str, outline: Outline, 
                         project: sourdough.Project) -> Outline:
        if name not in outline:
            outline[name] = Details(name = name)   
        for key, value in outline[name].items():
            if key.endswith(tuple(project.hierarchy.keys())):
                key_name, key_suffix = self._divide_key(key = key)
                kind = key_suffix.rstrip('s')
                contents = sourdough.tools.listify(value)
                if key_name == name:
                    outline[name].contents = contents
                    outline[name].contains = kind
                for item in contents:
                    outline = self._process_components(
                        name = key_name,
                        base = kind,
                        contents = contents,
                        outline = outline)
            elif key.endswith('design'):
                outline[name].design = value
            else:
                outline[name].attributes[key] = value
        return outline
    
    def _process_components(self, name: str, base: str, 
                            contents: Mapping[str, Sequence[str]],
                            outline: Outline) -> Outline:
        return outline
        
    def _get_details(self, key: str, value: Sequence[str],
                     project: sourdough.Project) -> Details:
        """[summary]

        Args:
            key (str): [description]
            value (Sequence[str]): [description]
            project (sourdough.Project): [description]

        Returns:
            Details: [description]
            
        """
        
        
        design = self._get_design(name = name, project = project)
        attributes = self._get_attributes(
            name = name, 
            project = project)
        contents = sourdough.tools.listify(value)
        details = Details(
            name = name,
            contains = contains,
            design = design,
            contents = contents,
            attributes = attributes)
        return details
        
    def _process_value(self, name: str, contents: Sequence[str],
                       outline: Outline) -> Outline:
        for item in contents:
            outline[item].contents = contents
            outline = self._process_value()
            name, suffix = self._divide_key(key = key)
            contains = suffix.rstrip('s')
        
        
 
    def _add_bases(details: Details) -> Dict[str, str]:
        bases = {}
        for item in details.contents:
            bases[item] = details.contains
        return bases

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

    def _get_attributes(self, name: str, 
                        project: sourdough.Project) -> Mapping[str, Any]:
        """[summary]

        Args:
            name (str): [description]
            project (sourdough.Project): [description]

        Returns:
            Mapping[str, Any]: [description]
            
        """
        attributes = {}
        try:
            for key, value in project.settings[name].items():
                if not (key.endswith(tuple(project.hierarchy.keys())) 
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
        base = 'pipeline'
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
        deliverable = self._create_component(
            name = project.name,
            project = project)
        deliverable = self._organize_component(
            component = deliverable,
            project = project)
        print('test deliverable', deliverable)
        project.design = deliverable
        return project     

    """ Private Methods """

    def _create_component(self, name: str, 
                          project: sourdough.Project) -> sourdough.Component:
        instance = self._instance_component(name = name, project = project)
        if isinstance(instance, Iterable):
            component = self._finalize_structure(
                component = instance, 
                project = project)
        else:
            component = self._finalize_element(
                component = instance, 
                project = project)
        return component
        
    def _instance_component(self, name: str, 
                            project: sourdough.Project) -> sourdough.Component:
        details = project.design[name]
        bases = project.components
        try:
            base = bases[details.base]
        except KeyError:
            try:
                base = bases[details.design]
            except KeyError:
                raise KeyError(f'{name} component cannot be found')  
        component = base(name = name, contents = details.contents)
        return component     

    def _finalize_structure(self, component: sourdough.Component,
                            project: sourdough.Project) -> sourdough.Component:
        new_contents = []
        for item in component:
            print('test item', item)
            new_contents.append(self._create_component(
                name = item, 
                project = project))
        component.contents = new_contents
        print('test component new contents', component)
        # component = self._add_attributes(
        #     component = component, 
        #     project = project)
        return component

    def _finalize_element(self, component: sourdough.Component,
                          project: sourdough.Project) -> sourdough.Component:
        # component = self._add_attributes(
        #     component = component, 
        #     project = project)
        return component

    def _add_attributes(self, 
            component: sourdough.Component,
            project: sourdough.Project) -> sourdough.Component:
        """[summary]

        Returns:
            [type]: [description]
            
        """
        attributes = project.design[component.name].attributes
        for key, value in attributes.items():
            if (project.settings['general']['settings_priority']
                    or not hasattr(component, key)):
                setattr(component, key, value)
        return component  
 
    # def _organize_component(self, component: sourdough.Component,
    #                         project: sourdough.Project) -> sourdough.Component:
    #     for item in component:
    #         item.design = 
            
    #             self._origin
                
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
        for component in project.design:
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
