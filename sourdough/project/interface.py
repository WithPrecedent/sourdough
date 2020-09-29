"""
project: interface for sourdough project construction and iteration
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Project (Hybrid): interface for sourdough projects.

"""
from __future__ import annotations
import abc
import collections.abc
import dataclasses
import inspect
import pathlib
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Union)
import warnings

import sourdough


@dataclasses.dataclass
class Workshop(sourdough.Catalog):

    contents: Mapping[str, Callable] = dataclasses.field(default_factory = dict)
    project: Project = None

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass
        # Checks to see if 'project' exists.
        if self.project is None:
            raise ValueError(
                f'{self.__class__.__name__} requires a Project instance')
        # Creates base classes with selected Quirk mixins.
        self.create_bases()
        # Point the 'bases' of Project to 'contents' attribute.
        Project.bases = self.contents
    
    """ Public Methods """
    
    def create_bases(self) -> None:
        """[summary]

        Returns:
            [type]: [description]
        """
        quirks = self._get_settings_quirks()
        for key, value in self.project.bases.items():
            self.contents[key] = self.create_class(
                name = key, 
                base = value, 
                quirks = quirks)
        return self
            
    def create_class(self, name: str, base: Callable, 
                     quirks: Sequence[sourdough.Quirk]) -> Callable:
        """[summary]

        Args:
            name (str): [description]
            base (Callable): [description]
            quirks (Sequence[sourdough.Quirk])

        Returns:
            Callable: [description]
            
        """
        if quirks:
            bases = quirks.append(base)
            new_base = dataclasses.dataclass(type(name, tuple(bases), {}))
            # Recursively adds quirks to items in the 'registry' of 'base'.
            if hasattr(base, 'registry'):
                new_registry = {}
                for key, value in base.registry.items():
                    new_registry[key] = self.create_class(
                        name = key,
                        base = value,
                        quirks = quirks)
                new_base.registry = new_registry
        else:
            new_base = base
        return new_base
             
    """ Private Methods """
    
    def _get_settings_quirks(self) -> Sequence[sourdough.Quirk]:
        """[summary]

        Returns:
            Sequence[sourdough.Quirk]: [description]
            
        """
        settings_keys = {
            'verbose': 'talker', 
            'early_validation': 'validator', 
            'conserve_memory': 'conserver'}
        quirks = []
        for key, value in settings_keys.items():
            try:
                if self.project.settings['general'][key]:
                    quirks.append(sourdough.Quirk.options[value])
            except KeyError:
                pass
        return quirks

 
# @dataclasses.dataclass
# class Overview(sourdough.Lexicon):
#     """Dictionary of different Element types in a Structure instance.
    
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
#         # Calls parent initialization method(s).
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

            
@dataclasses.dataclass
class Project(sourdough.Component):
    """Constructs, organizes, and implements a sourdough project.
        
    Args:
        settings (Union[sourdough.Settings, str, pathlib.Path]]): 
            an instance of Settings or a str or pathlib.Path containing the 
            file path where a file of a supported file type with settings for a 
            Settings instance is located. Defaults to None.
        filer (Union[sourdough.Filer, str, pathlib.Path]]): an instance of 
            Filer or a str or pathlib.Path containing the full path of where the 
            root folder should be located for file input and output. A Filer
            instance contains all file path and import/export methods for use 
            throughout sourdough. Defaults to None.
        workflow (Union[sourdough.Workflow, Sequence[Union[sourdough.Workflow, 
            str]]]): base Workflow class, a list of Workflow subclasses, or 
            a list of str corresponding to Workflow subclasses in 
            Workflow.library. These classes are used for the construction and
            application of a sourdough project. Defaults to sourdough.Workflow
            which will use the default subclasses of Draft, Publish, Apply.
        design (sourdough.Component): base class for the pieces of the 
            project's composite object. Defaults to sourdough.Component.
            Component.library will automatically contain all imported 
            subclasses and those will be the only permitted pieces of a 
            sourdough composite object. One imported component must be Manager
            or a subclass.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Component is called, 'name' is set based upon
            the '_get_name' method in Component. If that method is not 
            overridden by a subclass instance, 'name' will be assigned to the 
            snake case version of the class name ('__class__.__name__').
        identification (str): a unique identification name for a 
            Project instance. The name is used for creating file folders
            related to the 'Project'. If not provided, a string is created from
            'name' and the date and time. This is a notable difference
            between an ordinary Structure instancce and a Project instance. Other
            Structures are not given unique identification. Defaults to None.   
        automatic (bool): whether to automatically advance 'workflow' (True) or 
            whether the workflow must be changed manually by using the 'advance' 
            or '__iter__' methods (False). Defaults to True.
        data (object): any data object for the project to be applied.         
        bases ()
    
    Attributes:
        design (sourdough.Structure): the iterable composite object created by
            Project.
        index (int): the current index of the iterator in the instance. It is
            set to -1 in the '__post_init__' method.
        stage (str): name of the last stage that has been implemented. It is set
            to 'initialize' in the '__post_init__' method.
        previous_stage (str): name of the previous stage to the last stage that
            has been implemented. It is set by the 'advance' method.
            
    """
    settings: Union[sourdough.Settings, str, pathlib.Path] = None
    filer: Union[sourdough.Filer, str, pathlib.Path] = None
    workflow: Union[str, sourdough.Workflow] = 'editor'
    design: Union[str, sourdough.Structure] = 'pipeline'
    name: str = None
    identification: str = None
    automatic: bool = True
    data: object = None
    results: Mapping[str, object] = dataclasses.field(default_factory = dict)
    bases: ClassVar[Mapping[str, Callable]] = sourdough.Catalog(
        contents = {
            'design': sourdough.Structure,
            'stage': sourdough.Stage,
            'workflow': sourdough.Workflow,
            'step': sourdough.components.Step,
            'technique': sourdough.components.Technique,
            'component': sourdough.Component})

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass
        # Removes various python warnings from console output.
        warnings.filterwarnings('ignore')
        # Sets unique project 'identification', if not passed.
        self.identification = self._get_identification()
        # Validates or converts 'settings' and 'filer'.
        self._validate_settings()
        self._validate_filer()
        # Creates instances of the Workshop class builder.
        self.workshop = Workshop(project = self)
        # Initializes 'workflow' instance.
        self._initialize_workflow()
        # Advances through 'workflow' if 'automatic' is True.
        if self.automatic:
            self._auto_workflow()

    """ Public Methods """
    
    def advance(self, stage: str = None) -> None:
        """Advances to next item in 'workflow' or to 'stage' argument.
        
        This method only needs to be called manually if 'automatic' is False.
        Otherwise, this method is automatically called when the class is 
        instanced.
        
        Args:
            stage (str): name of item in 'workflow'. Defaults to None. 
                If not passed, the method goes to the next item in workflow.
                
        Raises:
            ValueError: if 'stage' is neither None nor in 'workflow'.
            IndexError: if 'advance' is called at the last stage in 'workflow'.
            
        """
        if stage is None:
            try:
                new_stage = self.workflow[self.index + 1]
            except IndexError:
                raise IndexError(f'{self.name} cannot advance further')
        else:
            try:
                new_stage = self.workflow[stage]
            except KeyError:
                raise ValueError(f'{stage} is not a recognized stage')
        self.index += 1
        self.previous_stage: str = self.stage
        self.stage = new_stage
        return self

    def iterate(self, 
            manager: 'sourdough.Manager') -> (
                'sourdough.Manager'):
        """Advances to next stage and applies that stage to 'manager'.
        Args:
            manager (sourdough.Manager): instance to apply the next 
                stage's methods to.
                
        Raises:
            IndexError: if this instance is already at the last stage.
        Returns:
            sourdough.Manager: with the last stage applied.
            
        """
        if self.index == len(self.workflow) - 1:
            raise IndexError(
                f'{self.name} is at the last stage and cannot further iterate')
        else:
            self.advance()
            self.workflow[self.index].create(manager = manager)
        return manager
            
    """ Dunder Methods """
    
    def __iter__(self) -> Iterable:
        """Returns iterable of methods of 'workflow'.
        
        Returns:
            Iterable: 'create' methods of 'workflow'.
            
        """
        return iter([getattr(s, 'create') for s in self.workflow])

    def __next__(self) -> Callable:
        """Returns next method after method matching 'item'.
        
        Returns:
            Callable: next method corresponding to those listed in 'options'.
            
        """
        if self.index < len(self.workflow):
            self.advance()
            return getattr(self.workflow[self.index], 'create')
        else:
            raise StopIteration()

    """ Private Methods """

    def _get_identification(self) -> None:
        """Sets unique 'identification' str based upon date and time."""
        if self.identification is None:
            return sourdough.tools.datetime_string(prefix = self.name)
    
    def _validate_settings(self) -> None:
        """Validates 'settings' or converts it to a Settings instance."""
        if not isinstance(self.settings, sourdough.Settings):
            self.settings = sourdough.Settings(
                contents = self.settings,
                defaults = {
                    'general': {
                        'verbose': False,
                        'early_validation': False,
                        'conserve_memery': False},
                    'files': {
                        'source_format': 'csv',
                        'interim_format': 'csv',
                        'final_format': 'csv',
                        'file_encoding': 'windows-1252'}})
        # Adds 'general' section attributes from 'settings'.
        self.settings.inject(instance = self)
        return self

    def _validate_filer(self) -> None:
        """Validates 'filer' or converts it to a Filer instance."""
        if not isinstance(self.filer, sourdough.Filer):
            self.filer = sourdough.Filer(
                root_folder = self.filer, 
                settings = self.settings)
        return self

    def _initialize_workflow(self) -> None:
        """Validates or converts 'workflow' and initializes it."""
        if 'workflow' not in self.bases:
            self.__class__.bases['workflow'] = self.workshop.create_class(
                name = 'workflow',
                base = sourdough.Workflow,
                quirks = self.workshop._get_settings_quirks())
        if (inspect.isclass(self.workflow) 
                and (issubclass(self.workflow, self.bases['workflow'])
                     or self.workflow == self.bases['workflow'])):
            self.workflow = self.workflow()
        elif isinstance(self.workflow, str):
            self.workflow = self.bases['workflow'].instance(
                key = self.workflow)
        else:
            raise TypeError(
                f'workflow must be a str matching a key in '
                f'{self.bases["workflow"]}.library or a '
                f'{self.bases["workflow"]} subclass')
        return self

    # def _initialize_design(self) -> None:
    #     """Validates or converts 'design' and initializes it."""
    #     if 'design' not in self.bases:
    #         self.__class__.bases['design'] = self.workshop.create_class(
    #             name = 'design',
    #             base = sourdough.Structure,
    #             quirks = self.workshop._get_settings_quirks())
    #     if (inspect.isclass(self.design) 
    #             and (issubclass(self.design, self.bases['design'])
    #                  or self.design == self.bases['design'])):
    #         self.design = self.design()
    #     elif isinstance(self.design, str):
    #         self.design = self.bases['design'].instance(
    #             key = self.design)
    #     else:
    #         raise TypeError(
    #             f'design must be a str matching a key in '
    #             f'{self.bases["design"]}.library or a '
    #             f'{self.bases["design"]} subclass')
    #     return self    
                     
    def _auto_workflow(self) -> None:
        """Advances through the stored Workflow instances."""
        for stage in self.workflow:
            print('test stage', stage)
            if hasattr(self, 'verbose') and self.verbose:
                print(f'Beginning {stage.name} process')
            self = stage.perform(project = self)
        return self
