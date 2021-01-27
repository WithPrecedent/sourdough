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
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import sourdough



@dataclasses.dataclass
class ProcessedSection(object):
    
    components: Dict[str, List] = dataclasses.field(default_factory = dict)
    contains: Dict[str, str] = dataclasses.field(default_factory = dict)
    design: str = None
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
    
    def create(self, node: str) -> sourdough.project.Workflow:
        """Creates a Creator instance from a section of a Settings instance.

        Args:
            node (str): starting node in the workflow being created.
                
        Returns:
            Workflow: derived from 'section'.
            
        """
        processed = self.parse_section(name = node)
        adjacency = self.create_adjacency(processed = processed)
        components = self.create_components(processed = processed)
        return sourdough.project.Workflow(
            contents = adjacency, 
            components = components)

    def parse_section(self, name: str) -> ProcessedSection:
        """[summary]

        Args:

        Returns:
            ProcessedSection
            
        """
        section = self.settings[name]
        processed = ProcessedSection()
        processed.design = self._get_design(name = name, section = section)
        component_suffixes = self.library.suffixes
        section_component = self.library.borrow(name = [name, processed.design])
        parameters = self._get_parameters(component = section_component)
        for key, value in section.items():
            prefix, suffix = self._divide_key(key = key)
            if 'design' == suffix:
                pass
            elif suffix in component_suffixes:
                processed.contains[prefix] = [suffix[:-1]]
                processed.components[prefix] = value 
            elif suffix in parameters:
                processed.parameters[suffix] = value 
            elif prefix == name:
                processed.attributes[suffix] = value
            else:
                processed.other[key] = value
        return processed
   

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
            component: Type[sourdough.types.Base], 
            skip: List[str] = lambda: ['name', 'contents']) -> Tuple[str]:
        """
        """
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
            processed: ProcessedSection) -> sourdough.project.Component:
        for key, value in processed.attributes.items():
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

    """ Class Methods """

    def add(self, nodes: List[List[str]], 
            workflow: sourdough.project.Workflow) -> sourdough.project.Workflow:
        """[summary]

        Args:
            nodes (Sequence[str]): [description]
            workflow (sourdough.project.Workflow): [description]

        Returns:
            sourdough.project.Workflow: [description]
            
        """
        for plan in nodes:
            for endpoint in workflow.endpoints:
                workflow.add_edge(start = endpoint, stop = plan[0])
            workflow.append(nodes = nodes)
        return workflow
       
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
    