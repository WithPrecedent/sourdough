"""
resources: default settings, options, and rules
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    settings (dict): default settings for a Settings instance.

    
"""
from __future__ import annotations
import dataclasses
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import sourdough 


""" Default Options for Settings """

settings: Mapping[str, Any] = {
    'general': {
        'verbose': False,
        'parallelize': True,
        'conserve_memery': False},
    'files': {
        'source_format': 'csv',
        'interim_format': 'csv',
        'final_format': 'csv',
        'file_encoding': 'windows-1252'}}


""" Catalogs of Created Classes and Objects """

@dataclasses.dataclass
class Options(object):
    """[summary]

    Args:
        
    """
    creators: Mapping[str, Type]
    products: Mapping[str, Type]
    components: Mapping[str, Type]
    instances: Mapping[str, object]
    algorithms: Mapping[str, Type]
    criteria: Mapping[str, Callable]


options: Options = Options(
    creators = sourdough.types.Catalog(),
    products = sourdough.types.Catalog(),
    components = sourdough.types.Catalog(),
    instances = sourdough.types.Catalog(),
    algorithms = sourdough.types.Catalog(),
    criteria = sourdough.types.Catalog(always_return_list= True))


""" Default Rules """

@dataclasses.dataclass
class Rules(object):
    """
    """
    options: Options
    skip_sections: Sequence[str]
    skip_suffixes: Sequence[str]
    special_section_suffixes: Sequence[str]
    default_design: str 
    validations: Sequence[str]

    """ Properties """
    
    @property
    def component_suffixes(self) -> Tuple[str]: 
        return tuple(k + 's' for k in self.options.components.keys()) 


rules: Rules = Rules(
    options = options,
    skip_sections = ['general', 'files'],
    skip_suffixes = ['parameters'],
    special_section_suffixes = ['design'],
    default_design = 'pipeline',
    validations = ['settings', 'name', 'identification', 'manager', 'creators'])
