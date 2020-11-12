"""
Creators: interim classes for sourdough Directors
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
    """Information to construct a sourdough Component.
    
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
        """Returns pretty string representation of a class instance.
        
        Returns:
            str: normal representation of a class instance.
        
        """
        return pprint.pformat(self, sort_dicts = False, compact = True)


@dataclasses.dataclass
class Architect(sourdough.Creator):
    """Creates a blueprint of a workflow.

    Architect is a dictionary representation of the overall project workflow. 
    in the blueprint produced, all components are listed by key names and the 
    information needed for Component construction are stored in Details 
    instances, which are stored as values.
    
    Args:
        contents (Mapping[str, Details]]): stored dictionary with Details
            instances as values. Defaults to an empty dict.
                        
    """
    action: str = 'drafting'
    needs: str = 'blueprint'
    produces: str = 'outline'

    """ Public Methods """
    
    def create(self, previous: sourdough.Settings, 
               project: sourdough.Project) -> sourdough.Creator:
        """Creates a blueprint based on 'settings'.

        Args:
            previous (sourdough.Settings): sourdough configuration options to
                create an blueprint.
            project (sourdough.Project): a Project instance with resources and
                other information needed for blueprint construction.

        Returns:
            Project: with modifications made to its 'design' attribute.
            
        """ 
        blueprint = sourdough.types.Lexicon()
        suffixes = tuple(project.resources.bases.keys())
        for name, section in previous.items():
            # Tests whether the section in 'settings' is related to the 
            # construction of a project object by examining the key names to see
            # if any end in a suffix corresponding to a known base type. If so, 
            # that section is harvested for information which is added to 
            # 'blueprint'.
            print('test iter settings', name)
            if any([i.endswith(suffixes) for i in section.keys()]):
                blueprint = self._process_section(
                    name = name,
                    blueprint = blueprint,
                    settings = previous,
                    project = project,
                    base = 'workflow')
        print('test blueprint', blueprint)
        return blueprint
        
    """ Private Methods """
    
    def _process_section(self, name: str, blueprint: sourdough.Lexicon,
                         settings: sourdough.Settings, 
                         project: sourdough.Project, base: str) -> sourdough.Lexicon:
        """[summary]

        Args:
            name (str): [description]
            blueprint (sourdough.Lexicon): [description]
            project (sourdough.Project): [description]

        Returns:
            sourdough.Lexicon: [description]
            
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
                blueprint = self._add_details(
                    name = key_name, 
                    blueprint = blueprint,
                    contents = contents,
                    base = base)
                for item in contents:
                    if item in settings:
                        blueprint = self._process_section(
                            name = item,
                            blueprint = blueprint,
                            project = project,
                            base = contains)
                    else:
                        blueprint = self._add_details(
                            name = item, 
                            blueprint = blueprint,
                            base = contains)
            # keys ending with 'design' hold values of a Component's design.
            elif key.endswith('design'):
                blueprint = self._add_details(
                    name = name, 
                    blueprint = blueprint, 
                    design = value)
            # All other keys are presumed to be attributes to be added to a
            # Component instance.
            else:
                blueprint = self._add_details(
                    name = name,
                    blueprint = blueprint,
                    attributes = {key: value})
        return blueprint

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
    def _add_details(name: str, blueprint: sourdough.Lexicon, **kwargs) -> sourdough.Lexicon:
        """[summary]

        Args:
            name (str): [description]
            blueprint (sourdough.Lexicon): [description]

        Returns:
            sourdough.Lexicon: [description]
            
        """
        # Stores a mostly empty Details instance in 'blueprint' if none currently
        # exists corresponding to 'name'. This check is performed to prevent
        # overwriting of existing information in 'blueprint' during recursive
        # calls.
        if name not in blueprint:
            blueprint[name] = Details(name = name)
        # Adds any kwargs to 'blueprint' as appropriate.
        for key, value in kwargs.items():
            if isinstance(getattr(blueprint[name], key), str):
                pass
            elif isinstance(getattr(blueprint[name], key), dict):
                getattr(blueprint[name], key).update(value) 
            else:
                setattr(blueprint[name], key, value)           
        return blueprint

    """ Dunder Methods """
    
    def __str__(self) -> str:
        return pprint.pformat(self, sort_dicts = False, compact = True)


@dataclasses.dataclass
class Supervisor(sourdough.Creator):
    """Constructs finalized workflow.
    
    Args:
                        
    """
    action: str = 'publishing'
    needs: str = 'blueprint'
    produces: str = 'workflow'

    """ Public Methods """

    def create(self, previous: sourdough.Lexicon, 
               project: sourdough.Project) -> sourdough.Component:
        """Drafts a Plan instance based on 'blueprint'.
            
        """ 
        project.results.plan = self._create_component(
            name = project.name, 
            previous = previous,
            project = project)
        return project
    
    """ Private Methods """

    def _create_component(self, name: str, previous: sourdough.Creator,
                          project: sourdough.Project) -> sourdough.Component:
        """[summary]

        Args:
            name (str): [description]
            project (sourdough.Project): [description]

        Returns:
            sourdough.Component: [description]
            
        """
        component = self._get_component(name = name, previous = previous, 
                                        project = project)
        return self._finalize_component(
            component = component, 
            project = project)

    def _get_component(self, name: str, previous: sourdough.Creator,
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

    def _create_parallel(self, component: sourdough.Component,
                         project: sourdough.Project) -> sourdough.elements.Flow:
        """[summary]

        Args:
            component (sourdough.Component): [description]
            components (Mapping[str, sourdough.Component]): [description]
            project (sourdough.Project): [description]

        Returns:
            sourdough.elements.Flow: [description]
            
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

    def _create_serial(self, component: sourdough.Component, 
                       project: sourdough.Project) -> sourdough.elements.Flow:
        """[summary]

        Args:
            component (sourdough.Component): [description]
            components (Mapping[str, sourdough.Component]): [description]
            project (sourdough.Project): [description]

        Returns:
            sourdough.elements.Flow: [description]
            
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
            component: sourdough.Component,
            project: sourdough.Project) -> sourdough.Component:
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
class Results(sourdough.Creator, sourdough.types.Lexicon):
    """A container for any results produced by a Project instance.

    Attributes are dynamically added by Director instances at runtime.

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
    action: str = 'applying'
    needs: str = 'workflow'
    produces: str = 'results'
    identification: str = None

    """ Public Methods """
    
    def add(self, name: str, value: Any) -> None:
        """
        """
        setattr(self, name, value)
        return self
    
    """ Public Methods """
 
    def create(self, previous: sourdough.Creator, 
               project: sourdough.Project) -> sourdough.Creator:        
        """Drafts a Plan instance based on 'blueprint'.
            
        """
        kwargs = {}
        results = self.__class__(
            contents = self.contents, 
            identification = self.identification)
        if project.data is not None:
            kwargs['data'] = project.data
        for component in previous:
            component.apply(**kwargs)
        return project

    