"""
interfaces: abstract base classes for core sourdough interfaces.
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Although python doesn't require the separation of interfaces in the same way
that more structured languages do, this module is included to make it clearer
for users trying to expand sourdough's functionality. The included abstract base
classes show the required and included methods for all of the core classes in 
sourdough. So, whether you intend to directly subclass or write alternate 
classes for use in sourdough, these abstract base classes show how to survive 
static type-checkers and other internal checks made by sourdough.

Contents:
    Constructor (ABC):
    Element (collections.abc.Container, ABC):
    Vessel (Iterable, ABC): abstract base class for sourdough iterables. All 
        subclasses must have an 'add' method as well as store their contents in 
        the 'contents' attribute.
    Coordinator (Vessel, ABC):
    
"""
from __future__ import annotations
import abc
import collections.abc
import dataclasses
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import sourdough


@dataclasses.dataclass
class Constructor(abc.ABC):
    """Parent for classes that construct other classes or objects.
    
    Subclasses must have a 'create' method.
    
    """

    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Initializes class instance.
        
        Although this method ordinarily does nothing, it makes the order of the
        inherited classes less important with multiple inheritance, such as when 
        adding sourdough quirks. 
        
        """
        # Calls parent initialization methods, if they exist.
        try:
            super().__post_init__()
        except AttributeError:
            pass
     
    """ Required Subclass Methods """ 
     
    @abc.abstractmethod
    def create(self, **kwargs) -> Any:
        """Subclasses must provide their own methods."""
        pass

    """ Dunder Methods """

    def __contains__(self, item: Any) -> bool:
        """Returns whether 'item' is in or equal to 'contents'.

        Args:
            item (Any): item to check versus 'contents'
            
        Returns:
            bool: if 'item' is in or equal to 'contents' (True). Otherwise, it
                returns False.

        """
        try:
            return item in self.contents
        except TypeError:
            return item == self.contents
        return self
    

@dataclasses.dataclass
class Element(collections.abc.Container, abc.ABC):
    """Parent for classes stored in composite structures.
    
    Automatically provides a 'name' attribute to a part of a composite 
    structure, if it isn't otherwise passed.

    Subclasses must provide their own 'apply' methods.

    Args:
        contents (Any): stored item(s).
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Configuration instance, 
            'name' should match the appropriate section name in a Configuration 
            instance. Defaults to None. 

    """
    contents: Any = None
    name: str = None
    
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

    """ Private Methods """
    
    def _get_name(self) -> str:
        """Returns snakecase of the class name.

        If a user wishes to use an alternate naming system, a subclass should
        simply override this method. 
        
        Returns:
            str: name of class for internal referencing and some access methods.
        
        """
        return sourdough.tools.snakify(self.__class__.__name__)

    """ Public Methods """
    
    @abc.abstractmethod
    def apply(self, data: Any = None, **kwargs) -> Any:
        """Subclasses must provide their own methods."""
        pass 

    
@dataclasses.dataclass
class Vessel(collections.abc.Iterable, abc.ABC):
    """Interface for sourdough iterables.
  
    A Vessel differs from a general python iterable in 3 ways:
        1) It must include an 'add' method which provides the default mechanism
            for adding new items to the iterable. All of the other appropriate
            methods for adding to a python iterable ('append', 'extend', 
            'update', etc.) remain, but 'add' allows a subclass to designate the
            preferred method of adding to the iterable's stored data.
        2) It allows the '+' operator to be used to join a Vessel subclass 
            instance of the same general type (Mapping, Sequence, Tuple, etc.). 
            The '+' operator calls the Vessel subclass 'add' method to implement 
            how the added item(s) is/are added to the Vessel subclass instance.
        3) The internally stored iterable is located in the 'contents' 
            attribute. This allows for consistent coordination among classes and
            mixins.
    
    Args:
        contents (Iterable[Any]): stored iterable. Defaults to None.
              
    """
    contents: Iterable[Any] = None

    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Initializes class instance.
        
        Although this method ordinarily does nothing, it makes the order of the
        inherited classes less important with multiple inheritance, such as when 
        adding sourdough quirks. 
        
        """
        # Calls parent initialization methods, if they exist.
        try:
            super().__post_init__()
        except AttributeError:
            pass
          
    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def add(self, item: Any) -> None:
        """Adds 'item' to 'contents' in the default manner.
        
        Subclasses must provide their own methods."""
        pass
    
    """ Dunder Methods """

    def __add__(self, other: Any) -> None:
        """Combines argument with 'contents' using the 'add' method.

        Args:
            other (Any): item to add to 'contents' using the 'add' method.

        """
        self.add(other)
        return self

    def __iter__(self) -> Iterable[Any]:
        """Returns iterable of 'contents'.

        Returns:
            Iterable: of 'contents'.

        """
        return iter(self.contents)


@dataclasses.dataclass
class Coordinator(Vessel, abc.ABC):
    """Abstract base class for organizers and directors for Constructors
    
    Subclasses must have a 'validate' method which either validates or converts
    instance attributes.
    
    Args:
        contents (Iterable[Any]): stored iterable. Defaults to None.
              
    """
    contents: Iterable[Any] = None
    
    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def validate(self, **kwargs) -> Any:
        """Subclasses must provide their own methods."""
        pass
    
    """ Public Methods """
    
    def advance(self) -> Any:
        """Returns next product of an instance iterable."""
        return self.__next__()

    def complete(self) -> None:
        """Executes each step in an instance's iterable."""
        for item in iter(self):
            self.__next__()
        return self
 