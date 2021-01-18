"""
workshop: interface for runtime class and object product
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:

"""
from __future__ import annotations
import abc
import dataclasses
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import sourdough 


@dataclasses.dataclass
class Workshop(abc.ABC):
    """[summary]

    Args:
        sourdough ([type]): [description]
        
    """
    registry: ClassVar[Mapping[str, Type]] = sourdough.types.Catalog()
 
    """ Public Methods """
    
    def acquire(self, name: str) -> Type:
        """Returns the stored class matching 'name'.

        Args:
            name (str): key name of stored class in 'registry' to returned.

        Returns:
            Type: stored class.
            
        """
        return self.registry.select(key = name)

    def build(self, name: str, 
              quirks: Union[str, Sequence[str]] = None) -> Type:
        """Returns the stored class instance matching 'name'.

        Args:
            name (str): key name of stored class in 'registry' to returned.
            kwargs: parameters and arguments to pass to the instanced class.

        Returns:
            Type: stored class instance.
            
        """
        bases = []
        if quirks is not None:
            bases.extend(sourdough.tools.listify(
                sourdough.quirks.QuirksWorkshop.registry.select(key = quirks)))
        bases.append(self.acquire(name = name))
        return dataclasses.dataclass(type(name, tuple(bases), {}))
    
    def instance(self, name: str, quirks: Union[str, Sequence[str]] = None, 
                 **kwargs) -> object:
        """Returns the stored class instance matching 'name'.

        Args:
            name (str): key name of stored class in 'registry' to returned.
            kwargs: parameters and arguments to pass to the instanced class.

        Returns:
            Type: stored class instance.
            
        """
        if quirks is None:
            return self.acquire(name = name)(**kwargs)
        else:
            return self.build(name = name, quirks = quirks)(**kwargs)


@dataclasses.dataclass
class Product(abc.ABC):
    """[summary]

    Args:
        sourdough ([type]): [description]
        
    """
    workshop: ClassVar[Workshop] = dataclasses.field(repr = False, default = None)

    """ Initialization Methods """
    
    def __init_subclass__(cls, **kwargs):
        """Adds 'cls' to 'workshop.registry' if it is a concrete class."""
        super().__init_subclass__(**kwargs)
        if not abc.ABC in cls.__bases__:
            key = sourdough.tools.snakify(cls.__name__)
            cls.workshop.registry[key] = cls
