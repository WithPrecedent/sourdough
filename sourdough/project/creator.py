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
    
    """ Required Subclass Class Methods """
    
    @abc.abstractmethod
    def create(self, node: str, **kwargs) -> sourdough.project.Workflow:
        """Subclasses must provide their own methods."""
        pass

    """ Properties """
    
    @property
    def settings(self) -> sourdough.project.Settings:
        return self.manager.project.settings

    @property
    def library(self) -> sourdough.types.Library:
        return self.manager.bases.workflow.library
    
    """ Private Methods """

    def _parse_section(self, node: str) -> Dict[str, List[str]]:
        """[summary]

        Args:
            self ([type]): [description]
            List ([type]): [description]

        Returns:
            [type]: [description]
            
        """
        section = self.settings[node]
        component_suffixes = self.library.suffixes
        component_keys = [
            k for k in section.keys() if k.endswith(component_suffixes)]
        if component_keys:
            components_key = [i for i in component_keys if i.startswith(node)][0]
            components = sourdough.tools.listify(section.pop(components_key))
            subcomponents = {}
            for name in components:
                subcomponent_key = [
                    i for i in component_keys if i.startswith(name)][0]
                subcomponents[name] = component_keys[subcomponent_key]
        else:
            subcomponents = None
        return subcomponents
    
    
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
    
    def add(self, nodes: Sequence[str], 
            workflow: sourdough.project.Workflow) -> sourdough.project.Workflow:
        """[summary]

        Args:
            nodes (Sequence[str]): [description]
            workflow (sourdough.project.Workflow): [description]

        Returns:
            sourdough.project.Workflow: [description]
            
        """
        for endpoint in workflow.endpoints:
            workflow.add_edge(start = endpoint, stop = nodes[0])
        workflow = workflow.append(nodes = nodes)
        return workflow
    
    def create(self, node: str, **kwargs) -> sourdough.project.Workflow:
        """Creates a Creator instance from a section of a Settings instance.

        Args:
            node (str): starting node in the workflow being created.
                
        Returns:
            Workflow: derived from 'section'.
            
        """
        workflow = sourdough.project.Workflow()
        
        return  
    

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
    