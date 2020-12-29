"""
application: 
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:


"""
from __future__ import annotations
import dataclasses
import multiprocessing
import textwrap
from types import ModuleType
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import sourdough

  
@dataclasses.dataclass
class Workflow(sourdough.base.Component):
    
    def apply(self, manager: sourdough.Manager) -> sourdough.Manager:
        """Subclasses must provide their own methods."""
        return manager


@dataclasses.dataclass
class Step(sourdough.base.Component):
    
    def apply(self, manager: sourdough.Manager) -> sourdough.Manager:
        """Subclasses must provide their own methods."""
        return manager


@dataclasses.dataclass
class Technique(sourdough.base.Component):
    
    def apply(self, manager: sourdough.Manager) -> sourdough.Manager:
        """Subclasses must provide their own methods."""
        return manager


@dataclasses.dataclass
class Package(sourdough.quirks.Loader):
    """Base classes for a sourdough projects.
    
    Args:
        manager (Union[str, Type]): class for organizing, implementing, and
            iterating the package's classes and functions. Defaults to 
            'sourdough.Manager'.
        workflow (Union[str, Type]): the workflow to use in a sourdough 
            project. Defaults to 'sourdough.products.Workflow'.
            
    """
    rules: Union[str, Type, object] = Rules
    manager: Union[str, Type] = Manager
    component: Union[str, Type] = 'sourdough.base.Component'
    
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent and/or mixin initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass
        # Instances 'rules' if not already instanced.
        if isinstance(self, 'rules', str) or inspect.isclass(self.rules):
            self.rules = self.rules()
        
    """ Properties """
    
    def component_suffixes(self) -> Tuple[str]:
        return tuple(key + 's' for key in self.component.registry.keys()) 
        