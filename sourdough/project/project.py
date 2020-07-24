"""
project: interface for sourdough projects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Project (OptionsMixin, Plan): iterable which contains the needed
        information and data for constructing and executing tree objects.

"""
import dataclasses
import pathlib
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union
import warnings

import sourdough

 
@dataclasses.dataclass
class Project(sourdough.OptionsMixin, sourdough.Plan):
    """Constructs, organizes, and stores tree Workers and Actions.
    
    A Project inherits all of the differences between a Plan and a python
    list.

    A Project differs from a Plan in 5 significant ways:
        1) The Project is the public interface to composite object construction 
            and application. It may store the composite object instance(s) as 
            well as any required classes (such as those stored in the 'data' 
            attribute). This includes Settings and Filer, stored in the 
            'settings' and 'filer' attributes, respectively.
        2) Project stores Creator subclass instances in 'contents'. Those 
            instances are used to assemble and apply the parts of Plan 
            instances.
        3) Project includes an 'automatic' attribute which can be set to perform
            all of its methods if all of the necessary arguments are passed.
        4) It has an OptionsMixin, which contains a Catalog instance storing
            default Creator instances in 'options'.
        5)
        
    Args:
        contents (Sequence[Union[sourdough.Creator, str]]]): list of 
            Creator subclass instances or strings which correspond to keys in 
            'options'. Defaults to 'default', which will use the 'defaults' 
            attribute of 'options' to select Creator instances.
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
        automatic (bool): whether to automatically advance 'contents' (True) or 
            whether the contents must be changed manually by using the 'advance' 
            or '__iter__' methods (False). Defaults to True.
        structures (ClassVar[sourdough.Catalog]): a class attribute storing
            composite structure options.            
        options (ClassVar[sourdough.Catalog]): a class attribute storing
            components of a composite structure.
    
    Attributes:
        plan (sourdough.Plan): the iterable composite object created by Project.
        index (int): the current index of the iterator in the instance. It is
            set to -1 in the '__post_init__' method.
        stage (str): name of the last stage that has been implemented. It is set
            to 'initialize' in the '__post_init__' method.
        previous_stage (str): name of the previous stage to the last stage that
            has been implemented. It is set by the 'advance' method.
            
    """
    contents: Sequence['sourdough.Creator'] = dataclasses.field(
        default_factory = lambda: [
            sourdough.Author, sourdough.Publisher, sourdough.Reader])
    name: str = None
    settings: Union['sourdough.Settings', str, pathlib.Path] = None
    filer: Union['sourdough.Filer', str, pathlib.Path] = None
    structure: str = dataclasses.field(default_factory = 'chained')
    automatic: bool = True
    structures: ClassVar['sourdough.Catalog'] = sourdough.Catalog(
        contents = {
            'chained': sourdough.structures.Chained, 
            'comparative': sourdough.structures.Comparative,
            'cycle': sourdough.structures.Cycle,
            'directed': sourdough.structures.DirectedGraph,
            'flat': sourdough.structures.Flat})
    options: ClassVar['sourdough.Catalog'] = sourdough.Catalog()    
    
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls inherited initialization method.
        super().__post_init__()
        # Removes various python warnings from console output.
        warnings.filterwarnings('ignore')
        # Validates or creates a 'Settings' instance.
        self.settings = sourdough.Settings(contents = self.settings)
        # Adds 'general' section attributes from 'settings'.
        self.settings.inject(instance = self)
        # Validates or creates a Filer' instance.
        self.filer = sourdough.Filer(
            root_folder = self.filer, 
            settings = self.settings)
        # Initializes or validates a composite Plan instance.
        self.plan = self.structures[self.structure](name = self.name)
        # Initializes Creator instances stored in 'contents'.
        self.contents = self._initialize_creators(contents = self.contents)
        # Sets current 'stage' and 'index' for that 'stage'.
        self.index: int = -1
        self.stage: str = 'initialize' 
        # Advances through 'contents' if 'automatic' is True.
        if self.automatic:
            self.plan = self._auto_contents(plan = self.plan)

    """ Public Methods """

    def validate(self, 
            contents: 'sourdough.Creator') -> Sequence['sourdough.Creator']:
        """Validates that all 'contents' are Creator subclass instances.

        Args:
            contents (sourdough.Creator): list of Creator subclass instances.

        Raises:
            TypeError: if an item in 'contents' is not a Creator subclass 
                instance.
            
        Returns:
            Sequence[sourdough.Creator]: a list with Creator subclass instances.
                  
        """
        if all(issubclass(c, sourdough.Creator) for c in contents):
            return contents
        else:       
            raise TypeError(f'contents must only contain Creator subclasses')
                 
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

    def iterate(self, plan: 'sourdough.Plan') -> 'sourdough.Plan':
        """Advances to next stage and applies that stage to 'plan'.

        Args:
            plan (sourdough.Plan): instance to apply the next stage's methods 
                to.
                
        Raises:
            IndexError: if this instance is already at the last stage.

        Returns:
            sourdough.Plan: with the last stage applied.
            
        """
        if self.index == len(self.contents) - 1:
            raise IndexError(
                f'{self.name} is at the last stage and cannot further iterate')
        else:
            self.advance()
            self.contents[self.index].create(plan = plan)
        return plan
            
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

    def _initialize_creators(self, 
            contents: Sequence['sourdough.Creator']) -> Sequence[
                'sourdough.Creator']:
        """Instances each Creator in 'contents'.
        
        Args:
            contents (Sequence[sourdough.Creator]): list of Creator classes.
        
        Returns:
            Sequence[sourdough.Creator]: list of Creator classes.
        
        """
        new_contents = []
        for creator in contents:
            try:
                new_contents.append(creator(project = self))
            except TypeError:
                if isinstance(creator, sourdough.Creator):
                    new_contents.append(creator)
                else:
                    raise TypeError(f'{creator} is not a Creator type')
        return new_contents   
                     
    def _auto_contents(self, plan: 'sourdough.Plan') -> 'sourdough.Plan':
        """Automatically advances through and iterates stored Creator instances.

        Args:
            plan (sourdough.Plan): an instance containing any data for the plan 
                methods to be applied to.
                
        Returns:
            sourdough.Plan: modified by the stored Creator instance's 
                'create' methods.
            
        """
        for stage in self.contents:
            self.iterate(plan = plan)
        return plan
