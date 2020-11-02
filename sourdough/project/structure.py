"""
structure: base classes for composite objects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:

"""
from __future__ import annotations
import abc
import collections.abc
import dataclasses
import pprint
import textwrap
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Union)

import sourdough 


@dataclasses.dataclass
class Component(sourdough.quirks.Registrar, sourdough.quirks.Librarian, 
                collections.abc.Container):
    """Base container class for sourdough composite objects.
    
    A Component has a 'name' attribute for internal referencing and to allow 
    sourdough iterables to function propertly. Component instances can be used 
    to create a variety of composite data structures such as trees, cycles, 
    contests, studies, and graphs.
    
    Args:
        contents (Any): item(s) contained by a Component instance.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. 

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

    """ Required Subclass Methods """

    @abc.abstractmethod
    def apply(self, project: sourdough.Project) -> sourdough.Project:
        """Subclasses must provide their own methods."""
        return project

    """ Class Methods """
    
    @classmethod
    def register(cls) -> None:
        """Registers a subclass in a Catalog."""
        key = sourdough.tools.snakify(cls.__name__)
        sourdough.project.resources.components[key] = cls
        return cls
    
    """ Public Methods """
    
    def deposit(self) -> None:
        """Stores a subclass instance in a Catalog."""
        sourdough.project.resources.options[self.name] = self
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
    
    def __contains__(self, item: Any) -> bool:
        """Returns whether 'item' is in the 'contents' attribute.
        
        Args:
            item (Any): item to look for in 'contents'.
            
        Returns:
            bool: whether 'item' is in 'contents' if it is a Collection.
                Otherwise, it evaluates if 'item' is equivalent to 'contents'.
                
        """
        try:
            return item in self.contents
        except TypeError:
            return item == self.contents
    
    
           
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



# @dataclasses.dataclass
# class Design(object):
    
#     parallels: Sequence[str] = dataclasses.field(default_factory = list)
#     hierarchy: Mapping[str, Callable] = dataclasses.field(default_factory = dict)
    
    
# @dataclasses.dataclass   
# class SimplifyDesign(Design):

#     parallels: Sequence[str] = dataclasses.field(default_factory = ['steps'])
#     hierarchy: Mapping[str, Sequence[str]] = dataclasses.field(
#         default_factory = lambda: {
#             'workers': ['workers', 'steps', 'techniques'],
#             'steps': ['techniques'],
#             'techniques': [None]})

