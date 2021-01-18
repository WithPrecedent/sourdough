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

       

@dataclasses.dataclass
class Plan(sourdough.Component):
    """Initialized sourdough Component instances without structure.
    
    Args:
        contents (Sequence[sourdough.Component]): stored list with Component 
            instances in its final, iterable structure.
              
    """
    contents: Sequence[sourdough.Component] = dataclasses.field(
        default_factory = list)
    
    """ Class Methods """
    
    @classmethod
    def create(cls, manager: sourdough.base.Manager) -> None:
        
        return cls   
              

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
        # Creates an object to store the project outline.
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
                base = self.manager.default_design)
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
    
    def _process_section(self, name: str, base: str, **kwargs) -> Outline:
        """[summary]

        Args:
            name (str): [description]
            outline (Outline): [description]

        Returns:
            sourdough.types.Lexicon: [description]
            
        """
        kwargs = self._initialize_kwargs(name = name, kwargs = kwargs)
        kwargs['base'] = base
        attributes = {}
        # Iterates through each key, value pair in a Configuration section and stores 
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
                kwargs[suffix] = value
            elif suffix in self.mananger.project.bases.component_suffixes:
                value_sequence = sourdough.tools.listify(value)
                contains = suffix.rstrip('s')
                items = [tuple(i, contains) for i in value_sequence]
                if prefix == name:
                    kwargs['contents'].extend(items)
                else:
                    kwargs['subcontents'][prefix] = items
            # All other keys are presumed to be attributes to be added to a
            # Component instance.
            else:
                attributes[key] = value
        component = self._create_component(**kwargs)
        try:
            component.parameters = self.manager.project.settings[
                f'{name}_parameters']
        except KeyError:
            pass
        for key, value in attributes.items():
            setattr(component, key, value)
        return component

    def _initialize_kwargs(self, name: str, 
                           kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """[summary]

        Args:
            name (str): [description]
            kwargs (Dict[str, Any]): [description]

        Returns:
            Dict[str, Any]: [description]
        """
        new_kwargs = self.mananger.project.settings.rules.special
        new_kwargs.update(kwargs)
        new_kwargs['name'] = name
        new_kwargs['subcontents'] = {}
        return new_kwargs
     
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
            suffix = key.split(divider)[-1]
            prefix = key[:-len(suffix) - 1]
        else:
            prefix = suffix = key
        return prefix, suffix

    def _create_component(self, name: str, **kwargs) -> sourdough.Component:
        """[summary]
        """
        try: 
            component = self.mananger.project.bases.component.acquire(
                name = name)
        except KeyError:
            try:
                component = self.mananger.project.bases.component.acquire(
                    name = kwargs['design'])
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




    def _process_node(self, node: sourdough.base.Node, 
                      outline: Outline) -> Tuple[sourdough.Component, Outline]:
        """ 
        """
        component, outline = self._create_component(
            node = node, 
            outline = outline)
        if isinstance(component, Iterable):
            new_contents = []
            for item in component:
                if isinstance(item, str):
                    inner_node = outline.pop(item)
                    component, outline = self._process_node(
                        node = inner_node, 
                        outline = outline)
                    new_contents.append(component)
                elif isinstance(item, inspect.isclass):
                    new_contents.append(item)()
                else:
                    new_contents.append(item)
            component.contents = new_contents
        return component, outline

    def _create_component(self, node: sourdough.base.Node,
                          outline: Outline) -> Tuple[sourdough.Component, Outline]:
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
                        outline: Outline) -> Tuple[sourdough.Component, Outline]:
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
            component.contents = sourdough.base.options.algorithms[component.name]
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
