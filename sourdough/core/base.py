"""
foundation: sourdough base factory classes
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Factory (ABC): abstract base class that maintains a 'name' property and
        registers non-abstract subclasses using that 'name' property.
 
"""
from __future__ import annotations
import abc
import dataclasses
import functools
import inspect
from typing import (
    Any, Callable, ClassVar, Dict, Iterable, List, Mapping, Sequence, Union)

import sourdough


@dataclasses.dataclass
class Quirk(sourdough.Factory, abc.ABC):
    """Base class for sourdough mixins.
    
    Quirk automatically stores all non-abstract subclasses in the 'options' 
    class attribute.

    Args:
        options (ClassVar[Catalog[str, Quirk]]): Catalog instance which stores 
            subclasses.
                
    """
    library: ClassVar[Mapping[str, Callable]] = sourdough.Catalog()
    
    """ Initialization Methods """
    
    """ Required Subclass Methods """
    
    @classmethod
    @abc.abstractmethod
    def inject(self, item: Any) -> Any:
        """Subclasses must provide their own methods.
        
        This method should add methods, attributes, and/or properties to the
        passed argument.
        
        """
        pass
    