"""
outputs: interim classes for sourdough Workflows
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:

"""
from __future__ import annotations
import copy
import dataclasses
import functools
import inspect
import itertools
import pprint
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Union)

import sourdough


@dataclasses.dataclass
class Details(sourdough.types.Progression):
    """Basic characteristics of a sourdough Component.
    
    Args:
        contents (Sequence[str]): stored list of str. Included items should 
            correspond to keys in an Outline and/or Component subclasses. 
            Defaults to an empty list.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. 
        base (str): name of base class associated with the Component to be 
            created.
        design (str): name of design base class associated with the Component
            to be created.
        parameters (Mapping[str, Any]): parameters to be used for the stored
            object(s) in its/their creation.
        attributes (Mapping[str, Any]): attributes to add to the created
            Component object. The keys should be name of the attribute and the
            values should be the value stored for that attribute.
            
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
class Outline(sourdough.Stage, sourdough.types.Lexicon):
    """Output of the the drafting process.

    Outline is a dictionary representation of the overall project design. All
    Components are listed by key names and the information needed for Component
    construction are stored in Details instances.
    
    Args:
        contents (Mapping[str, Details]]): stored dictionary with Details
            instances as values. Defaults to an empty dict.
                        
    """
    contents: Mapping[str, Details] = dataclasses.field(default_factory = dict)
    action: str = 'drafting'

    """ Public Methods """
    
    def create(self, previous: sourdough.Stage, 
               project: sourdough.Project) -> sourdough.Stage:
        """Creates an Outline instance based on 'settings'.

        Args:
            settings (sourdough.Settings):
            project (sourdough.Project): a Project instance for which 'design'
                should be created based on its 'settings' and other attributes.

        Returns:
            Project: with modifications made to its 'design' attribute.
            
        """ 
        if inspect.isclass(self):
            outline = self()
        else:
            outline = self.__class__()
        suffixes = tuple(project.resources.bases.keys())
        for name, section in previous.items():
            # Tests whether the section in 'settings' is related to the 
            # construction of a project object by examining the key names to see
            # if any end in a suffix corresponding to a known base type. If so, 
            # that section is harvested for information which is added to 
            # 'outline'.
            print('test iter settings', name)
            if any([i.endswith(suffixes) for i in section.keys()]):
                outline = self._process_section(
                    name = name,
                    outline = outline,
                    settings = previous,
                    project = project,
                    base = 'worker')
        print('test outline', outline)
        return outline
        
    """ Private Methods """
    
    def _process_section(self, name: str, outline: Outline,
                         settings: sourdough.Settings, 
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
        for key, value in settings[name].items():
            # keys ending with specific suffixes trigger further parsing and 
            # searching throughout 'settings'.
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
                    if item in settings:
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

    @staticmethod
    def _divide_key(key: str) -> Sequence[str, str]:
        """[summary]

        Args:
            key (str): [description]

        Returns:
            
            Sequence[str, str]: [description]
            
        """
        suffix = key.split('_')[-1][:-1]
        prefix = key[:-len(suffix) - 2]
        return prefix, suffix
    
    @staticmethod    
    def _add_details(name: str, outline: Outline, **kwargs) -> Outline:
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

    """ Dunder Methods """
    
    def __str__(self) -> str:
        return pprint.pformat(self, sort_dicts = False, compact = True)


@dataclasses.dataclass
class Agenda(sourdough.Stage, sourdough.types.Hybrid):
    """Output of the the drafting process.

    Outline is a dictionary representation of the overall project design. All
    Components are listed by key names and the information needed for Component
    construction are stored in Details instances.
    
    Args:
                        
    """
    contents: sourdough.structure.Component = None
    action: str = 'publishing'

    """ Public Methods """

    def create(self, previous: sourdough.Stage, 
               project: sourdough.Project) -> sourdough.Stage:
        """Drafts a Plan instance based on 'outline'.
            
        """ 
        project.results.plan = self._create_component(
            name = project.name, 
            previous = previous,
            project = project)
        return project
    
    """ Private Methods """

    def _create_component(self, name: str, previous: sourdough.Stage,
                          project: sourdough.Project) -> sourdough.structure.Component:
        """[summary]

        Args:
            name (str): [description]
            project (sourdough.Project): [description]

        Returns:
            sourdough.structure.Component: [description]
            
        """
        component = self._get_component(name = name, previous = previous, 
                                        project = project)
        return self._finalize_component(
            component = component, 
            project = project)

    def _get_component(self, name: str, previous: sourdough.Stage,
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
        print('test previous', previous)
        details = previous[name]
        kwargs = {'name': name, 'contents': previous.contents}
        try:
            component = copy.deepcopy(project.resources.options[name])
            for key, value in kwargs.items():
                if value:
                    setattr(component, key, value)
        except KeyError:
            try:
                component = project.resources.components[name]
                component = component(**kwargs)
            except KeyError:
                try:
                    component = project.resources.components[details.design]
                    component = component(**kwargs)
                except KeyError:
                    try:
                        component = project.resources.components[details.base]
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
            possible.append(previous[item].contents)
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
        attributes = previous[component.name].attributes
        for key, value in attributes.items():
            # if (project.settings['general']['settings_priority']
            #         or not hasattr(component, key)):
            setattr(component, key, value)
        return component    


@dataclasses.dataclass
class Results(sourdough.Stage, sourdough.types.Lexicon):
    """A container for any results produced by a Project instance.

    Attributes are dynamically added by Workflow instances at runtime.

    Args:
        contents (Mapping[str, Details]]): stored dictionary with Details
            instances as values. Defaults to an empty dict.
        identification (str): a unique identification name for a Project 
            instance. The name is used for creating file folders related to the 
            project. If it is None, a str will be created from 'name' and the 
            date and time. 'identification' is also stored in a Results
            instance to connect it to any output if it is separated from a
            Project instance.

    """
    contents: Mapping[str, Details] = dataclasses.field(default_factory = dict)
    identification: str = None

    """ Public Methods """
    
    def add(self, name: str, value: Any) -> None:
        """
        """
        setattr(self, name, value)
        return self
    
    """ Public Methods """

    @classmethod
    @functools.singledispatchmethod    
    def create(self, previous: sourdough.Stage, 
               project: sourdough.Project) -> sourdough.Stage:        
        """Drafts a Plan instance based on 'outline'.
            
        """
        kwargs = {}
        results = self.__class__(
            contents = self.contents, 
            identification = self.identification)
        if project.data is not None:
            kwargs['data'] = project.data
        for component in agenda:
            component.apply(**kwargs)
        return project

    """ Dunder Methods """

    def __contains__(self, item: str) -> bool:
        """Returns whether an attribute named 'item' exists.

        This allows external methods and functions to use the "x in [Results 
        instance]" syntax to see if a specific attribute has been added.

        Args:
            item (str): the name of the attribute to check for.

        Returns:
            bool: whether there is an attribute named 'item'
            
        """
        return hasattr(self, item)
    