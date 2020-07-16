"""
.. module:: manager
:synopsis: sourdough workflow controller
:publisher: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import dataclasses
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
        2) All sourdough configuration class instances are stored and maintained
            here. This includes Configuration, Filer, and Options. They are
            stored in the 'configuration', 'filer', and 'options' attributes,
            respectively.
        3) Manager only stores Creator subclass instances in 'contents'. Those 
            instances are used to assemble the parts of a Project instance.
        4) Manager includes an 'automatic' attribute which can be set to perform
            all of its methods if all of the necessary arguments are passed.
        5) It has an OptionsMixin, which contains a Catalog instance used to 
            store various runtime strategies and options to use. These can 
            either be chosen in the attached Configuration instance, by you
            during execution, or both.
        
    Args:
        contents (Sequence[Union[sourdough.base.Creator, str]]]): list of Creator 
            subclass instances or strings which correspond to keys in 'options'. 
            Defaults to 'default', which will use the 'defaults' attribute of 
            'options' to select Creator instances.
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
        project (Union['sourdough.project'], str]): a Project instance
            or strings which correspond to keys in 'project_options'. Defaults 
            to 'default', which will use the 'defaults' attribute of 
            'project_options' to select a Project instance.
        configuration (Union[sourdough.base.Configuration, str]]): an instance of 
            Configuration or a string containing the file path where a file of a 
            supported file type with settings for an Configuration instance is 
            located. Defaults to None.
        filer (Union[sourdough.base.Filer, str]]): an instance of Filer or a 
            string containing the full path of where the root folder should be 
            located for file input and output. A Filer instance contains all 
            file path and import/export methods for use throughout sourdough.base. 
            Defaults to None.
        automatic (bool]): whether to automatically advance 'contents'
            (True) or whether the stages must be changed manually by using the 
            'advance' or '__iter__' methods (False). Defaults to True.
            
    """
    contents: Sequence[Union[
        'sourdough.base.Creator', 
        str]] = dataclasses.field(default_factory = lambda: 'default')
    name: str = None
    project: Union['sourdough.project', str] = dataclasses.field(
        default_factory = lambda: 'default')
    configuration: Union['sourdough.base.Configuration', str] = None
    filer: Union['sourdough.base.Filer', str] = None
    automatic: bool = True
    options: ClassVar['sourdough.base.Catalog'] = sourdough.base.Catalog(
        contents = {
            'draft': sourdough.base.Author,
            'publish': sourdough.base.Publisher,
            'apply': sourdough.base.Reader},
        defaults = ['draft', 'publish', 'apply'])
    
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls inherited initialization method.
        super().__post_init__()
        # Removes various python warnings from console output.
        warnings.filterwarnings('ignore')
        # Validates or creates a 'Configuration' instance.
        self.configuration = sourdough.base.Configuration(
            contents = self.configuration)
        # Validates or creates a Filer' instance.
        self.filer = sourdough.base.Filer(
            root_folder = self.filer, 
            configuration = self.configuration)
        # Adds 'general' section attributes from 'configuration'.
        self.configuration.inject(instance = self)
        # Initializes or validates a Project instance.
        self.project = self._initialize_project(
            project = self.project,
            configuration = self.configuration)
        # Sets current 'stage' and 'index' for that 'stage'.
        self.index = -1
        self.stage = 'initialize' 
        # Advances through 'contents' if 'automatic' is True.
        if self.automatic:
            self.project = self._auto_contents(project = self.project)

    """ Public Methods """

    def validate(self, 
            stages: Sequence[Union[str, 'sourdough.base.Creator']],
            **kwargs) -> Sequence['sourdough.base.Creator']:
        """Creates Creator instances, when necessary, in 'contents'

        Args:
            stages (Sequence[Union[str, sourdough.base.Creator]]): a list of strings 
                corresponding to keys in the 'options' class attribute or 
                Creator subclass instances.
            kwargs: any extra arguments to send to each created Creator instance.
                These will have no effect on Creator subclass instances already 
                stored in the 'options' class attribute.

        Raises:
            KeyError: if 'stages' contains a string which does not match a key 
                in the 'options' class attribute.
            TypeError: if an item in 'stages' is neither a str nor Creator 
                subclass.
            
        Returns:
            Sequence[sourdough.base.Creator]: a list with only Creator subclass instances.
                  
        """       
        new_contents = []
        for stage in stages:
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
        self.previous_stage = self.stage
        self.stage = new_stage
        return self

    def iterate(self, project: 'sourdough.project') -> 'sourdough.project':
        """Advances to next stage and applies that stage to 'project'.

        Args:
            project (sourdough.project): instance to apply the next stage's
                methods to.
                
        Raises:
            IndexError: if this instance is already at the last stage.

        Returns:
            sourdough.project: with the last stage applied.
            
        """
        if self.index == len(self.contents) - 1:
            raise IndexError(
                f'{self.name} is at the last stage and cannot further iterate')
        else:
            self.advance()
            self.contents[self.index].apply(project = project)
        return project
            
    """ Dunder Methods """
    
    def __iter__(self) -> Iterable:
        """Returns iterable of methods of 'contents'.
        
        Returns:
            Iterable: 'apply' methods of 'contents'.
            
        """
        return iter([getattr(s, 'apply') for s in self.contents])

    def __next__(self) -> Callable:
        """Returns next method after method matching 'item'.
        
        Returns:
            Callable: next method corresponding to those listed in 'options'.
            
        """
        if self.index < len(self.contents):
            self.advance()
            return getattr(self.contents[self.index], 'apply')
        else:
            raise StopIteration()
     
    """ Private Methods """

    def _initialize_project(self, 
            project: Union['sourdough.project', str],
            **kwargs) -> 'sourdough.project':
        """Creates or validates a Project or Project subclass instance.

        Args:
            project (Union[sourdough.project, str]): either a Project instance,
                Project subclass, Project subclass instance, or str matching
                a key in 'project_options'.
            kwargs: any extra arguments to send to the created Project instance.
                These will have no effect on Project instances already stored in 
                the 'project_options' class attribute.

        Raises:
            KeyError: if 'project' contains a string which does not match a key 
                in the 'project_options' class attribute.
            TypeError: if an item in 'project' is neither a str nor Project 
                subclass or instance.
            
        Returns:
            sourdough.project: a completed Project or subclass instance.
                  
        """       
        if isinstance(project, str):
            try:
                instance = self.project_options[project](**kwargs)
            except KeyError:
                KeyError(f'{project} is not a recognized project')
        elif isinstance(project, sourdough.project):
            instance = project
        elif issubclass(project, sourdough.project):
            instance = project(**kwargs)
        else:
            raise TypeError(f'{project} must be a str or Project type')
        return instance
   
    def _initialize_designs(self, **kwargs) -> Mapping[str, 'sourdough.base.Design']:
        """Creates or validates 'design_options'.

        Args:
            kwargs: any extra arguments to send to the created Design instances.
            
        Returns:
            Mapping[str, sourdough.base.Design]: dictionary with str keys and values of
                Design instances that are available to use.
                  
        """  
        designs = {}
        for key, value in self.design_options.items():
            designs[key] = value(**kwargs)
        return designs
                        
    def _auto_contents(self, 
            project: 'sourdough.project') -> 'sourdough.project':
        """Automatically advances through and iterates stored Creator instances.

        Args:
            project (sourdough.project): an instance containing any data for 
                the project methods to be applied to.
                
        Returns:
            sourdough.project: modified by the stored Creator instance's 'apply' 
                methods.
            
        """
        for stage in self.contents:
            self.iterate(project = project)
        return project


@dataclasses.dataclass
class Manager(sourdough.base.Progression, sourdough.base.ProxyMixin):
    """Basic project construction and management class.

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough.base. For example if a 
            sourdough instance needs settings from a Configuration instance, 'name' 
            should match the appropriate section name in the Configuration instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Component is called, 'name' is set based upon
            the '_get_name' method in Component. If that method is not 
            overridden by a subclass instance, 'name' will be assigned to the 
            snake case version of the class name ('__class__.__name__').
        contents (Sequence[Union['sourdough.base.Stage', str]]]): list of Stage
            instance or strings which correspond to keys in 'options'.
            Defaults to 'default', which will use the 'defaults' attribute of
            'options' to select Stage instance.
        project (Union['sourdough.project'], str]): a Project instance
            or strings which correspond to keys in 'project_options'. Defaults 
            to 'default', which will use the 'defaults' attribute of 
            'project_options' to select a Project instance.
        settings (Union[sourdough.base.Configuration, str]]): an instance of 
            Configuration or a string containing the file path where a file of a 
            supported file type with settings for an Configuration instance is 
            located. Defaults to None.
        filer (Union[sourdough.base.Filer, str]]): an instance of Filer or a 
            string containing the full path of where the root folder should be 
            located for file input and output. A Filer instance contains all 
            file path and import/export methods for use throughout sourdough.base. 
            Defaults to None.
        automatic (bool]): whether to automatically advance 'contents'
            (True) or whether the stages must be changed manually by using the 
            'advance' or '__iter__' methods (False). Defaults to True.
        project_options (ClassVar['sourdough.base.Catalog']): stores options for
            the 'project' attribute.
        options (ClassVar['sourdough.base.Stages']): stores options for the 
            'contents' attribute.
        design_options (ClassVar['sourdough.base.Designs']): stores options used by
            the stages stored in 'contents' to design Component instances within
            a 'project'.
            
    """
    name: str = None
    contents: Sequence[Union['sourdough.base.Stage', str]] = dataclasses.field(
        default_factory = lambda: 'default')
    project: Union['sourdough.project', str] = dataclasses.field(
        default_factory = lambda: 'default')
    settings: Union['sourdough.base.Configuration', str] = None
    filer: Union['sourdough.base.Filer', str] = None
    automatic: bool = True
    
    project_options: ClassVar['sourdough.base.Catalog'] = sourdough.base.Catalog(
        contents = {
            'generic': sourdough.project},
        defaults = 'generic')
    options: ClassVar['sourdough.base.Catalog'] = sourdough.base.Catalog(
        contents = {
            'draft': sourdough.base.Author,
            'publish': sourdough.base.Publisher,
            'apply': sourdough.base.Reader},
        defaults = ['draft', 'edit', 'publish', 'apply'])
    design_options: ClassVar['sourdough.base.Catalog'] = sourdough.base.Catalog(
        contents = {
            'chained': sourdough.base.structure.designs.ChainedDesign,
            'comparative': sourdough.base.structure.designs.ComparativeDesign},
        defaults = 'chained')
    
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls inherited initialization method.
        super().__post_init__()
        # Removes various python warnings from console output.
        warnings.filterwarnings('ignore')
        # Validates or creates a 'Configuration' instance.
        self.settings = sourdough.base.Configuration(contents = self.settings)
        # Validates or creates a Filer' instance.
        self.filer = sourdough.base.Filer(
            root_folder = self.filer, 
            settings = self.settings)
        # # Creates proxy property referring 'contents' access to 'contents'. This 
        # # allows this instance to use inherited access methods which refer to
        # # 'contents'.
        # self.contents = copy.copy(self.contents)
        # self.proxify(proxy = 'contents', attribute = 'contents')
        # Adds 'general' section attributes from 'settings' in 'project' and 
        # this instance.
        self.settings.inject(instance = self)
        self.settings.inject(instance = self.project)
        # Creates a dictionary of available designs for Plan instances.
        self.designs = self._initialize_designs(settings = self.settings)
        # Initializes 'contents' to regulate an instance's workflow.
        self.contents = self._initialize_stages(
            stages = self.contents,
            settings = self.settings,
            designs = self.designs)
        # Initializes or validates a Project instance.
        self.project = self._initialize_project(
            project = self.project,
            settings = self.settings)
        # Sets current 'stage' and 'index' for that 'stage'.
        self.index = -1
        self.stage = 'initialize' 
        # Advances through 'contents' if 'automatic' is True.
        if self.automatic:
            self.project = self._auto_contents(project = self.project)
            
    """ Class Methods """

    @classmethod   
    def add_project_option(cls, 
            name: str, 
            option: 'sourdough.project') -> None:
        """Adds a project to 'project_options'.

        Args:
            name (str): key to use for storing 'option'.
            option (sourdough.project): the subclass to store in the 
                'project_options' class attribute.

        Raises:
            TypeError: if 'option' is not a Project subclass
            
        """
        if issubclass(option, sourdough.project):
            cls.project_options[name] = option
        elif isinstance(option, sourdough.project):
            cls.project_options[name] = option.__class__
        else:
            raise TypeError('option must be a Project subclass')
        return cls  
    
    @classmethod   
    def add_stage_option(cls, 
            name: str, 
            option: 'sourdough.base.Stage') -> None:
        """Adds a stage to 'options'.

        Args:
            name (str): key to use for storing 'option'.
            option (sourdough.base.Stage): the subclass to store in the 
                'options' class attribute.

        Raises:
            TypeError: if 'option' is not a Stage subclass
            
        """
        if issubclass(option, sourdough.base.Stage):
            cls.options[name] = option
        elif isinstance(option, sourdough.base.Stage):
            cls.options[name] = option.__class__
        else:
            raise TypeError('option must be a Stage subclass')
        return cls  

    @classmethod
    def add_design_option(cls, 
            name: str, 
            option: 'sourdough.base.Design') -> None:
        """Adds a design to 'design_options'.

        Args:
            name (str): key to use for storing 'option'.
            option (sourdough.base.Design): the subclass to store in the 
                'design_options' class attribute.

        Raises:
            TypeError: if 'option' is not a Design subclass.
            
        """
        if issubclass(option, sourdough.base.Design):
            cls.design_options[name] = option
        elif isinstance(option, sourdough.base.Design):
            cls.designoptions[name] = option.__class__
        else:
            raise TypeError('option must be a Design subclass')
        return cls  

    """ Public Methods """
    
    def add(self, *args, **kwargs) -> None:
        """Adds passed arguments to the 'project' attribute.
        
        This method delegates the addition to the current Stage instance. This
        means that different arguments might need to be passed based upon the
        current state of the workflow.
        
        Args:
            args and kwargs: arguments to pass to the delegated method.


        """
        self.project = self.contents[self.index].add(
            self.project, *args, **kwargs)
        return self
                 
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
        self.previous_stage = self.stage
        self.stage = new_stage
        return self

    def iterate(self, project: 'sourdough.project') -> 'sourdough.project':
        """Advances to next stage and applies that stage to 'project'.

        Args:
            project (sourdough.project): instance to apply the next stage's
                methods to.
                
        Raises:
            IndexError: if this instance is already at the last stage.

        Returns:
            sourdough.project: with the last stage applied.
            
        """
        if self.index == len(self.contents) - 1:
            raise IndexError(
                f'{self.name} is at the last stage and cannot further iterate')
        else:
            self.advance()
            self.contents[self.index].apply(project = project)
        return project
            
    """ Dunder Methods """
    
    def __iter__(self) -> Iterable:
        """Returns iterable of methods of 'contents'.
        
        Returns:
            Iterable: 'apply' methods of 'contents'.
            
        """
        return iter([getattr(s, 'apply') for s in self.contents])

    def __next__(self) -> Callable:
        """Returns next method after method matching 'item'.
        
        Returns:
            Callable: next method corresponding to those listed in 
                'options'.
            
        """
        if self.index < len(self.contents):
            self.advance()
            return getattr(self.contents[self.index], 'apply')
        else:
            raise StopIteration()
     
    """ Private Methods """

    def _initialize_stages(self, 
            stages: Sequence[Union[str, 'sourdough.base.Stage']],
            **kwargs) -> Sequence['sourdough.base.Stage']:
        """Creates Stage instances, when necessary, in 'contents'

        Args:
            stages (MutableSequence[Union[str, sourdough.base.Stage]]): a list of strings 
                corresponding to keys in the 'options' class attribute or 
                Stage subclass instances.
            kwargs: any extra arguments to send to each created Stage instance.
                These will have no effect on Stage subclass instances already 
                stored in the 'options' class attribute.

        Raises:
            KeyError: if 'stages' contains a string which does not match a key 
                in the 'options' class attribute.
            TypeError: if an item in 'stages' is neither a str nor Stage 
                subclass.
            
        Returns:
            Sequence[sourdough.base.Stage]: a list with only Stage subclass instances.
                  
        """       
        new_contents = []
        for stage in stages:
            if isinstance(stage, str):
                try:
                    new_contents.append(self.options[stage](**kwargs))
                except KeyError:
                    KeyError(f'{stage} is not a recognized stage')
            elif isinstance(stage, sourdough.base.Stage):
                new_contents.append(stage)
            elif issubclass(stage, sourdough.base.Stage):
                new_contents.append(stage(**kwargs))
            else:
                raise TypeError(f'{stage} must be a str or Stage type')
        return new_contents
    
    def _initialize_project(self, 
            project: Union['sourdough.project', str],
            **kwargs) -> 'sourdough.project':
        """Creates or validates a Project or Project subclass instance.

        Args:
            project (Union[sourdough.project, str]): either a Project instance,
                Project subclass, Project subclass instance, or str matching
                a key in 'project_options'.
            kwargs: any extra arguments to send to the created Project instance.
                These will have no effect on Project instances already stored in 
                the 'project_options' class attribute.

        Raises:
            KeyError: if 'project' contains a string which does not match a key 
                in the 'project_options' class attribute.
            TypeError: if an item in 'project' is neither a str nor Project 
                subclass or instance.
            
        Returns:
            sourdough.project: a completed Project or subclass instance.
                  
        """       
        if isinstance(project, str):
            try:
                instance = self.project_options[project](**kwargs)
            except KeyError:
                KeyError(f'{project} is not a recognized project')
        elif isinstance(project, sourdough.project):
            instance = project
        elif issubclass(project, sourdough.project):
            instance = project(**kwargs)
        else:
            raise TypeError(f'{project} must be a str or Project type')
        return instance
   
    def _initialize_designs(self, **kwargs) -> Mapping[str, 'sourdough.base.Design']:
        """Creates or validates 'design_options'.

        Args:
            kwargs: any extra arguments to send to the created Design instances.
            
        Returns:
            Mapping[str, sourdough.base.Design]: dictionary with str keys and values of
                Design instances that are available to use.
                  
        """  
        designs = {}
        for key, value in self.design_options.items():
            designs[key] = value(**kwargs)
        return designs
                        
    def _auto_contents(self, 
            project: 'sourdough.project') -> 'sourdough.project':
        """Automatically advances through and iterates stored Stage instances.

        Args:
            project (sourdough.project): an instance containing any data for 
                the project methods to be applied to.
                
        Returns:
            sourdough.project: modified by the stored Stage instance's 'apply' 
                methods.
            
        """
        for stage in self.contents:
            self.iterate(project = project)
        return project


@dataclasses.dataclass
class Director(Progression):
    """Base class for iterables storing Stage instances.
    
    Director builds on Progression by 

    Args:
        contents (Sequence[Union['sourdough.base.Stage', str]]]): list of 
            Stage instance or strings which correspond to keys in 
            'options'. Defaults to 'default', which will use the 
            'defaults' attribute of 'options' to select Stage instance.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough.base. For example if a 
            sourdough instance needs settings from a Configuration instance, 'name' 
            should match the appropriate section name in the Configuration instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Component is called, 'name' is set based upon
            the '_get_name' method in Component. If that method is not 
            overridden by a subclass instance, 'name' will be assigned to the 
            snake case version of the class name ('__class__.__name__').
        project (Union['sourdough.project'], str]): a Project instance
            or strings which correspond to keys in 'project_options'. Defaults 
            to 'default', which will use the 'defaults' attribute of 
            'project_options' to select a Project instance.
        settings (Union[sourdough.base.Configuration, str]]): an instance of 
            Configuration or a string containing the file path where a file of a 
            supported file type with settings for an Configuration instance is 
            located. Defaults to None.
        filer (Union[sourdough.base.Filer, str]]): an instance of Filer or a 
            string containing the full path of where the root folder should be 
            located for file input and output. A Filer instance contains all 
            file path and import/export methods for use throughout sourdough.base. 
            Defaults to None.
        automatic (bool]): whether to automatically advance 'contents'
            (True) or whether the stages must be changed manually by using the 
            'advance' or '__iter__' methods (False). Defaults to True.
        project_options (ClassVar['sourdough.base.Catalog']): stores options for
            the 'project' attribute.
        options (ClassVar['sourdough.base.Stages']): stores options for the 
            'contents' attribute.
        design_options (ClassVar['sourdough.base.Designs']): stores options used by
            the stages stored in 'contents' to design Component instances within
            a 'project'.
            
    """
    contents: Sequence[Union[
        'sourdough.base.Stage', 
        str]] = dataclasses.field(default_factory = lambda: 'default')
    name: str = None
    project: Union['sourdough.project', str] = dataclasses.field(
        default_factory = lambda: 'default')
    settings: Union['sourdough.base.Configuration', str] = None
    filer: Union['sourdough.base.Filer', str] = None
    automatic: bool = True
    
    project_options: ClassVar['sourdough.base.Catalog'] = sourdough.base.Catalog(
        contents = {
            'generic': Plan},
        defaults = ['generic'])
    options: ClassVar['sourdough.base.Catalog'] = sourdough.base.Catalog(
        contents = {
            'draft': sourdough.base.Author,
            'publish': sourdough.base.Publisher,
            'apply': sourdough.base.Reader},
        defaults = ['draft', 'edit', 'publish', 'apply'])
    # design_options: ClassVar['sourdough.base.Catalog'] = sourdough.base.Catalog(
    #     contents = {
    #         'chained': sourdough.base.structure.designs.ChainedDesign,
    #         'comparative': sourdough.base.structure.designs.ComparativeDesign},
    #     defaults = ['chained'])
    
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls inherited initialization method.
        super().__post_init__()
        # Removes various python warnings from console output.
        warnings.filterwarnings('ignore')
        # Validates or creates a 'Configuration' instance.
        self.settings = sourdough.base.Configuration(contents = self.settings)
        # Validates or creates a Filer' instance.
        self.filer = sourdough.base.Filer(
            root_folder = self.filer, 
            settings = self.settings)
        # # Creates proxy property referring 'contents' access to 'contents'. This 
        # # allows this instance to use inherited access methods which refer to
        # # 'contents'.
        # self.contents = copy.copy(self.contents)
        # self.proxify(proxy = 'contents', attribute = 'contents')
        # Adds 'general' section attributes from 'settings' in 'project' and 
        # this instance.
        self.settings.inject(instance = self)
        self.settings.inject(instance = self.project)
        # Creates a dictionary of available designs for Plan instances.
        self.designs = self._initialize_designs(settings = self.settings)
        # Initializes 'contents' to regulate an instance's workflow.
        self.contents = self._initialize_stages(
            stages = self.contents,
            settings = self.settings,
            designs = self.designs)
        # Initializes or validates a Project instance.
        self.project = self._initialize_project(
            project = self.project,
            settings = self.settings)
        # Sets current 'stage' and 'index' for that 'stage'.
        self.index = -1
        self.stage = 'initialize' 
        # Advances through 'contents' if 'automatic' is True.
        if self.automatic:
            self.project = self._auto_contents(project = self.project)
            
    """ Class Methods """

    @classmethod   
    def add_project_option(cls, 
            name: str, 
            option: 'sourdough.project') -> None:
        """Adds a project to 'project_options'.

        Args:
            name (str): key to use for storing 'option'.
            option (sourdough.project): the subclass to store in the 
                'project_options' class attribute.

        Raises:
            TypeError: if 'option' is not a Project subclass
            
        """
        if issubclass(option, sourdough.project):
            cls.project_options[name] = option
        elif isinstance(option, sourdough.project):
            cls.project_options[name] = option.__class__
        else:
            raise TypeError('option must be a Project subclass')
        return cls  
    
    @classmethod   
    def add_stage_option(cls, 
            name: str, 
            option: 'sourdough.base.Stage') -> None:
        """Adds a stage to 'options'.

        Args:
            name (str): key to use for storing 'option'.
            option (sourdough.base.Stage): the subclass to store in the 
                'options' class attribute.

        Raises:
            TypeError: if 'option' is not a Stage subclass
            
        """
        if issubclass(option, sourdough.base.Stage):
            cls.options[name] = option
        elif isinstance(option, sourdough.base.Stage):
            cls.options[name] = option.__class__
        else:
            raise TypeError('option must be a Stage subclass')
        return cls  

    # @classmethod
    # def add_design_option(cls, 
    #         name: str, 
    #         option: 'sourdough.base.Design') -> None:
    #     """Adds a design to 'design_options'.

    #     Args:
    #         name (str): key to use for storing 'option'.
    #         option (sourdough.base.Design): the subclass to store in the 
    #             'design_options' class attribute.

    #     Raises:
    #         TypeError: if 'option' is not a Design subclass.
            
    #     """
    #     if issubclass(option, sourdough.base.Design):
    #         cls.design_options[name] = option
    #     elif isinstance(option, sourdough.base.Design):
    #         cls.designoptions[name] = option.__class__
    #     else:
    #         raise TypeError('option must be a Design subclass')
    #     return cls  

    """ Public Methods """
    
    def add(self, *args, **kwargs) -> None:
        """Adds passed arguments to the 'project' attribute.
        
        This method delegates the addition to the current Stage instance. This
        means that different arguments might need to be passed based upon the
        current state of the workflow.
        
        Args:
            args and kwargs: arguments to pass to the delegated method.


        """
        self.project = self.contents[self.index].add(
            self.project, *args, **kwargs)
        return self
                 
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
        self.previous_stage = self.stage
        self.stage = new_stage
        return self

    def iterate(self, project: 'sourdough.project') -> 'sourdough.project':
        """Advances to next stage and applies that stage to 'project'.

        Args:
            project (sourdough.project): instance to apply the next stage's
                methods to.
                
        Raises:
            IndexError: if this instance is already at the last stage.

        Returns:
            sourdough.project: with the last stage applied.
            
        """
        if self.index == len(self.contents) - 1:
            raise IndexError(
                f'{self.name} is at the last stage and cannot further iterate')
        else:
            self.advance()
            self.contents[self.index].apply(project = project)
        return project
            
    """ Dunder Methods """
    
    def __iter__(self) -> Iterable:
        """Returns iterable of methods of 'contents'.
        
        Returns:
            Iterable: 'apply' methods of 'contents'.
            
        """
        return iter([getattr(s, 'apply') for s in self.contents])

    def __next__(self) -> Callable:
        """Returns next method after method matching 'item'.
        
        Returns:
            Callable: next method corresponding to those listed in 
                'options'.
            
        """
        if self.index < len(self.contents):
            self.advance()
            return getattr(self.contents[self.index], 'apply')
        else:
            raise StopIteration()
     
    """ Private Methods """

    def _initialize_stages(self, 
            stages: Sequence[Union[str, 'sourdough.base.Stage']],
            **kwargs) -> Sequence['sourdough.base.Stage']:
        """Creates Stage instances, when necessary, in 'contents'

        Args:
            stages (MutableSequence[Union[str, sourdough.base.Stage]]): a list of strings 
                corresponding to keys in the 'options' class attribute or 
                Stage subclass instances.
            kwargs: any extra arguments to send to each created Stage instance.
                These will have no effect on Stage subclass instances already 
                stored in the 'options' class attribute.

        Raises:
            KeyError: if 'stages' contains a string which does not match a key 
                in the 'options' class attribute.
            TypeError: if an item in 'stages' is neither a str nor Stage 
                subclass.
            
        Returns:
            Sequence[sourdough.base.Stage]: a list with only Stage subclass instances.
                  
        """       
        new_contents = []
        for stage in stages:
            if isinstance(stage, str):
                try:
                    new_contents.append(self.options[stage](**kwargs))
                except KeyError:
                    KeyError(f'{stage} is not a recognized stage')
            elif isinstance(stage, sourdough.base.Stage):
                new_contents.append(stage)
            elif issubclass(stage, sourdough.base.Stage):
                new_contents.append(stage(**kwargs))
            else:
                raise TypeError(f'{stage} must be a str or Stage type')
        return new_contents
    
    def _initialize_project(self, 
            project: Union['sourdough.project', str],
            **kwargs) -> 'sourdough.project':
        """Creates or validates a Project or Project subclass instance.

        Args:
            project (Union[sourdough.project, str]): either a Project instance,
                Project subclass, Project subclass instance, or str matching
                a key in 'project_options'.
            kwargs: any extra arguments to send to the created Project instance.
                These will have no effect on Project instances already stored in 
                the 'project_options' class attribute.

        Raises:
            KeyError: if 'project' contains a string which does not match a key 
                in the 'project_options' class attribute.
            TypeError: if an item in 'project' is neither a str nor Project 
                subclass or instance.
            
        Returns:
            sourdough.project: a completed Project or subclass instance.
                  
        """       
        if isinstance(project, str):
            try:
                instance = self.project_options[project](**kwargs)
            except KeyError:
                KeyError(f'{project} is not a recognized project')
        elif isinstance(project, sourdough.project):
            instance = project
        elif issubclass(project, sourdough.project):
            instance = project(**kwargs)
        else:
            raise TypeError(f'{project} must be a str or Project type')
        return instance
   
    def _initialize_designs(self, **kwargs) -> Mapping[str, 'sourdough.base.Design']:
        """Creates or validates 'design_options'.

        Args:
            kwargs: any extra arguments to send to the created Design instances.
            
        Returns:
            Mapping[str, sourdough.base.Design]: dictionary with str keys and values of
                Design instances that are available to use.
                  
        """  
        designs = {}
        for key, value in self.design_options.items():
            designs[key] = value(**kwargs)
        return designs
                        
    def _auto_contents(self, 
            project: 'sourdough.project') -> 'sourdough.project':
        """Automatically advances through and iterates stored Stage instances.

        Args:
            project (sourdough.project): an instance containing any data for 
                the project methods to be applied to.
                
        Returns:
            sourdough.project: modified by the stored Stage instance's 'apply' 
                methods.
            
        """
        for stage in self.contents:
            self.iterate(project = project)
        return project
