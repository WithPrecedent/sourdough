"""
components: classes for sourdough composite objects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    
"""
from __future__ import annotations
import abc
import dataclasses
import textwrap
import typing
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Union)

import sourdough


@dataclasses.dataclass
class Component(sourdough.quirks.Registrar, sourdough.quirks.Librarian, abc.ABC):
    """Base class for parts of sourdough composite objects.
    
    A Component has a 'name' attribute for internal referencing and to allow 
    sourdough iterables to function propertly. Component instances can be used 
    to create a variety of composite data structures such as trees, cycles, 
    contests, studies, and graphs.
    
    Attributes:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. 
    
    """
    
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Sets 'name' attribute.
        if not hasattr(self, 'name') or self.name is None:  
            self.name = self._get_name()
        # Calls parent and/or mixin initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass

    """ Class Methods """
    
    @classmethod
    def register(cls) -> None:
        key = sourdough.tools.snakify(cls.__name__)
        sourdough.inventory.components[key] = cls
        return cls
    
    """ Public Methods """
    
    def deposit(self) -> None:
        sourdough.inventory.options[self.name] = self
        return self

    """ Private Methods """
    
    def _get_name(cls) -> str:
        """Returns 'name' of class instance for use throughout sourdough.
        
        This method converts the class name from CapitalCase to snake_case.
        
        If a user wishes to use an alternate naming system, a subclass should
        simply override this method. 
        
        Returns:
            str: name of class for internal referencing and some access methods.
        
        """
        return sourdough.tools.snakify(cls.__name__)

    """ Dunder Methods """
        
    # def __str__(self) -> str:
    #     """Returns pretty string representation of an instance.
        
    #     Returns:
    #         str: pretty string representation of an instance.
            
    #     """
    #     new_line = '\n'
    #     representation = [f'sourdough {self.__class__.__name__}']
    #     attributes = [a for a in self.__dict__ if not a.startswith('_')]
    #     for attribute in attributes:
    #         value = getattr(self, attribute)
    #         if (isinstance(value, Component) 
    #                 and isinstance(value, (Sequence, Mapping))):
    #             representation.append(
    #                 f'''{attribute}:{new_line}{textwrap.indent(
    #                     str(value.contents), '    ')}''')            
    #         elif (isinstance(value, (Sequence, Mapping)) 
    #                 and not isinstance(value, str)):
    #             representation.append(
    #                 f'''{attribute}:{new_line}{textwrap.indent(
    #                     str(value), '    ')}''')
    #         else:
    #             representation.append(f'{attribute}: {str(value)}')
    #     return new_line.join(representation)  
    

@dataclasses.dataclass
class Worker(Component, sourdough.Hybrid):
    """Base class for composite objects in sourdough projects.
    
    Worker differs from an ordinary Hybrid in 1 significant way:
        1) It is mixed in with Sequencify which allows for type validation and 
            conversion, using the 'verify' and 'convert' methods.
            
    Args:
        contents (Sequence[Union[str, Component]]): a list of str or Components. 
            Defaults to an empty list.
        name (str): property which designates the internal reference of a class 
            instance that is used throughout sourdough. For example, if a 
            sourdough instance needs options from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            Defaults to None. If 'name' is None, it will be assigned to the 
            snake case version of the class name ('__name__' or 
            '__class__.__name__').
                            
    """
    name: str = None
    contents: Union[Sequence[str], Sequence[Any]] = dataclasses.field(
        default_factory = list)
    
    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent and/or mixin initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass 
        # Initializes 'index' for iteration.
        self.index = -1

    """ Public Methods """
    
    def perform(self, data: object = None, **kwargs) -> NotImplementedError:
        """Subclasses must provide their own methods.       
        
        """
        raise NotImplementedError(
            'subclasses of Worker must provide their own perform methods')
                   
    """ Required Subclass Methods """
    
    # @abc.abstractmethod
    # def iterate(self, **kwargs) -> Iterable:
    #     pass
    
    # @abc.abstractmethod
    # def activate(self, **kwargs) -> Iterable:
    #     pass    
    
    # @abc.abstractmethod
    # def finalize(self, **kwargs) -> Iterable:
    #     pass
  
    """ Dunder Methods """
    
    # def __iter__(self) -> Iterable:
    #     if self.index + 1 < len(self.contents):
    #         self.index += 1
    #         yield self.iterate()
    #     else:
    #         raise StopIteration


@dataclasses.dataclass
class Element(Component):
    """                     
    """
    name: str = None
    contents: Union[object, Callable] = None
    
    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent and/or mixin initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass 

    """ Public Methods """
    
    def perform(self, data: object = None, **kwargs) -> NotImplementedError:
        """Subclasses must provide their own methods.       
        
        """
        raise NotImplementedError(
            'subclasses of Element must provide their own perform methods') 
