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
import types
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Union)
import warnings

import sourdough 


DEFAULTS = {'settings': sourdough.Settings,
            'manager': sourdough.Manager,
            'workflow': 'editor'}

@dataclasses.dataclass
class Project(sourdough.types.Lexicon):
    """Constructs, organizes, and implements a sourdough project.
        
    Args:
        contents (Mapping[Any, Stage]]): stored dictionary that stores completed
            Stage instances created by a Workflow instance. Defaults to an empty 
            dict.
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
        workflow (Union[sourdough.Workflow, str]): Workflow subclass, 
            Workflow subclass instance, or a str corresponding to a key in 
            'workflows'. Defaults to None.
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
        automatic (bool): whether to automatically advance 'workflow' (True) or 
            whether the workflow must be advanced manually (False). Defaults to 
            True.
        data (object): any data object for the project to be applied.         
  
            
    """
    contents: Mapping[Any, sourdough.Stage] = dataclasses.field(
        default_factory = dict)
    settings: Union[sourdough.Settings, str, pathlib.Path] = None
    manager: Union[sourdough.Manager, str, pathlib.Path] = None
    workflow: Union[sourdough.Workflow, str] = None
    name: str = None
    identification: str = None
    automatic: bool = True
    data: object = None
    resources: ClassVar[types.ModuleType] = sourdough.project.resources
    _validations: ClassVar[Sequence[str]] = [
        'settings', 'name', 'identification', 'manager', 'workflow']
    
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
        # Advances through 'workflow' if 'automatic' is True.
        if self.automatic:
            self._auto_workflow()

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
        """Validates 'settings' or converts it to a Settings instance."""
        if not isinstance(self.settings, sourdough.Settings):
            self.settings = sourdough.Settings(contents = self.settings)
        # Adds 'general' section attributes from 'settings'.
        self.settings.inject(instance = self)
        return self

    def _validate_name(self) -> None:
        """Infers name as the first appropriate section name in 'settings'."""
        if not self.name:
            for section in self.settings.keys():
                if section not in ['general', 'files']:
                    self.name = section
                    break
        if not self.name:
            self.name = sourdough.tools.snakify(self.__class__)
        return self

    def _validate_identification(self) -> None:
        """Creates unique 'identification' str based upon date and time."""
        if not self.identification:
            self.identification = sourdough.tools.datetime_string(
                prefix = self.name)
        return self

    def _validate_manager(self) -> None:
        """Validates 'manager' or converts it to a Manager instance."""
        if not isinstance(self.manager, sourdough.Manager):
            self.manager = sourdough.Manager(
                root_folder = self.manager, 
                settings = self.settings)
        return self
    
    def _validate_workflow(self) -> None:
        """Validates or converts 'workflow' and initializes it."""
        try:
            self.workflow = self.settings[self.name]['workflow']
        except KeyError:
            if self.workflow is None:
                self.workflow = 'editor'
        if inspect.isclass(self.workflow):
            self.workflow = self.workflow(project = self)
        elif isinstance(self.workflow, str):
            self.workflow = self.resources.workflows.instance(
                key = self.workflow,
                project = self)
        elif not isinstance(self.workflow, sourdough.Workflow):
            raise TypeError(
                f'workflow must be a str matching a key in workflows, a '
                f'Workflow subclass, or a Workflow subclass instance')
        return self
                     
    def _auto_workflow(self) -> None:
        """Advances through the stored Workflow instances."""
        for stage in self.workflow:
            if hasattr(self, 'verbose') and self.verbose:
                print(f'Beginning {stage.action} process')
            self = stage.perform(project = self)
        return self

    """ Dunder Methods """
    
    def __iter__(self) -> Iterable:
        return iter(self.workflow)

# @dataclasses.dataclass
# class Overview(sourdough.types.Lexicon):
#     """Dictionary of different Element types in a Worker instance.
    
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
#         if self.structure.structure is not None:
#             self.add({
#                 'name': self.structure.name, 
#                 'structure': self.structure.structure.name})
#             for key, value in self.structure.structure.options.items():
#                 matches = self.structure.find(
#                     self._get_type, 
#                     element = value)
#                 if len(matches) > 0:
#                     self.contents[f'{key}s'] = matches
#         else:
#             raise ValueError(
#                 'structure must be a Role for an overview to be created.')
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

        