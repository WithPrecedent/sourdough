"""
nodes:
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:

    
"""
from __future__ import annotations
import abc
import copy
import dataclasses
import itertools
import multiprocessing
import pprint
import textwrap
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import sourdough  

@dataclasses.dataclass
class Node(object):
    
    name: str = None
    step: str = None


@dataclasses.dataclass
class Workflow(sourdough.quirks.Element, 
               sourdough.composites.Graph, 
               sourdough.types.Base, 
               abc.ABC):
    """Base class for workflows in a sourdough project.
    
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Configuration instance, 
            'name' should match the appropriate section name in a Configuration 
            instance. Defaults to None.
        library (ClassVar[Library]): related Library instance that will store
            subclasses and allow runtime construction and instancing of those
            stored subclasses.
        
    """
    name: str = None
    step: str = None
    library: ClassVar[sourdough.types.Library] = sourdough.types.Library()

    """ Required Subclass Class Methods """
    
    @abc.abstractclassmethod
    def create(cls, **kwargs) -> Workflow:
        """Subclasses must provide their own class methods."""
        pass
    
