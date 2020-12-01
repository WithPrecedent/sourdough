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
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)
import warnings

import sourdough 


@dataclasses.dataclass
class Project(sourdough.types.Lexicon):
    """Constructs, organizes, and implements a sourdough project.
    
    Unlike an ordinary Lexicon, a Project instance will iterate 'creators' 
    instead of 'contents'. However, all access methods still point to 
    'contents', which is where the results of iterating the class are stored.
        
    Args:
        contents (Mapping[str, object]]): stored objects created by 'creators'.
             defaults to an empty dict.
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
        resources (object):
        
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
    contents: Sequence[Any] = dataclasses.field(default_factory = dict)
    settings: Union[object, Type, str, pathlib.Path] = None
    manager: Union[object, Type, str, pathlib.Path] = None
    resources: object = dataclasses.field(default_factory = sourdough.Resources)
    creators: Sequence[Union[object, Type, str]] = dataclasses.field(
        default_factory = lambda: ['architect', 'builder', 'worker'])
    name: str = None
    identification: str = None
    automatic: bool = True
    data: object = None
    _validations: Sequence[str] = dataclasses.field(default_factory = lambda: [
        'settings', 'name', 'identification', 'manager', 'creators'])
    
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
        try:
            for validation in self._validations:
                getattr(self, f'_validate_{validation}')()
        except AttributeError:
            pass
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
            self.settings = self.resources.settings(contents = self.settings)
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
        if inspect.isclass(self.manager):
            self.manager = self.manager(settings = self.settings)
        elif (self.manager is None 
              or not isinstance(self.manager, (str, pathlib.Path))):
            self.manager = self.resources.manager(
                root_folder = self.manager, 
                settings = self.settings)
        else:
            self.manager.settings = self.settings
        return self

    def _validate_creators(self) -> None:
        """[summary]

        Raises:
            TypeError: [description]

        Returns:
            [type]: [description]
            
        """
        new_creators = []
        for creator in self.creators:
            if isinstance(creator, str):
                new_creators.append(self.resources.creator.acquire(creator)())
            elif inspect.isclass(creator):
                new_creators.append(creator())
            else:
                new_creators.append(creator)
        print('test creators', new_creators)
        self.creators = new_creators
        return self

    def _auto_create(self) -> None:
        """Advances through the stored Creator instances."""
        for creator in iter(self):
            self.contents.update({creator.produces: self.__next__()})
        return self
    
    """ Dunder Methods """
    
    def __next__(self) -> Any:
        """[summary]

        Returns:
            Any:
            
        """
        if self.index < len(self.creators):
            creator = self.creators[self.index]()
            if hasattr(self, 'verbose') and self.verbose:
                print(f'{creator.action} {creator.produces} from {creator.needs}')
            creation = creator.create(project = self)
            self.index += 1
        else:
            raise IndexError()
        return creation
    
    def __iter__(self) -> Iterable:
        return iter(self.creators)


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

        