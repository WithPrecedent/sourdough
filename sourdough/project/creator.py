"""
creator: produces workflows and their components
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:


"""
from __future__ import annotations
import abc
import copy
import dataclasses
import inspect
import itertools
from os import PRIO_PGRP
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import sourdough


@dataclasses.dataclass
class Blueprint(object):
    """[summary]

    Args:
        object ([type]): [description]
        
    """
    name: str = None
    components: Dict[str, List] = dataclasses.field(default_factory = dict)
    designs: Dict[str, str] = dataclasses.field(default_factory = dict)
    parameters: Dict[str, Any] = dataclasses.field(default_factory = dict)
    attributes: Dict[str, Any] = dataclasses.field(default_factory = dict)
    other: Dict[str, Any] = dataclasses.field(default_factory = dict)


@dataclasses.dataclass
class Creator(sourdough.types.Base, abc.ABC):
    """Creates a sourdough object.
    
    Args:
        manager (Manager): associated project manager containing needed data
            for creating objects.
        library (ClassVar[Library]): related Library instance that will store
            subclasses and allow runtime construction and instancing of those
            stored subclasses.
                       
    """
    manager: sourdough.project.Manager = dataclasses.field(
        repr = False, 
        default = None)
    library: ClassVar[sourdough.types.Library] = sourdough.types.Library()
               
    """ Required Subclass Class Methods """
    
    @abc.abstractmethod
    def create(self, **kwargs) -> sourdough.types.Base:
        """Subclasses must provide their own methods."""
        pass
    

@dataclasses.dataclass
class WorkflowCreator(abc.ABC):
    """Creates a sourdough object.
    
    Args:
        manager (Manager): associated project manager containing needed data
            for creating objects.
                       
    """
    manager: sourdough.project.Manager = dataclasses.field(
        repr = False, 
        default = None)

    """ Properties """
    
    @property
    def settings(self) -> sourdough.project.Settings:
        return self.manager.project.settings

    @property
    def library(self) -> sourdough.types.Library:
        return self.manager.bases.workflow.library
     
    """ Required Public Methods """
    
    def create(self, name: str) -> sourdough.project.Workflow:
        """Creates a Creator instance from a section of a Settings instance.

        Args:
            name (str): starting node in the workflow being created.
                
        Returns:
            Workflow: derived from 'section'.
            
        """
        blueprint = self.parse_section(name = name)
        graph = self.create_graph(blueprint = blueprint)
        components = self.create_components(blueprint = blueprint)
        return sourdough.project.Workflow(
            graph = graph, 
            components = components)

    def parse_section(self, name: str) -> Blueprint:
        """[summary]

        Args:

        Returns:
            Blueprint
            
        """
        section = self.settings[name]
        blueprint = Blueprint(name = name)
        design = self._get_design(name = name, section = section)
        blueprint.designs[name] = design
        parameters = self._get_parameters(names = [name, design])
        for key, value in section.items():
            prefix, suffix = self._divide_key(key = key)
            if 'design' == suffix:
                pass
            elif suffix in self.library.suffixes:
                blueprint.bases.update(dict.fromkeys(value, suffix[:-1]))
                blueprint.components[prefix] = value 
            elif suffix in parameters:
                blueprint.parameters[suffix] = value 
            elif prefix == name:
                blueprint.attributes[suffix] = value
            else:
                blueprint.other[key] = value
        return blueprint
   
    def create_components(self, 
            blueprint: Blueprint) -> Dict[str, sourdough.project.Component]:
        """
        """
        instances = {}
        design = blueprint.designs[blueprint.name]
        section_keys = [blueprint.name, design]
        section_component = self.library.borrow(name = [section_keys])
        instances[blueprint.name] = section_component(
            name = blueprint.name, 
            **blueprint.parameters)
        for value in blueprint.components.values():
            for item in value:
                if not item in self.settings:
                    subcomponent_keys = [item, blueprint.designs[item]]
                    subcomponent = self.library.borrow(name = subcomponent_keys)
                    instance = subcomponent(name = item)
                    instances[item] = self._inject_attributes(
                        component = instance, 
                        blueprint = blueprint)
        return instances
                     
    """ Private Methods """

    def _get_design(self, name: str, section: Mapping[str, Any]) -> str:
        """
        """
        try:
            design = section[f'{name}_design']
        except KeyError:
            try:
                design = section[f'design']
            except KeyError:
                try:
                    design = self.settings['sourdough'][f'default_design']
                except KeyError:
                    design = None
        return design

    def _get_parameters(self, 
            names: List[str], 
            skip: List[str] = lambda: [
                'name', 'contents', 'design']) -> Tuple[str]:
        """
        """
        component = self.library.borrow(name = names)
        parameters = list(component.__annotations__.keys())
        return tuple(i for i in parameters if i not in [skip])

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

    def _inject_attributes(self, 
            component: sourdough.project.Component, 
            blueprint: Blueprint) -> sourdough.project.Component:
        """[summary]

        Args:
            component (sourdough.project.Component): [description]
            blueprint (Blueprint): [description]

        Returns:
            sourdough.project.Component: [description]
        """
        for key, value in blueprint.attributes.items():
            setattr(component, key, value)
        return component
          

@dataclasses.dataclass
class Planner(WorkflowCreator):
    """Creates a serial workflow without branching.

    An Planner is a sequence of nodes with one entering edge and one departing 
    edge (serial workflow).
            
    Args:
        manager (Manager): associated project manager containing needed data
            for creating objects.
                       
    """
    manager: sourdough.project.Manager = dataclasses.field(
        repr = False, 
        default = None)
    
    """ Public Methods """

    def create_graph(self, 
            blueprint: Blueprint) -> Dict[str, List[str]]:
        """[summary]

        Args:
            blueprint (Blueprint): [description]

        Returns:
            Dict[str, List[str]]: [description]
            
        """
        graph = sourdough.composites.Graph()
        graph = self._add_plan(
            contents = blueprint.contents[blueprint.name],
            blueprint = blueprint,
            graph = graph)
        return graph

    """ Private Methods """
          
    def _add_plan(self, 
            contents: List[str], 
            blueprint: Blueprint,
            graph: sourdough.composites.Graph) -> sourdough.composites.Graph:
        """[summary]

        Args:
            contents (List[str]): [description]
            blueprint (Blueprint): [description]
            graph (sourdough.composites.Graph): [description]

        Returns:
            sourdough.composites.Graph: [description]
            
        """
        for item in contents:
            try:
                subcontents = blueprint.components[item]
                graph = self._add_plan(
                    contents = subcontents,
                    blueprint = blueprint,
                    graph = graph)
            except KeyError:
                graph.extend(contents)
        return graph
                
        
@dataclasses.dataclass
class Researcher(WorkflowCreator):
    """Creates a parallel workflow with edges to multiple serial workflows.

    A Researcher creates a braching set of nodes with one entering edge 
    connected to each serial workflow 
    
    Args:
        manager (Manager): associated project manager containing needed data
            for creating objects.
                       
    """
    manager: sourdough.project.Manager = dataclasses.field(
        repr = False, 
        default = None)

    """ Public Methods """

    def create_graph(self, 
            blueprint: Blueprint) -> Dict[str, List[str]]:
        """[summary]

        Args:
            blueprint (Blueprint): [description]

        Returns:
            Dict[str, List[str]]: [description]
            
        """
        graph = sourdough.composites.Graph()
        graph = self._add_plan(
            contents = blueprint.contents[blueprint.name],
            blueprint = blueprint,
            graph = graph)
        return graph
       
    def create(self, 
            node: str,
            contents: Sequence[str], 
            section: Mapping[str, Any],
            component_keys: Sequence[str],
            prefix: str = 'plan', 
            **kwargs) -> Creator:
        """Creates a Creator instance from a section of a Settings instance.

        Args:
            section (Mapping[str, Any]): section of a Settings instance to
                use to create a Creator.
                
        Returns:
            Creator: derived from 'section'
            
        """
        possible = []
        for item in contents:
            inner_key = [i for i in component_keys if i.startswith(item)][0]
            inner_contents = sourdough.tools.listify(section.pop(inner_key))
            possible.append(inner_contents)
        # Computes Cartesian product of possible permutations.
        permutations = list(map(list, itertools.product(*possible)))
        for plan in permutations:
            workflow = self._create_agenda(nodes = plan, workflow = workflow)
        keys = {f'{prefix}_{i}' for i in len(permutations)}
        contents = dict(zip(keys, contents))
        return self(contents = contents, node = node, **kwargs)   

    """ Private Methods """
          
    def _add_plan(self, 
            contents: List[str], 
            blueprint: Blueprint,
            graph: sourdough.composites.Graph) -> sourdough.composites.Graph:
        """[summary]

        Args:
            contents (List[str]): [description]
            blueprint (Blueprint): [description]
            graph (sourdough.composites.Graph): [description]

        Returns:
            sourdough.composites.Graph: [description]
            
        """
        for item in contents:
            try:
                subcontents = blueprint.components[item]
                graph = self._add_plan(
                    contents = subcontents,
                    blueprint = blueprint,
                    graph = graph)
            except KeyError:
                graph.extend(contents)
        return graph
      