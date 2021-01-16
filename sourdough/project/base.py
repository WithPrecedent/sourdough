"""
base: essential classes applying sourdough's core to a project
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Bases
    Settings
    Filer
    Creator
    Component

"""
from __future__ import annotations
import abc
import dataclasses
import pathlib
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import sourdough
    

@dataclasses.dataclass
class Bases(sourdough.quirks.Loader):
    """Base classes for a sourdough projects.
    
    Changing the attributes on a Bases instance allows users to specify 
    different base classes for a sourdough project in the necessary categories.
    Project will automatically use the base classes in the Bases instance 
    passed to it.
    
    Since this is a subclass of Loader, attribute values can either be classes
    or strings of the import path of classes. In the latter case, the base
    classes will be lazily loaded when called.
    
    Args:
        settings (Union[str, Type]): configuration class or a str of the import
            path for the configuration class. 
        file (Union[str, Type]): file management class or a str of the import
            path for the file management class. 
        component (Union[str, Type]): base node class or a str of the import
            path for the base node class. 
        creator (Union[str, Type]): base builder class or a str of the import
            path for the base builder class.
            
    """
    settings: Union[str, Type] = 'sourdough.project.Settings'
    filer: Union[str, Type] = 'sourdough.project.Filer' 
    component: Union[str, Type] = 'sourdough.project.Component'
    creator: Union[str, Type] = 'sourdough.project.Creator'

    """ Properties """
    
    def component_suffixes(self) -> Tuple[str]:
        """[summary]

        Returns:
            Tuple[str]: [description]
        """
        return tuple(key + 's' for key in self.component.registry.keys()) 
    
    def creator_suffixes(self) -> Tuple[str]:
        """[summary]

        Returns:
            Tuple[str]: [description]
        """
        return tuple(key + 's' for key in self.creator.registry.keys()) 
   
    """ Public Methods """
   
    def get_class(self, name: str, kind: str) -> Type:
        """[summary]

        Args:
            name (str): [description]

        Returns:
            Type: [description]
        """
        base = getattr(self, kind)
        if hasattr(base, 'registry'):
            try:
                product = base.registry.acquire(key = name)
            except KeyError:
                product = base
        else:
            product = base
        return product   
    
    
@dataclasses.dataclass
class Settings(sourdough.resources.Configuration):
    """Loads and Stores configuration settings for a Project.

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
                'file_encoding': 'windows-1252'}})
    skip: Sequence[str] = dataclasses.field(
        default_factory = lambda: ['general', 'files', 'filer', 'parameters'])


@dataclasses.dataclass
class Filer(sourdough.resources.Clerk):
    pass



@dataclasses.dataclass
class Component(sourdough.quirks.Registrar, sourdough.structures.Node):
    """[summary]

    Args:
        sourdough ([type]): [description]
        sourdough ([type]): [description]
        
    """
    contents: sourdough.quirks.Element = None 
    name: str = None
    registry: ClassVar[Mapping[str, Creator]] = sourdough.types.Catalog()


@dataclasses.dataclass
class Creator(sourdough.quirks.Registrar, sourdough.quirks.Validator, 
              sourdough.structures.Producer, abc.ABC):
    """[summary]

    Args:
        sourdough ([type]): [description]
        sourdough ([type]): [description]
        sourdough ([type]): [description]
        
    """
    contents: Mapping[str, str] = dataclasses.field(default_factory = lambda: {
        'name': None,
        'contents': [],
        'subcontents': {},
        'design': 'pipeline', 
        'needs': [], 
        'produces': str, 
        'iterations': 1, 
        'criteria': [], 
        'parallel': False,
        'parameters': {}})
    settings: Union[object, Type, pathlib.Path, str, Mapping] = None
    bases: object = Bases()
    automatic: bool = True
    validations: ClassVar[Sequence[str]] = dataclasses.field(
        default_factory = list)
    registry: ClassVar[Mapping[str, Creator]] = sourdough.types.Catalog()
    
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent and/or mixin initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass
        # Calls validation methods based on items listed in 'validations'.
        self.validate()
                 
    """ Required Subclass Methods """ 
     
    @abc.abstractmethod
    def create(self, **kwargs) -> Any:
        """Subclasses must provide their own methods."""
        pass

    """ Private Methods """
    
    def _kwargify(self, name: str) -> Dict[str, Any]:
        section = self.creator.settings[name]
        design = self.creator.settings[name]
    
    def _section_to_component(self, name: str, **kwargs) -> Type[Any]:
        """[summary]

        Args:
            name (str): [description]

        Returns:
            Type: [description]
            
        """
        section = self.creator.settings[name]
        design = self.creator.settings[name]
        if hasattr(self.creator.bases.component, 'registry'):
            try:
                component = self.base.registry.acquire(key = name)
            except KeyError:
                try:
                    design = self.creator.settings
                    product = self.base.registry.acquire(key = kwargs['design'])
                except (KeyError, TypeError):
                    product = self.base
        else:
            product = self.base
        return product        


@dataclasses.dataclass
class Manager(Creator):
    """Directs and stores objects created by a creator.
    
    A Director is not necessary, but provides a convenient way to store objects
    created by a sourdough creator.
    
    Args:

    
    """
    contents: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    name: str = None
    creators: Mapping[str, Creator] = dataclasses.field(default_factory = dict)
    project: Union[object, Type] = None
    automatic: bool = True
    validations: ClassVar[Sequence[str]] = dataclasses.field(
        default_factory = lambda: ['creators'])   
    
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent and/or mixin initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass
        # Calls validation methods based on items listed in 'validations'.
        self.validate()
        # Advances through 'creator' stages if 'automatic' is True.
        if self.automatic:
            self.complete()
              
    """ Public Methods """
    
    def create(self, name: str = None, **kwargs) -> None:
        """Builds and stores an instance based on 'name' and 'kwargs'.

        Args:
            name (str): name of a class stored in 'creator.base.registry.' If 
                there is no registry, 'name' is None, or 'name' doesn't match a 
                key in 'creator.base.registry', then an instance of 
                'creator.base' is instanced and stored.
            kwargs (Dict[Any, Any]): any specific parameters that a user wants
                passed to a class when an instance is created.
            
        """
        if name is not None:
            self.contents[name] = self.creators[name].create(name = name, 
                                                             **kwargs)
        else:
            for key, creator in self.creators.items():
                self.contents[key] = creator.create(name = key, **kwargs)
        return self
    
    """ Private Methods """

    def _validate_creators(self) -> None:
        """
        
        """

        return self
       
    """ Dunder Methods """
    
    def __iter__(self) -> Iterable[Any]:
        """Returns iterable of 'creators'.

        Returns:
            Iterable: of 'creators'.

        """
        return iter(self.creators)

   
@dataclasses.dataclass
class Worker(Creator):
    """Builds complex class instances.

    For any parameters which require further construction code, a subclass
    should include a method named '_get_{name of a key in 'contents'}'. That
    method should return the value for the named parameter.

    Args:
        contents (Mapping[str, Any]): keys are the names of the parameters to
            pass when an object is created. Values are the defaults to use when
            there is not a method named with this format: '_get_{key}'. Keys
            are iterated in order when the 'create' method is called. Defaults
            to an empty dict.
        base (Type): a class that can either be a class to create an instance
            from or a class with a 'registry' attribute that holds stored
            classes. If a user intends to get a class stored in the 'registry'
            attribute, they need to pass a 'name' argument to the 'create' 
            method which corresponds to a key in the registry. Defaults to None.
        
    """
    contents: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    base: Type = None
    
    """ Public Methods """

    def create(self, name: str = None, **kwargs) -> object:
        """Builds and returns an instance based on 'name' and 'kwargs'.

        Args:
            name (str): name of a class stored in 'base.registry.' If there is
                no registry, 'name' is None, or 'name' doesn't match a key in
                'base.registry', then an instance of 'base' is returned.
            kwargs (Dict[Any, Any]): any specific parameters that a user wants
                passed to a class when an instance is created.

        Returns:
            object: an instance of a stored class.
            
        """
        for parameter in self.contents.keys():
            if parameter not in kwargs:
                try:
                    method = getattr(self, f'_get_{parameter}')
                    kwargs[parameter] = method(name = name, **kwargs)
                except KeyError:
                    kwargs[parameter] = self.contents[parameter]
        product = self.produce(name = name)
        return product(**kwargs) 
    
    def produce(self, name: str) -> Type:
        """Returns a class stored in 'base.registry' or 'base'.

        Args:
            name (str): the name of the sought class corresponding to a key in
                'base.registry'. If 'name' is None or doesn't match a key in
                'base.registry', the class listed in 'base' is returned instead.

        Returns:
            Type: a stored class.
            
        """
        try:
            product = self.base.acquire(key = name)
        except (KeyError, AttributeError, TypeError):
            product = self.base
        return product  

