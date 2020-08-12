"""
composites: sourdough composite objects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:


"""
from __future__ import annotations
import abc
import dataclasses
from typing import (Any, Callable, ClassVar, Container, Generic, Iterable, 
                    Iterator, Mapping, Sequence, Tuple, TypeVar, Union)

import sourdough


@dataclasses.dataclass
class Composite(sourdough.RegistryMixin, sourdough.Hybrid, abc.ABC):
    """Base class for composite objects in sourdough projects.
        
    Args:
        contents (Sequence[Union[str, sourdough.Component]]): a list of str or
            Components. 
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Element is called, 'name' is set based upon
            the 'get_name' method in Element. If that method is not 
            overridden by a subclass instance, 'name' will be assigned to the 
            snake case version of the class name ('__class__.__name__').
    
    """
    contents: Sequence[Union[str, sourdough.Component]] = dataclasses.field(
        default_factory = list)
    name: str = None
    registry: ClassVar[sourdough.Inventory] = sourdough.Inventory()
    _excess_attributes: Sequence[str] = ['registry', '_exceess_attributes']
    
    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def iterate(self, **kwargs) -> Iterator:
        pass
    
    @abc.abstractmethod
    def activate(self, **kwargs) -> Iterator:
        pass    
    
    @abc.abstractmethod
    def finalize(self, **kwargs) -> Iterator:
        pass
    
    """ Dunder Methods """
    
    def __iter__(self) -> Iterator:
        return self.iterate()

    
@dataclasses.dataclass
class Aggregation(Composite, sourdough.Component):
    """Base class for composite objects in sourdough projects.
    
    Distinguishing characteristics of an Aggregation:
        1) Order doesn't matter.
        2) All stored Components must be of the same type.
        
    Args:
        contents (Sequence[Union[str, sourdough.Component]]): a list of str or
            Components. 
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Element is called, 'name' is set based upon
            the 'get_name' method in Element. If that method is not 
            overridden by a subclass instance, 'name' will be assigned to the 
            snake case version of the class name ('__class__.__name__').
    
    """
    contents: Sequence[Union[str, sourdough.Component]] = dataclasses.field(
        default_factory = list)
    name: str = None
   

@dataclasses.dataclass
class SerialComposite(Composite, sourdough.Component):
    """Base class for serial composite objects in sourdough projects.
        
    Args:
        contents (Sequence[Union[str, sourdough.Component]]): a list of str or
            Components. 
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Element is called, 'name' is set based upon
            the 'get_name' method in Element. If that method is not 
            overridden by a subclass instance, 'name' will be assigned to the 
            snake case version of the class name ('__class__.__name__').
    
    """
    contents: Sequence[Union[str, sourdough.Component]] = dataclasses.field(
        default_factory = list)
    name: str = None
         
    
@dataclasses.dataclass
class Pipeline(SerialComposite):
    """Base class for composite objects in sourdough projects.

    Distinguishing characteristics of a Contest:
        1) Follows a sequence of instructions (serial structure).
        2) It may pass data or other arguments to the next step in the sequence.
        
    Args:
        contents (Sequence[Union[str, sourdough.Component]]): a list of str or
            Components. 
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Element is called, 'name' is set based upon
            the 'get_name' method in Element. If that method is not 
            overridden by a subclass instance, 'name' will be assigned to the 
            snake case version of the class name ('__class__.__name__').
    
    """
    contents: Sequence[Union[str, sourdough.Component]] = dataclasses.field(
        default_factory = list)
    name: str = None
            

@dataclasses.dataclass
class ParallelComposite(Composite, sourdough.Component):
    """Base class for parallel composite objects in sourdough projects.
        
    Args:
        contents (Sequence[Union[str, sourdough.Component]]): a list of str or
            Components. 
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Element is called, 'name' is set based upon
            the 'get_name' method in Element. If that method is not 
            overridden by a subclass instance, 'name' will be assigned to the 
            snake case version of the class name ('__class__.__name__').
    
    """
    contents: Sequence[Union[str, sourdough.Component]] = dataclasses.field(
        default_factory = list)
    iterations: int = 10
    name: str = None


@dataclasses.dataclass
class Contest(ParallelComposite):
    """Base class for composite objects in sourdough projects.

    Distinguishing characteristics of a Contest:
        1) Repeats a Pipeline with different options (parallel structure).
        2) Chooses the best option based upon selected criteria.
        
    Args:
        contents (Sequence[Union[str, sourdough.Component]]): a list of str or
            Components. 
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Element is called, 'name' is set based upon
            the 'get_name' method in Element. If that method is not 
            overridden by a subclass instance, 'name' will be assigned to the 
            snake case version of the class name ('__class__.__name__').
    
    """
    contents: Sequence[Union[
        Tuple[str, str], 
        sourdough.Pipeline]] = dataclasses.field(default_factory = list)
    iterations: int = 10
    criteria: str = None
    name: str = None
    
    
@dataclasses.dataclass
class Study(ParallelComposite):
    """Base class for composite objects in sourdough projects.

    Distinguishing characteristics of a Study:
        1) Repeats a Pipeline with different options (parallel structure).
        2) Maintains all of the repetitions without selecting or averaging the 
            results.
           
    Args:
        contents (Sequence[Union[str, sourdough.Component]]): a list of str or
            Components. 
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Element is called, 'name' is set based upon
            the 'get_name' method in Element. If that method is not 
            overridden by a subclass instance, 'name' will be assigned to the 
            snake case version of the class name ('__class__.__name__').
    
    """
    contents: Sequence[Union[
        Tuple[str, str], 
        sourdough.Pipeline]] = dataclasses.field(default_factory = list)
    iterations: int = None
    name: str = None
    
    
@dataclasses.dataclass
class Survey(ParallelComposite):
    """Base class for composite objects in sourdough projects.

    Distinguishing characteristics of a Survey:
        1) Repeats a Pipeline with different options (parallel structure).
        2) Averages or otherwise combines the results based upon selected 
            criteria.
            
    Args:
        contents (Sequence[Union[str, sourdough.Component]]): a list of str or
            Components. 
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Element is called, 'name' is set based upon
            the 'get_name' method in Element. If that method is not 
            overridden by a subclass instance, 'name' will be assigned to the 
            snake case version of the class name ('__class__.__name__').
    
    """
    contents: Sequence[Union[
        Tuple[str, str], 
        sourdough.Pipeline]] = dataclasses.field(default_factory = list)
    iterations: int = 10
    criteria: str = None
    name: str = None
        
        

# @dataclasses.dataclass
# class Graph(Composite, sourdough.Component):
#     """Base class for composite objects in sourdough projects.

#     Distinguishing characteristics of a Graph:
#         1) Iteration is not defined by ordering of contents.
#         2) Incorporates Edges as part of its structure.
#         3) All Components must be connected (sourdough does not presently
#             support graphs with unconnected objects).
            
#     Args:
#         contents (Sequence[Union[str, sourdough.Component]]): a list of str or
#             Components. 
#         name (str): designates the name of a class instance that is used for 
#             internal referencing throughout sourdough. For example if a 
#             sourdough instance needs settings from a Settings instance, 'name' 
#             should match the appropriate section name in the Settings instance. 
#             When subclassing, it is sometimes a good idea to use the same 'name' 
#             attribute as the base class for effective coordination between 
#             sourdough classes. Defaults to None. If 'name' is None and 
#             '__post_init__' of Element is called, 'name' is set based upon
#             the 'get_name' method in Element. If that method is not 
#             overridden by a subclass instance, 'name' will be assigned to the 
#             snake case version of the class name ('__class__.__name__').
    
#     """
#     contents: Sequence[Union[str, sourdough.Component]] = dataclasses.field(
#         default_factory = list)
#     name: str = None
    