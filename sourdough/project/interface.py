"""
interface: user interface for sourdough project construction and iteration
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents: 
    Bases (Loader):
    Project (Hybrid): access point and interface for creating and implementing
        sourdough projects.

"""
from __future__ import annotations
from _typeshed import NoneType
import dataclasses
import inspect
import logging
import pathlib
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Set, Tuple, Type, Union)
import warnings

import sourdough 


logger = logging.getLogger()


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
        filer (Union[str, Type]): file management class or a str of the import
            path for the file management class. 
        component (Union[str, Type]): base node class or a str of the import
            path for the base node class. 
        manager (Union[str, Type]): base director class or a str of the import
            path for the base director class.
        quirk (Union[str, Type]): base mixin class or a str of the import
            path for the base mixin class. This base is only needed if the
            user is creating custom classes from strings at runtime using the
            sourdough Library class.
            
    """
    settings: Union[str, Type] = 'sourdough.resources.Settings'
    filer: Union[str, Type] = 'sourdough.resources.Filer' 
    structure: Union[str, Type] = 'sourdough.composites.Structure'
    component: Union[str, Type] = 'sourdough.nodes.Component'
    creator: Union[str, Type] = 'sourdough.workshop.Creator'
    manager: Union[str, Type] = 'sourdough.workshop.Manager'
    quirk: Union[str, Type] = 'sourdough.quirks.Quirk'

    """ Properties """

    @property
    def component_suffixes(self) -> Tuple[str]:
        """[summary]

        Returns:
            Tuple[str]: [description]
        """
        return self._get_suffixes(name = 'component')
    
    @property
    def manager_suffixes(self) -> Tuple[str]:
        """[summary]

        Returns:
            Tuple[str]: [description]
        """
        return self._get_suffixes(name = 'manager')
   
    """ Public Methods """
   
    def _get_suffixes(self, name: str) -> Tuple[str]:
        return tuple(key + 's' for key in getattr(self, name).library.keys())
   
    def get_class(self, name: Union[str, Sequence[str]], kind: str) -> Type:
        """[summary]

        Args:
            name (str): [description]

        Returns:
            Type: [description]
            
        """
        base = getattr(self, kind)
        product = None
        for key in sourdough.tools.listify(name):
            try:
                product = base.duplicate(name = key)
                break
            except (AttributeError, KeyError):
                pass
        product = product or base
        return product   


@dataclasses.dataclass
class Project(sourdough.quirks.Element, sourdough.quirks.Validator,
              sourdough.types.Lexicon):
    """Constructs, organizes, and implements a sourdough project.

    Args:
        contents (Mapping[str, object]): keys are names of objects stored and 
            values are the stored objects. Defaults to an empty dict.
        managers (Mapping[str, Union[Type, str]]): related manager which constructs objects to be 
            stored in 'contents'. Defaults to an empty list.
        settings (Union[sourdough.base.Settings, str, pathlib.Path]]): a
            Settings-compatible subclass or instance, a str or pathlib.Path 
            containing the file path where a file of a 
            supported file type with settings for a Configuration instance is 
            located. Defaults to the default Configuration instance.
        filer (Union[Type, str, pathlib.Path]]): a Clerk-compatible class or a 
            str or pathlib.Path containing the full path of where the root 
            folder should be located for file input and output. A 'filer' must 
            contain all file path and import/export methods for use throughout 
            sourdough. Defaults to the default Clerk instance. 
        bases (ClassVar[object]): contains information about default base 
            classes used by a Director instance. Defaults to an instance of 
            SimpleBases.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Configuration instance, 
            'name' should match the appropriate section name in a Configuration 
            instance. Defaults to None. 
        identification (str): a unique identification name for a Director 
            instance. The name is used for creating file folders related to the 
            project. If it is None, a str will be created from 'name' and the 
            date and time. Defaults to None.   
        automatic (bool): whether to automatically advance 'manager' (True) or 
            whether the manager must be advanced manually (False). Defaults to 
            True.
        data (object): any data object for the project to be applied. If it is
            None, an instance will still execute its workflow, but it won't
            apply it to any external data. Defaults to None.  
        validations (Sequence[str]): 


    """
    contents: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    managers: Mapping[str, Union[Type, str]] = dataclasses.field(
        default_factory = sourdough.types.Lexicon)
    settings: Union[object, Type, pathlib.Path, str, Mapping] = None
    filer: Union[object, Type, pathlib.Path, str] = None
    bases: object = sourdough.base.Bases()
    structure: Union[Type, object, str] = None
    name: str = None
    identification: str = None
    automatic: bool = True
    data: Any = None
    validations: Sequence[str] = dataclasses.field(default_factory = lambda: [
        'settings', 'name', 'identification', 'filer', 'structure', 'managers'])
    
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
        # Adds 'general' section attributes from 'settings'.
        self.settings.inject(instance = self)
        # Sets index for iteration.
        self.index = 0
        # Advances through 'contents' if 'automatic' is True.
        if self.automatic:
            print('test yes auto')
            self.complete() 
    
    """ Properties """
    
    @property
    def workflow(self) -> Mapping[str, object]:
        return self.contents
    
    @workflow.setter
    def workflow(self, value: Mapping[str, object]) -> None:
        self.contents = value
        return self
    
    @workflow.deleter
    def workflow(self) -> None:
        self.contents = {}
        return self
   
    """ Public Methods """
    
                    
    """ Private Methods """
    
    def _validate_settings(self, settings: Union[object, pathlib.Path, str, 
                                                 Mapping]) -> object:
        """Validates 'settings' or converts it to a Configuration instance.
        
        The method also injects the 'general' section of a Configuration 
        instance into this Director instance as attributes. This allows easy, 
        direct access of settings like 'verbose'.
        
        """
        if isinstance(settings, self.bases.settings):
            pass
        elif inspect.isclass(settings):
            settings = settings()
        elif settings is None or isinstance(settings, 
                                            (str, pathlib.Path, Mapping)):
            settings = self.bases.settings(contents = settings)
        else:
            raise TypeError(
                'settings must be a Configuration, Path, str, or None type.')
        # Adds 'general' section attributes from 'settings'.
        settings.inject(instance = self)
        return settings

    def _validate_name(self, name: str) -> str:
        """Creates 'name' if one doesn't exist.
        
        If 'name' was not passed, this method first tries to infer 'name' as the 
        first appropriate section name in 'settings'. If that doesn't work, it 
        uses the snakecase name of the class.
        
        """
        if not name:
            node_sections = self.settings.excludify(subset = self.settings.skip)
            try:
                name = node_sections.keys()[0]
            except IndexError:
                name = sourdough.tools.snakify(self.__class__)
        return name

    def _validate_identification(self, identification) -> str:
        """Creates unique 'identification' if one doesn't exist.
        
        By default, 'identification' is set to the 'name' attribute followed by
        an underscore and the date and time.
        
        """
        if not identification:
            identification = sourdough.tools.datetime_string(prefix = self.name)
        return identification

    def _validate_filer(self, filer: Union[object, pathlib.Path, str]) -> object:
        """Validates 'filer' or converts it to a Clerk instance.
        
        If a file path is passed, that becomes the root folder with the default
        file structure in the default Clerk instance.
        
        If an object is passed, its 'settings' attribute is replaced with this 
        instance's 'settings'.
        
        """
        if isinstance(filer, self.bases.filer):
            filer.settings = self.settings
        elif inspect.isclass(filer):
            filer = filer(settings = self.settings)
        elif filer is None or isinstance(filer, (str, pathlib.Path)):
            filer = self.bases.filer(
                root_folder = filer, 
                settings = self.settings)
        else:
            raise TypeError('filer must be a Clerk, Path, str, or None type.')
        return filer

    def _validate_managers(self, managers: Mapping[str, Union[object, str]]) -> (
            Mapping[str, object]):
        """Validates 'managers' or converts them to Manager subclasses.
        
        """
        if not managers:
            try:
                managers = self.settings[self.name][f'{self.name}_managers']
            except KeyError:
                pass
        new_managers = []
        for item in managers:
            new_managers.append(self._validate_manager(manager = item))
        return new_managers

    def _validate_manager(self, manager: Union[str, object]) -> object:
        """
        """
        if isinstance(manager, str):
            manager = self.bases.get_class(name = manager, kind = 'manager')
            manager = manager(name = manager, project = self)
        elif inspect.isclass(manager):
            manager = manager(project = self)
        elif isinstance(manager, self.bases.settings.manager):
            manager.project = self
        else:
            raise TypeError(
                'contents must be a list of str or Director types')
        return manager

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
        