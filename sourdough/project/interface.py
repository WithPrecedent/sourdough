"""
interface: user interface for sourdough project construction and iteration
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Bases (object): base classes for a Project.
    Project (Lexicon): access point and interface for creating and implementing 
        a sourdough project.
    Manager (Lexicon): access point and interface for creating and implementing
        multiple sourdough projects.

"""
from __future__ import annotations
import dataclasses
import inspect
import pathlib
from types import ModuleType
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)
import warnings

import sourdough 
  

@dataclasses.dataclass
class Bases(sourdough.quirks.Loader):
    """Base classes for a sourdough project.
    
    Args:
        settings (Type): the configuration class to use in a sourdough project.
            Defaults to sourdough.Settings.
        clerk (Type): the file clerk class to use in a sourdough project.
            Defaults to sourdough.Clerk.   
        creator (Type): the product/builder class to use in a sourdough 
            project. Defaults to sourdough.Creator.    
        product (Type): the product output class to use in a sourdough 
            project. Defaults to sourdough.Product. 
        component (Type): the node class to use in a sourdough project. Defaults 
            to sourdough.Component. 
        workflow (Type): the workflow to use in a sourdough project. Defaults to 
            sourdough.products.Workflow.      
            
    """
    settings: Type = 'sourdough.Settings'
    clerk: Type = 'sourdough.Clerk'
    creator: Type = 'sourdough.Creator'
    product: Type = 'sourdough.Product'
    component: Type = 'sourdough.Component'
    workflow: Type = 'sourdough.products.Workflow'

      
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
            supported file type with settings for a Settings instance is 
            located. Defaults to the default Settings instance.
        clerk (Union[Type, str, pathlib.Path]]): a Clerk-compatible class,
            or a str or pathlib.Path containing the full path of where the root 
            folder should be located for file input and output. A 'clerk'
            must contain all file path and import/export methods for use 
            throughout sourdough. Defaults to the default Clerk instance. 
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
        rules (ClassVar[object]):
        options (ClassVar[object]):
         
    """
    contents: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    settings: Union[object, Type, str, pathlib.Path] = None
    clerk: Union[object, Type, str, pathlib.Path] = None
    manager: Union[object, Type] = None
    creators: Sequence[Union[Type, str]] = dataclasses.field(
        default_factory = lambda: ['architect', 'builder', 'worker'])
    name: str = None
    identification: str = None
    automatic: bool = True
    data: object = None
    bases: ClassVar[object] = Bases()
    rules: ClassVar[object] = sourdough.rules
    options: ClassVar[object] = None
    
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent and/or mixin initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass
        # Sets 'manager' if none was passed.
        self._validate_manager()
        # Converts 'creators' to classes, if necessary.
        self._validate_creators() 
        # Sets index for iteration.
        self.index = 0
        # Advances through 'creators' if 'automatic' is True.
        if self.automatic:
            self._auto_create()

    """ Public Methods """
    
    def advance(self) -> Any:
        """Returns next product created in iterating a Project instance."""
        return self.__next__()

    """ Private Methods """
        
    def _validate_manager(self) -> None:
        """Validates 'manager' or converts it to a Manager instance.
        
        This method is needed when Project or its subclass is used as the 
        primary access point.
        
        """
        if self.manager is None:
            Manager.bases = self.bases
            Manager.rules = self.rules
            Manager.options = self.options
            self.manager = Manager(
                contents = self,
                settings = self.settings,
                clerk = self.clerk,
                name = self.name,
                identification = self.identification,
                automatic = self.automatic,
                data = self.data)
            self.settings = self.manager.settings
            self.clerk = self.manager.clerk
            self.name = self.manager.name,
            self.identification = self.manager.identification
            self.data = self.manager.data
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
            if hasattr(self, 'verbose') and self.manager.verbose:
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


@dataclasses.dataclass
class Manager(sourdough.types.Lexicon):
    """Constructs, organizes, and implements a a collection of projects.

    Args:
        contents (Mapping[str, Union[str, Project]]]): stored Project instances
            or the names of previously created Project instances stored in 
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
            SimpleBases.

    """
    contents: Mapping[str, Project] = dataclasses.field(default_factory = dict)
    settings: Union[object, Type, str, pathlib.Path] = None
    clerk: Union[object, Type, str, pathlib.Path] = None
    name: str = None
    identification: str = None
    automatic: bool = True
    data: Any = None
    _validated: bool = False

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Sets flag so that stored projects to do not unnecessarily validate
        # assorted attributes.
        self._validated = True
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

    """ Public Methods """
    
    def advance(self) -> Any:
        """Returns next product created in iterating a Project instance."""
        return self.__next__()
            
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
            # print('test settings', self.bases.settings)
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

    def _validate_clerk(self) -> None:
        """Validates 'clerk' or converts it to a Clerk instance.
        
        If a file path is passed, that becomes the root folder with the default
        file structure in the default Clerk instance.
        
        If an object is passed, its 'settings' attribute is replaced with the 
        Project instance's 'settings'.
        
        """
        if inspect.isclass(self.clerk):
            self.clerk = self.clerk(settings = self.settings)
        elif (self.clerk is None 
              or isinstance(self.clerk, (str, pathlib.Path))):
            self.clerk = self.bases.clerk(
                root_folder = self.clerk, 
                settings = self.settings)
        else:
            self.clerk.settings = self.settings
        return self

    def _create_project(self, project: str) -> Project:
        """[summary]

        Args:
            project (str): [description]

        Returns:
            Project: [description]
            
        """
        project = sourdough.tools.importify(
            module = self.contents[project],
            key = 'project')
        options = self._get_options(project = project)
        rules = self._get_rules(project = project, options = options)
        return project(
            settings = self.settings,
            clerk = self.clerk,
            identification = self.identification,
            data = self.data,
            system = self.system,
            options = options,
            rulse = rules)
     
    def _get_options(self, project: str) -> sourdough.project.resources.Options:
        """[summary]

        Args:
            project (str): [description]

        Returns:
            sourdough.project.resources.Options: [description]
        """
        options = getattr(self.contents[project], 'options')
        try:
            algorithms = getattr(self.contents[project], 'algorithms')
        except KeyError:
            algorithms = getattr(self.contents[project], 'get_algorithms')(
                settings = self.settings)
        options.algorithms = algorithms
        return options    
    
    def _get_rules(self, project: str, 
                   options: sourdough.project.resources.Options) -> (
                       sourdough.project.resources.Rules):
        """[summary]

        Args:
            project (str): [description]

        Returns:
            sourdough.project.resources.Rules: [description]
        """
        try:
            rules = getattr(self.contents[project], 'rules')
        except KeyError:
            rules = sourdough.rules
        rules.options = options
        return rules
           
    def _validate_data(self) -> None:
        """Validates 'data' or converts it to a Dataset instance."""
        pass
    
    def _auto_create(self) -> None:
        """Advances through the stored Creator instances.
        
        The results of the iteration is that each item produced is stored in 
        'content's with a key of the 'produces' attribute of each project.
        
        """
        for project in iter(self):
            self.contents.update({project.produces: self.__next__()})
        return self
    
    """ Dunder Methods """
    
    def __next__(self) -> Project:
        """Returns completed Project instance.

        Returns:
            Any: item project by the 'create' method of a Creator.
            
        """
        if self.index < len(self.contents):
            project = self.contents[self.index]()
            if hasattr(self, 'verbose') and self.verbose:
                print(
                    f'{project.action} {project.produces} from {project.needs}')
            self.index += 1
            product = project.create(project = self)
        else:
            raise IndexError()
        return product
           