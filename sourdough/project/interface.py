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
from typing import (
    Any, Callable, ClassVar, Dict, Iterable, List, Mapping, Sequence, Union)
import warnings

import sourdough


@dataclasses.dataclass
class Workshop(sourdough.base.Factory):

    name: str
    selections: Mapping[str, str]
    bases: ClassVar[
        sourdough.base.Catalog[str, Callable]] = sourdough.base.Catalog(
            contents = {
                'workflow': sourdough.Workflow,
                'components': sourdough.Component})
    quirks: ClassVar[
        sourdough.base.Catalog[str, Callable]] = sourdough.base.Catalog(
            contents = {
                'validator': sourdough.quirks.Validator,
                'registry': sourdough.quirks.Registry})
        
    def __new__(cls, name: str, selections: Mapping[str, str], **kwargs) -> Any:
        """
        """
        bases = tuple(cls.bases[k].select(v) for k, v in selections.items())
        quirks = tuple(cls.quirks[k].select(v) for k, v in selections.items())
        product = type(name = name, bases = bases)
        for quirk in quirks:
            product = quirk.inject(item = product)
        return product
            
        
@dataclasses.dataclass
class Project(sourdough.base.Element, collections.abc.Iterable):
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
        registered ()
    
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
        # Validates various attributes or converts them to the proper type.
        for attribute in self.registered.keys():
            getattr(self, f'_validate_{attribute}')()
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
                        'verbose': True,
                        'early_validation': True,
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

    def _validate_workflow(self) -> None:
        """Validates 'workflow' or converts it to a list of Workflow subclasses.
        """
        if (inspect.isclass(self.workflow) 
                and (issubclass(self.workflow, self.registered['workflow'])
                     or self.workflow == self.registered['workflow'])):
            self.workflow = self.workflow()
        elif isinstance(self.workflow, str):
            self.workflow = self.registered['workflow'].instance(
                key = self.workflow)
        else:
            raise TypeError(
                f'workflow must be a str matching a key in '
                f'{self.registered["workflow"]}.library or a '
                f'{self.registered["workflow"]} subclass')
        return self

    def _validate_design(self) -> None:
        """Validates 'design' as a Component or its subclass."""
        if (inspect.isclass(self.design) 
                and (issubclass(self.design, self.registered['design'])
                     or self.design == self.registered['design'])):
            self.design = self.design()
        elif isinstance(self.design, str):
            self.design = self.registered['design'].instance(
                key = self.design)
        else:
            raise TypeError(
                f'design must be a str matching a key in '
                f'{self.registered["design"]}.library or a '
                f'{self.registered["design"]} subclass')
        return self    
                     
    def _auto_workflow(self) -> None:
        """Advances through the stored Workflow instances.

        Args:
                
        Returns:
            
        """
        for stage in self.workflow:
            print('test stage', stage)
            if hasattr(self, 'verbose') and self.verbose:
                print(f'Beginning {stage.name} process')
            self = stage.perform(project = self)
        return self
