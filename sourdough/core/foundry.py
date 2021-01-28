"""
foundry: base classes for building other sourdough classes
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Builder (ABC): base class for all sourdough constructors of composite
        structures. All subclasses must have a 'create' method. Its 'library'
        class attribute stores all subclasses.
    Director (Lexicon, ABC)
        
"""
from __future__ import annotations
import abc
import dataclasses
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import sourdough 


@dataclasses.dataclass
class Builder(sourdough.types.Base, abc.ABC):
    """Creates a sourdough object.

    All Builder subclasses should follow the naming convention of:
            '{Base class being built}Builder'. 
    This allows the Builder to be properly matched with the class being 
    constructed without using an extraneous mapping to link the two.

    Args:
        manager (Director): associated project manager containing needed data
            for creating objects.
        library (ClassVar[Library]): related Library instance that will store
            subclasses and allow runtime construction and instancing of those
            stored subclasses.
                       
    """
    manager: sourdough.project.Director = dataclasses.field(
        repr = False, 
        default = None)
    library: ClassVar[sourdough.types.Library] = sourdough.types.Library()
    
    """ Initialization Methods """
    
    def __init_subclass__(cls, **kwargs):
        """Adds 'cls' to 'library' if it is a concrete class."""
        super().__init_subclass__(**kwargs)
        # Creates 'library' class attribute if it doesn't exist.
        if not hasattr(cls, 'library'):  
            cls.library = sourdough.types.Library()
        if not abc.ABC in cls.__bases__:
            key = sourdough.tools.snakify(cls.__name__)
            # Removes '_creator' from class name so that the key is consistent
            # with the key name for the class being constructed.
            try:
                key.remove('_creator')
            except ValueError:
                pass
            cls.library[key] = cls
                          
    """ Required Subclass Class Methods """
    
    @abc.abstractmethod
    def create(self, **kwargs) -> sourdough.types.Base:
        """Subclasses must provide their own methods."""
        pass

    """ Properties """
    
    @property
    def settings(self) -> sourdough.project.Settings:
        return self.manager.project.settings
    

@dataclasses.dataclass
class Director(sourdough.quirks.Element, sourdough.types.Base, abc.ABC):
    """Directs actions of a stored Builder instance.

    All Director subclasses should follow the naming convention of:
            '{Base class being built}Director'. 
    This allows the Director to be properly matched with the class being 
    constructed without using an extraneous mapping to link the two.

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Configuration instance, 
            'name' should match the appropriate section name in a Configuration 
            instance. Defaults to None. 
    
    """
    name: str = None
    library: ClassVar[sourdough.types.Library] = sourdough.types.Library()
    
    """ Initialization Methods """
    
    def __init_subclass__(cls, **kwargs):
        """Adds 'cls' to 'library' if it is a concrete class."""
        super().__init_subclass__(**kwargs)
        # Creates 'library' class attribute if it doesn't exist.
        if not hasattr(cls, 'library'):  
            cls.library = sourdough.types.Library()
        if not abc.ABC in cls.__bases__:
            key = sourdough.tools.snakify(cls.__name__)
            # Removes '_manager' from class name so that the key is consistent
            # with the key name for the class being constructed.
            try:
                key.remove('_manager')
            except ValueError:
                pass
            cls.library[key] = cls
                 
    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def create(self, **kwargs) -> sourdough.types.Base:
        """Subclasses must provide their own methods."""
        pass

    """ Properties """
    
    @property
    def settings(self) -> sourdough.project.Settings:
        return self.project.settings