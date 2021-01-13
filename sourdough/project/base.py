"""
bases: essential classes applying sourdough's core to a project
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Settings
    Filer
    Creator
    Component

"""
from __future__ import annotations
import dataclasses
import pathlib
from types import ModuleType
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import sourdough
    

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
        skip (Sequence[str]): names of suffixes to skip when constructing nodes
            for a sourdough project.

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
    skip: Sequence[str] = dataclasses.field(
        default_factory = lambda: ['general', 'files', 'parameters'])


@dataclasses.dataclass
class Filer(sourdough.files.Clerk):
    pass


@dataclasses.dataclass
class Manager(sourdough.quirks.Registrar, sourdough.quirks.Element, 
              sourdough.structures.Builder):

    contents: sourdough.structures.Graph = sourdough.structures.Graph()
    builders: Mapping[str, Creator] = dataclasses.field(default_factory = dict)
    name: str = None
    project: Union[object, Type] = None
    automatic: bool = True
    validations: Sequence[str] = dataclasses.field(default_factory = lambda: [
        'builders'])
    registry: ClassVar[Mapping[str, Manager]] = sourdough.types.Catalog()
    
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent and/or mixin initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass
        # Calls validation methods based on items listed in 'validations'.
        for validation in self.validations:
            getattr(self, f'_validate_{validation}')()
        # Advances through 'creator' stages if 'automatic' is True.
        if self.automatic:
            self.complete()
    
    """ Private Methods """

    def _validate_builders(self) -> None:
        """
        
        """

        return self


@dataclasses.dataclass
class Creator(sourdough.quirks.Registrar, sourdough.quirks.Element, 
              sourdough.structures.Builder):
    
    contents: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    base: Type = None
    name: str = None
    manager: Manager = None
    registry: ClassVar[Mapping[str, Creator]] = sourdough.types.Catalog()


@dataclasses.dataclass
class Component(sourdough.quirks.Registrar, sourdough.structures.Node):
    
    contents: sourdough.quirks.Element = None 
    name: str = None
    registry: ClassVar[Mapping[str, Creator]] = sourdough.types.Catalog()


@dataclasses.dataclass
class Worker(Component, sourdough.types.Hybrid):
    
    contents: Sequence[Component] = dataclasses.field(default_factory = list) 
    name: str = None
    iterations: Union[int, str] = 1
    criteria: Union[str, Callable, Sequence[Union[Callable, str]]] = None
    parallel: ClassVar[bool] = False
    
    """ Public Methods """
    
    def apply(self, data: Any = None, **kwargs) -> Any:
        """[summary]

        Args:
            data (Any, optional): [description]. Defaults to None.

        Returns:
            Any: [description]
        """
        for node in self.contents:
            if data is None:
                node.apply(data = data, **kwargs)
            else:
                data = node.apply(data = data, **kwargs)
        if data is None:
            return self
        else:
            return data

             
@dataclasses.dataclass
class Step(Component, sourdough.types.Proxy):
    """Wrapper for a Technique.

    Subclasses of Step can store additional methods and attributes to apply to 
    all possible technique instances that could be used. This is often useful 
    when using parallel Worklow instances which test a variety of strategies 
    with similar or identical parameters and/or methods.

    A Step instance will try to return attributes from Technique if the
    attribute is not found in the Step instance. 

    Args:
        contents (Technique): technique instance to be used in a Workflow.
            Defaults ot None.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Configuration instance, 
            'name' should match the appropriate section name in a Configuration 
            instance. Defaults to None. 
                        
    """
    contents: Union[Technique, str] = None
    name: str = None
                
    """ Properties """
    
    @property
    def technique(self) -> Technique:
        return self.contents
    
    @technique.setter
    def technique(self, value: Technique) -> None:
        self.contents = value
        return self
    
    @technique.deleter
    def technique(self) -> None:
        self.contents = None
        return self
    
    """ Public Methods """
    
    def apply(self, data: object = None, **kwargs) -> object:
        """Applies Technique instance in 'contents'.
        
        The code below outlines a basic method that a subclass should build on
        for a properly functioning Step.
        
        Applies stored 'contents' with 'parameters'.
        
        Args:
            data (object): optional object to apply 'contents' to. Defaults to
                None.
                
        Returns:
            object: with any modifications made by 'contents'. If data is not
                passed, nothing is returned.        
        
        """
        if data is None:
            self.contents.apply(**kwargs)
            return self
        else:
            return self.contents.apply(data = data, **kwargs)


@dataclasses.dataclass
class Technique(Component):
    """Base class for primitive objects in a sourdough composite object.
    
    The 'contents' and 'parameters' attributes are combined at the last moment
    to allow for runtime alterations.
    
    Args:
        contents (Callable, str): core object used by the 'apply' method or a
            str matching a callable object in the algorithms resource. Defaults 
            to None.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Configuration instance, 
            'name' should match the appropriate section name in a Configuration 
            instance. Defaults to None. 
        parameters (Mapping[Any, Any]]): parameters to be attached to 'contents' 
            when the 'apply' method is called. Defaults to an empty dict.
                                    
    """
    contents: Union[Callable, str] = None
    name: str = None
    parameters: Mapping[Any, Any] = dataclasses.field(default_factory = dict)

    """ Properties """
    
    @property
    def algorithm(self) -> Union[object, str]:
        return self.contents
    
    @algorithm.setter
    def algorithm(self, value: Union[object, str]) -> None:
        self.contents = value
        return self
    
    @algorithm.deleter
    def algorithm(self) -> None:
        self.contents = None
        return self
        
    """ Public Methods """
    
    def apply(self, data: object = None, **kwargs) -> object:
        """Applies stored 'contents' with 'parameters'.
        
        Args:
            data (object): optional object to apply 'contents' to. Defaults to
                None.
                
        Returns:
            object: with any modifications made by 'contents'. If data is not
                passed, nothing is returned.        
        
        """
        if data is None:
            if self.contents:
                data = self.contents.apply(**self.parameters, **kwargs)
            return data
        else:
            if self.contents:
                return self.contents.apply(data, **self.parameters, **kwargs)
            else:
                return None

