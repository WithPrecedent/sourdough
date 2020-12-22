"""
creators: classes for building products of a sourdough project
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Architect (Creator):
    Builder (Creator):
    Worker (Creator):
    
"""
from __future__ import annotations
import copy
import dataclasses
import itertools
import pprint
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import sourdough  
                       

@dataclasses.dataclass
class Architect(sourdough.Creator):
    """Creates a blueprint of a sourdough Plan.

    Architect creates a dictionary representation, a blueprint, of the overall 
    manager Plan. In the blueprint produced, keys are the names of components 
    and values are Instruction instances.
    
    Args:
                        
    """
    action: ClassVar[str] = 'Drafting'
    needs: ClassVar[Union[str, Tuple[str]]] = 'settings'
    produces: ClassVar[Type] = 'blueprint'

    """ Public Methods """
    
    def create(self, manager: sourdough.Manager) -> sourdough.types.Lexicon:
        """Creates a blueprint based on 'manager.project.settings'.

        Args:
            manager (sourdough.Manager): a Project instance with options and
                other information needed for blueprint construction.

        Returns:
            Project: with modifications made to its 'design' attribute.
            
        """ 
        blueprint = manager.bases.product.acquire(key = self.produces)(
            identification = manager.project.identification)
        for name, section in manager.project.settings.items():
            # Tests whether the section in 'manager.project.settings' is related to the 
            # construction of a project object by examining the key names to see
            # if any end in a suffix corresponding to a known base type. If so, 
            # that section is harvested for information which is added to 
            # 'blueprint'.
            if (not name.endswith(tuple(sourdough.rules.skip_suffixes))
                    and name not in sourdough.rules.skip_sections
                    and any(
                        [i.endswith(sourdough.options.component_suffixes) 
                        for i in section.keys()])):
                blueprint = self._add_instructions(
                    name = name,
                    design = None,
                    blueprint = blueprint,
                    manager = manager)
        return blueprint
        
    """ Private Methods """
    
    def _add_instructions(self, name: str, design: str,
                          blueprint: sourdough.products.Blueprint,
                          manager: sourdough.Manager, **kwargs) -> (
                              sourdough.products.Blueprint):
        """[summary]

        Args:
            name (str): [description]
            blueprint (sourdough.types.Lexicon): [description]
            manager (sourdough.Manager): [description]

        Returns:
            sourdough.types.Lexicon: [description]
            
        """
        if name not in blueprint:
            blueprint[name] = sourdough.products.Instructions(name = name)
        # Adds appropraite design type to 'blueprint' for 'name'.
        blueprint[name].design = self._get_design(
            name = name, 
            design = design,
            manager = manager)
        # Adds any appropriate parameters to 'blueprint' for 'name'.
        blueprint[name].parameters = self._get_parameters(
            name = name, 
            manager = manager)
        # If 'name' is in 'settings', this method iterates through each key, 
        # value pair in section and stores or extracts the information needed
        # to fill out the appropriate Instructions instance in blueprint.
        if name in manager.project.settings:
            instructions_attributes = {}
            for key, value in manager.project.settings[name].items():
                # If a 'key' has an underscore, text after the last underscore 
                # becomes the 'suffix' and text before becomes the 
                # 'prefix'. If there is no underscore, 'prefix' and
                # 'suffix' are both assigned to 'key'.
                prefix, suffix = self._divide_key(key = key)
                # A 'key' ending with one of the component-related suffixes 
                # triggers recursive searching throughout 'manager.project.settings'.
                if suffix in sourdough.options.component_suffixes:
                    contains = suffix.rstrip('s')
                    blueprint[prefix].contents = sourdough.tools.listify(value)
                    for item in blueprint[prefix].contents:
                        blueprint = self._add_instructions(
                            name = item,
                            design = contains,
                            blueprint = blueprint,
                            manager = manager)
                elif suffix in sourdough.rules.special_section_suffixes:
                    instruction_kwargs = {suffix: value}
                    blueprint = self._add_instruction(
                        name = prefix, 
                        blueprint = blueprint,
                        **instruction_kwargs)
                # All other keys are presumed to be attributes to be added to a
                # Component instance.
                else:
                    blueprint[name].attributes.update({key: value})
        return blueprint

    def _get_design(self, name: str, design: str, 
                    manager: sourdough.Manager) -> str:
        """[summary]

        Args:
            name (str): [description]
            design (str): [description]
            manager (sourdough.Manager): [description]

        Returns:
            str: [description]
            
        """
        try:
            return manager.project.settings[name][f'{name}_design']
        except KeyError:
            if design is None:
                return sourdough.rules.default_design
            else:
                return design

    def _get_parameters(self, name: str, 
                        manager: sourdough.Manager) -> Dict[Any, Any]:
        """[summary]

        Args:
            name (str): [description]
            project (sourdough.Manager): [description]

        Returns:
            sourdough.types.Lexicon: [description]
            
        """
        try:
            return manager.project.settings[f'{name}_parameters']
        except KeyError:
            return {}
        
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
       
    def _add_instruction(self, name: str, 
                         blueprint: sourdough.products.Blueprint, 
                         **kwargs) -> sourdough.products.Blueprint:
        """[summary]

        Args:
            name (str): [description]
            blueprint (sourdough.types.Lexicon): [description]

        Returns:
            sourdough.types.Lexicon: [description]
            
        """
        # Adds any kwargs to 'blueprint' as appropriate.
        for key, value in kwargs.items():
            if isinstance(getattr(blueprint[name], key), list):
                getattr(blueprint[name].key).extend(
                    sourdough.tools.listify(value))
            elif isinstance(getattr(blueprint[name], key), dict):
                getattr(blueprint[name], key).update(value) 
            else:
                setattr(blueprint[name], key, value)           
        return blueprint

    """ Dunder Methods """
    
    def __str__(self) -> str:
        return pprint.pformat(self, sort_dicts = False, compact = True)
           
      
@dataclasses.dataclass
class Builder(sourdough.Creator):
    """Constructs finalized plan.
    
    Args:
                        
    """
    action: ClassVar[str] = 'Creating'
    needs: ClassVar[Union[str, Tuple[str]]] = 'blueprint'
    produces: ClassVar[Type] = 'plan'

    """ Public Methods """

    def create(self, manager: sourdough.Manager) -> sourdough.Component:
        """Drafts a Workflow instance based on 'blueprint' in 'manager'.
            
        """ 
        plan = manager.bases.product.acquire(key = self.produces)(
            identification = manager.project.identification)
        plan.contents = self._create_component(
            name = manager.project.name, 
            manager = manager)
        return plan
    
    """ Private Methods """

    def _create_component(self, name: str, 
                          manager: sourdough.Manager) -> sourdough.Component:
        """[summary]

        Args:
            name (str): [description]
            manager (sourdough.Manager): [description]

        Returns:
            sourdough.Component: [description]
            
        """
        component = self._get_component(name = name, manager = manager)
        return self._finalize_component(component = component, 
                                        manager = manager)

    def _get_component(self, name: str,
                       manager: sourdough.Manager) -> sourdough.Component:
        """[summary]

        Args:
            name (str): [description]
            manager (sourdough.Manager): [description]

        Raises:
            KeyError: [description]

        Returns:
            Mapping[str, sourdough.Component]: [description]
            
        """
        instructions = manager['blueprint'][name]
        kwargs = {'name': name, 'contents': instructions.contents}
        try:
            component = manager.basescomponent.borrow(key = name)
            for key, value in kwargs.items():
                if value:
                    setattr(component, key, value)
        except KeyError:
            try:
                component = manager.basescomponent.acquire(key = name)
                component = component(**kwargs)
            except KeyError:
                try:
                    component = manager.basescomponent.acquire(
                        key = instructions.design)
                    component = component(**kwargs)
                except KeyError:
                    raise KeyError(f'{name} component does not exist')
        return component

    def _finalize_component(self, component: sourdough.Component,
                            manager: sourdough.Manager) -> sourdough.Component:
        """[summary]

        Args:
            component (sourdough.Component): [description]
            manager (sourdough.Manager): [description]

        Returns:
            sourdough.Component: [description]
            
        """
        if isinstance(component, Iterable):
            if component.parallel:
                finalizer = self._finalize_parallel
            else:
                finalizer = self._finalize_serial
        else:
            finalizer = self._finalize_element
        component = finalizer(component = component, manager = manager)
        component = self._add_attributes(
            component = component, 
            manager = manager)
        return component

    def _finalize_parallel(self, component: sourdough.Component,
                           manager: sourdough.Manager) -> sourdough.Component:
        """[summary]

        Args:
            component (sourdough.Component): [description]
            manager (sourdough.Manager): [description]

        Returns:
            sourdough.Component: [description]
            
        """
        # Creates empy list of lists for all possible permutations to be stored.
        possible = []
        # Populates list of lists with different options.
        for item in component.contents:
            possible.append(manager['blueprint'][item].contents)
        # Computes Cartesian product of possible permutations.
        combos = list(map(list, itertools.product(*possible)))
        wrappers = [
            self._create_component(i, manager) for i in component.contents]
        new_contents = []
        for combo in combos:
            new_combo = [self._create_component(i, manager) for i in combo]
            steps = []
            for i, step in enumerate(wrappers):
                new_step = copy.deepcopy(step)
                new_step.contents = new_combo[i]
                steps.append(new_step)
            new_contents.append(steps)
        component.contents = new_contents
        component = self._add_attributes(
            component = component, 
            manager = manager)
        return component

    def _finalize_serial(self, component: sourdough.Component, 
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
            instance = self._create_component(
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
            component.contents = sourdough.options.algorithms[component.name]
        except KeyError:
            component.contents = None
        return component
    
    def _add_attributes(self, component: sourdough.Component,
                        manager: sourdough.Manager) -> sourdough.Component:
        """[summary]

        Returns:
            [type]: [description]
            
        """
        attributes = manager['blueprint'][component.name].attributes
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
        results = manager.basesproduct.acquire(key = self.produces)(
            identification = manager.project.identification)
        if manager.project.data is not None:
            kwargs['data'] = manager.project.data
        for component in manager['plan']:
            results.update({component.name: component.apply(**kwargs)})
        return results
