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
class Details(sourdough.Lexicon):
    """Basic characteristics of a group of sourdough Components.
    
    Args:
        contents (Mapping[str, str]): stored dictionary. Defaults to an empty 
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
    contents: Mapping[str, str] = dataclasses.field(default_factory = dict)
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
                contents = dict.fromkeys(
                    sourdough.tools.listify(value), 
                    contains)
                outline = self._add_details(
                    name = key_name, 
                    outline = outline,
                    contents = contents,
                    base = base)
                for item in contents.keys():
                    if item in project.settings:
                        outline = self._process_section(
                            name = item,
                            outline = outline,
                            project = project,
                            base = contents[item])
                    else:
                        outline = self._add_details(
                            name = item, 
                            outline = outline,
                            base = contents[item])
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
            elif not getattr(outline[name], key):
                setattr(outline[name], key, value)
            else:
                if isinstance(value, list):
                    getattr(outline[name], key).extend(value)
                else:
                    try:
                        getattr(outline[name], key).append(value)
                    except (AttributeError, TypeError):
                        getattr(outline[name], key).update(value)             
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
        # composite = project.components.build(
        #     name = 'worker', 
        #     design = project.design[project.name].design)
        components = {}
        for name, details in project.design.items():
            components = self._add_component(
                name = name, 
                components = components,
                project = project)
        root = components.pop(project.name)
        root = self._organize_worker(
            worker = root,
            components = components,
            project = project)
        print('test deliverable', root)
        return root
    
    """ Private Methods """

    def _add_component(self, name: str,
                       components: Mapping[str, sourdough.Component],
                       project: sourdough.Project) -> Mapping[
                           str, sourdough.Component]:
        """[summary]

        Args:
            name (str): [description]
            components (Mapping[str, sourdough.Component]): [description]
            project (sourdough.Project): [description]

        Raises:
            KeyError: [description]

        Returns:
            Mapping[ str, sourdough.Component]: [description]
            
        """
        details = project.design[name]
        try:
            component = project.components[details.design]
        except KeyError:
            try:
                component = project.components[details.base]
            except KeyError:
                try:
                    component = project.options[details.name]
                except KeyError:
                    raise KeyError(f'{name} component does not exist')
        components[name] = component(name = name)
        return components   
            
    def _organize_worker(self, worker: sourdough.worker, 
                         components: Mapping[str, sourdough.Component],
                         project: sourdough.Project) -> sourdough.Worker:
        """[summary]

        Args:
            worker (sourdough.worker): [description]
            components (Mapping[str, sourdough.Component]): [description]
            project (sourdough.Project): [description]

        Returns:
            sourdough.Worker: [description]
            
        """
        for item in project.design[worker.name].keys():
            component = components.pop(item)
            print('test item', item)
            if isinstance(component, Iterable):
                print('test yes iterable')
                component = self._organize_worker(
                    worker = component,
                    components = components,
                    project = project)
            else:
                try:
                    component.contents = project.options[component.contents]
                except (TypeError, KeyError):
                    component.conents = None
            worker.add(component)
        return worker
                
            
                
                
                      
        # deliverable = self._create_component(
        #     name = project.name,
        #     project = project)
        # deliverable = self._organize_component(
        #     component = deliverable,
        #     project = project)
        # print('test deliverable', deliverable)
        # project.design = deliverable
        # return project     

  

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
