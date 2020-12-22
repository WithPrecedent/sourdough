"""
interface: user interface for sourdough project construction and iteration
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Bases (object): base classes for a Manager.
    Manager (Lexicon): access point and interface for creating and implementing 
        a sourdough manager.project.
    Manager (Lexicon): access point and interface for creating and implementing
        multiple sourdough projects.

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
class Project(sourdough.types.Hybrid):
    """Constructs, organizes, and implements a a collection of projects.

    Args:
        contents (Mapping[str, Union[str, Manager]]]): stored Manager instances
            or the names of previously created Manager instances stored in 
            'sourdough.projects'. Defaults to an empty dict.
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
        bases (ClassVar[object]): contains information about default base 
            classes used by a Manager instance. Defaults to an instance of 
            SimpleBases.

    """
    contents: Union[str, sourdough.Manager] = dataclasses.field(
        default_factory = list)
    settings: Union[object, Type, str, pathlib.Path] = None
    clerk: Union[object, Type, str, pathlib.Path] = None
    name: str = None
    identification: str = None
    automatic: bool = True
    data: Any = None
    validations: Sequence[str] = dataclasses.field(default_factory = lambda: [
        'settings', 'name', 'identification', 'clerk', 'projects'])
    bases: ClassVar[object] = sourdough.bases
    rules: ClassVar[object] = sourdough.rules
    
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
    
    def advance(self) -> Any:
        """Returns next product created in iterating a Manager instance."""
        return self.__next__()

    def complete(self) -> None:
        """Executes and stores each Manager instance.
        
        """
        new_managers = []
        for manager in iter(self):
            new_managers.append[self.__next__()]
        self.contents = new_managers
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
            for section in self.settings.keys():
                if section not in self.rules.skip_sections():
                    self.name = section
                    break
        if not self.name:
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
        
        If an object is passed, its 'settings' attribute is replaced with the 
        Manager instance's 'settings'.
        
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

    def _validate_projects(self) -> None:
        """Validates 'contents' or converts it to Project instances.
        
        """
        if not self.contents:
            try:
                self.contents = self.settings[self.name][f'{self.name}_managers']
            except KeyError:
                pass
        new_contents = []
        for item in self.contents:
            print('test manager', item)
            if isinstance(item, str):
                try:
                    new_contents.append(sourdough.options.managers.select(item))
                except KeyError:
                    new_contents.append(self.bases.manager)
            else:
                new_contents.append(item)
        self.contents = new_contents
        return self

    """ Dunder Methods """     
    
    def __next__(self) -> object:
        """Returns completed Manager instance.

        Returns:
            Any: item project by the 'create' method of a Creator.
            
        """
        if self.index < len(self.contents):
            manager = self.contents[self.index](
                project = self,
                data = self.data)
            if hasattr(self, 'verbose') and self.verbose:
                print(f'Starting {manager.__name__}')
            new_manager = manager.complete()
            self.index += 1
            if hasattr(self, 'verbose') and self.verbose:
                print(f'Completed {manager.__name__}')
        else:
            raise IndexError()
        return new_manager
           