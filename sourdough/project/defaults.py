"""
defaults: default base classes, rules, resources, and settings
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:

"""
from __future__ import annotations
import dataclasses
import pprint
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import sourdough 


settings = {
    'general': {
        'verbose': False,
        'parallelize': True,
        'conserve_memery': False},
    'files': {
        'source_format': 'csv',
        'interim_format': 'csv',
        'final_format': 'csv',
        'file_encoding': 'windows-1252'}}


@dataclasses.dataclass
class Bases(sourdough.quirks.Loader):
    """
    """
    modules: Sequence[str] = dataclasses.field(
        default_factory = lambda: ['sourdough'])
    settings: Type = 'Settings'
    manager: Type = 'Manager'
    creator: Type = 'Creator'
    deliverable: Type = 'Deliverable'
    component: Type = 'Component'
    
    """ Public Methods """
    
    def load(self, key: str) -> Type:
        value = getattr(self, key)
        if isinstance(value, str):
            return super().load(key = key)
        else:
            return value
    
    
@dataclasses.dataclass
class Resources(object):
    """
    """   
    creators: Mapping[str, Type] = dataclasses.fields(
        default_factory = sourdough.types.Catalog)
    deliverables: Mapping[str, Type] = dataclasses.fields(
        default_factory = sourdough.types.Catalog)
    components: Mapping[str, Type] = dataclasses.fields(
        default_factory = sourdough.types.Catalog)
    instances: Mapping[str, object] = dataclasses.fields(
        default_factory = sourdough.types.Catalog)
    algorithms: Mapping[str, Type] = dataclasses.fields(
        default_factory = sourdough.types.Catalog)
    
    """ Dunder Methods """

    def __str__(self) -> str:
        """Returns pretty string representation of a class instance.
        
        Returns:
            str: normal representation of a class instance.
        
        """
        return pprint.pformat(self, sort_dicts = False, compact = True)


@dataclasses.dataclass
class Rules(object):
    """
        
    """
    resources: Resources
    skip_sections: Sequence[str] = dataclasses.field(
        default_factory = lambda: ['general', 'files'])
    skip_suffixes: Sequence[str] = dataclasses.field(
        default_factory = lambda: ['parameters'])
    special_section_suffixes: Sequence[str] = dataclasses.field(
        default_factory = lambda: ['design'])
    default_design: str = 'pipeline'
    
    """ Properties """

    @property
    def component_suffixes(self) -> Tuple[str]:
        return tuple(k + 's' for k in self.resources.components.keys()) 
  