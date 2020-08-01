"""
manager: interface for sourdough project construction and iteration
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Manager (Hybrid): creates a project using stored Action subclass instances.

"""

import dataclasses
import pathlib
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union
import warnings

import sourdough


@dataclasses.dataclass
class Manager(sourdough.OptionsMixin, sourdough.Worker):
    """Constructs, organizes, and stores tree Workers and Actions.
    
    A Project inherits all of the differences between a Hybrid and a python
    list.

    A Project differs from a Hybrid in 5 significant ways:
        1) The Project is the public interface to composite object construction 
            and application. It may store the composite object instance(s) as 
            well as any required classes (such as those stored in the 'data' 
            attribute). This includes Settings and Filer, stored in the 
            'settings' and 'filer' attributes, respectively.
        2) Project stores Action subclass instances in 'contents'. Those 
            instances are used to assemble and apply the parts of Hybrid 
            instances.
        3) Project includes an 'automatic' attribute which can be set to perform
            all of its methods if all of the necessary arguments are passed.
        4) It has an OptionsMixin, which contains a Catalog instance storing
            default Action instances in 'options'.
        5)
        
    Args:
        contents (Sequence[Union[sourdough.Action, str]]]): list of 
            Action subclass instances or strings which correspond to keys in 
            'options'. Defaults to 'default', which will use the 'defaults' 
            attribute of 'options' to select Action instances.
        name (str): structureates the name of a class instance that is used for 
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
        settings (Union[sourdough.Settings, str, pathlib.Path]]): 
            an instance of Settings or a str or pathlib.Path containing the 
            file path where a file of a supported file type with settings for a 
            Settings instance is located. Defaults to None.
        filer (Union[sourdough.Filer, str, pathlib.Path]]): an instance of 
            Filer or a str or pathlib.Path containing the full path of where the 
            root folder should be located for file input and output. A Filer
            instance contains all file path and import/export methods for use 
            throughout sourdough. Defaults to None.
        structure (str): type of structure for the project's composite object.
            Defaults to 'tree'.
        identification (str): a unique identification name for a 
            Manager instance. The name is used for creating file folders
            related to the 'Manager'. If not provided, a string is created from
            'name' and the date and time. This is a notable difference
            between an ordinary Worker instancce and a Manager instance. Other
            Workers are not given unique identification. Defaults to None.   
        automatic (bool): whether to automatically advance 'contents' (True) or 
            whether the contents must be changed manually by using the 'advance' 
            or '__iter__' methods (False). Defaults to True.
        structures (ClassVar[sourdough.Catalog]): a class attribute storing
            composite structure options.            
        options (ClassVar[sourdough.Catalog]): a class attribute storing
            components of a composite structure.
    
    Attributes:
        project (sourdough.Worker): the iterable composite object created by
            Manager.
        index (int): the current index of the iterator in the instance. It is
            set to -1 in the '__post_init__' method.
        stage (str): name of the last stage that has been implemented. It is set
            to 'initialize' in the '__post_init__' method.
        previous_stage (str): name of the previous stage to the last stage that
            has been implemented. It is set by the 'advance' method.
            
    """
    contents: Sequence['sourdough.Action'] = dataclasses.field(
        default_factory = list)
    settings: Union['sourdough.Settings', str, pathlib.Path] = None
    filer: Union['sourdough.Filer', str, pathlib.Path] = None
    structure: Union['sourdough.Structure', str] = 'creator'
    name: str = None
    identification: str = None
    automatic: bool = True
    data: object = None
    project: 'sourdough.Worker' = sourdough.Worker
    _default: Any = None
    options: ClassVar['sourdough.Inventory'] = sourdough.Inventory(
        contents = {
            'creator': sourdough.Creator,
            'cycle': sourdough.Cycle,
            'graph': sourdough.Graph, 
            'progression': sourdough.Progression, 
            'study': sourdough.Study,
            'tree': sourdough.Tree})

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent initialization method(s).
        super().__post_init__()
        # Removes various python warnings from console output.
        warnings.filterwarnings('ignore')
        # Sets unique project 'identification', if not passed.
        self.identification = self.identification or self._set_identification()
        # Validates or creates a 'Settings' instance.
        self.settings = sourdough.Settings(contents = self.settings)
        # Adds 'general' section attributes from 'settings'.
        self.settings.inject(instance = self)
        # Validates or creates a Filer' instance.
        self.filer = sourdough.Filer(
            root_folder = self.filer, 
            settings = self.settings)
        # Initializes a composite object subclass instance.
        self.project.options = self.options
        self.project = self.project(name = self.name)
        # Initializes Action instances stored in 'contents'.
        self.contents = self._initialize_contents(contents = self.contents)
        # Advances through 'contents' if 'automatic' is True.
        if self.automatic:
            self.project = self._auto_contents(project = self.project)
        
    """ Private Methods """

    def _set_identification(self) -> None:
        """Sets unique 'identification' str based upon date and time."""
        return sourdough.utilities.datetime_string(prefix = self.name)
    
    def _initialize_contents(self, 
            contents: Sequence['sourdough.Action']) -> Sequence[
                'sourdough.Action']:
        """Instances each Action in 'contents'.
        
        Args:
            contents (Sequence[sourdough.Action]): list of Action classes.
        
        Returns:
            Sequence[sourdough.Action]: list of Action classes.
        
        """
        if not contents:
            contents = self.structure.options['default']
        new_contents = []
        for creator in contents:
            new_contents.append(creator(manager = self))
        return new_contents   
                     
    def _auto_contents(self, project: 'sourdough.Worker') -> 'sourdough.Worker':
        """Automatically advances through and iterates stored Action instances.

        Args:
            project (sourdough.Worker): an instance containing any data for the 
                worker methods to be applied to.
                
        Returns:
            sourdough.Worker: modified by the stored Action instance's 'perform' 
                methods.
            
        """
        for stage in self:
            if hasattr(self, 'verbose') and self.verbose:
                print(f'Beginning {stage.name} process')
            project = stage.perform(worker = project)
            print('test project', project.contents)
            # print('test stage overview', project.overview)
        return project
    