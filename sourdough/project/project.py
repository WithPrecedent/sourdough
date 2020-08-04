"""
manager: interface for sourdough project construction and iteration
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Project (Hybrid): creates a project using stored Action subclass instances.

"""

import abc
import dataclasses
import pathlib
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union
import warnings

import sourdough


@dataclasses.dataclass
class ComponentsMixin(sourdough.Action, abc.ABC):
    """Mixin which stores subclasses in a 'components' class attribute.

    Args:
        components (ClassVar[sourdough.Inventory]): the instance which stores 
            subclass in a Inventory instance.

    Namespaces: 'components', 'register_from_disk', 'build', 
        'find_subclasses', '_import_from_path', '_get_subclasse'
    
    """
    components: ClassVar['sourdough.Inventory'] = sourdough.Inventory()
    
    """ Initialization Methods """
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Adds new subclass to 'components'.
        if not hasattr(super(), 'components') and issubclass(sourdough.Action):
            cls.components[cls.get_name()] = cls
                
    """ Public Methods """
    
    def build(self, key: Union[str, Sequence[str]], **kwargs) -> Any:
        """Creates instance(s) of a class(es) stored in 'components'.

        Args:
            key (str): name matching a key in 'components' for which the value
                is sought.

        Raises:
            TypeError: if 'key' is neither a str nor Sequence type.
            
        Returns:
            Any: instance(s) of a stored class(es) with kwargs passed as 
                arguments.
            
        """
        if isinstance(key, str):
            return self.components.create(key = key, **kwargs)
        elif isinstance(key, Sequence):
            instances = []
            for item in key:
                instances.append(self.components.create(name = item, **kwargs))
            return instances
        else:
            raise TypeError('key must be a str or list type')    
 
 
@dataclasses.dataclass
class Project(sourdough.OptionsMixin, sourdough.Worker):
    """Constructs, organizes, and stores tree Workers and Actions.
    
    A Manager inherits all of the differences between a Hybrid and a python
    list.

    A Manager differs from a Hybrid in 5 significant ways:
        1) The Manager is the public interface to composite object construction 
            and application. It may store the composite object instance(s) as 
            well as any required classes (such as those stored in the 'data' 
            attribute). This includes Settings and Filer, stored in the 
            'settings' and 'filer' attributes, respectively.
        2) Manager stores Action subclass instances in 'contents'. Those 
            instances are used to assemble and apply the parts of Hybrid 
            instances.
        3) Manager includes an 'automatic' attribute which can be set to perform
            all of its methods if all of the necessary arguments are passed.
        4) It has an OptionsMixin, which contains a Catalog instance storing
            default Action instances in 'options'.
        5)
        
    Args:
        contents (Sequence[Union[sourdough.Action, str]]]): list of 
            Action subclass instances or strings which correspond to keys in 
            'options'. Defaults to 'default', which will use the 'defaults' 
            attribute of 'options' to select Action instances.
        name (str): roleates the name of a class instance that is used for 
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
        role (str): type of role for the project's composite object.
            Defaults to 'tree'.
        identification (str): a unique identification name for a 
            Project instance. The name is used for creating file folders
            related to the 'Project'. If not provided, a string is created from
            'name' and the date and time. This is a notable difference
            between an ordinary Worker instancce and a Project instance. Other
            Workers are not given unique identification. Defaults to None.   
        automatic (bool): whether to automatically advance 'contents' (True) or 
            whether the contents must be changed manually by using the 'advance' 
            or '__iter__' methods (False). Defaults to True.
        roles (ClassVar[sourdough.Catalog]): a class attribute storing
            composite role options.            
        options (ClassVar[sourdough.Catalog]): a class attribute storing
            components of a composite role.
    
    Attributes:
        manager (sourdough.Worker): the iterable composite object created by
            Project.
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
    role: Union['sourdough.Role', str] = 'creator'
    name: str = None
    identification: str = None
    automatic: bool = True
    data: object = None
    manager: 'sourdough.Worker' = sourdough.Manager
    components: ClassVar['sourdough.Inventory'] = sourdough.Inventory()

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
        # Initializes project manager.
        self._initialize_manager()
        # Initializes Action instances stored in 'contents'.
        self.contents = self._initialize_contents(contents = self.contents)
        # Advances through 'contents' if 'automatic' is True.
        if self.automatic:
            self.manager = self._auto_contents(manager = self.manager)
        
    """ Private Methods """

    def _set_identification(self) -> None:
        """Sets unique 'identification' str based upon date and time."""
        return sourdough.utilities.datetime_string(prefix = self.name)
    
    def _initialize_manager(self) -> None:
        """Initializes a Manager instance for the 'manager' attribute."""
        try:
            self.manager = self.manager(
                name = self.name,
                identification = self.identification)
        except TypeError:
            if not isinstance(self.manager, sourdough.Manager):
                raise TypeError('manager must be a Manager type')
        return self
    
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
            contents = self.role.options['default']
        new_contents = []
        for creator in contents:
            new_contents.append(creator(manager = self))
        return new_contents   
                     
    def _auto_contents(self, manager: 'sourdough.Worker') -> 'sourdough.Worker':
        """Automatically advances through and iterates stored Action instances.

        Args:
            manager (sourdough.Worker): an instance containing any data for the 
                worker methods to be applied to.
                
        Returns:
            sourdough.Worker: modified by the stored Action instance's 'perform' 
                methods.
            
        """
        for stage in self:
            if hasattr(self, 'verbose') and self.verbose:
                print(f'Beginning {stage.name} process')
            manager = stage.perform(worker = manager)
            print('test manager', manager.contents)
            # print('test stage overview', manager.overview)
        return manager
    