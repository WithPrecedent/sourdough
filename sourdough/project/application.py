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
class Bases(sourdough.quirks.Loader):
    """Base classes for a sourdough projects.
    
    Args:
        director (Union[str, Type]): class for organizing, implementing, and
            iterating the package's classes and functions. Defaults to 
            'sourdough.Director'.
            
    """
    settings: Union[str, Type] = 'sourdough.Settings'
    clerk: Union[str, Type] = 'sourdough.Clerk' 
    director: Union[str, Type] = 'sourdough.Director'
    creator: Union[str, Type] = 'sourdough.Creator'
    component: Union[str, Type] = 'sourdough.base.Component'

    """ Properties """
    
    def component_suffixes(self) -> Tuple[str]:
        return tuple(key + 's' for key in self.component.registry.keys()) 
    
    def director_suffixes(self) -> Tuple[str]:
        return tuple(key + 's' for key in self.director.registry.keys()) 
   
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
    skip: Sequence[str] = dataclasses.field(
        default_factory = lambda: ['general', 'files', 'parameters'])


@dataclasses.dataclass
class Factory(sourdough.quirks.Registrar, sourdough.types.Lexicon, abc.ABC):
    
    contents: Mapping[str, str] = dataclasses.field(default_factory = dict)

    """ Public Methods """
    
    def create(self, outline: Outline, director: sourdough.Director, 
               **kwargs) -> object:
        """[summary]

        Args:
            name (str): [description]
            director (sourdough.Director): [description]

        Returns:
            object: [description]
            
        """
        for parameter in self.contents.keys():
            if parameter not in kwargs:
                try:
                    kwargs[parameter] = getattr(self, f'get_{parameter}')(
                        name = name, 
                        director = director)
                except KeyError:
                    try:
                        kwargs[parameter] = director.project.settings[name][
                            f'{name}_{parameter}']
                    except KeyError:
                        try: 
                            kwargs[parameter] = director.project.settings[name][
                                parameter]
                        except KeyError:
                            pass
        product = self.get_product(name = name, **kwargs)
        return product(**kwargs)    
        
    def create_contained(self, name: str, director: sourdough.Director, 
                         **kwargs) -> object:
        """[summary]

        Args:
            name (str): [description]
            director (sourdough.Director): [description]

        Returns:
            object: [description]
            
        """
        for parameter in self.contents.keys():
            if parameter not in kwargs:
                try:
                    kwargs[parameter] = getattr(self, f'get_{parameter}')(
                        name = name, 
                        director = director)
                except KeyError:
                    try:
                        kwargs[parameter] = director.project.settings[name][
                            f'{name}_{parameter}']
                    except KeyError:
                        try: 
                            kwargs[parameter] = director.project.settings[name][
                                parameter]
                        except KeyError:
                            pass
        contained = self._get_contained(name = name, **kwargs)
        return contained(**kwargs)

    """ Private Methods """

    def _get_contained(self, name: str, **kwargs: Dict[str, Any]) -> Type:
        """[summary]

        Args:
            name (str): [description]

        Returns:
            Type: [description]
        """
        if hasattr(self.base, 'registry'):
            try:
                product = self.base.registry.acquire(key = name)
            except KeyError:
                try:
                    product = self.base.registry.acquire(key = kwargs['design'])
                except (KeyError, TypeError):
                    product = self.base
        else:
            product = self.base
        return product        


@dataclasses.dataclass
class Author(sourdough.base.Creator):
    """Initialized sourdough Component instances without structure.
    
    Args:
        contents (Mapping[str, sourdough.Component]): stored dictionary with 
            keys as names of Components and values as Component instances.
              
    """
    contents: Mapping[str, sourdough.Component] = dataclasses.field(
        default_factory = dict)
    
    """ Class Methods """
    
    @classmethod
    def create(cls, manager: sourdough.base.Manager) -> None:
        
        return cls
    
    """ Public Methods """
    
    def add_component(self, component: sourdough.Component) -> None:
        self.contents[component.name] = component
        return self
    
    def add_subcomponent(self, parent: str, 
                         component: sourdough.Component) -> None:
        self.contents[parent].add(component)
        return self
 

@dataclasses.dataclass
class Factory(sourdough.quirks.Registrar, sourdough.types.Lexicon, abc.ABC):
    """
            
    Args:
        
    """
    contents: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    base: Type = None

    """ Public Methods """
    
    def create(self, name: str, director: sourdough.Director, 
               **kwargs) -> object:
        """[summary]

        Args:
            name (str): [description]
            director (sourdough.Director): [description]

        Returns:
            object: [description]
            
        """
        for parameter in self.contents.keys():
            if parameter not in kwargs:
                try:
                    kwargs[parameter] = getattr(self, f'get_{parameter}')(
                        name = name, 
                        director = director)
                except KeyError:
                    try:
                        kwargs[parameter] = director.project.settings[name][
                            f'{name}_{parameter}']
                    except KeyError:
                        try: 
                            kwargs[parameter] = director.project.settings[name][
                                parameter]
                        except KeyError:
                            pass
        product = self.get_product(name = name, **kwargs)
        return product(**kwargs)

    def get_product(self, name: str, **kwargs: Dict[str, Any]) -> Type:
        """[summary]

        Args:
            name (str): [description]

        Returns:
            Type: [description]
        """
        if hasattr(self.base, 'registry'):
            try:
                product = self.base.registry.acquire(key = name)
            except KeyError:
                try:
                    product = self.base.registry.acquire(key = kwargs['design'])
                except (KeyError, TypeError):
                    product = self.base
        else:
            product = self.base
        return product        

@dataclasses.dataclass
class Creator(sourdough.base.Factory):
    """
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
    base: Type = sourdough.base.Component
    
    """ Public Methods """

    def build(self, name: str, 
              director: sourdough.Director) -> sourdough.base.Component:
        
        return component

    def get_name(self, name: str, director: sourdough.Director) -> str:
        """[summary]

        Args:
            name (str): [description]
            director (sourdough.Director): [description]

        Returns:
            str: [description]
        """
        return name

    def get_contents(self, name: str, director: sourdough.Director) -> List[str]:
        """[summary]

        Args:
            name (str): [description]
            director (sourdough.Director): [description]

        Returns:
            List[str]: [description]
        """
        section = director.project.settings[name]
        component_suffixes = director.project.bases.component_suffixes
        contents = self.contents['contents']
        for key, value in section.items():
            prefix, suffix = self._divide_key(key = key)
            if prefix == name and suffix in component_suffixes:
                value_sequence = sourdough.tools.listify(value)
                contains = suffix.rstrip('s')
                items = [tuple(item, contains) for item in value_sequence]
                contents.append(items)
        return contents
    
    def get_subcontents(self, name: str, 
                        director: sourdough.Director) -> Dict[str, str]:
        """[summary]

        Args:
            name (str): [description]
            director (sourdough.Director): [description]

        Returns:
            Dict[str, str]: [description]
        """
        section = director.project.settings[name]
        component_suffixes = director.project.bases.component_suffixes
        subcontents = self.contents['subcontents']
        for key, value in section.items():
            prefix, suffix = self._divide_key(key = key)
            if prefix != name and suffix in component_suffixes:
                value_sequence = sourdough.tools.listify(value)
                contains = suffix.rstrip('s')
                items = [tuple(item, contains) for item in value_sequence]
                if prefix not in subcontents:
                    subcontents[prefix] = []
                subcontents[prefix].append(items)
        return subcontents
    
    def get_parameters(self, name: str, 
                       director: sourdough.Director) -> Dict[str, str]:
        try:
            return director.project.settings[f'{name}_parameters']
        except KeyError:
            return self.contents['parameters']

    """ Private Methods """
         
    def _divide_key(self, key: str, divider: str = None) -> Tuple[str, str]:
        """[summary]

        Args:
            key (str): [description]

        Returns:
            
            Tuple[str, str]: [description]
            
        """
        if divider is None:
            divider = '_'
        if divider in key:
            suffix = key.split(divider)[-1]
            prefix = key[:-len(suffix) - 1]
        else:
            prefix = suffix = key
        return prefix, suffix


          
@dataclasses.dataclass
class Manager(sourdough.base.Director):
    """Constructs, organizes, and implements part of a sourdough project.
        
    Args:
        contents (Mapping[str, object]]): stored objects created by the 
            'create' methods of 'stages'. Defaults to an empty dict.
        stages (Sequence[Union[Type, str]]): a Creator-compatible classes or
            strings corresponding to the keys in registry of the default
            'stage' in 'bases'. Defaults to a list of 'architect', 
            'builder', and 'worker'. 
        project (sourdough.Project)
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example if a 
            sourdough instance needs settings from a Configuration instance, 'name' 
            should match the appropriate section name in the Configuration instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. If it is None, the 'name' will be attempted to be 
            inferred from the first section name in 'settings' after 'general' 
            and 'files'. If that fails, 'name' will be the snakecase name of the
            class. Defaults to None. 
        identification (str): a unique identification name for a Director 
            instance. The name is used for creating file folders related to the 
            project. If it is None, a str will be created from 'name' and the 
            date and time. Defaults to None.   
        automatic (bool): whether to automatically advance 'director' (True) or 
            whether the director must be advanced manually (False). Defaults to 
            True.
        data (object): any data object for the project to be applied. If it is
            None, an instance will still execute its workflow, but it won't
            apply it to any external data. Defaults to None.  
        bases (ClassVar[object]): contains information about default base 
            classes used by a Director instance. Defaults to an instance of 
            Bases.
        rules (ClassVar[object]):
        options (ClassVar[object]):
         
    """
    contents: Mapping[str, object] = dataclasses.field()
    project: Union[object, Type] = None
    creator: Union[object, Type] = None
    name: str = None
    automatic: bool = True
    data: object = None
    validations: Sequence[str] = dataclasses.field(default_factory = lambda: [
        'name', 'creator'])
    default_design: str = 'pipeline'
    registry: ClassVar[Mapping[str, Director]] = sourdough.types.Catalog()
    
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

    """ Public Methods """
    
    def draft(self) -> None:
        
    
    
    
    
    
    def advance(self) -> Any:
        """Returns next product created in iterating a Director instance."""
        return self.__next__()

    def complete(self) -> None:
        """Advances through the stored Creator instances.
        
        The results of the iteration is that each item produced is stored in 
        'content's with a key of the 'produces' attribute of each stage.
        
        """
        self.creator.complete()
        return self
    
    """ Private Methods """
    
    def _validate_name(self) -> None:
        """Creates 'name' if one doesn't exist."""
        if not self.name:
            self.name = sourdough.tools.snakify(self.__class__)
        return self
    
    def _validate_creator(self) -> None:
        """Creates 'name' if one doesn't exist.
        
        If 'name' was not passed, this method first tries to infer 'name' as the 
        first appropriate section name in 'settings'. If that doesn't work, it 
        uses the snakecase name of the class.
        
        """
        if not self.name:
            node_sections = self.settings.excludify(subset = self.rules.skip)
            try:
                self.name = node_sections.keys()[0]
            except IndexError:
                self.name = sourdough.tools.snakify(self.__class__)
        return self
    
    """ Dunder Methods """

    def __iter__(self) -> None:
        """
        """
        self.creator.__next__()
        return self
 
    def __next__(self) -> None:
        """
        """
        self.creator.__next__()
        return self









@dataclasses.dataclass
class Workflow(sourdough.base.Component):
    
    def apply(self, director: sourdough.Director) -> sourdough.Director:
        """Subclasses must provide their own methods."""
        return director


@dataclasses.dataclass
class Step(sourdough.base.Component):
    
    def apply(self, director: sourdough.Director) -> sourdough.Director:
        """Subclasses must provide their own methods."""
        return director


@dataclasses.dataclass
class Technique(sourdough.base.Component):
    
    def apply(self, director: sourdough.Director) -> sourdough.Director:
        """Subclasses must provide their own methods."""
        return director


        