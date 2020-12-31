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
        manager (Union[str, Type]): class for organizing, implementing, and
            iterating the package's classes and functions. Defaults to 
            'sourdough.Manager'.
        workflow (Union[str, Type]): the workflow to use in a sourdough 
            project. Defaults to 'sourdough.products.Workflow'.
            
    """
    settings: Union[str, Type] = 'sourdough.Settings'
    clerk: Union[str, Type] = 'sourdough.Clerk' 
    manager: Union[str, Type] = 'sourdough.Manager'
    creator: Union[str, Type] = 'sourdough.Factory'
    component: Union[str, Type] = 'sourdough.Component'

    """ Properties """
    
    def component_suffixes(self) -> Tuple[str]:
        return tuple(key + 's' for key in self.component.registry.keys()) 
    

@dataclasses.dataclass
class Project(sourdough.types.Hybrid):
    """Constructs, organizes, and implements a a collection of projects.

    Args:
        contents (Sequence[Union[str, sourdough.Manager]]): stored Manager
            classes, Manager instances, or the names of Manager subclasses 
            stored in 'options'. Defaults to an empty list.
        settings (Union[Type, str, pathlib.Path]]): a Settings-compatible class,
            a str or pathlib.Path containing the file path where a file of a 
            supported file type with settings for a Settings instance is 
            located. Defaults to the default Settings instance.
        clerk (Union[Type, str, pathlib.Path]]): a Clerk-compatible class or a 
            str or pathlib.Path containing the full path of where the root 
            folder should be located for file input and output. A 'clerk' must 
            contain all file path and import/export methods for use throughout 
            sourdough. Defaults to the default Clerk instance. 
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            If it is None, the 'name' will be attempted to be inferred from the 
            first section name in 'settings' after 'general' and 'files'. If 
            that fails, 'name' will be the snakecase name of the class. Defaults 
            to None. 
        identification (str): a unique identification name for a Manager 
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
            classes used by a Manager instance. Defaults to an instance of 
            SimpleBases.

    """
    contents: Sequence[Any] = dataclasses.field(default_factory = list)
    managers: Union[sourdough.Manager, str] = dataclasses.field(
        default_factory = list)
    settings: Union[sourdough.Settings, str, pathlib.Path] = None
    clerk: Union[sourdough.Clerk, str, pathlib.Path] = None
    bases: object = Bases()
    name: str = None
    identification: str = None
    automatic: bool = True
    data: Any = None
    validations: Sequence[str] = dataclasses.field(default_factory = lambda: [
        'settings', 'name', 'identification', 'clerk', 'managers'])
    
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
    
    def add_manager(self, manager: Union[str, Type, object]) -> None:
        """

        Args:
            mananger (Union[str, Type, object]): [description]
        """
        self.managers.append(self._validate_manager(manager = manager))
        return self  
    
    def advance(self) -> Any:
        """Returns next product created in iterating a Manager instance."""
        return self.__next__()

    def complete(self) -> None:
        """Executes each step in an instance's iterable."""
        for manager in iter(self):
            self.__next__()
        return self
                              
    """ Private Methods """
    
    def _validate_settings(self) -> None:
        """Validates 'settings' or converts it to a Settings instance.
        
        The method also injects the 'general' section of a Settings instance
        into this Manager instance as attributes. This allows easy, direct 
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
                'settings must be a Settings, Path, str, or None type.')
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

    def _validate_managers(self) -> None:
        """Validates 'contents' or converts it to Manager instances.
        
        """
        if not self.contents:
            try:
                self.contents = self.settings[self.name][f'{self.name}_managers']
            except KeyError:
                pass
        new_contents = []
        for item in self.contents:
            new_contents.append(self._validate_manager(manager = item))
        self.contents = new_contents
        return self

    def _validate_manager(self, manager: Union[str, sourdough.Manager]) -> None:
        """
        """
        if isinstance(manager, str):
            try:
                manager = self.bases.manager.registry.select(key = manager)
            except KeyError:
                manager = self.bases.manager
            manager = manager(name = manager, project = self)
        elif inspect.isclass(manager):
            manager = manager(project = self)
        elif isinstance(manager, self.bases.settings.manager):
            manager.project = self
        else:
            raise TypeError(
                'contents must be a list of str or Manager types')
        return manager
    
    """ Dunder Methods """     

    def __iter__(self) -> Iterable:
        """Returns iterable of a Project instance.

        Returns:
            Iterable: of the Project instance.

        """
        return iter(self)
 
    def __next__(self) -> object:
        """Returns completed Manager instance.

        Returns:
            Any: item project by the 'create' method of a Creator.
            
        """
        if self.index < len(self.managers):
            manager = self.managers[self.index]
            if hasattr(self, 'verbose') and self.verbose:
                print(f'Starting {manager.__name__}')
            manager.complete()
            self.index += 1
            if hasattr(self, 'verbose') and self.verbose:
                print(f'Completed {manager.__name__}')
        else:
            raise IndexError()
        return self
           