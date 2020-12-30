"""
converters: functions for converting one type of sourdough object to another
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    
"""
from __future__ import annotations
import copy
import dataclasses
import inspect
import itertools
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import sourdough  


""" Proxy Types for Annotation """

Outline = sourdough.types.Lexicon
Plan = sourdough.Component
Results = sourdough.types.Lexicon


@dataclasses.dataclass
class Creator(sourdough.Factory):
    """
            
    Args:
        
    """
    contents: Mapping[str, str] = dataclasses.field(default_factory = lambda: {
        'Drafting': 'outline', 
        'Building': 'plan', 
        'Applying': 'results'})
    manager: object = None

    """ Public Methods """

    def create_outline(self) -> Outline:
        """Creates an Outline based on 'manager.project.settings'.

        Returns:
            Outline: stored instructions for creating sourdough
                components.
            
        """
        # Creates Lexicon to store a project outline.
        outline = Outline()
        # Determines sections of 'project.settings' to exclude in creating 
        # sourdough project components.
        skip_suffixes = self.manager.project.settings.rules.skip
        skipables = [i for i in self.manager.project.settings.keys() 
                  if not i.endswith(tuple(skip_suffixes))]
        # Creates subset of 'project.settings' with only sections related to
        # sourdough project components.
        component_settings = self.manager.project.settings.excludify(skipables)
        for section in component_settings.keys():
            outline[section] = self._process_section(
                name = section, 
                outline = outline)
        return outline

    def create_plan(self) -> Union[Plan, Sequence[Plan]]:
        """Drafts a Plan based on an Outline in 'mananger'.
            
        """ 
        outline = copy.deepcopy(self.manager['outline'])
        nodes = outline.keys()
        shell = []
        for name in nodes:
            try:
                node = outline.pop(name)
                plan, outline = self._process_node(
                    node = node,
                    outline = outline)
                shell.append(plan)
            except KeyError:
                pass
        if len(shell) == 1:
            return shell[0]
        else:
            return shell
    
    """ Private Methods """
    
    def _process_section(self, name: str, outline: Outline, **kwargs) -> Outline:
        """[summary]

        Args:
            name (str): [description]
            outline (Outline): [description]

        Returns:
            sourdough.types.Lexicon: [description]
            
        """
        node = sourdough.base.Node(name = name, **kwargs)
        # Iterates through each key, value pair in a Settings section and stores 
        # or extracts the information needed to create a Component subclass
        # instance.
        for key, value in self.manager.project.settings[name].items():
            # If a 'key' has an underscore, text after the last underscore 
            # becomes the 'suffix' and text before becomes the 'prefix'. If 
            # there is no underscore, 'prefix' and 'suffix' are both assigned to 
            # 'key'.
            prefix, suffix = self._divide_key(key = key)
            # Depending upon 'suffix', different actions are taken.
            if suffix in self.manager.project.settings.rules.special:
                node.builders[suffix] = value
            elif suffix in self.mananger.project.bases.component_suffixes:
                contains = suffix.rstrip('s')
                items = [
                    tuple(i, contains) for i in sourdough.tools.listify(value)]
                node.contents.append({prefix: items})
            # All other keys are presumed to be attributes to be added to a
            # Component instance.
            else:
                node.builders['attributes'].update({key: value})
        try:
            node.executors = self.manager.project.settings[f'{name}_parameters']
        except KeyError:
            pass
        return node
        
    def _divide_key(self, key: str, divider: str = None) -> Tuple[str, str]:
        """[summary]

        Args:
            key (str): [description]

        Returns:
            
            Tuple[str, str]: [description]
            
        """
        if divider is None:
            divider = '_'
        if divider in key:
            suffix = key.split('_')[-1]
            prefix = key[:-len(suffix) - 1]
        else:
            prefix = suffix = key
        return prefix, suffix

    def _process_node(self, node: sourdough.base.Node, 
                      outline: Outline) -> sourdough.Component:
        """ 
        """
        component, outline = self._create_component(
            node = node, 
            outline = outline)
        if isinstance(component, Iterable):
            new_contents = []
            for item in component:
                if isinstance(item, str):
                    node = outline.pop(item)
                    component, outline = self._process_node(
                        node = node, 
                        outline = outline)
                    new_contents.append(component)
                elif isinstance(item, inspect.isclass):
                    new_contents.append(item)()
                else:
                    new_contents.append(item)
            component.contents = new_contents
        return component, outline

    def _create_component(self, node: sourdough.base.Node,
                          outline: Outline) -> sourdough.Component:
        """[summary]
        """
        try: 
            component = self.mananger.project.bases.component.acquire(
                name = node.name)
        except KeyError:
            try:
                component = self.mananger.project.bases.component.acquire(
                    name = node.builders['design'])
            except (KeyError, TypeError):
                component = self.mananger.project.bases.component.acquire(
                    name = node.builders['base'])
        attributes = node.builders.pop('attributes')
        kwargs = node.builders
        kwargs['parameters'] = node.executors
        kwargs['name'] = node.name
        kwargs['contents'] = node.contents
        component = component(**kwargs)
        for key, value in attributes.items():
            setattr(component, key, value)
        component.contents, outline = self._process_contents(
            component = component, 
            outline = outline)
        return component, outline

    def _process_contents(self, component: sourdough.Component,
                          outline: Outline) -> Tuple[sourdough.Component, Outline]:
        """[summary]

        Args:
            component (sourdough.Component): [description]
            outline (Outline): [description]

        Returns:
            Tuple[sourdough.Component, Outline]: [description]
        """
        if component.parallel:
            component, outline = self._process_parallel(
                component = component, 
                outline = outline)
        else:
            component, outline = self._process_serial(
                component = component, 
                outline = outline)
        return component, outline

    def _process_parallel(self, component: sourdough.Component,
                          outline: Outline) -> Tuple[sourdough.Component, Outline]:
        """
        """
        # Creates empy list of lists for all possible permutations to be stored.
        possible = []
        # Populates list of lists with different options.
        for item in component.contents:
            possible.append(manager['outline'][item].contents)
        # Computes Cartesian product of possible permutations.
        combos = list(map(list, itertools.product(*possible)))
        wrappers = [
            _create_component(i, manager) for i in component.contents]
        new_contents = []
        for combo in combos:
            new_combo = [_create_component(i, manager) for i in combo]
            steps = []
            for i, step in enumerate(wrappers):
                new_step = copy.deepcopy(step)
                new_step.contents = new_combo[i]
                steps.append(new_step)
            new_contents.append(steps)
        component.contents = new_contents
        component = _add_attributes(
            component = component, 
            manager = manager)
        return component

    def _process_serial(self, component: sourdough.Component, 
                         manager: sourdough.Manager) -> sourdough.Component:
        """[summary]

        Args:
            component (sourdough.Component): [description]
            manager (sourdough.Manager): [description]

        Returns:
            Component: [description]
            
        """
        new_contents = []
        for item in component.contents:
            instance = _create_component(
                name = item, 
                manager = manager)
            new_contents.append(instance)
        component.contents = new_contents
        return component

    def _finalize_element(self, component: sourdough.Component, 
                          manager: sourdough.Manager) -> sourdough.Component:
        """[summary]

        Args:
            component (sourdough.Component): [description]
            manager (sourdough.Manager): [description]

        Returns:
            Component: [description]
            
        """
        try:
            component.contents = sourdough.resources.options.algorithms[component.name]
        except KeyError:
            component.contents = None
        return component
    
    def _add_attributes(self, component: sourdough.Component,
                        manager: sourdough.Manager) -> sourdough.Component:
        """[summary]

        Returns:
            [type]: [description]
            
        """
        attributes = manager['outline'][component.name].attributes
        for key, value in attributes.items():
            setattr(component, key, value)
        return component    


@dataclasses.dataclass
class Worker(sourdough.Creator):
    """Applies a project Workflow and produces results.

    Args:

    """
    action: ClassVar[str] = 'Computing'
    needs: ClassVar[Union[str, Tuple[str]]] = 'plan'
    produces: ClassVar[str] = 'results'
    
    """ Public Methods """
 
    def create(self, manager: sourdough.Manager, 
               **kwargs) -> sourdough.types.Lexicon:        
        """Computes results based on a plan.
            
        """
        results = manager.basesproduct.acquire(key = produces)(
            identification = manager.project.identification)
        if manager.project.data is not None:
            kwargs['data'] = manager.project.data
        for component in manager['plan']:
            results.update({component.name: component.apply(**kwargs)})
        return results
