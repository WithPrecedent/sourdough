"""
.. module:: director
:synopsis: sourdough workflow controller
:publisher: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import copy
import dataclasses
from typing import Any, ClassVar, Iterable, Mapping, Sequence, Tuple, Union
import warnings

import sourdough
 
 
@dataclasses.dataclass
class Manager(sourdough.base.Plan, sourdough.mixins.ProxyMixin):
    """Basic project construction and management class.

    Args:
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. If the class instance
            needs settings from the shared Settings instance, 'name' should
            match the appropriate section name in that Settings instance. When
            subclassing, it is a good settings to use the same 'name' attribute
            as the base class for effective coordination between sourdough
            classes. Defaults to None or __class__.__name__.lower().
        contents (Optional[Sequence[Union['sourdough.Stage', str]]]): list of Stage
            instance or strings which correspond to keys in 'stage_options'.
            Defaults to 'default', which will use the 'defaults' attribute of
            'stage_options' to select Stage instance.
        project (Optional[Union['sourdough.Project'], str]): a Project instance
            or strings which correspond to keys in 'project_options'. Defaults 
            to 'default', which will use the 'defaults' attribute of 
            'project_options' to select a Project instance.
        settings (Optional[Union[sourdough.Settings, str]]): an instance of 
            Settings or a string containing the file path where a file of a 
            supported file type with settings for an Settings instance is 
            located. Defaults to None.
        filer (Optional[Union[sourdough.Filer, str]]): an instance of Filer or a 
            string containing the full path of where the root folder should be 
            located for file input and output. A Filer instance contains all 
            file path and import/export methods for use throughout sourdough. 
            Defaults to None.
        automatic (Optional[bool]): whether to automatically advance 'contents'
            (True) or whether the stages must be changed manually by using the 
            'advance' or '__iter__' methods (False). Defaults to True.
        project_options (ClassVar['sourdough.Catalog']): stores options for
            the 'project' attribute.
        stage_options (ClassVar['sourdough.Stages']): stores options for the 
            'contents' attribute.
        design_options (ClassVar['sourdough.Designs']): stores options used by
            the stages stored in 'contents' to design Component instances within
            a 'project'.
            
    """
    name: Optional[str] = None
    contents: Optional[Sequence[Union['sourdough.Stage', str]]] = dataclasses.field(
        default_factory = lambda: 'default')
    project: Optional[Union['sourdough.Project', str]] = dataclasses.field(
        default_factory = lambda: 'default')
    settings: Optional[Union['sourdough.Settings', str]] = None
    filer: Optional[Union['sourdough.Filer', str]] = None
    automatic: Optional[bool] = True
    
    project_options: ClassVar['sourdough.Catalog'] = sourdough.Catalog(
        contents = {
            'generic': sourdough.Project},
        defaults = 'generic')
    stage_options: ClassVar['sourdough.Catalog'] = sourdough.Catalog(
        contents = {
            'draft': sourdough.Author,
            'publish': sourdough.Publisher,
            'apply': sourdough.Reader},
        defaults = ['draft', 'edit', 'publish', 'apply'])
    design_options: ClassVar['sourdough.Catalog'] = sourdough.Catalog(
        contents = {
            'chained': sourdough.structure.designs.ChainedDesign,
            'comparative': sourdough.structure.designs.ComparativeDesign},
        defaults = 'chained')
    
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls inherited initialization method.
        super().__post_init__()
        # Removes various python warnings from console output.
        warnings.filterwarnings('ignore')
        # Validates or creates a 'Settings' instance.
        self.settings = sourdough.Settings(contents = self.settings)
        # Validates or creates a Filer' instance.
        self.filer = sourdough.Filer(
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
        # Creates a dictionary of available designs for Worker instances.
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
            option: 'sourdough.Project') -> None:
        """Adds a project to 'project_options'.

        Args:
            name (str): key to use for storing 'option'.
            option (sourdough.Project): the subclass to store in the 
                'project_options' class attribute.

        Raises:
            TypeError: if 'option' is not a Project subclass
            
        """
        if issubclass(option, sourdough.Project):
            cls.project_options[name] = option
        elif isinstance(option, sourdough.Project):
            cls.project_options[name] = option.__class__
        else:
            raise TypeError('option must be a Project subclass')
        return cls  
    
    @classmethod   
    def add_stage_option(cls, 
            name: str, 
            option: 'sourdough.Stage') -> None:
        """Adds a stage to 'stage_options'.

        Args:
            name (str): key to use for storing 'option'.
            option (sourdough.Stage): the subclass to store in the 
                'stage_options' class attribute.

        Raises:
            TypeError: if 'option' is not a Stage subclass
            
        """
        if issubclass(option, sourdough.Stage):
            cls.stage_options[name] = option
        elif isinstance(option, sourdough.Stage):
            cls.stage_options[name] = option.__class__
        else:
            raise TypeError('option must be a Stage subclass')
        return cls  

    @classmethod
    def add_design_option(cls, 
            name: str, 
            option: 'sourdough.Design') -> None:
        """Adds a design to 'design_options'.

        Args:
            name (str): key to use for storing 'option'.
            option (sourdough.Design): the subclass to store in the 
                'design_options' class attribute.

        Raises:
            TypeError: if 'option' is not a Design subclass.
            
        """
        if issubclass(option, sourdough.Design):
            cls.design_options[name] = option
        elif isinstance(option, sourdough.Design):
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
                 
    def advance(self, stage: Optional[str] = None) -> None:
        """Advances to next item in 'contents' or to 'stage' argument.

        This method only needs to be called manually if 'automatic' is False.
        Otherwise, this method is automatically called when the class is 
        instanced.

        Args:
            stage (Optional[str]): name of item in 'contents'. Defaults to None. 
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

    def iterate(self, project: 'sourdough.Project') -> 'sourdough.Project':
        """Advances to next stage and applies that stage to 'project'.

        Args:
            project (sourdough.Project): instance to apply the next stage's
                methods to.
                
        Raises:
            IndexError: if this instance is already at the last stage.

        Returns:
            sourdough.Project: with the last stage applied.
            
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
                'stage_options'.
            
        """
        if self.index < len(self.contents):
            self.advance()
            return getattr(self.contents[self.index], 'apply')
        else:
            raise StopIteration()
     
    """ Private Methods """

    def _initialize_stages(self, 
            stages: Sequence[Union[str, 'sourdough.Stage']],
            **kwargs) -> Sequence['sourdough.Stage']:
        """Creates Stage instances, when necessary, in 'contents'

        Args:
            stages (MutableSequence[Union[str, sourdough.Stage]]): a list of strings 
                corresponding to keys in the 'stage_options' class attribute or 
                Stage subclass instances.
            kwargs: any extra arguments to send to each created Stage instance.
                These will have no effect on Stage subclass instances already 
                stored in the 'stage_options' class attribute.

        Raises:
            KeyError: if 'stages' contains a string which does not match a key 
                in the 'stage_options' class attribute.
            TypeError: if an item in 'stages' is neither a str nor Stage 
                subclass.
            
        Returns:
            Sequence[sourdough.Stage]: a list with only Stage subclass instances.
                  
        """       
        new_contents = []
        for stage in stages:
            if isinstance(stage, str):
                try:
                    new_contents.append(self.stage_options[stage](**kwargs))
                except KeyError:
                    KeyError(f'{stage} is not a recognized stage')
            elif isinstance(stage, sourdough.Stage):
                new_contents.append(stage)
            elif issubclass(stage, sourdough.Stage):
                new_contents.append(stage(**kwargs))
            else:
                raise TypeError(f'{stage} must be a str or Stage type')
        return new_contents
    
    def _initialize_project(self, 
            project: Union['sourdough.Project', str],
            **kwargs) -> 'sourdough.Project':
        """Creates or validates a Project or Project subclass instance.

        Args:
            project (Union[sourdough.Project, str]): either a Project instance,
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
            sourdough.Project: a completed Project or subclass instance.
                  
        """       
        if isinstance(project, str):
            try:
                instance = self.project_options[project](**kwargs)
            except KeyError:
                KeyError(f'{project} is not a recognized project')
        elif isinstance(project, sourdough.Project):
            instance = project
        elif issubclass(project, sourdough.Project):
            instance = project(**kwargs)
        else:
            raise TypeError(f'{project} must be a str or Project type')
        return instance
   
    def _initialize_designs(self, **kwargs) -> Mapping[str, 'sourdough.Design']:
        """Creates or validates 'design_options'.

        Args:
            kwargs: any extra arguments to send to the created Design instances.
            
        Returns:
            Mapping[str, sourdough.Design]: dictionary with str keys and values of
                Design instances that are available to use.
                  
        """  
        designs = {}
        for key, value in self.design_options.items():
            designs[key] = value(**kwargs)
        return designs
                        
    def _auto_contents(self, 
            project: 'sourdough.Project') -> 'sourdough.Project':
        """Automatically advances through and iterates stored Stage instances.

        Args:
            project (sourdough.Project): an instance containing any data for 
                the project methods to be applied to.
                
        Returns:
            sourdough.Project: modified by the stored Stage instance's 'apply' 
                methods.
            
        """
        for stage in self.contents:
            self.iterate(project = project)
        return project
