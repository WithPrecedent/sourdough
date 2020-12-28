"""
converters: functions for converting one type of sourdough object to another
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
class Instructions(sourdough.types.Progression):
    """Information to construct a sourdough Component.
    
    Args:
        contents (Sequence[str]): stored list of str. Included items should 
            correspond to keys in an Outline and/or Component subclasses. 
            Defaults to an empty list.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance.
            Defaults to None. 
        design (str): name of design base class associated with the Component
            to be created. Defaults to None.
        parameters (Mapping[str, Any]): parameters to be used for the stored
            object(s) in its/their product. Defaults to an empty dict.
        attributes (Mapping[str, Any]): attributes to add to the created
            Component object. The keys should be name of the attribute and the
            values should be the value stored for that attribute. Defaults to
            an empty dict.
            
    """
    contents: Sequence[str] = dataclasses.field(default_factory = list)
    name: str = None
    design: str = None
    parameters: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    attributes: Mapping[str, Any] = dataclasses.field(default_factory = dict)
                         

def settings_to_outline(manager: object) -> sourdough.types.Lexicon:
    """Creates a outline based on 'manager.project.settings'.

    Args:
        manager (sourdough.Manager): an instance with options and
            other information needed for outline construction.

    Returns:
        sourdough.types.Lexicon: stored instructions for creating sourdough
            workflows.
        
    """
    # Creates Lexicon to store a project outline.
    outline = sourdough.types.Lexicon()
    # Determines sections of 'project.settings' to exclude in creating sourdough
    # workflow.
    subset = [i for i in manager.project.settings.keys() 
              if not i.endswith(tuple(manager.project.settings.rules.skip))]
    # Creates subset of 'project.settings' with only sections related to
    # sourdough workflows.
    node_settings = manager.project.settings.excludify(subset)
    for name, section in node_settings.items():
        outline = _process_section(
            name = name,
            design = None,
            outline = outline,
            manager = manager)
    return outline

def _process_section(name: str, design: str, outline: sourdough.types.Lexicon,
                      manager: sourdough.Manager, **kwargs) -> (
                          sourdough.types.Lexicon):
    """[summary]

    Args:
        name (str): [description]
        outline (sourdough.types.Lexicon): [description]
        manager (sourdough.Manager): [description]

    Returns:
        sourdough.types.Lexicon: [description]
        
    """
    if name not in outline:
        outline[name] = sourdough.products.Instructions(name = name)
    # Adds appropraite design type to 'outline' for 'name'.
    outline[name].design = _get_design(
        name = name, 
        design = design,
        manager = manager)
    # Adds any appropriate parameters to 'outline' for 'name'.
    outline[name].parameters = _get_parameters(
        name = name, 
        manager = manager)
    # If 'name' is in 'settings', this method iterates through each key, 
    # value pair in section and stores or extracts the information needed
    # to fill out the appropriate Instructions instance in outline.
    if name in manager.project.settings:
        instructions_attributes = {}
        for key, value in manager.project.settings[name].items():
            # If a 'key' has an underscore, text after the last underscore 
            # becomes the 'suffix' and text before becomes the 
            # 'prefix'. If there is no underscore, 'prefix' and
            # 'suffix' are both assigned to 'key'.
            prefix, suffix = _divide_key(key = key)
            # A 'key' ending with one of the component-related suffixes 
            # triggers recursive searching throughout 'manager.project.settings'.
            if suffix in sourdough.resources.options.component_suffixes:
                contains = suffix.rstrip('s')
                outline[prefix].contents = sourdough.tools.listify(value)
                for item in outline[prefix].contents:
                    outline = _add_instructions(
                        name = item,
                        design = contains,
                        outline = outline,
                        manager = manager)
            elif suffix in manager.project.settings.rules.special_section_suffixes:
                instruction_kwargs = {suffix: value}
                outline = _add_instruction(
                    name = prefix, 
                    outline = outline,
                    **instruction_kwargs)
            # All other keys are presumed to be attributes to be added to a
            # Component instance.
            else:
                outline[name].attributes.update({key: value})
    return outline

def _get_design(name: str, design: str, 
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
            return manager.project.settings.rules.default_design
        else:
            return design

def _get_parameters(name: str, 
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
    
def _divide_key(key: str, divider: str = None) -> Tuple[str, str]:
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
    
def _add_instruction(name: str, 
                        outline: sourdough.types.Lexicon, 
                        **kwargs) -> sourdough.types.Lexicon:
    """[summary]

    Args:
        name (str): [description]
        outline (sourdough.types.Lexicon): [description]

    Returns:
        sourdough.types.Lexicon: [description]
        
    """
    # Adds any kwargs to 'outline' as appropriate.
    for key, value in kwargs.items():
        if isinstance(getattr(outline[name], key), list):
            getattr(outline[name].key).extend(
                sourdough.tools.listify(value))
        elif isinstance(getattr(outline[name], key), dict):
            getattr(outline[name], key).update(value) 
        else:
            setattr(outline[name], key, value)           
    return outline

def outline_to_workflow(manager: object) -> object:
    
    return manager


def workflow_to_results(manager: object) -> object:
    
    return manager


@dataclasses.dataclass
class Architect(sourdough.Creator):
    """Creates a outline of a sourdough Plan.

    Architect creates a dictionary representation, a outline, of the overall 
    manager Plan. In the outline produced, keys are the names of components 
    and values are Instruction instances.
    
    Args:
                        
    """
    action: ClassVar[str] = 'Drafting'
    needs: ClassVar[Union[str, Tuple[str]]] = 'settings'
    produces: ClassVar[Type] = 'outline'

    """ Public Methods """
    
    def create(self, manager: sourdough.Manager) -> sourdough.types.Lexicon:
        """Creates a outline based on 'manager.project.settings'.

        Args:
            manager (sourdough.Manager): a Project instance with options and
                other information needed for outline construction.

        Returns:
            Project: with modifications made to its 'design' attribute.
            
        """ 
        outline = manager.bases.product.acquire(key = produces)(
            identification = manager.project.identification)
        for name, section in manager.project.settings.items():
            # Tests whether the section in 'manager.project.settings' is related to the 
            # construction of a project object by examining the key names to see
            # if any end in a suffix corresponding to a known base type. If so, 
            # that section is harvested for information which is added to 
            # 'outline'.
            if (not name.endswith(tuple(manager.project.settings.rules.skip_suffixes))
                    and name not in manager.project.settings.rules.skip_sections
                    and any(
                        [i.endswith(sourdough.resources.options.component_suffixes) 
                        for i in section.keys()])):
                outline = _add_instructions(
                    name = name,
                    design = None,
                    outline = outline,
                    manager = manager)
        return outline
        
    """ Private Methods """
    
    def _add_instructions(self, name: str, design: str,
                          outline: sourdough.types.Lexicon,
                          manager: sourdough.Manager, **kwargs) -> (
                              sourdough.types.Lexicon):
        """[summary]

        Args:
            name (str): [description]
            outline (sourdough.types.Lexicon): [description]
            manager (sourdough.Manager): [description]

        Returns:
            sourdough.types.Lexicon: [description]
            
        """
        if name not in outline:
            outline[name] = sourdough.products.Instructions(name = name)
        # Adds appropraite design type to 'outline' for 'name'.
        outline[name].design = _get_design(
            name = name, 
            design = design,
            manager = manager)
        # Adds any appropriate parameters to 'outline' for 'name'.
        outline[name].parameters = _get_parameters(
            name = name, 
            manager = manager)
        # If 'name' is in 'settings', this method iterates through each key, 
        # value pair in section and stores or extracts the information needed
        # to fill out the appropriate Instructions instance in outline.
        if name in manager.project.settings:
            instructions_attributes = {}
            for key, value in manager.project.settings[name].items():
                # If a 'key' has an underscore, text after the last underscore 
                # becomes the 'suffix' and text before becomes the 
                # 'prefix'. If there is no underscore, 'prefix' and
                # 'suffix' are both assigned to 'key'.
                prefix, suffix = _divide_key(key = key)
                # A 'key' ending with one of the component-related suffixes 
                # triggers recursive searching throughout 'manager.project.settings'.
                if suffix in sourdough.resources.options.component_suffixes:
                    contains = suffix.rstrip('s')
                    outline[prefix].contents = sourdough.tools.listify(value)
                    for item in outline[prefix].contents:
                        outline = _add_instructions(
                            name = item,
                            design = contains,
                            outline = outline,
                            manager = manager)
                elif suffix in manager.project.settings.rules.special_section_suffixes:
                    instruction_kwargs = {suffix: value}
                    outline = _add_instruction(
                        name = prefix, 
                        outline = outline,
                        **instruction_kwargs)
                # All other keys are presumed to be attributes to be added to a
                # Component instance.
                else:
                    outline[name].attributes.update({key: value})
        return outline

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
                return manager.project.settings.rules.default_design
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
                         outline: sourdough.types.Lexicon, 
                         **kwargs) -> sourdough.types.Lexicon:
        """[summary]

        Args:
            name (str): [description]
            outline (sourdough.types.Lexicon): [description]

        Returns:
            sourdough.types.Lexicon: [description]
            
        """
        # Adds any kwargs to 'outline' as appropriate.
        for key, value in kwargs.items():
            if isinstance(getattr(outline[name], key), list):
                getattr(outline[name].key).extend(
                    sourdough.tools.listify(value))
            elif isinstance(getattr(outline[name], key), dict):
                getattr(outline[name], key).update(value) 
            else:
                setattr(outline[name], key, value)           
        return outline

    """ Dunder Methods """
    
    def __str__(self) -> str:
        return pprint.pformat(self, sort_dicts = False, compact = True)
           
      
@dataclasses.dataclass
class Builder(sourdough.Creator):
    """Constructs finalized plan.
    
    Args:
                        
    """
    action: ClassVar[str] = 'Creating'
    needs: ClassVar[Union[str, Tuple[str]]] = 'outline'
    produces: ClassVar[Type] = 'plan'

    """ Public Methods """

    def create(self, manager: sourdough.Manager) -> sourdough.Component:
        """Drafts a Workflow instance based on 'outline' in 'manager'.
            
        """ 
        plan = manager.bases.product.acquire(key = produces)(
            identification = manager.project.identification)
        plan.contents = _create_component(
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
        component = _get_component(name = name, manager = manager)
        return _finalize_component(component = component, 
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
        instructions = manager['outline'][name]
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
                finalizer = _finalize_parallel
            else:
                finalizer = _finalize_serial
        else:
            finalizer = _finalize_element
        component = finalizer(component = component, manager = manager)
        component = _add_attributes(
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
