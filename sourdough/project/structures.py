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
import itertools
import more_itertools
from typing import (Any, Callable, ClassVar, Container, Generic, Iterable, 
                    Iterator, Mapping, Sequence, Tuple, TypeVar, Union)

import sourdough


@dataclasses.dataclass
class Overview(sourdough.base.Lexicon):
    """Dictionary of different Element types in a Structure instance.
    
    Args:
        contents (Mapping[Any, Any]]): stored dictionary. Defaults to an empty 
            dict.
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
    contents: Mapping[Any, Any] = dataclasses.field(default_factory = dict)
    name: str = None
    structure: sourdough.Structure = None
    
    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent initialization method(s).
        super().__post_init__()
        if self.structure.structure is not None:
            self.add({
                'name': self.structure.name, 
                'structure': self.structure.structure.name})
            for key, value in self.structure.structure.options.items():
                matches = self.structure.find(
                    self._get_type, 
                    element = value)
                if len(matches) > 0:
                    self.contents[f'{key}s'] = matches
        else:
            raise ValueError(
                'structure must be a Role for an overview to be created.')
        return self          
    
    """ Dunder Methods """
    
    def __str__(self) -> str:
        """Returns pretty string representation of an instance.
        
        Returns:
            str: pretty string representation of an instance.
            
        """
        new_line = '\n'
        representation = [f'sourdough {self.get_name}']
        for key, value in self.contents.items():
            if isinstance(value, Sequence):
                names = [v.name for v in value]
                representation.append(f'{key}: {", ".join(names)}')
            else:
                representation.append(f'{key}: {value}')
        return new_line.join(representation)    

    """ Private Methods """

    def _get_type(self, 
            item: sourdough.base.Element, 
            element: sourdough.base.Element) -> Sequence[sourdough.base.Element]: 
        """[summary]

        Args:
            item (self.stored_types): [description]
            self.stored_types (self.stored_types): [description]

        Returns:
            Sequence[self.stored_types]:
            
        """
        if isinstance(item, element):
            return [item]
        else:
            return []

    
@dataclasses.dataclass
class Aggregation(sourdough.Structure, sourdough.Component):
    """Base class for composite objects in sourdough projects.
    
    Distinguishing characteristics of an Aggregation:
        1) Order doesn't matter.
        2) All stored Components must be of the same type.
        3) Stored Components do not need to be connected.
        
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
class SerialStructure(sourdough.Structure, sourdough.Component, abc.ABC):
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
            
    
@dataclasses.dataclass
class Pipeline(SerialStructure):
    """Base class for composite objects in sourdough projects.

    Distinguishing characteristics of a Contest:
        1) Follows a sequence of instructions (serial structure).
        2) It may pass data or other arguments to the next step in the sequence.
        3) Only one connection or path exists between each object.
        
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
class ParallelStructure(sourdough.Structure, sourdough.Component, abc.ABC):
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
    criteria: str = None
    name: str = None
            
    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def organize(self, **kwargs) -> Iterator:
        pass
    
    @abc.abstractmethod
    def iterate(self, **kwargs) -> Iterator:
        pass
    
    @abc.abstractmethod
    def activate(self, **kwargs) -> Iterator:
        pass    
    
    @abc.abstractmethod
    def finalize(self, **kwargs) -> Iterator:
        pass


@dataclasses.dataclass
class Contest(ParallelStructure):
    """Base class for composite objects in sourdough projects.

    Distinguishing characteristics of a Contest:
        1) Repeats a Pipeline with different options (parallel structure).
        2) Chooses the best option based upon selected criteria.
        3) Each stored Component is only attached to the Contest with exactly 
            one connection (these connections are not defined separately - they
            are simply part of the parallel structure).
        
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
class Study(ParallelStructure):
    """Base class for composite objects in sourdough projects.

    Distinguishing characteristics of a Study:
        1) Repeats a Pipeline with different options (parallel structure).
        2) Maintains all of the repetitions without selecting or averaging the 
            results.
        3) Each stored Component is only attached to the Study with exactly 
            one connection (these connections are not defined separately - they
            are simply part of the parallel structure).
                      
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
    contents: Union[
        sourdough.Outline,
        sourdough.Pipeline] = dataclasses.field(default_factory = list)
    iterations: int = None
    name: str = None

    """ Public Methods """
    
    def organize(self, settings: sourdough.Settings) -> None:
        """[summary]

        Args:
            structure (sourdough.Structure): [description]

        Returns:
            sourdough.Structure: [description]
        """
        new_contents = []
        steps = list(self.contents.keys())
        possible = list(self.contents.values())
        permutations = list(map(list, itertools.product(*possible)))
        for pipeline in permutations:
            instance = Pipeline()
            for item in pipeline:
                if isinstance(item, Sequence):
                    
                else:
                    
                component = self._get_component(
                    key = item, 
                    generic = self.contents.generic)
                if isinstance(item, sourdough.Structure):
                    self.organize()
            new_contents.append(instance)
        self.contents = new_contents
        return self
        
    
@dataclasses.dataclass
class Survey(ParallelStructure):
    """Base class for composite objects in sourdough projects.

    Distinguishing characteristics of a Survey:
        1) Repeats a Pipeline with different options (parallel structure).
        2) Averages or otherwise combines the results based upon selected 
            criteria.
        3) Each stored Component is only attached to the Survey with exactly 
            one connection (these connections are not defined separately - they
            are simply part of the parallel structure).    
                    
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
# class Graph(sourdough.Structure, sourdough.Component):
#     """Base class for composite objects in sourdough projects.

#     Distinguishing characteristics of a Graph:
#         1) Iteration is not defined by ordering of contents.
#         2) Incorporates Edges as part of its structure.
#         3) All Components must be connected (sourdough does not presently
#             support graphs with unconnected graphs).
            
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
    