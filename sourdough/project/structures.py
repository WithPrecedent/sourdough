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
import collections.abc
import dataclasses
import itertools
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union

import more_itertools

import sourdough

 
@dataclasses.dataclass
class Structure(sourdough.LoaderMixin, collections.abc.Iterator, abc.ABC):
    """Contains default types for composite structures to be loaded.
    
    Args:  
        modules (str): name of module where object to use is located (can either 
            be a sourdough or non-sourdough module). Defaults to 'sourdough'.
            
    """
    modules: Union[str, Sequence[str]] = dataclasses.field(
        default_factory = lambda: list)
    components: Mapping[str, str] = dataclasses.field(
        default_factory = lambda: dict)
    _loaded: Mapping[str, Any] = dataclasses.field(
        default_factory = lambda: dict)  
    
    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def design(self, plan: 'sourdough.Plan') -> 'sourdough.Plan':  
        """Subclasses must provide their own methods."""
        pass

    @abc.abstractmethod
    def iterable(self, **kwargs) -> Iterable:  
        """Subclasses must provide their own methods."""
        pass


@dataclasses.dataclass
class Tree(Structure, abc.ABC):
    
    modules: str = dataclasses.field(
        default_factory = lambda: [
            'sourdough.project.workers',
            'sourdough.project.actions'])
    components: Mapping[str, str] = dataclasses.field(
        default_factory = lambda: {
            'root': 'Manager'
            'workers': 'Worker',
            'tasks': 'Task',
            'techniques': 'Technique'})
    _loaded: Mapping[str, Any] = dataclasses.field(
        default_factory = lambda: dict()) 
        

@dataclasses.dataclass
class Chained(Tree):
    """Contains default types for composite structures
    
            
    """      
    
    """ Public Methods """
    
    def design(self, plan: 'sourdough.Plan') -> 'sourdough.Plan':  
        """[summary]

        Returns:
            [type]: [description]
            
        """
        return plan    

    def iterable(self) -> Iterable:
        return iter(self.contents)
    
    
    
@dataclasses.dataclass
class Comparative(Tree):
    """Contains default types for composite structures
    
            
    """    

    """ Public Methods """
    
    def design(self, plan: 'sourdough.Plan') -> 'sourdough.Plan':  
        """[summary]

        Returns:
            [type]: [description]
            
        """
        return plan    

@dataclasses.dataclass
class Collapsed(Structure):
    """Contains default types for composite structures
    
            
    """    
    def iterable(self) -> Iterable:
        return more_itertools.collapse(self.contents) 


@dataclasses.dataclass
class Repeater(Structure):
    """Contains default types for composite structures
    
            
    """    
    def iterable(self) -> Iterable:
        return itertools.tee(self.contents, count = 2)
    
 
@dataclasses.dataclass
class Cycle(Structure):
    """Contains default types for composite structures
    
            
    """    
    modules: str = dataclasses.field(
        default_factory = lambda: [
            'sourdough.project.graphs',
            'sourdough.project.actions'])
    components: Mapping[str, str] = dataclasses.field(
        default_factory = lambda: {
            'root': 'Node'
            'node': 'Node',
            'edges': 'Edge',
            'task': 'Task',
            'techniques': 'Technique'})
    _loaded: Mapping[str, Any] = dataclasses.field(
        default_factory = lambda: dict())  

    def iterable(self) -> Iterable:
        return itertools.cycle(self.contents)   


@dataclasses.dataclass
class Graph(Structure, abc.ABC):
    """Contains default types for composite structures
    
            
    """    
    modules: str = dataclasses.field(
        default_factory = lambda: [
            'sourdough.project.graphs',
            'sourdough.project.actions'])
    components: Mapping[str, str] = dataclasses.field(
        default_factory = lambda: {
            'root': 'Node'
            'node': 'Node',
            'edges': 'Edge',
            'task': 'Task',
            'techniques': 'Technique'})
    _loaded: Mapping[str, Any] = dataclasses.field(
        default_factory = lambda: dict()) 
    
    """ Public Methods """
    
    def design(self, plan: 'sourdough.Plan') -> 'sourdough.Plan':  
        """[summary]

        Returns:
            [type]: [description]
            
        """
        return plan   


@dataclasses.dataclass
class DirectedGraph(Structure, abc.ABC):
    """Contains default types for composite structures
    
            
    """   
    
    def iterable(self) -> Iterable:
        return self

