"""
interface: user interface for sourdough project construction and iteration
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Bases (Loader): stores base classes for a Project. Bases allows the base
        classes to be listed as import strings that will be lazily loaded when
        first accessed. 
    Project (Hybrid): access point and interface for creating and implementing
        sourdough projects.

"""
from __future__ import annotations
import dataclasses
import inspect
import pathlib
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)
import warnings

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
    factory: Union[str, Type] = 'sourdough.Creator'
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
class Project(sourdough.types.Hybrid):
    """Constructs, organizes, and implements a a collection of projects.

    Args:
        contents (Sequence[Union[str, sourdough.Director]]): stored Director
            classes, Director instances, or the names of Director subclasses 
            stored in 'options'. Defaults to an empty list.
        settings (Union[Type, str, pathlib.Path]]): a Configuration-compatible class,
            a str or pathlib.Path containing the file path where a file of a 
            supported file type with settings for a Configuration instance is 
            located. Defaults to the default Configuration instance.
        clerk (Union[Type, str, pathlib.Path]]): a Clerk-compatible class or a 
            str or pathlib.Path containing the full path of where the root 
            folder should be located for file input and output. A 'clerk' must 
            contain all file path and import/export methods for use throughout 
            sourdough. Defaults to the default Clerk instance. 
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example if a 
            sourdough instance needs settings from a Configuration instance, 'name' 
            should match the appropriate section name in the Configuration instance. 
            If it is None, the 'name' will be attempted to be inferred from the 
            first section name in 'settings' after 'general' and 'files'. If 
            that fails, 'name' will be the snakecase name of the class. Defaults 
            to None. 
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
        validations (Sequence[str]): 
        bases (ClassVar[object]): contains information about default base 
            classes used by a Director instance. Defaults to an instance of 
            SimpleBases.

    """
    contents: Sequence[Any] = dataclasses.field(default_factory = list)
    directors: Union[sourdough.base.Director, str] = dataclasses.field(
        default_factory = list)
    settings: Union[sourdough.types.Configuration, str, pathlib.Path] = None
    clerk: Union[sourdough.Clerk, str, pathlib.Path] = None
    bases: object = Bases()
    factory: Union[sourdough.base.Factory, str] = None
    name: str = None
    identification: str = None
    automatic: bool = True
    data: Any = None
    validations: Sequence[str] = dataclasses.field(default_factory = lambda: [
        'settings', 'name', 'identification', 'clerk', 'directors', 'factory'])
    
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent and/or mixin initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass
        # Removes various python warnings from console output.
        warnings.filterwarnings('ignore')
        # Calls validation methods based on items listed in 'validations'.
        for validation in self.validations:
            getattr(self, f'_validate_{validation}')()
        # Sets index for iteration.
        self.index = 0
        # Advances through 'contents' if 'automatic' is True.
        if self.automatic:
            print('test yes auto')
            self.complete()
            
    """ Public Methods """
    
    def add_director(self, director: Union[str, Type, object]) -> None:
        """

        Args:
            mananger (Union[str, Type, object]): [description]
        """
        self.directors.append(self._validate_director(director = director))
        return self  
    
    def advance(self) -> Any:
        """Returns next product created in iterating a Director instance."""
        return self.__next__()

    def complete(self) -> None:
        """Executes each step in an instance's iterable."""
        for director in iter(self):
            self.__next__()
        return self
                              
    """ Private Methods """
    
    def _validate_settings(self) -> None:
        """Validates 'settings' or converts it to a Configuration instance.
        
        The method also injects the 'general' section of a Configuration instance
        into this Director instance as attributes. This allows easy, direct 
        access of settings like 'verbose'.
        
        """
        if isinstance(self.settings, self.bases.settings):
            pass
        elif inspect.isclass(self.settings):
            self.settings = self.settings()
        elif (self.settings is None 
              or isinstance(self.settings, (str, pathlib.Path))):
            self.settings = self.bases.settings(contents = self.settings)
        else:
            raise TypeError(
                'settings must be a Configuration, Path, str, or None type.')
        # Adds 'general' section attributes from 'settings'.
        self.settings.inject(instance = self)
        return self

    def _validate_name(self) -> None:
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

    def _validate_identification(self) -> None:
        """Creates unique 'identification' if one doesn't exist.
        
        By default, 'identification' is set to the 'name' attribute followed by
        an underscore and the date and time.
        
        """
        if not self.identification:
            self.identification = sourdough.tools.datetime_string(
                prefix = self.name)
        return self

    def _validate_clerk(self) -> None:
        """Validates 'clerk' or converts it to a Clerk instance.
        
        If a file path is passed, that becomes the root folder with the default
        file structure in the default Clerk instance.
        
        If an object is passed, its 'settings' attribute is replaced with this 
        instance's 'settings'.
        
        """
        if isinstance(self.clerk, self.bases.clerk):
            self.clerk.settings = self.settings
        elif inspect.isclass(self.clerk):
            self.clerk = self.clerk(settings = self.settings)
        elif (self.clerk is None 
              or isinstance(self.clerk, (str, pathlib.Path))):
            self.clerk = self.bases.clerk(
                root_folder = self.clerk, 
                settings = self.settings)
        else:
            raise TypeError('clerk must be a Clerk, Path, str, or None type.')
        return self

    def _validate_directors(self) -> None:
        """Validates 'contents' or converts it to Director instances.
        
        """
        if not self.contents:
            try:
                self.contents = self.settings[self.name][
                    f'{self.name}_directors']
            except KeyError:
                pass
        new_contents = []
        for item in self.contents:
            new_contents.append(self._validate_director(director = item))
        self.contents = new_contents
        return self

    def _validate_director(self, director: Union[str, sourdough.Director]) -> None:
        """
        """
        if isinstance(director, str):
            director = self.bases.get_class(name = director, kind = 'director')
            director = director(name = director, project = self)
        elif inspect.isclass(director):
            director = director(project = self)
        elif isinstance(director, self.bases.settings.director):
            director.project = self
        else:
            raise TypeError(
                'contents must be a list of str or Director types')
        return director

    def _validate_factory(self) -> None:
        """Validates 'factory' or converts it to a Factory instance.'"""
        if isinstance(self.factory, self.bases.factory):
            pass
        elif isinstance(self.factory, str):
            self.factory = self.bases.get_class(
                name = self.factory, 
                kind = 'factory')()
        elif inspect.isclass(self.factory):
            self.factory = self.factory()
        elif self.factory is None:
            self.factory = self.bases.factory()
        else:
            raise TypeError('factory must be a Factory, str, or None type.')
        return self
       
    """ Dunder Methods """     

    def __iter__(self) -> Iterable:
        """Returns iterable of a Project instance.

        Returns:
            Iterable: of the Project instance.

        """
        return iter(self)
 
    def __next__(self) -> object:
        """Returns completed Director instance.

        Returns:
            Any: item project by the 'create' method of a Creator.
            
        """
        if self.index < len(self.directors):
            director = self.directors[self.index]
            if hasattr(self, 'verbose') and self.verbose:
                print(f'Starting {director.__name__}')
            director.complete()
            self.index += 1
            if hasattr(self, 'verbose') and self.verbose:
                print(f'Completed {director.__name__}')
        else:
            raise IndexError()
        return self
           