"""
.. module:: manager
:synopsis: sourdough workflow controller
:publisher: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import dataclasses
import pathlib
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union
import warnings

import sourdough
 
 
@dataclasses.dataclass
class Manager(sourdough.base.OptionsMixin, sourdough.base.Progression):
    """Stores and iterates over Creator instances.
    
    A Manager inherits all of the differences between a Progression and a python
    list.

    A Manager differs from a Progression in 5 significant ways:
        1) The Manager is the public interface to Project construction and 
            application. It may store the Project instance itself as well as
            any required classes (such as those stored in the 'data' attribute).
            This includes Settings, Filer, and Options. They are stored in 
            the 'settings', 'filer', and 'options' attributes, 
            respectively.
        2) Manager only stores Creator subclass instances in 'contents'. Those 
            instances are used to assemble the parts of a Project instance.
        3) Manager includes an 'automatic' attribute which can be set to perform
            all of its methods if all of the necessary arguments are passed.
        4) It has an OptionsMixin, which contains a Catalog instance storing
            Default Creator instances which can be used.
        
    Args:
        contents (Sequence[Union[sourdough.base.Creator, str]]]): list of 
            Creator subclass instances or strings which correspond to keys in 
            'options'. Defaults to 'default', which will use the 'defaults' 
            attribute of 'options' to select Creator instances.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough.base. For example if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Component is called, 'name' is set based upon
            the '_get_name' method in Component. If that method is not 
            overridden by a subclass instance, 'name' will be assigned to the 
            snake case version of the class name ('__class__.__name__').
        project (sourdough.project.Project): a Project instance for the Manager. 
            Defaults to None.
        settings (Union[sourdough.base.Settings, str, pathlib.Path]]): 
            an instance of Settings or a str or pathlib.Path containing the 
            file path where a file of a supported file type with settings for a 
            Settings instance is located. Defaults to None.
        filer (Union[sourdough.base.Filer, str, pathlib.Path]]): an instance of 
            Filer or a str or pathlib.Path containing the full path of where the 
            root folder should be located for file input and output. A Filer
            instance contains all file path and import/export methods for use 
            throughout sourdough. Defaults to None.
        automatic (bool): whether to automatically advance 'contents' (True) or 
            whether the contents must be changed manually by using the 'advance' 
            or '__iter__' methods (False). Defaults to True.
        options (ClassVar[sourdough.base.Catalog]): a class attribute storing
            default Creator classes which can be used in project construction
            and application. 
    
    Attributes:
        index (int): the current index of the iterator in the instance. It is
            set to -1 in the '__post_init__' method.
        stage (str): name of the last stage that has been implemented. It is set
            to 'initialize' in the '__post_init__' method.
        previous_stage (str): name of the previous stage to the last stage that
            has been implemented. It is set by the 'advance' method.
            
    """
    contents: Sequence[Union[
        'sourdough.base.Creator', 
        str]] = dataclasses.field(default_factory = lambda: 'default')
    name: str = None
    project: 'sourdough.project.Project' = None
    settings: Union[
        'sourdough.base.Settings', 
        str, 
        pathlib.Path] = None
    filer: Union['sourdough.base.Filer', str, pathlib.Path] = None
    automatic: bool = True
    options: ClassVar['sourdough.base.Catalog'] = sourdough.base.Catalog(
        contents = {
            'draft': sourdough.base.Author,
            'publish': sourdough.base.Publisher,
            'apply': sourdough.base.Worker},
        defaults = ['draft', 'publish', 'apply'])
    
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls inherited initialization method.
        super().__post_init__()
        # Removes various python warnings from console output.
        warnings.filterwarnings('ignore')
        # Validates or creates a 'Settings' instance.
        self.settings = sourdough.base.Settings(
            contents = self.settings)
        # Validates or creates a Filer' instance.
        self.filer = sourdough.base.Filer(
            root_folder = self.filer, 
            settings = self.settings)
        # Adds 'general' section attributes from 'settings'.
        self.settings.inject(instance = self)
        # Initializes or validates a Project instance.
        self.project = self._initialize_project(
            project = self.project,
            settings = self.settings)
        # Sets current 'stage' and 'index' for that 'stage'.
        self.index: int = -1
        self.stage: str = 'initialize' 
        # Advances through 'contents' if 'automatic' is True.
        if self.automatic:
            self.project = self._auto_contents(project = self.project)

    """ Public Methods """

    def validate(self, 
            contents: Sequence[Union['sourdough.base.Creator', str]],
            **kwargs) -> Sequence['sourdough.base.Creator']:
        """Creates Creator instances, when necessary, in 'contents'

        Args:
            contents (Sequence[Union[sourdough.base.Creator, str]]]): list of 
                Creator subclass instances or strings which correspond to keys 
                in 'options'. 
            kwargs: any extra arguments to send to each created Creator 
                instance. These will have no effect on Creator subclass 
                instances already stored in the 'options' class attribute.

        Raises:
            KeyError: if 'contents' contains a string which does not match a key 
                in the 'options' class attribute.
            TypeError: if an item in 'contents' is neither a str nor Creator 
                subclass.
            
        Returns:
            Sequence[sourdough.base.Creator]: a list with only Creator subclass 
                instances.
                  
        """       
        new_contents = []
        for stage in contents:
            if isinstance(stage, str):
                try:
                    new_contents.append(self.options[stage](**kwargs))
                except KeyError:
                    KeyError(f'{stage} is not a recognized stage')
            elif isinstance(stage, sourdough.base.Creator):
                new_contents.append(stage)
            elif issubclass(stage, sourdough.base.Creator):
                new_contents.append(stage(**kwargs))
            else:
                raise TypeError(f'{stage} must be a str or Creator type')
        return new_contents
                 
    def advance(self, stage: str = None) -> None:
        """Advances to next item in 'contents' or to 'stage' argument.

        This method only needs to be called manually if 'automatic' is False.
        Otherwise, this method is automatically called when the class is 
        instanced.

        Args:
            stage (str): name of item in 'contents'. Defaults to None. 
                If not passed, the method goes to the next item in contents.

        Raises:
            ValueError: if 'stage' is neither None nor in 'contents'.
            IndexError: if 'advance' is called at the last stage in 'contents'.

        """
        if stage is None:
            try:
                new_stage = self.contents[self.index + 1]
            except IndexError:
                raise IndexError(f'{self.name} cannot advance further')
        else:
            try:
                new_stage = self.contents[stage]
            except KeyError:
                raise ValueError(f'{stage} is not a recognized stage')
        self.index += 1
        self.previous_stage: str = self.stage
        self.stage = new_stage
        return self

    def iterate(self, 
            project: 'sourdough.project.Project') -> (
                'sourdough.project.Project'):
        """Advances to next stage and applies that stage to 'project'.

        Args:
            project (sourdough.project.Project): instance to apply the next 
                stage's methods to.
                
        Raises:
            IndexError: if this instance is already at the last stage.

        Returns:
            sourdough.project.Project: with the last stage applied.
            
        """
        if self.index == len(self.contents) - 1:
            raise IndexError(
                f'{self.name} is at the last stage and cannot further iterate')
        else:
            self.advance()
            self.contents[self.index].create(project = project)
        return project
            
    """ Dunder Methods """
    
    def __iter__(self) -> Iterable:
        """Returns iterable of methods of 'contents'.
        
        Returns:
            Iterable: 'create' methods of 'contents'.
            
        """
        return iter([getattr(s, 'create') for s in self.contents])

    def __next__(self) -> Callable:
        """Returns next method after method matching 'item'.
        
        Returns:
            Callable: next method corresponding to those listed in 'options'.
            
        """
        if self.index < len(self.contents):
            self.advance()
            return getattr(self.contents[self.index], 'create')
        else:
            raise StopIteration()
     
    """ Private Methods """
                        
    def _auto_contents(self, 
            project: 'sourdough.project.Project') -> (
                'sourdough.project.Project'):
        """Automatically advances through and iterates stored Creator instances.

        Args:
            project (sourdough.project.Project): an instance containing any data 
                for the project methods to be applied to.
                
        Returns:
            sourdough.project.Project: modified by the stored Creator instance's 
                'create' methods.
            
        """
        for stage in self.contents:
            self.iterate(project = project)
        return project
