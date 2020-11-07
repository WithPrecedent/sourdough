"""
standard: basic Workflow
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Details (Progression): basic information needed to construct composite 
        objects.
    Outline (Lexicon): dictionary of Details instances with complete information
        needed to construct a set of related composite objects.
    Draft (Stage): creates an Outline instance from a Settings instance.
    Publish (Stage): creates a Worker instance from an Outline instance.
    Apply (Stage): executes a Worker instance and possibly applies its methods
        to external data.
    Editor (Workflow): an iterable list of the Draft, Publish, and Apply Stages.

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
class Draft(sourdough.workflow.Stage):
    """Constructs an Outline instance from a project's settings.
    
    Args:
        action (str): name of the action of the 'perform' method. It is used to
            create clear and grammatically correct logging and console messages.
    
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
        outline = Outline()
        suffixes = tuple(project.bases.keys())
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
        project.results.outline = outline
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
            if key.endswith(tuple(project.bases.keys())):
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
class Publish(sourdough.workflow.Stage):
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
        project.results.plan = self._create_component(
            name = project.name, 
            project = project)
        return project
    
    """ Private Methods """

    def _create_component(self, name: str,
                          project: sourdough.Project) -> sourdough.structure.Component:
        """[summary]

        Args:
            name (str): [description]
            project (sourdough.Project): [description]

        Returns:
            sourdough.structure.Component: [description]
            
        """
        component = self._get_component(name = name, project = project)
        return self._finalize_component(
            component = component, 
            project = project)

    def _get_component(self, name: str,
                       project: sourdough.Project) -> sourdough.structure.Component:
        """[summary]

        # Args:o
            name (str): [description]
            components (Mapping[str, sourdough.structure.Component]): [description]
            project (sourdough.Project): [description]

        Raises:
            KeyError: [description]

        Returns:
            Mapping[ str, sourdough.structure.Component]: [description]
            
        """
        details = project.results.outline[name]
        kwargs = {
            'name': name,
            'contents': project.results.outline[name].contents}
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

    def _finalize_component(self, component: sourdough.structure.Component,
                            project: sourdough.Project) -> sourdough.structure.Component:
        """[summary]

        Args:
            component (sourdough.structure.Component): [description]
            project (sourdough.Project): [description]

        Returns:
            sourdough.structure.Component: [description]
            
        """
        if isinstance(component, Iterable):
            if component.branches:
                component = self._create_parallel(
                    component = component, 
                    project = project)
            else:
                component = self._create_serial(
                    component = component, 
                    project = project)
        else:
            pass
        return component

    def _create_parallel(self, component: sourdough.structure.Component,
                         project: sourdough.Project) -> sourdough.components.Worker:
        """[summary]

        Args:
            component (sourdough.structure.Component): [description]
            components (Mapping[str, sourdough.structure.Component]): [description]
            project (sourdough.Project): [description]

        Returns:
            sourdough.components.Worker: [description]
            
        """
        possible = []
        for item in component.contents:
            possible.append(project.results.outline[item].contents)
        combos = list(map(list, itertools.product(*possible)))
        wrappers = [self._get_component(i, project) for i in component.contents]
        new_contents = []
        for combo in combos:
            combo = [self._get_component(i, project) for i in combo]
            steps = []
            for i, step in enumerate(wrappers):
                step.contents = combo[i]
                steps.append(step)
            new_contents.append(steps)
        component.contents = new_contents
        component = self._add_attributes(
            component = component, 
            project = project)
        return component

    def _create_serial(self, component: sourdough.structure.Component, 
                       project: sourdough.Project) -> sourdough.components.Worker:
        """[summary]

        Args:
            component (sourdough.structure.Component): [description]
            components (Mapping[str, sourdough.structure.Component]): [description]
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

    def _add_attributes(self, 
            component: sourdough.structure.Component,
            project: sourdough.Project) -> sourdough.structure.Component:
        """[summary]

        Returns:
            [type]: [description]
            
        """
        attributes = project.results.outline[component.name].attributes
        for key, value in attributes.items():
            # if (project.settings['general']['settings_priority']
            #         or not hasattr(component, key)):
            setattr(component, key, value)
        return component    

                
@dataclasses.dataclass
class Apply(sourdough.workflow.Stage):
    """
    
    """
    action: str = 'application' 

    """ Public Methods """
        
    def perform(self, project: sourdough.Project, **kwargs) -> sourdough.Project:
        """Applies the action plan created by 'Publish'.
    
        If 'project.data' isn't None, it will be added to the kwargs passed to 
        the 'perform' method of each Component in 'project.results.plan'.

        Returns:
            [type] -- [description]                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           
        """
        if project.data is not None:
            kwargs['data'] = project.data
        for component in project.results.plan:
            component.apply(**kwargs)
        return project


@dataclasses.dataclass
class Editor(sourdough.workflow.Workflow):
    """Three-step workflow that allows user editing and easy serialization.
    
    Args:
        contents (Sequence[Union[str, Stage]]): a list of str or Stages. 
            Defaults to an empty list.
        project (sourdough.Project): related project instance.
        
    """
    contents: Sequence[Union[str, sourdough.workflow.Stage]] = dataclasses.field(
        default_factory = lambda: [Draft, Publish, Apply])
    project: sourdough.Project = None
    name: str = None
