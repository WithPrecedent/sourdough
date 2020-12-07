"""
defaults: default resources, rules, and settings
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    settings (dict): default settings for a Settings instance.
    creators (Catalog): stored Creator subclasses. By default, snakecase names
        of the subclasses are used as the keys.
    
    components (Catalog): stored Component subclasses. By default, snakecase
        names of the subclasses are used as the keys.
    instances (Catalog): stored instances of Component subclasses. By default,
        the 'name' attribute of the instances are used as the keys.
    algorithms (Catalog): stored classes of algorithms, usually from other
        packages. The keys are assigned by the user or a package utilizing the
        sourdough framework.
    
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

creators: Mapping[str, Type] = sourdough.types.Catalog()
creations: Mapping[str, Type] = sourdough.types.Catalog()
components: Mapping[str, Type] = sourdough.types.Catalog()
instances: Mapping[str, object] = sourdough.types.Catalog()
algorithms: Mapping[str, Type] = sourdough.types.Catalog()
criteria: Mapping[str, Callable] = sourdough.types.Catalog(
    always_return_list = True)

resources: Mapping[str, sourdough.types.Catalog] = {
    'creators': creators,
    'creations': creations,
    'components': components,
    'instances': instances,
    'algorithms': algorithms}


""" Default Rules """

@dataclasses.dataclass
class Rules(object):
    
    skip_sections: Sequence[str] = dataclasses.field(
        default_factory = lambda: ['general', 'files'])
    skip_suffixes: Sequence[str] = dataclasses.field(
        default_factory = lambda: ['parameters'])
    special_section_suffixes: Sequence[str] = dataclasses.field(
        default_factory = lambda: ['design'])
    default_design: str = 'pipeline'
    validations: Sequence[str] = dataclasses.field(
        default_factory = lambda: ['settings', 'name', 'identification', 
                                   'manager', 'creators'])
        
    @property
    def component_suffixes(self) -> Tuple[str]: 
        return tuple(k + 's' for k in components.keys()) 

rules: Rules = Rules()
