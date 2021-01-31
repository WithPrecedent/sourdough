"""
base: essential base classes for a sourdough project
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Settings
    Filer
    Workflow
    
    Creator
    Component

"""
from __future__ import annotations
import abc
import dataclasses
import pathlib
import types
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import sourdough


@dataclasses.dataclass
class Settings(sourdough.Base, sourdough.Configuration):
    """Loads and stores configuration settings for a Project.

    Args:
        contents (Union[str, pathlib.Path, Mapping[str, Mapping[str, Any]]]): a 
            dict, a str file path to a file with settings, or a pathlib Path to
            a file with settings. Defaults to en empty dict.
        infer_types (bool): whether values in 'contents' are converted to other 
            datatypes (True) or left alone (False). If 'contents' was imported 
            from an .ini file, a False value will leave all values as strings. 
            Defaults to True.
        defaults (Mapping[str, Mapping[str]]): any default options that should
            be used when a user does not provide the corresponding options in 
            their configuration settings. Defaults to a dict with 'general'
            and 'files' section listed in the class annotations.
        skip (Sequence[str]): names of suffixes to skip when constructing nodes
            for a sourdough project.

    """
    contents: Union[str, pathlib.Path, Mapping[str, Mapping[str, Any]]] = (
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
                'file_encoding': 'windows-1252'},
            'sourdough': {
                'default_design': 'workflow'}})
    skip: Sequence[str] = dataclasses.field(
        default_factory = lambda: [
            'general', 
            'files', 
            'sourdough', 
            'parameters'])


@dataclasses.dataclass
class Filer(sourdough.Base, sourdough.Clerk):
    pass  


@dataclasses.dataclass
class Builder(sourdough.Base, abc.ABC):
    """Creates a sourdough object.

    Args:
        library (ClassVar[Library]): related Library instance that will store
            subclasses and allow runtime construction and instancing of those
            stored subclasses.
                       
    """
    library: ClassVar[sourdough.Library] = sourdough.Library()
    
    """ Initialization Methods """
    
    def __init_subclass__(cls, **kwargs):
        """Adds 'cls' to 'library' if it is a concrete class."""
        super().__init_subclass__(**kwargs)
        if not abc.ABC in cls.__bases__:
            key = sourdough.tools.snakify(cls.__name__)
            # Removes '_builder' from class name so that the key is consistent
            # with the key name for the class being constructed.
            try:
                key.replace('_builder', '')
            except ValueError:
                pass
            cls.library[key] = cls
                          
    """ Required Subclass Class Methods """
    
    @abc.abstractmethod
    def create(self, **kwargs) -> sourdough.Base:
        """Subclasses must provide their own methods."""
        pass
    

@dataclasses.dataclass
class Director(sourdough.quirks.Element, sourdough.Base, abc.ABC):
    """Directs actions of a stored Builder instance.

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Configuration instance, 
            'name' should match the appropriate section name in a Configuration 
            instance. Defaults to None. 
    
    """
    name: str = None
    library: ClassVar[sourdough.Library] = sourdough.Library()
    
    """ Initialization Methods """
    
    def __init_subclass__(cls, **kwargs):
        """Adds 'cls' to 'library' if it is a concrete class."""
        super().__init_subclass__(**kwargs)
        if not abc.ABC in cls.__bases__:
            key = sourdough.tools.snakify(cls.__name__)
            # Removes '_director' from class name so that the key is consistent
            # with the key name for the class being constructed.
            try:
                key.replace('_director', '')
            except ValueError:
                pass
            cls.library[key] = cls
                 
    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def create(self, **kwargs) -> None:
        """Subclasses must provide their own methods."""
        pass

    @abc.abstractmethod
    def execute(self, **kwargs) -> None:
        """Subclasses must provide their own methods."""
        pass
    
  
@dataclasses.dataclass
class Results(sourdough.quirks.Element, sourdough.Base, types.SimpleNamespace):
    """Stores output of a Project.
    
    Args:
        name (str): ideally, this should be the 'name' of the related Project so
            that the Results can be matched with the Project.
        identification (str): ideally, this should be the 'identification' of 
            the related Project so that the Results can be matched with the 
            Project.          
            
    """
    name: str = None
    identification: str = None
