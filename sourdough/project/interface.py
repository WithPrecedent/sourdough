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
import pathlib
import types
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Union)
import warnings

import sourdough 


DEFAULTS = {
    'settings': sourdough.Settings,
    'manager': sourdough.Manager,
    'creator': sourdough.Creator,
    'creators': ['architect', 'supervisor', 'worker']}


@dataclasses.dataclass
class Project(sourdough.types.Hybrid):
    """Constructs, organizes, and implements a sourdough project.
    
    Unlike an ordinary Hybrid, a Project instance will iterate 'crators' 
    instead of 'contents'. However, all getters and setters still point to 
    'contents', which is where the results of 'creators' are stored.
        
    Args:
        contents (Mapping[str, object]]): stored dictionary that stores objects
            created by 'creators'.
        settings (Union[sourdough.Settings, str, pathlib.Path]]): an instance of 
            Settings or a str or pathlib.Path containing the file path where a 
            file of a supported file type with settings for a Settings instance 
            is located. Defaults to the default Settings instance.
        manager (Union[sourdough.Manager, str, pathlib.Path]]): an instance of 
            Manager or a str or pathlib.Path containing the full path of where 
            the root folder should be located for file input and output. A 
            Manager instance contains all file path and import/export methods 
            for use throughout sourdough. Defaults to the default Manager 
            instance. 
        creators (Sequence[Union[sourdough.Creator, str]]):
        
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. If it is None, the 'name' will be inferred from
            the first section name in 'settings' after 'general' and 'files'.
            Defaults to None. 
        identification (str): a unique identification name for a Project 
            instance. The name is used for creating file folders related to the 
            project. If it is None, a str will be created from 'name' and the 
            date and time. Defaults to None.   
        automatic (bool): whether to automatically advance 'director' (True) or 
            whether the director must be advanced manually (False). Defaults to 
            True.
        data (object): any data object for the project to be applied.         
  
            
    """
    contents: Sequence[sourdough.Creator] = dataclasses.field(
        default_factory = list)
    settings: Union[sourdough.Settings, str, pathlib.Path] = None
    manager: Union[sourdough.Manager, str, pathlib.Path] = None
    creators: Sequence[Union[sourdough.Creator, str]] = None
    name: str = None
    identification: str = None
    automatic: bool = True
    data: object = None
    resources: types.ModuleType = dataclasses.field(
        default_factory = lambda: sourdough.resources)
    defaults: Mapping[str, Any] = dataclasses.field(
        default_factory = lambda: DEFAULTS)
    _validations: ClassVar[Sequence[str]] = [
        'settings', 'name', 'identification', 'manager', 'creators']
    
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
        # Calls validation methods based on items listed in '_validations'.
        for validation in self._validations:
            getattr(self, f'_validate_{validation}')()
        # Advances through 'director' if 'automatic' is True.
        if self.automatic:
            self._auto_director()

    """ Class Methods """

    @classmethod
    def add_resource(cls, name: str, resource: sourdough.types.Lexicon) -> None:
        """[summary]

        Args:
            name (str): [description]
            resource (sourdough.types.Lexicon): [description]
            
        """
        setattr(cls.resources, name, resource)
        return cls
    
    @classmethod
    def add_to_resource(cls, name: str, key: str, value: Any) -> None:
        """[summary]

        Args:
            name (str): [description]
            key (str): [description]
            value (Any): [description]
            
        """
        getattr(cls.resources, name).add(item = {key: value})
        return cls

    """ Private Methods """
    
    def _validate_settings(self) -> None:
        """Validates 'settings' or converts it to a Settings instance.
        
        The method also injects the 'general' section of a Settings instance
        into this Project instance as attributes. This allows easy, direct 
        access of settings like 'verbose'.
        
        """
        if not isinstance(self.settings, self.defaults['settings']):
            self.settings = self.defaults['settings'](contents = self.settings)
        # Adds 'general' section attributes from 'settings'.
        self.settings.inject(instance = self)
        return self

    def _validate_name(self) -> None:
        """Creates 'name' if one doesn't exist.
        
        The method first tries to infers 'name' as the first appropriate section 
        name in 'settings'. If that doesn't work, it uses the snake case of the
        class.
        
        """
        if not self.name:
            for section in self.settings.keys():
                if section not in ['general', 'files']:
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
        """Validates 'manager' or converts it to a Manager instance."""
        if not isinstance(self.manager, self.defaults['manager']):
            self.manager = self.defaults['manager'](
                root_folder = self.manager, 
                settings = self.settings)
        return self

    def _validate_creators(self) -> None:
        """[summary]

        Raises:
            TypeError: [description]

        Returns:
            [type]: [description]
            
        """
        if self.creators is None:
            self.creators = self.defaults['creators']
        new_creators = []
        for creator in self.creators:
            if isinstance(creator, str):
                new_creators.append(self.resources.creators.instance(creator))
            elif issubclass(creator, self.defaults['creator']):
                new_creators.append(creator())
            else:
                raise TypeError(
                    f'All creators must be str or {self.defaults["creator"]} ' 
                    f'type')
        self.creators = new_creators
        return self

    def _get_last_product(self) -> object:
        """[summary]

        Returns:
            object: [description]
        """
        last_key = self.contents.keys()[:-1]
        return self.contents[last_key]

    def _auto_create(self) -> None:
        """Advances through the stored Creator instances."""
        for creator in self.creators:
            self.append(creator)
        return self
    
    """ Dunder Methods """
    
    def __next__(self) -> Project:
        """[summary]

        Returns:
            Project: [description]
            
        """
        if self.index < 0:
            previous = self.settings
        else:
            previous = self.contents[self.index]
        self.index += 1
        current = self.contents[self.index]
        print('test current in next', current)
        if hasattr(self.project, 'verbose') and self.verbose:
            print(f'Beginning {current.action} process')
        creation = current.create(previous = previous, project = self.project)
        print('test creation', creation)
        return creation
    
    def __iter__(self) -> Iterable:
        return self


# @dataclasses.dataclass
# class Overview(sourdough.types.Lexicon):
#     """Dictionary of different Element types in a Flow instance.
    
#     Args:
#         contents (Mapping[Any, Any]]): stored dictionary. Defaults to an empty 
#             dict.
#         name (str): designates the name of a class instance that is used for 
#             internal referencing throughout sourdough. For example, if a 
#             sourdough instance needs settings from a Settings instance, 'name' 
#             should match the appropriate section name in the Settings instance. 
#             When subclassing, it is sometimes a good idea to use the same 'name' 
#             attribute as the base class for effective coordination between 
#             sourdough classes. Defaults to None. If 'name' is None and 
#             '__post_init__' of Element is called, 'name' is set based upon
#             the 'get_name' method in Element. If that method is not overridden 
#             by a subclass instance, 'name' will be assigned to the snake case 
#             version of the class name ('__class__.__name__').
              
#     """
#     contents: Mapping[Any, Any] = dataclasses.field(default_factory = dict)
#     name: str = None
    
#     """ Initialization Methods """
    
#     def __post_init__(self) -> None:
#         """Initializes class instance attributes."""
#         # Calls parent and/or mixin initialization method(s).
#         super().__post_init__()
#         if self.workflow.workflow is not None:
#             self.add({
#                 'name': self.workflow.name, 
#                 'workflow': self.workflow.workflow.name})
#             for key, value in self.workflow.workflow.options.items():
#                 matches = self.workflow.find(
#                     self._get_type, 
#                     element = value)
#                 if len(matches) > 0:
#                     self.contents[f'{key}s'] = matches
#         else:
#             raise ValueError(
#                 'workflow must be a Role for an overview to be created.')
#         return self          
    
#     """ Dunder Methods """
    
#     def __str__(self) -> str:
#         """Returns pretty string representation of an instance.
        
#         Returns:
#             str: pretty string representation of an instance.
            
#         """
#         new_line = '\n'
#         representation = [f'sourdough {self.get_name}']
#         for key, value in self.contents.items():
#             if isinstance(value, Sequence):
#                 names = [v.name for v in value]
#                 representation.append(f'{key}: {", ".join(names)}')
#             else:
#                 representation.append(f'{key}: {value}')
#         return new_line.join(representation)    

#     """ Private Methods """

#     def _get_type(self, 
#             item: sourdough.Element, 
#             element: sourdough.Element) -> Sequence[sourdough.Element]: 
#         """[summary]

#         Args:
#             item (self.stored_types): [description]
#             self.stored_types (self.stored_types): [description]

#         Returns:
#             Sequence[self.stored_types]:
            
#         """
#         if isinstance(item, element):
#             return [item]
#         else:
#             return []

        