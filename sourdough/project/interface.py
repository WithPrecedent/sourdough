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
import copy
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
    settings: Union[str, Type] = 'sourdough.project.Settings'
    filer: Union[str, Type] = 'sourdough.project.Filer' 
    workflow: Union[str, Type] = 'sourdough.project.Workflow'
    component: Union[str, Type] = 'sourdough.project.Component'
    manager: Union[str, Type] = 'sourdough.project.Manager'

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
   
    # def get_class(self, name: Union[str, Sequence[str]], kind: str) -> Type:
    #     """[summary]

    #     Args:
    #         name (str): [description]

    #     Returns:
    #         Type: [description]
            
    #     """
    #     base = getattr(self, kind)
    #     product = None
    #     for key in sourdough.tools.listify(name):
    #         try:
    #             product = base.duplicate(name = key)
    #             break
    #         except (AttributeError, KeyError):
    #             pass
    #     product = product or base
    #     return product   


@dataclasses.dataclass
class Project(sourdough.quirks.Element, sourdough.quirks.Validator, 
              sourdough.composites.Pipeline):
    """Constructs, organizes, and implements a sourdough project.

    Args:
        contents (Mapping[str, object]): keys are names of objects stored and 
            values are the stored objects. Defaults to an empty dict.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Configuration instance, 
            'name' should match the appropriate section name in a Configuration 
            instance. Defaults to None. 
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
        workflow ()
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

    Attributes:
        creator
        
    """
    contents: Sequence[Union[
        sourdough.project.Manager, 
        Type[sourdough.project.Manager],
        str]] = dataclasses.field(default_factory = list)
    name: str = None
    settings: Union[
        sourdough.project.Settings, 
        Type[sourdough.project.Settings], 
        pathlib.Path, 
        str, 
        Mapping[str, Mapping[str, Any]]] = None
    filer: Union[
        sourdough.project.Filer, 
        Type[sourdough.project.Filer], 
        pathlib.Path, 
        str] = None
    bases: Bases = Bases()
    workflow: Union[
        sourdough.project.Workflow, 
        Type[sourdough.project.Workflow], 
        str] = None
    results: Mapping[str, Any] = dataclasses.field(
        default_factory = sourdough.types.Lexicon)
    identification: str = None
    automatic: bool = True
    data: Any = None
    validations: ClassVar[Sequence[str]] = [
        'settings', 'name', 'identification', 'filer', 'workflow', 'contents']
    
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent and/or mixin initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass
        # Calls validation methods.
        self.validate()
        # Removes various python warnings from console output.
        warnings.filterwarnings('ignore')
        # Adds 'general' section attributes from 'settings'.
        self.settings.inject(instance = self)
        # Sets index for iteration.
        self.index = 0
        # Calls 'create' and 'execute' if 'automatic' is True.
        if self.automatic:
            self.create()
            self.execute()
            
    """ Public Methods """

    def create(self, **kwargs) -> None:
        """[summary]

        Args:
            kwargs
            
        """
        for manager in self.contents:
            manager.create()
        return self
    
    def execute(self) -> None:
        """
        """
        for plan in self.workflow:
            plan.execute()
        return self
                  
    """ Private Methods """
    
    def _validate_settings(self, settings: Union[
            sourdough.project.Settings, 
            Type[sourdough.project.Settings], 
            pathlib.Path, 
            str, 
            Mapping[str, Mapping[str, Any]]]) -> sourdough.project.Settings:
        """Validates 'settings' or converts it to a Configuration instance.
        
        The method also injects the 'general' section of a Configuration 
        instance into this Director instance as attributes. This allows easy, 
        direct access of settings like 'verbose'.
        
        Args:
        
        
        """
        if isinstance(settings, self.bases.settings):
            pass
        elif inspect.isclass(settings):
            settings = settings()
        elif settings is None or isinstance(settings, 
                                            (str, pathlib.Path, Mapping)):
            settings = self.bases.settings(contents = settings)
        else:
            raise TypeError('settings must be a Settings, Path, str, or None.')
        # Adds 'general' section attributes from 'settings'.
        settings.inject(instance = self)
        return settings

    def _validate_name(self, name: str) -> str:
        """Creates 'name' if one doesn't exist.
        
        If 'name' was not passed, this method first tries to infer 'name' as the 
        first appropriate section name in 'settings'. If that doesn't work, it 
        uses the snakecase name of the class.
        
        Args:
        
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
        
        Args:
        
        
        """
        if not identification:
            identification = sourdough.tools.datetime_string(prefix = self.name)
        return identification

    def _validate_filer(self, filer: Union[
            sourdough.project.Filer, 
            Type[sourdough.project.Filer], 
            pathlib.Path, 
            str]) -> sourdough.project.Filer:
        """Validates 'filer' or converts it to a Clerk instance.
        
        If a file path is passed, that becomes the root folder with the default
        file workflow in the default Clerk instance.
        
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
            raise TypeError('filer must be a Filer, Path, str, or None.')
        return filer

    def _validate_workflow(self, workflow: Union[
            sourdough.project.Workflow, 
            Type[sourdough.project.Workflow], 
            str]) -> sourdough.project.Workflow:
        """Validates 'workflow' or converts it to a Structure instance.
        
        Args:
         
        """
        if workflow is None:
            try:
                workflow = self.settings[self.name][f'{self.name}_workflow']
            except KeyError:
                try:
                    workflow = self.settings[self.name]['workflow']
                except KeyError:
                    workflow = 'graph'
        if isinstance(workflow, str):
            workflow = self.bases.workflow.library.borrow(name = workflow)
            workflow = workflow(contains = self.bases.component)
        elif isinstance(workflow, self.bases.workflow):
            workflow.contains = self.bases.component
        elif inspect.isclass(workflow):
            workflow = workflow(contains = self.bases.component)
        else:
            raise TypeError('workflow must be a Workflow, str, or None.')
        return workflow
    
    def _validate_contents(self, contents: Sequence[Union[
            sourdough.project.Manager, 
            Type[sourdough.project.Manager],
            str]]) -> Sequence[sourdough.project.Manager]:
        """[summary]

        Args:
            contents (Sequence[Union[ sourdough.project.Manager, 
                Type[sourdough.project.Manager], str]]): [description]

        Returns:
            Sequence[sourdough.project.Manager]: [description]
            
        """
        if not contents:
            try:
                contents = self.settings[self.name][f'{self.name}_managers']
            except KeyError:
                pass
        new_contents = []
        for manager in contents:
            new_contents.append(self._validate_manager(manager = manager))
        return new_contents

    def _validate_manager(self, manager: Union[str, object]) -> object:
        """
        """
        if isinstance(manager, str):
            name = copy.deepcopy(manager)
            manager = self.bases.manager.library.borrow(
                name = [manager, 'manager'])
            manager = manager(name = name, project = self)
        elif issubclass(manager, sourdough.project.Manager):
            manager = manager(project = self)
        elif isinstance(manager, self.bases.settings.manager):
            manager.project = self
        else:
            raise TypeError('contents must be a list of str or Manager')
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
