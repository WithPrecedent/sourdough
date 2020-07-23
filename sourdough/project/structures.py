"""
structures: structure classes for sourdough projects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Project (OptionsMixin, Plan): iterable which contains the needed
        information and data for constructing and executing tree objects.

"""
import abc
import dataclasses
import itertools
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union

import more_itertools

import sourdough

 
@dataclasses.dataclass
class Structure(sourdough.LoaderMixin, sourdough.Component):
    """Contains default types for composite structures to be loaded.
    
    Args:  
        modules (str): name of module where object to use is located (can either 
            be a sourdough or non-sourdough module). Defaults to 'sourdough'.
         
    """
    name: str = None
    modules: Union[str, Sequence[str]] = dataclasses.field(
        default_factory = lambda: list)
    components: Mapping[str, str] = dataclasses.field(
        default_factory = lambda: dict)
    iterator: Union[str, Callable] = iter  
    _loaded: Mapping[str, Any] = dataclasses.field(
        default_factory = lambda: dict)


@dataclasses.dataclass
class TreeStructure(Structure, abc.ABC):
    
    modules: str = dataclasses.field(
        default_factory = lambda: [
            'sourdough.project.workers',
            'sourdough.project.actions'])
    components: Mapping[str, str] = dataclasses.field(
        default_factory = lambda: {
            'root': 'Manager',
            'workers': 'Worker',
            'tasks': 'Task',
            'techniques': 'Technique'})
    _loaded: Mapping[str, Any] = dataclasses.field(
        default_factory = lambda: dict()) 
        

@dataclasses.dataclass
class Chained(TreeStructure):
    """Contains default types for composite structures
    
            
    """      
    iterator: Union[str, Callable] = iter
    
      
@dataclasses.dataclass
class Comparative(TreeStructure):
    """Contains default types for composite structures
    
            
    """    
    iterator: Union[str, Callable] = itertools.product
      

@dataclasses.dataclass
class Flat(TreeStructure):
    """Contains default types for composite structures
    
            
    """    
    iterator: Union[str, Callable] = more_itertools.collapse


@dataclasses.dataclass
class GraphStructure(Structure, abc.ABC):
    """Contains default types for composite structures
    
            
    """    
    modules: str = dataclasses.field(
        default_factory = lambda: [
            'sourdough.project.graphs',
            'sourdough.project.actions'])
    components: Mapping[str, str] = dataclasses.field(
        default_factory = lambda: {
            'root': 'Node',
            'node': 'Node',
            'edges': 'Edge',
            'task': 'Task',
            'techniques': 'Technique'})
    _loaded: Mapping[str, Any] = dataclasses.field(
        default_factory = lambda: dict())  


@dataclasses.dataclass
class DirectedGraph(GraphStructure):
    """Contains default types for composite structures
    
            
    """   
    iterator: Union[str, Callable] = 'iterable'

 
@dataclasses.dataclass
class Cycle(Structure):
    """Contains default types for composite structures
    
            
    """    
    iterator: Union[str, Callable] = itertools.cycle
    