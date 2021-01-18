"""
workshop: interface for runtime class and object product
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:

"""
from __future__ import annotations
import abc
import collections.abc
import dataclasses
import inspect
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import sourdough 


@dataclasses.dataclass
class ComponentWorksop(sourdough.factory.Workshop):
    """[summary]

    Args:
        sourdough ([type]): [description]
    """
    registry: ClassVar[Mapping[str, Type]] = sourdough.types.Catalog()
 

@dataclasses.dataclass
class Component(sourdough.factory.Product, sourdough.workflows.Node):
    """[summary]

    Args:
        sourdough ([type]): [description]
    """
    name: str = None
    contents: Any = None

    """ Class Methods """

    @classmethod
    def register(cls) -> None:
        """Registers a subclass in a Catalog in ComponentWorkshop.
        
        The default 'register' method uses the snake-case name of the class as
        the key for the stored subclass.
        
        """
        key = sourdough.tools.snakify(cls.__name__)
        ComponentWorksop.registry[key] = cls
        return cls
    
# @dataclasses.dataclass
# class Workshop(sourdough.types.Catalog):

#     contents: Mapping[str, Callable] = dataclasses.field(default_factory = dict)
#     project: Project = None

#     """ Initialization Methods """

#     def __post_init__(self) -> None:
#         """Initializes class instance attributes."""
#         # Calls parent and/or mixin initialization method(s).
#         try:
#             super().__post_init__()
#         except AttributeError:
#             pass
#         # Checks to see if 'project' exists.
#         if self.project is None:
#             raise ValueError(
#                 f'{self.__class__.__name__} requires a Project instance')
#         # Creates base classes with selected Quirk mixins.
#         self.create_bases()
#         # Point the 'bases' of Project to 'contents' attribute.
#         Project.bases = self.contents
    
#     """ Public Methods """
    
#     def create_bases(self) -> None:
#         """[summary]

#         Returns:
#             [type]: [description]
#         """
#         quirks = self._get_settings_quirks()
#         for key, value in self.manager.project.bases.items():
#             self.contents[key] = self.create_class(
#                 name = key, 
#                 base = value, 
#                 quirks = quirks)
#         return self
            
#     def create_class(self, name: str, base: Callable, 
#                      quirks: Sequence[sourdough.Quirk]) -> Callable:
#         """[summary]

#         Args:
#             name (str): [description]
#             base (Callable): [description]
#             quirks (Sequence[sourdough.Quirk])

#         Returns:
#             Callable: [description]
            
#         """
#         if quirks:
#             bases = quirks.append(base)
#             new_base = dataclasses.dataclass(type(name, tuple(bases), {}))
#             # Recursively adds quirks to items in the 'registry' of 'base'.
#             if hasattr(base, 'registry'):
#                 newregistry = {}
#                 for key, value in base.registry.items():
#                     newregistry[key] = self.create_class(
#                         name = key,
#                         base = value,
#                         quirks = quirks)
#                 new_base.registry = newregistry
#         else:
#             new_base = base
#         return new_base
             
#     """ Private Methods """
    
#     def _get_settings_quirks(self) -> Sequence[sourdough.Quirk]:
#         """[summary]

#         Returns:
#             Sequence[sourdough.Quirk]: [description]
            
#         """
#         settings_keys = {
#             'verbose': 'talker', 
#             'early_validation': 'validator', 
#             'conserve_memory': 'conserver'}
#         quirks = []
#         for key, value in settings_keys.items():
#             try:
#                 if self.manager.project.settings['general'][key]:
#                     quirks.append(sourdough.Quirk.options[value])
#             except KeyError:
#                 pass
#         return quirks

 