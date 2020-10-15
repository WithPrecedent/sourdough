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
import copy
import dataclasses
import itertools
import pprint
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Union)

import sourdough


@dataclasses.dataclass
class Details(sourdough.Lexicon):
    """Basic characteristics of a group of sourdough Components.
    
    Args:
        contents (Sequence[str]): stored dictionary. Defaults to an empty 
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
        """Creates an Outline instance at 'design' based on 'settings'.

        Args:
            project (sourdough.Project): a Project instance for which 'design'
                should be created based on its 'settings' and other attributes.

        Returns:
            Project: with modifications made to its 'design' attribute.
            
        """ 
        outline = Outline(project = project)
        suffixes = tuple(project.hierarchy.keys())
        for name, section in project.settings.items():
            # Tests whether the section in 'settings' is related to the 
            # construction of a project object by examining the key names to see
            # if any end in a suffix corresponding to a known base type. If so, 
            # that section is harvested for information which is added to 
            # 'outline'.
            if any([i.endswith(suffixes) for i in section.keys()]):
                outline = self._process_section(
                    name = name,
                    outline = outline,
                    project = project,
                    base = 'worker')
        project.design = outline
        print('test project outline', project.design)
        return project
        
    """ Private Methods """
    
    def _process_section(self, name: str, outline: Outline, 
                         project: sourdough.Project, base: str) -> Outline:
        """[summary]

        Args:
            name (str): [description]
            outline (Outline): [description]
            project (sourdough.Project): [description]

        Returns:
            Outline: [description]
            
        """
        # Iterates through each key, value pair in section and stores or 
        # extracts the information as appropriate.
        for key, value in project.settings[name].items():
            # keys ending with specific suffixes trigger further parsing and 
            # searching throughout 'project.settings'.
            if key.endswith(tuple(project.hierarchy.keys())):
                # Each key contains a prefix which is the parent Component name 
                # and a suffix which is what that parent Component contains.
                key_name, key_suffix = self._divide_key(key = key)
                contains = key_suffix.rstrip('s')
                contents = sourdough.tools.listify(value) 
                outline = self._add_details(
                    name = key_name, 
                    outline = outline,
                    contents = contents,
                    base = base)
                for item in contents:
                    if item in project.settings:
                        outline = self._process_section(
                            name = item,
                            outline = outline,
                            project = project,
                            base = contains)
                    else:
                        outline = self._add_details(
                            name = item, 
                            outline = outline,
                            base = contains)
            # keys ending with 'design' hold values of a Component's design.
            elif key.endswith('design'):
                outline = self._add_details(
                    name = name, 
                    outline = outline, 
                    design = value)
            # All other keys are presumed to be attributes to be added to a
            # Component instance.
            else:
                outline = self._add_details(
                    name = name,
                    outline = outline,
                    attributes = {key: value})
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
        
    def _add_details(self, name: str, outline: Outline, **kwargs) -> Outline:
        """[summary]

        Args:
            name (str): [description]
            outline (Outline): [description]

        Returns:
            Outline: [description]
            
        """
        # Stores a mostly empty Details instance in 'outline' if none currently
        # exists corresponding to 'name'. This check is performed to prevent
        # overwriting of existing information in 'outline' during recursive
        # calls.
        if name not in outline:
            outline[name] = Details(name = name)
        # Adds any kwargs to 'outline' as appropriate.
        for key, value in kwargs.items():
            if isinstance(getattr(outline[name], key), str):
                pass
            elif isinstance(getattr(outline[name], key), dict):
                getattr(outline[name], key).update(value) 
            else:
                setattr(outline[name], key, value)           
        return outline
       
    
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
        root = self._create_component(name = project.name, project = project)
        print('test root', root)
        return root
    
    """ Private Methods """

    def _create_component(self, name: str,
                          project: sourdough.Project) -> sourdough.Component:
        """[summary]

        Args:
            name (str): [description]
            project (sourdough.Project): [description]

        Returns:
            sourdough.Component: [description]
            
        """
        component = self._get_component(name = name, project = project)
        return self._finalize_component(component = component, project = project)

    def _get_component(self, name: str,
                       project: sourdough.Project) -> sourdough.Component:
        """[summary]

        # Args:o
            name (str): [description]
            components (Mapping[str, sourdough.Component]): [description]
            project (sourdough.Project): [description]

        Raises:
            KeyError: [description]

        Returns:
            Mapping[ str, sourdough.Component]: [description]
            
        """
        details = project.design[name]
        kwargs = {
            'name': name,
            'contents': project.design[name].contents}
        try:
            component = copy.deepcopy(project.options[name])
            for key, value in kwargs.items():
                if value:
                    setattr(component, key, value)
        except KeyError:
            try:
                component = project.components[name]
                component = component(**kwargs)
            except KeyError:
                try:
                    component = project.components[details.design]
                    component = component(**kwargs)
                except KeyError:
                    try:
                        component = project.components[details.base]
                        component = component(**kwargs)
                    except KeyError:
                        raise KeyError(f'{name} component does not exist')
        return component

    def _finalize_component(self, component: sourdough.Component,
                            project: sourdough.Project) -> sourdough.Component:
        """[summary]

        Args:
            component (sourdough.Component): [description]
            project (sourdough.Project): [description]

        Returns:
            sourdough.Component: [description]
            
        """
        if isinstance(component, Iterable):
            if component.branches:
                print('test yes branches')
                component = self._create_branching(
                    component = component, 
                    project = project)
            else:
                component = self._create_straight(
                    component = component, 
                    project = project)
        else:
            pass
        return component

    def _create_branching(self, component: sourdough.Component,
                          project: sourdough.Project) -> sourdough.components.Worker:
        """[summary]

        Args:
            component (sourdough.Component): [description]
            components (Mapping[str, sourdough.Component]): [description]
            project (sourdough.Project): [description]

        Returns:
            sourdough.components.Worker: [description]
            
        """
        possible = []
        for item in component.contents:
            possible.append(project.design[item].contents)
        combos = list(map(list, itertools.product(*possible)))
        wrappers = [self._get_component(i, project) for i in self.contents]
        new_contents = []
        for combo in combos:
            combo = [self._get_component(i, project) for i in combo]
            print('test combo', combo)
            instance = sourdough.project.workers.Pipeline(
                contents = combo,
                steps = component.contents)
            instance.contents = [
                self._create_straight(i, project) for i in instance.contents]
            new_contents.append(instance)
        return self

    def _create_straight(self, component: sourdough.Component, 
                         project: sourdough.Project) -> sourdough.components.Worker:
        """[summary]

        Args:
            component (sourdough.Component): [description]
            components (Mapping[str, sourdough.Component]): [description]
            project (sourdough.Project): [description]

        Returns:
            sourdough.components.Worker: [description]
            
        """
        new_contents = []
        for item in component.contents:
            instance = self._get_component(
                name = item, 
                project = project)
            instance = self._finalize_component(
                component = instance, 
                project = project)
            new_contents.append(instance)
        component.contents = new_contents
        return component
    

  

    # def _finalize_design(self, component: sourdough.Component,
    #                         project: sourdough.Project) -> sourdough.Component:
    #     new_contents = []
    #     for item in component:
    #         print('test item', item)
    #         new_contents.append(self._create_component(
    #             name = item, 
    #             project = project))
    #     component.contents = new_contents
    #     print('test component new contents', component)
    #     # component = self._add_attributes(
    #     #     component = component, 
    #     #     project = project)
    #     return component

    # def _finalize_element(self, component: sourdough.Component,
    #                       project: sourdough.Project) -> sourdough.Component:
    #     # component = self._add_attributes(
    #     #     component = component, 
    #     #     project = project)
    #     return component

    # def _add_attributes(self, 
    #         component: sourdough.Component,
    #         project: sourdough.Project) -> sourdough.Component:
    #     """[summary]

    #     Returns:
    #         [type]: [description]
            
    #     """
    #     attributes = project.design[component.name].attributes
    #     for key, value in attributes.items():
    #         if (project.settings['general']['settings_priority']
    #                 or not hasattr(component, key)):
    #             setattr(component, key, value)
    #     return component  
 
    # # def _organize_component(self, component: sourdough.Component,
    # #                         project: sourdough.Project) -> sourdough.Component:
    # #     for item in component:
    # #         item.design = 
            
    # #             self._origin

                
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
