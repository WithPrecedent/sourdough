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
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Component is called, 'name' is set based upon
            the 'get_name' method in Component. If that method is not 
            overridden by a subclass instance, 'name' will be assigned to the 
            snake case version of the class name ('__class__.__name__').    
        module (str): name of module where object to use is located (can either 
            be a sourdough or non-sourdough module). Defaults to 'sourdough'.
        default_module (str): a backup name of module where object to use is 
            located (can either be a sourdough or non-sourdough module).
            Defaults to 'sourdough'.
        root (str): the top-level class in a composite structure (if one 
            exists). Defaults to str. 
        component (str): the typical intermediate-level class
            in a composite structure. Defaults to str. 
        base (str): the bottom-level primitive class in a
            composite structure. Defaults to str. 
        wrapper (str): the class for wrapping base, if one
            exists. Defaults to sourdough.Task.
        connector (str): the class for connecting composite
            objects, if one exists. Defaults to None.
            
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
    def __iter__(self) -> Iterator:  
        """Subclasses must provide their own methods."""
        pass

    @abc.abstractmethod
    def __next__(self) -> Iterator:  
        """Subclasses must provide their own methods."""
        pass


# @dataclasses.dataclass
# class Tree(Structure, abc.ABC):
    
#     modules: str = dataclasses.field(
#         default_factory = lambda: [
#             'sourdough.project.workers',
#             'sourdough.project.actions'])
#     components: Mapping[str, str] = dataclasses.field(
#         default_factory = lambda: {
#             'root': 'Manager'
#             'workers': 'Worker',
#             'tasks': 'Task',
#             'techniques': 'Technique'})
#     _loaded: Mapping[str, Any] = dataclasses.field(
#         default_factory = lambda: dict()) 
        

# @dataclasses.dataclass
# class Chained(Tree):
#     """Contains default types for composite structures
    
            
#     """      
    
#     """ Public Methods """
    
#     def design(self, plan: 'sourdough.Plan') -> 'sourdough.Plan':  
#         """[summary]

#         Returns:
#             [type]: [description]
            
#         """
#         return plan    

#     def __iter__(self) -> Iterable:
#         return iter(self.contents)
    
    
    
# @dataclasses.dataclass
# class Comparative(Tree):
#     """Contains default types for composite structures
    
            
#     """    

#     """ Public Methods """
    
#     def design(self, plan: 'sourdough.Plan') -> 'sourdough.Plan':  
#         """[summary]

#         Returns:
#             [type]: [description]
            
#         """
#         return plan    

# @dataclasses.dataclass
# class Collapsed(Structure):
#     """Contains default types for composite structures
    
            
#     """    
#     def __iter__(self) -> Iterable:
#         return more_itertools.collapse(self.contents) 

# @dataclasses.dataclass
# class Repeater(Structure):
#     """Contains default types for composite structures
    
            
#     """    
#     def __iter__(self) -> Iterable:
#         return itertools.tee(self.contents, count = 2)
    
 
# @dataclasses.dataclass
# class Cycle(Structure):
#     """Contains default types for composite structures
    
            
#     """    
#     modules: str = dataclasses.field(
#         default_factory = lambda: [
#             'sourdough.project.graphs',
#             'sourdough.project.actions'])
#     components: Mapping[str, str] = dataclasses.field(
#         default_factory = lambda: {
#             'root': 'Node'
#             'node': 'Node',
#             'edges': 'Edge',
#             'task': 'Task',
#             'techniques': 'Technique'})
#     _loaded: Mapping[str, Any] = dataclasses.field(
#         default_factory = lambda: dict())  

#     def __iter__(self) -> Iterable:
#         return itertools.cycle(self.contents)   

# @dataclasses.dataclass
# class Graph(Structure):
#     """Contains default types for composite structures
    
            
#     """    
#     modules: str = dataclasses.field(
#         default_factory = lambda: [
#             'sourdough.project.graphs',
#             'sourdough.project.actions'])
#     components: Mapping[str, str] = dataclasses.field(
#         default_factory = lambda: {
#             'root': 'Node'
#             'node': 'Node',
#             'edges': 'Edge',
#             'task': 'Task',
#             'techniques': 'Technique'})
#     _loaded: Mapping[str, Any] = dataclasses.field(
#         default_factory = lambda: dict()) 
    
#     """ Public Methods """
    
#     def design(self, plan: 'sourdough.Plan') -> 'sourdough.Plan':  
#         """[summary]

#         Returns:
#             [type]: [description]
            
#         """
#         return plan   


