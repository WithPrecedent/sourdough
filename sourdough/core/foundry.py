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
class Director(sourdough.types.Lexicon, sourdough.types.Base, abc.ABC):
    """Uses stored builders to create new items.
    
    A Director differs from a Lexicon in 3 significant ways:
        1) It stores a separate Lexicon called 'builders' which have classes
            used to create other items.
        2) It iterates 'builders' and stores its output in 'contents.' General
            access methods still point to 'contents'.
        3) It has an additional convenience methods called 'add_builder' for
            adding new items to 'builders', 'advance' for iterating one step,
            and 'complete' which completely iterates the instance and stores
            all results in 'contents'.
    
    Args:
        contents (Mapping[Any, Any]]): stored dictionary. Defaults to an empty 
            dict.
              
    """
    contents: Mapping[Any, Any] = dataclasses.field(default_factory = dict)
    builders: sourdough.types.Lexicon[str, Builder] = dataclasses.field(
        default_factory = sourdough.types.Lexicon)

    """ Public Methods """
     
    def add(self, item: Mapping[Any, Any], **kwargs) -> None:
        """Adds 'item' to the 'contents' attribute.
        
        Args:
            item (Mapping[Any, Any]): items to add to 'contents' attribute.
            kwargs: creates a consistent interface even when subclasses have
                additional parameters.
                
        """
        self.contents.update(item)
        return self

    def add_builder(self, item: Mapping[Any, Any], **kwargs) -> None:
        """Adds 'item' to the 'builders' attribute.
        
        Args:
            item (Mapping[Any, Any]): items to add to 'builders' attribute.
            kwargs: creates a consistent interface even when subclasses have
                additional parameters.
                
        """
        self.builders.add(item = item)
        return self

    def advance(self) -> Any:
        """Returns next product of an instance iterable.'
        
        Returns:
            Any: item created by a single iteration."""
        return self.__next__()

    def complete(self) -> None:
        """Executes each step in an instance's iterable."""
        for item in iter(self):
            self.__next__()
        return self

    """ Dunder Methods """
    
    def __iter__(self) -> Iterable[Any]:
        """Returns iterable of 'builders'.

        Returns:
            Iterable: of 'builders'.

        """
        return iter(self.builders)

    def __len__(self) -> int:
        """Returns length of iterable of 'builders'

        Returns:
            int: length of iterable 'builders'.

        """
        return len(self.__iter__()) 
  
   
@dataclasses.dataclass
class Builder(sourdough.types.Base, abc.ABC):
    """Creates a Structure subclass instance.

    All Builder subclasses should follow the naming convention of:
            '{Class being built}Builder'. 
    This allows the Builder to be properly matched with the class being 
    constructed without using an extraneous mapping to link the two.

    Args:
        base (Base):
        library (ClassVar[Library]): related Library instance that will store
            subclasses and allow runtime construction and instancing of those
            stored subclasses.
            
    """
    base: sourdough.types.Base
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
            # Removes '_builder' from class name so that the key is consistent
            # with the key name for the class being constructed.
            try:
                key.remove('_builder')
            except ValueError:
                pass
            cls.library[key] = cls
            
    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def create(self, source: Any, **kwargs) -> sourdough.types.Base:
        """Creates a Base subclass instance from 'source'.
        
        Subclasses must provide their own methods.

        Args:
            source (Any): source object from which to create an instance of a
                Base subclass.
            kwargs: additional arguments to pass when a Base subclass is
                instanced.
        
        Returns:
            Base: a sourdough Base subclass instance.
            
        """
        pass  
    
    """ Public Methods """
    
    def borrow(self, 
               keys: Union[str, Sequence[str]]) -> Type[sourdough.types.Base]:
        """[summary]

        Args:
            name (str): [description]

        Returns:
            Type: [description]
            
        """
        product = None
        for key in sourdough.tools.tuplify(keys):
            try:
                product = self.base.library.borrow(name = key)
                break
            except (AttributeError, KeyError):
                pass
        if product is None:
            raise KeyError(f'No match for {keys} was found in the '
                           f'{self.base.__name__} library.')
        return product 
