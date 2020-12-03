"""
creators: classes for building and storing different steps in sourdough project
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Instructions (Progression): information needed to create a single Component.
    Architect (Creator):
    Builder (Creator):
    Worker (Creator):
    
"""
from __future__ import annotations
import abc
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
class Blueprint(sourdough.types.Lexicon):
    """Class of essential information from Settings.
    
    Args:
        contents (Mapping[str, Instructions]]): stored dictionary which contains
            Instructions instances. Defaults to an empty dict.
        identification (str): a unique identification name for the related 
            Project instance.            
    """
    contents: Mapping[str, Instructions] = dataclasses.field(
        default_factory = dict)
    identification: str = None

    """ Public Methods """

    """ Dunder Methods """
    
    def __getitem__(self, key: str) -> Instructions:
        """Autovivifies if there is no Instructions instance.
        
        Args:
        
        """
        try:
            return super().__getitem__(key = key)
        except KeyError:
            super().__setitem__(key = key, value = Instructions(name = key))
            return self[key]
                   

@dataclasses.dataclass
class Architect(sourdough.Creator):
    """Creates a blueprint of a workflow.

    Architect creates a dictionary representation, a blueprint, of the overall 
    project workflow. In the blueprint produced, keys are the names of 
    components and values are Instruction instances.
    
    Args:
                        
    """
    action: ClassVar[str] = 'Drafting'
    needs: ClassVar[Union[str, Tuple[str]]] = 'settings'
    produces: ClassVar[str] = 'blueprint'

    """ Public Methods """
    
    def create(self, project: sourdough.Project) -> sourdough.types.Lexicon:
        """Creates a blueprint based on 'project.settings'.

        Args:
            project (sourdough.Project): a Project instance with resources and
                other information needed for blueprint construction.

        Returns:
            Project: with modifications made to its 'design' attribute.
            
        """ 
        blueprint = Blueprint(identification = project.identification)
        for name, section in project.settings.items():
            # Tests whether the section in 'project.settings' is related to the 
            # construction of a project object by examining the key names to see
            # if any end in a suffix corresponding to a known base type. If so, 
            # that section is harvested for information which is added to 
            # 'blueprint'.
            if (not name.endswith(tuple(project.rules.skip_suffixes))
                    and name not in project.rules.skip_sections
                    and any([i.endswith(project.rules.component_suffixes) 
                        for i in section.keys()])):
                blueprint = self._add_instructions(
                    name = name,
                    blueprint = blueprint,
                    design = None,
                    project = project)
        return blueprint
        
    """ Private Methods """
    
    def _add_instructions(self, name: str, blueprint: Blueprint, design: str,
                          project: sourdough.Project, **kwargs) -> Blueprint:
        """[summary]

        Args:
            name (str): [description]
            blueprint (sourdough.types.Lexicon): [description]
            project (sourdough.Project): [description]

        Returns:
            sourdough.types.Lexicon: [description]
            
        """
        # Adds appropraite design type to 'blueprint' for 'name'.
        blueprint[name].design = self._get_design(
            name = name, 
            design = design,
            project = project)
        # Adds any appropriate parameters to 'blueprint' for 'name'.
        blueprint[name].parameters = self._get_parameters(
            name = name, 
            project = project)
        print('test parameters', name, blueprint[name].parameters)
        print('test suffixes', project.rules.component_suffixes)
        # If 'name' is in 'settings', this method iterates through each key, 
        # value pair in section and stores or extracts the information needed
        # to fill out the appropriate Instructions instance in blueprint.
        if name in project.settings:
            instructions_attributes = {}
            for key, value in project.settings[name].items():
                # If a 'key' has an underscore, text after the last underscore 
                # becomes the 'suffix' and text before becomes the 
                # 'prefix'. If there is no underscore, 'prefix' and
                # 'suffix' are both assigned to 'key'.
                prefix, suffix = self._divide_key(key = key)
                # A 'key' ending with one of the component-related suffixes 
                # triggers recursive searching throughout 'project.settings'.
                if suffix in project.rules.component_suffixes:
                    contains = suffix.rstrip('s')
                    blueprint[prefix].contents = sourdough.tools.listify(value) 
                    blueprint = self._get_instructions(
                        name = prefix,
                        blueprint = blueprint,
                        project = project,
                        design = contains)
                elif suffix in project.rules.special_suffixes:
                    instruction_kwargs = {suffix: value}
                    blueprint = self._add_instruction(
                        name = prefix, 
                        blueprint = blueprint,
                        **instruction_kwargs)
                # All other keys are presumed to be attributes to be added to a
                # Component instance.
                else:
                    blueprint[name].attributes.update({key: value})
        for key, value in kwargs.items():
            setattr(blueprint[name], key, value)
        return blueprint

    def _get_design(self, name: str, design: str, 
                  project: sourdough.Project) -> str:
        """[summary]

        Args:
            name (str): [description]
            design (str): [description]
            project (sourdough.Project): [description]

        Returns:
            str: [description]
            
        """
        try:
            return project.settings[name][f'{name}_design']
        except KeyError:
            if design is None:
                return project.rules.default_design
            else:
                return design

    def _get_parameters(self, name: str, 
                        project: sourdough.Project) -> Dict[Any, Any]:
        """[summary]

        Args:
            name (str): [description]
            project (sourdough.Project): [description]

        Returns:
            sourdough.types.Lexicon: [description]
            
        """
        try:
            return project.settings[f'{name}_parameters']
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
            suffix = key.split('_')[-1][:-1]
            prefix = key[:-len(suffix) - 2]
        else:
            prefix = suffix = key
        return prefix, suffix
       
    def _add_instruction(self, name: str, blueprint: Blueprint, 
                         **kwargs) -> Blueprint:
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
    """Constructs finalized workflow.
    
    Args:
                        
    """
    action: ClassVar[str] = 'Creating'
    needs: ClassVar[Union[str, Tuple[str]]] = 'blueprint'
    produces: ClassVar[str] = 'workflow'

    """ Public Methods """

    def create(self, project: sourdough.Project) -> sourdough.Component:
        """Drafts a Workflow instance based on 'blueprint' in 'project'.
            
        """ 
        return self._create_component(name = project.name, project = project)
    
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
        workflow = self._get_component(name = name, project = project)
        return self._finalize_component(component = workflow, 
                                        project = project)

    def _get_component(self, name: str,
                       project: sourdough.Project) -> sourdough.Component:
        """[summary]

        Args:
            name (str): [description]
            project (sourdough.Project): [description]

        Raises:
            KeyError: [description]

        Returns:
            Mapping[str, sourdough.Component]: [description]
            
        """
        instructions = project['blueprint'][name]
        kwargs = {'name': name, 'contents': instructions.contents}
        try:
            component = project.resources.component.borrow(key = name)
            for key, value in kwargs.items():
                if value:
                    setattr(component, key, value)
        except KeyError:
            try:
                component = project.resources.component.acquire(key = name)
                component = component(**kwargs)
            except KeyError:
                try:
                    component = project.resources.component.acquire(
                        key = instructions.design)
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
            if component.parallel:
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
                         project: sourdough.Project) -> sourdough.Workflow:
        """[summary]

        Args:
            component (sourdough.Component): [description]
            components (Mapping[str, sourdough.Component]): [description]
            project (sourdough.Project): [description]

        Returns:
            sourdough.WorkFlow: [description]
            
        """
        possible = []
        for item in component.contents:
            possible.append(project['blueprint'][item].contents)
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
                       project: sourdough.Project) -> sourdough.Workflow:
        """[summary]

        Args:
            component (sourdough.Component): [description]
            components (Mapping[str, sourdough.Component]): [description]
            project (sourdough.Project): [description]

        Returns:
            Workflow: [description]
            
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

    def _add_attributes(self, component: sourdough.Component,
                        project: sourdough.Project) -> sourdough.Component:
        """[summary]

        Returns:
            [type]: [description]
            
        """
        attributes = project['blueprint'][component.name].attributes
        for key, value in attributes.items():
            setattr(component, key, value)
        return component    


@dataclasses.dataclass
class Worker(sourdough.Creator):
    """Applies a project Workflow and produces results.

    Args:

    """
    action: ClassVar[str] = 'Computing'
    needs: ClassVar[Union[str, Tuple[str]]] = 'workflow'
    produces: ClassVar[str] = 'results'
    
    """ Public Methods """
 
    def create(self, project: sourdough.Project, 
               **kwargs) -> sourdough.types.Lexicon:        
        """Computes results based on a workflow.
            
        """
        results = sourdough.types.Lexicon()
        if project.data is not None:
            kwargs['data'] = project.data
        for component in project['workflow']:
            results.update({component.name: component.apply(**kwargs)})
        return results
