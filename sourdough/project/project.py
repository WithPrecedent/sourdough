"""
project: interface for sourdough projects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Project (OptionsMixin, Hybrid): iterable which contains the needed
        information and data for constructing and executing tree objects.

"""
import dataclasses
import inspect
import itertools
import more_itertools
import pathlib
import textwrap
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union
import warnings

import sourdough



@dataclasses.dataclass
class Overview(sourdough.Lexicon):
    """Dictionary of different Component types in a Worker instance.
    
    Args:
        contents (Mapping[str, Any]]): stored dictionary. Defaults to an empty 
            dict.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Component is called, 'name' is set based upon
            the 'get_name' method in Component. If that method is not 
            overridden by a subclass instance, 'name' will be assigned to the 
            snake case version of the class name ('__class__.__name__').
              
    """
    contents: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    name: str = None
    worker: 'Worker' = None
    
    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent initialization method(s).
        super().__post_init__()
        if self.worker.structure is not None:
            self.contents.add({
                'name': self.worker.name, 
                'structure': self.worker.structure.name})
            for key, value in self.worker.structure.options.items():
                matches = self.worker.find(
                    self._get_type, 
                    component = value)
                if len(matches) > 0:
                    self.contents[f'{key}s'] = matches
        else:
            raise ValueError(
                'structure must be a Structure for an overview to be created.')
        return self          
    
    """ Dunder Methods """
    
    def __str__(self) -> str:
        """Returns pretty string representation of an instance.
        
        Returns:
            str: pretty string representation of an instance.
            
        """
        new_line = '\n'
        representation = [f'sourdough {self._get_name}']
        for key, value in self.contents.items():
            if isinstance(value, Sequence):
                names = [v.name for v in value]
                representation.append(f'{key}: {", ".join(names)}')
            else:
                representation.append(f'{key}: {value}')
        return new_line.join(representation)    

    """ Private Methods """

    def _get_type(self, 
            item: 'sourdough.Component', 
            component: 'sourdough.Component') -> Sequence[
                'sourdough.Component']: 
        """[summary]

        Args:
            item (sourdough.Component): [description]
            sourdough.Component (sourdough.Component): [description]

        Returns:
            Sequence[sourdough.Component]:
            
        """
        if isinstance(item, component):
            return [item]
        else:
            return []
 

@dataclasses.dataclass
class Worker(sourdough.OptionsMixin, sourdough.Hybrid):
    """Iterator in sourdough composite projects.

    Worker inherits all of the differences between a Hybrid and a python list.
    
    A Worker differs from a Hybrid in 3 significant ways:
        1) It has a 'structure' attribute which indicates how the contained 
            iterator should be ordered. 
        2) An 'overview' property is added which returns a dict of the names
            of the various parts of the tree objects. It doesn't include the
            hierarchy itself. Rather, it includes lists of all the types of
            sourdough.Component objects.
        
    Args:
        contents (Sequence[sourdough.Component]]): stored iterable of Action
            subclasses. Defaults to an empty list.
        name (str): creates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Component is called, 'name' is set based upon
            the 'get_name' method in sourdough.Component. If that method is not 
            overridden by a subclass instance, 'name' will be assigned to the 
            snake case version of the class name ('__class__.__name__').
        structure (sourdough.Structure): structure for the organization, iteration,
            and composition of 'contents'.
        _default (Any): default value to use when there is a KeyError using the
            'get' method.

    Attributes:
        contents (Sequence[sourdough.Component]): all objects in 'contents' must 
            be sourdough Component subclass instances and are stored in a list.

    ToDo:
        draw: a method for producting a diagram of a Worker instance's 
            'contents' to the console or a file.
            
    """
    contents: Union[
        'sourdough.Component',
        Mapping[str, 'sourdough.Component'], 
        Sequence['sourdough.Component']] = dataclasses.field(
            default_factory = list)
    name: str = None
    structure: 'sourdough.Structure' = None
    _default: Any = None
    options: ClassVar['sourdough.Catalog'] = sourdough.Catalog()
    structures: ClassVar['sourdough.Catalog'] = sourdough.Catalog()

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent initialization method(s).
        super().__post_init__()
        # Validates or converts 'structure'.
        self.structure = self._validate_structure(structure = self.structure)
            
    """ Properties """
    
    @property
    def overview(self) -> Mapping[str, Sequence[str]]:
        """Returns a dict snapshot of a Worker subclass instance.
        
        Returns:
            Mapping[str, Sequence[str]]: configured according to the 
                '_get_overview' method.
        
        """
        return Overview(worker = self)

    """ Dunder Methods """
    
    def __iter__(self) -> Iterable:
        """Returns iterable of 'contents' based upon 'structure'.
        
        Returns:
            Iterable: of 'contents'.
            
        """
        return self.structure.__iter__()
    
    """ Private Methods """
    
    def _validate_structure(self,
            structure: Union[
                str, 
                'sourdough.Structure']) -> 'sourdough.Structure':
        """Returns a Structure instance based upon 'structure'.

        Args:
            structure (Union[str, sourdough.structures.Structure]): str matching
                a key in 'structures', a Structure subclass, or a Structure
                subclass instance.

        Raises:
            TypeError: if 'structure' is neither a str nor Structure type.

        Returns:
            sourdough.structures.Structure: a Structure subclass instance.
            
        """
        if isinstance(structure, str):
            return self.structures[structure](worker = self)
        elif (inspect.isclass(structure) 
                and issubclass(structure, sourdough.Structure)):
            return structure(worker = self) 
        elif isinstance(structure, sourdough.Structure):
            structure.worker = self
            structure = structure.__post_init__()
            return structure
        else:
            raise TypeError('structure must be a str or Structure type')

 
@dataclasses.dataclass
class Project(Worker):
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
        plan (sourdough.Hybrid): the iterable composite object created by Project.
        index (int): the current index of the iterator in the instance. It is
            set to -1 in the '__post_init__' method.
        stage (str): name of the last stage that has been implemented. It is set
            to 'initialize' in the '__post_init__' method.
        previous_stage (str): name of the previous stage to the last stage that
            has been implemented. It is set by the 'advance' method.
            
    """
    contents: Sequence['sourdough.Action'] = dataclasses.field(
        default_factory = list)
    name: str = None
    settings: Union['sourdough.Settings', str, pathlib.Path] = None
    filer: Union['sourdough.Filer', str, pathlib.Path] = None
    structure: Union['sourdough.Structure', str] = 'creator'
    plan: 'Worker' = Worker
    identification: str = None
    automatic: bool = True
    data: object = None
    _default: Any = None
    options: ClassVar['sourdough.Catalog'] = sourdough.Catalog()
    structures: ClassVar['sourdough.Catalog'] = sourdough.Catalog(
        contents = {
            'creator': sourdough.structures.Creator,
            'cycle': sourdough.structures.Cycle,
            'graph': sourdough.structures.Graph, 
            'progression': sourdough.structures.Progression, 
            'study': sourdough.structures.Study,
            'tree': sourdough.structures.Tree})

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
        # Initializes a composite Hybrid subclass instance.
        self.plan = self.plan(name = self.name, structures = self.structures)
        # Initializes Action instances stored in 'contents'.
        self.contents = self._initialize_contents(contents = self.contents)
        # Sets current 'stage' and 'index' for that 'stage'.
        self.index: int = -1
        self.stage: str = 'initialize' 
        # Advances through 'contents' if 'automatic' is True.
        if self.automatic:
            self.plan = self._auto_contents(plan = self.plan)
        
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
        new_contents = []
        for creator in contents:
            try:
                new_contents.append(creator(project = self))
            except TypeError:
                if isinstance(creator, sourdough.Action):
                    new_contents.append(creator)
                else:
                    raise TypeError(f'{creator} is not a Action type')
        return new_contents   
                     
    def _auto_contents(self, plan: 'sourdough.Hybrid') -> 'sourdough.Hybrid':
        """Automatically advances through and iterates stored Action instances.

        Args:
            plan (sourdough.Hybrid): an instance containing any data for the plan 
                methods to be applied to.
                
        Returns:
            sourdough.Hybrid: modified by the stored Action instance's 
                'perform' methods.
            
        """
        for stage in self.contents:
            plan = self.iterate(plan = plan)
            # print('test plan', plan)
            print('test stage overview', stage.name, plan.overview)
        return plan
