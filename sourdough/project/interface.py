"""
interface: user interface for sourdough project construction and iteration
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Project (Lexicon): interface for sourdough projects.

"""
from __future__ import annotations
import dataclasses
import inspect
import pathlib
import pprint
from types import ModuleType
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)
import warnings

import sourdough 
  

@dataclasses.dataclass
class Bases(object):
    """Base classes for a sourdough project.
    
    Args:
        settings (Type): the configuration class to use in a sourdough project.
            Defaults to sourdough.Settings.
        manager (Type): the file manager class to use in a sourdough project.
            Defaults to sourdough.Manager.   
        creator (Type): the product/builder class to use in a sourdough 
            project. Defaults to sourdough.Creator.    
        product (Type): the product output class to use in a sourdough 
            project. Defaults to sourdough.Product. 
        component (Type): the node class to use in a sourdough project. Defaults 
            to sourdough.Component. 
        workflow (Type): the workflow to use in a sourdough project. Defaults to 
            sourdough.products.Workflow.      
            
    """
    settings: Type = sourdough.Settings
    manager: Type = sourdough.Manager
    creator: Type = sourdough.Creator
    product: Type = sourdough.Product
    component: Type = sourdough.Component
    workflow: Type = sourdough.products.Workflow
  
      
@dataclasses.dataclass
class Project(sourdough.types.Lexicon):
    """Constructs, organizes, and implements a sourdough project.
    
    Unlike an ordinary Lexicon, a Project instance will iterate 'creators' 
    instead of 'contents'. However, all access methods still point to 
    'contents', which is where the results of iterating the class are stored.
        
    Args:
        contents (Mapping[str, object]]): stored objects created by the 
            'create' methods of 'creators'. Defaults to an empty dict.
        settings (Union[Type, str, pathlib.Path]]): a Settings-compatible class,
            a str or pathlib.Path containing the file path where a file of a 
            supported file type with settings for a Settings instance is located. 
            Defaults to the default Settings instance.
        manager (Union[Type, str, pathlib.Path]]): a Manager-compatible class,
            or a str or pathlib.Path containing the full path of where the root 
            folder should be located for file input and output. A 'manager'
            must contain all file path and import/export methods for use 
            throughout sourdough. Defaults to the default Manager instance. 
        creators (Sequence[Union[Type, str]]): a Creator-compatible classes or
            strings corresponding to the keys in registry of the default
            'creator' in 'bases'. Defaults to a list of 'architect', 
            'builder', and 'worker'. 
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. If it is None, the 'name' will be attempted to be 
            inferred from the first section name in 'settings' after 'general' 
            and 'files'. If that fails, 'name' will be the snakecase name of the
            class. Defaults to None. 
        identification (str): a unique identification name for a Project 
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
            classes used by a Project instance. Defaults to an instance of 
            Bases.

                  
    """
    contents: Sequence[Any] = dataclasses.field(default_factory = dict)
    settings: Union[object, Type, str, pathlib.Path] = None
    manager: Union[object, Type, str, pathlib.Path] = None
    creators: Sequence[Union[Type, str]] = dataclasses.field(
        default_factory = lambda: ['architect', 'builder', 'worker'])
    name: str = None
    identification: str = None
    automatic: bool = True
    data: object = None
    bases: ClassVar[object] = Bases()
    
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
        for validation in sourdough.rules.validations:
            getattr(self, f'_validate_{validation}')()
        # Sets index for iteration.
        self.index = 0
        # Advances through 'creators' if 'automatic' is True.
        if self.automatic:
            self._auto_create()

    """ Private Methods """
    
    def _validate_settings(self) -> None:
        """Validates 'settings' or converts it to a Settings instance.
        
        The method also injects the 'general' section of a Settings instance
        into this Project instance as attributes. This allows easy, direct 
        access of settings like 'verbose'.
        
        """
        if inspect.isclass(self.settings):
            self.settings = self.settings()
        elif (self.settings is None 
              or isinstance(self.settings, (str, pathlib.Path))):
            self.settings = self.bases.settings(contents = self.settings)
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
                if section not in sourdough.rules.skip_sections():
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

    def _validate_manager(self) -> None:
        """Validates 'manager' or converts it to a Manager instance.
        
        If a file path is passed, that becomes the root folder with the default
        file structure in the default Manager instance.
        
        If an object is passed, its 'settings' attribute is replaced with the 
        Project instance's 'settings'.
        
        """
        if inspect.isclass(self.manager):
            self.manager = self.manager(settings = self.settings)
        elif (self.manager is None 
              or isinstance(self.manager, (str, pathlib.Path))):
            self.manager = self.bases.manager(
                root_folder = self.manager, 
                settings = self.settings)
        else:
            self.manager.settings = self.settings
        return self

    def _validate_creators(self) -> None:
        """Validates 'creators' or converts it to a list of Creator instances.
        
        If strings are passed, those are converted to classes from the registry
        of the designated 'creator' in bases'.
        
        """
        new_creators = []
        for creator in self.creators:
            if isinstance(creator, str):
                new_creators.append(self.bases.creator.acquire(creator))
            else:
                new_creators.append(creator)
        self.creators = new_creators
        return self
    
    def _auto_create(self) -> None:
        """Advances through the stored Creator instances.
        
        The results of the iteration is that each item produced is stored in 
        'content's with a key of the 'produces' attribute of each creator.
        
        """
        for creator in iter(self):
            self.contents.update({creator.produces: self.__next__()})
        return self
    
    """ Dunder Methods """
    
    def __next__(self) -> Any:
        """Returns products of the next Creator in 'creators'.

        Returns:
            Any: item creator by the 'create' method of a Creator.
            
        """
        if self.index < len(self.creators):
            creator = self.creators[self.index]()
            if hasattr(self, 'verbose') and self.verbose:
                print(
                    f'{creator.action} {creator.produces} from {creator.needs}')
            self.index += 1
            product = creator.create(project = self)
        else:
            raise IndexError()
        return product
    
    def __iter__(self) -> Iterable:
        """Returns iterable of 'creators'.
        
        Returns:
            Iterable: iterable sequence of 'creators'.
            
        """
        return iter(self.creators)
      