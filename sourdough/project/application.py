"""
application: 
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:


"""
from __future__ import annotations
import dataclasses
import inspect
from types import ModuleType
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import sourdough


@dataclasses.dataclass
class ManagerBases(sourdough.quirks.Loader):
    """Base classes for a sourdough projects.
    
    Args:
        manager (Union[str, Type]): class for organizing, implementing, and
            iterating the package's classes and functions. Defaults to 
            'sourdough.Manager'.
        workflow (Union[str, Type]): the workflow to use in a sourdough 
            project. Defaults to 'sourdough.products.Workflow'.
            
    """
    manager: Union[str, Type] = 'sourdough.Manager'
    component: Union[str, Type] = 'sourdough.Component'
    
    
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


        