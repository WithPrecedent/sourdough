"""
directors: 
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
class Coordinator(sourdough.types.Base, abc.ABC):
    """[summary]

    Args:
        sourdough ([type]): [description]
        
    """
    
    library: ClassVar[sourdough.types.Library] = sourdough.types.Library()
  
    """ Required Subclass Methods """ 
     
    @abc.abstractmethod
    def create(self, **kwargs) -> Any:
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


@dataclasses.dataclass
class Manager(Coordinator):
    """[summary]

    Args:
        sourdough ([type]): [description]
    """
    contents: Mapping[str, Any] = dataclasses.field(default_factory = dict)
