"""
application: classes and functions applying sourdough's core to a project
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:


"""
from __future__ import annotations
import dataclasses
import inspect
import pathlib
from types import ModuleType
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import sourdough


@dataclasses.dataclass
class Rules(object):
    """Designates rules for parsing a Settings instance.
    
    Args:
        skip (Sequence[str]): designates suffixes of Settings sections to ignore 
            when creating project components. Defaults to a list of 'general', 
            'files', and 'parameters'.
        special (Mapping[str: Any]): designates suffixes which must be included
            to properly create a Component. For any str listed in 'special'. 
            Defaults to a dict with the contents designated in the class 
            annotations.
            
    To Do:
        Move 'special' to inferences from Component base class annotation.
        
    """
    skip: Sequence[str] = dataclasses.field(
        default_factory = lambda: ['general', 'files', 'parameters'])
    special: Mapping[str, Any] = dataclasses.field(
        default_factory = lambda: {
            'design': None, 
            'needs': [], 
            'produces': str, 
            'iterations': 1, 
            'criteria': [], 
            'parallel': False})


@dataclasses.dataclass
class Settings(sourdough.types.Configuration):
    """Loads and Stores configuration settings for a Project.

    Args:
        contents (Union[str, pathlib.Path, Mapping[Any, Mapping[Any, Any]]]): a 
            dict, a str file path to a file with settings, or a pathlib Path to
            a file with settings. Defaults to en empty dict.
        infer_types (bool]): whether values in 'contents' are converted to other 
            datatypes (True) or left alone (False). If 'contents' was imported 
            from an .ini file, a False value will leave all values as strings. 
            Defaults to True.
        defaults (Mapping[str, Mapping[str]]): any default options that should
            be used when a user does not provide the corresponding options in 
            their configuration settings. Defaults to a dict with 'general'
            and 'files' section listed in the class annotations.

    """
    contents: Union[str,pathlib.Path, Mapping[str, Mapping[str, Any]]] = (
        dataclasses.field(default_factory = dict))
    infer_types: bool = True
    defaults: Mapping[str, Mapping[str, Any]] = dataclasses.field(
        default_factory = lambda: {
            'general': {
                'verbose': False,
                'parallelize': True,
                'conserve_memery': False},
            'files': {
                'source_format': 'csv',
                'interim_format': 'csv',
                'final_format': 'csv',
                'file_encoding': 'windows-1252'}})
    rules: object = Rules()








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


        