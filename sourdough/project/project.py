"""
.. module: project
:synopsis: sourdough Project and related classes
:publisher: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import abc
import dataclasses
import copy
import inspect
import itertools
import more_itertools
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union

import sourdough


@dataclasses.dataclass
class Technique(sourdough.Task):
    """Base class for creating or modifying data objects.

    Args:
        algorithm (object): core object used by the 'apply' method. Defaults to 
            None.
        parameters (Mapping[str, Any]]): parameters to be attached to
            'algorithm' when the 'apply' method is called. Defaults to an empty
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
    algorithm: object = None
    parameters: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    name: str = None
    
    """ Required Subclass Methods """
    
    def apply(self, data: object = None, **kwargs) -> object:
        """Subclasses must provide their own methods."""
        raise NotImplementedError(
            'Technique subclasses must include apply methods')
    
    """ Dunder Methods """

    def __repr__(self) -> str:
        """Returns string representation of a class instance."""
        return self.__str__()

    def __str__(self) -> str:
        """Returns string representation of a class instance."""
        return (
            f'sourdough {self.__class__.__name__} {self.name}\n'
            f'step: {self.step.name}\n'
            f'algorithm: {str(self.algorithm)}\n'
            f'parameters: {str(self.parameters)}\n')
        
            
@dataclasses.dataclass
class Step(sourdough.Task):
    """Base class for wrapping a Technique.

    A Step is a basic wrapper for a Technique that adds a 'name' for the
    'plan' that a stored technique instance is associated with. Subclasses of
    Step can store additional methods and attributes to apply to all possible
    technique instances that could be used. This is often useful when creating
    'comparative' Plan instances which test a variety of strategies with
    similar or identical parameters and/or methods.

    A Plan instance will try to return attributes from 'technique' if the
    attribute is not found in the Plan instance. 

    Args:
        plan (str): the name of the plan in a Plan instance that 
            the algorithm is being performed. This attribute is generally 
            optional but can be useful for tracking and/or displaying the status 
            of iteration. It is automatically created when using a chained or 
            comparative Plan. Defaults to None.
        technique (technique): technique object for this plan in a sourdough
            sequence. Defaults to None.
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
    plan: str = dataclasses.field(default_factory = lambda: '')
    technique: Union[Technique, str] = None
    name: str = None

    """ Dunder Methods """

    def __getattr__(self, attribute: str) -> Any:
        """Looks for 'attribute' in 'technique'.

        Args:
            attribute (str): name of attribute to return.

        Returns:
            Any: matching attribute.

        Raises:
            AttributeError: if 'attribute' is not found in 'technique'.

        """
        try:
            return getattr(self.technique, attribute)
        except AttributeError:
            raise AttributeError(
                f'{attribute} neither found in {self.name} nor \
                    {self.technique}')

    def __repr__(self) -> str:
        """Returns string representation of a class instance."""
        return self.__str__()

    def __str__(self) -> str:
        """Returns string representation of a class instance."""
        return (
            f'sourdough {self.__class__.__name__} {self.name}\n'
            f'plan: {self.plan.name}\n'
            f'technique: {str(self.technique)}\n')


@dataclasses.dataclass
class Plan(sourdough.OptionsMixin, sourdough.Progression):
    """Base class for iterables storing Task instances.

    Args:
        contents (Sequence[sourdough.Task]]): stored iterable of 
            actions to apply in order. Defaults to an empty list.
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
        options (ClassVar['sourdough.Corpus']): a sourdough dictionary of 
            available Task instances available to use.
        design (str): the name of the structural design that should
            be used to create objects in an instance. This should correspond
            to a key in a Manager instance's 'designs' class attribute. 
            Defaults to 'chained'.
            
    """
    contents: Union[
        Sequence['sourdough.Task'], 
        str] = dataclasses.field(default_factory = list)
    name: str = None
    options: ClassVar['sourdough.Corpus'] = sourdough.Corpus(
        always_return_list = True)
    design: str = dataclasses.field(default_factory = lambda: 'chained')

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        super().__post_init__()
        # Converts str in 'contents' to objects.
        self.contents = self._validate_contents(contents = self.contents)

    """ Public Methods """
    
    def apply(self, data: object = None) -> object:
        """Applies stored Task instances to 'data'.

        Args:
            data (object): an object to be modified and/or analyzed by stored 
                Task instances. Defaults to None.

        Returns:
            object: data, possibly with modifications made by Operataor 
                instances.
            If data is not passed, no object is returned.
            
        """
        if data is None:
            for operator in self.__iter__():
                operator.apply()
            return self
        else:
            for operator in self.__iter__():
                data = operator.apply(data = data)
            return data
             
    """ Properties """
    
    @property
    def overview(self) -> 'Overview':
        """Returns a string snapshot of a Plan subclass instance.
        
        Returns:
            Overview: configured according to the '_get_overview' method.
        
        """
        return self._get_overview() 

    @property    
    def plans(self) -> Sequence['Plan']:
        """
        """
        return [isinstance(i, Plan) for i in self._get_flattened()]
 
    @property
    def steps(self) -> Sequence['Step']:
        """[summary]

        Returns:
            [type]: [description]
        """
        return [isinstance(i, Step) for i in self._get_flattened()]
    
    @property    
    def techniques(self) -> Sequence['Technique']:
        """[summary]

        Returns:
            [type]: [description]
        """
        return [isinstance(i, Technique) for i in self._get_flattened()]
    
    """ Private Methods """
    
    def _validate_contents(self, 
            contents: Union[Sequence['sourdough.Task'], str] ) -> Sequence[
                'sourdough.Task']:
        """[summary]

        Returns:
            [type]: [description]
            
        """
        new_contents = []
        for step in contents:
            if isinstance(step, str):
                try:
                    new_contents.append[self.options[step]]
                except KeyError:
                    new_contents.append[step]
            else:
                new_contents.append[step]
        return new_contents
    
    def _get_flattened(self) -> Sequence[Union[
            'sourdough.Plan', 
            'sourdough.Step', 
            'sourdough.Technique']]:
        return more_itertools.collapse(self.contents)
        
    def _get_overview(self) -> Mapping[str, Sequence[str]]:
        """
        """
        overview = {}
        overview['plans'] = [p.name for p in self.plans]
        overivew['steps'] = [t.name for t in self.steps]
        overview['techniques'] = [t.name for t in self.techniques]
        return overview

    
@dataclasses.dataclass
class Project(Plan):
    """Basic sourdough project container.
    
    Subclasses can easily expand upon the basic design and functionality of this
    class. Or, if the underlying structure is acceptable, you can simply add to
    the 'options' class attribute. This can be done manually or with the 
    'add_option' method inherited from Plan.

    Args:
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
        contents (Sequence[Union[sourdough.Plan, sourdough.Step, str]]]): 
            stored Plan or Step instances or strings corresponding to keys in
            'options'. Defaults to an empty list.  
        design (str): the name of the structural design that should
            be used to create objects in an instance. This should correspond
            to a key in a Manager instance's 'designs' class attribute. 
            Defaults to 'chained'.
        identification (str): a unique identification name for a 
            Project instance. The name is used for creating file folders
            related to the 'Project'. If not provided, a string is created from
            'name' and the date and time. This is a notable difference
            between an ordinary Plan instancce and a Project instance. Other
            Plans are not given unique identification. Defaults to None.    
        data (Any]): a data object to apply any constructed objects to.
            This need only be provided when the class is instanced for
            automatic execution. Defaults to None. If you are working on a data-
            focused Project, consider using siMpLify instead 
            (https://github.com/WithPrecedent/simplify). It applies sourdough
            in the data science context. sourdough itself treats 'data' as an
            unknown object of any type which offers more flexibility of design.
        options (ClassVar['sourdough.Corpus']): an instance to store possible
            Plan and Step classes for use in the Project. Defaults to an
            empty Corpus instance.
                             
    """  
    name: str = None
    contents: Sequence[Union[
        'sourdough.Plan', 
        'sourdough.Step', 
        str]] = dataclasses.field(default_factory = list) 
    design: str = dataclasses.field(default_factory = lambda: 'chained')
    data: Any = None
    identification: str = None
    options: ClassVar['sourdough.Corpus'] = sourdough.Corpus()

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls inherited initialization method.
        super().__post_init__()
        # Creates unique 'identification' based upon date and time if none 
        # exists.
        self.identification = (
            self.identification or sourdough.tools.datetime_string(
                prefix = self.name))

  
# @dataclasses.dataclass
# class Director(Progression):
#     """Base class for iterables storing Stage instances.
    
#     Director builds on Progression by 

#     Args:
#         contents (Sequence[Union['sourdough.Stage', str]]]): list of 
#             Stage instance or strings which correspond to keys in 
#             'stage_options'. Defaults to 'default', which will use the 
#             'defaults' attribute of 'stage_options' to select Stage instance.
#         name (str): designates the name of a class instance that is used for 
#             internal referencing throughout sourdough. For example if a 
#             sourdough instance needs settings from a Settings instance, 'name' 
#             should match the appropriate section name in the Settings instance. 
#             When subclassing, it is sometimes a good idea to use the same 'name' 
#             attribute as the base class for effective coordination between 
#             sourdough classes. Defaults to None. If 'name' is None and 
#             '__post_init__' of Component is called, 'name' is set based upon
#             the '_get_name' method in Component. If that method is not 
#             overridden by a subclass instance, 'name' will be assigned to the 
#             snake case version of the class name ('__class__.__name__').
#         project (Union['sourdough.Project'], str]): a Project instance
#             or strings which correspond to keys in 'project_options'. Defaults 
#             to 'default', which will use the 'defaults' attribute of 
#             'project_options' to select a Project instance.
#         settings (Union[sourdough.Settings, str]]): an instance of 
#             Settings or a string containing the file path where a file of a 
#             supported file type with settings for an Settings instance is 
#             located. Defaults to None.
#         filer (Union[sourdough.Filer, str]]): an instance of Filer or a 
#             string containing the full path of where the root folder should be 
#             located for file input and output. A Filer instance contains all 
#             file path and import/export methods for use throughout sourdough. 
#             Defaults to None.
#         automatic (bool]): whether to automatically advance 'contents'
#             (True) or whether the stages must be changed manually by using the 
#             'advance' or '__iter__' methods (False). Defaults to True.
#         project_options (ClassVar['sourdough.Corpus']): stores options for
#             the 'project' attribute.
#         stage_options (ClassVar['sourdough.Stages']): stores options for the 
#             'contents' attribute.
#         design_options (ClassVar['sourdough.Designs']): stores options used by
#             the stages stored in 'contents' to design Component instances within
#             a 'project'.
            
#     """
#     contents: Sequence[Union[
#         'sourdough.Stage', 
#         str]] = dataclasses.field(default_factory = lambda: 'default')
#     name: str = None
#     project: Union['sourdough.Project', str] = dataclasses.field(
#         default_factory = lambda: 'default')
#     settings: Union['sourdough.Settings', str] = None
#     filer: Union['sourdough.Filer', str] = None
#     automatic: bool = True
    
#     project_options: ClassVar['sourdough.Corpus'] = sourdough.Corpus(
#         contents = {
#             'generic': Plan},
#         defaults = ['generic'])
#     stage_options: ClassVar['sourdough.Corpus'] = sourdough.Corpus(
#         contents = {
#             'draft': sourdough.Author,
#             'publish': sourdough.Publisher,
#             'apply': sourdough.Reader},
#         defaults = ['draft', 'edit', 'publish', 'apply'])
#     # design_options: ClassVar['sourdough.Corpus'] = sourdough.Corpus(
#     #     contents = {
#     #         'chained': sourdough.structure.designs.ChainedDesign,
#     #         'comparative': sourdough.structure.designs.ComparativeDesign},
#     #     defaults = ['chained'])
    
#     """ Initialization Methods """

#     def __post_init__(self) -> None:
#         """Initializes class instance attributes."""
#         # Calls inherited initialization method.
#         super().__post_init__()
#         # Removes various python warnings from console output.
#         warnings.filterwarnings('ignore')
#         # Validates or creates a 'Settings' instance.
#         self.settings = sourdough.Settings(contents = self.settings)
#         # Validates or creates a Filer' instance.
#         self.filer = sourdough.Filer(
#             root_folder = self.filer, 
#             settings = self.settings)
#         # # Creates proxy property referring 'contents' access to 'contents'. This 
#         # # allows this instance to use inherited access methods which refer to
#         # # 'contents'.
#         # self.contents = copy.copy(self.contents)
#         # self.proxify(proxy = 'contents', attribute = 'contents')
#         # Adds 'general' section attributes from 'settings' in 'project' and 
#         # this instance.
#         self.settings.inject(instance = self)
#         self.settings.inject(instance = self.project)
#         # Creates a dictionary of available designs for Plan instances.
#         self.designs = self._initialize_designs(settings = self.settings)
#         # Initializes 'contents' to regulate an instance's workflow.
#         self.contents = self._initialize_stages(
#             stages = self.contents,
#             settings = self.settings,
#             designs = self.designs)
#         # Initializes or validates a Project instance.
#         self.project = self._initialize_project(
#             project = self.project,
#             settings = self.settings)
#         # Sets current 'stage' and 'index' for that 'stage'.
#         self.index = -1
#         self.stage = 'initialize' 
#         # Advances through 'contents' if 'automatic' is True.
#         if self.automatic:
#             self.project = self._auto_contents(project = self.project)
            
#     """ Class Methods """

#     @classmethod   
#     def add_project_option(cls, 
#             name: str, 
#             option: 'sourdough.Project') -> None:
#         """Adds a project to 'project_options'.

#         Args:
#             name (str): key to use for storing 'option'.
#             option (sourdough.Project): the subclass to store in the 
#                 'project_options' class attribute.

#         Raises:
#             TypeError: if 'option' is not a Project subclass
            
#         """
#         if issubclass(option, sourdough.Project):
#             cls.project_options[name] = option
#         elif isinstance(option, sourdough.Project):
#             cls.project_options[name] = option.__class__
#         else:
#             raise TypeError('option must be a Project subclass')
#         return cls  
    
#     @classmethod   
#     def add_stage_option(cls, 
#             name: str, 
#             option: 'sourdough.Stage') -> None:
#         """Adds a stage to 'stage_options'.

#         Args:
#             name (str): key to use for storing 'option'.
#             option (sourdough.Stage): the subclass to store in the 
#                 'stage_options' class attribute.

#         Raises:
#             TypeError: if 'option' is not a Stage subclass
            
#         """
#         if issubclass(option, sourdough.Stage):
#             cls.stage_options[name] = option
#         elif isinstance(option, sourdough.Stage):
#             cls.stage_options[name] = option.__class__
#         else:
#             raise TypeError('option must be a Stage subclass')
#         return cls  

#     # @classmethod
#     # def add_design_option(cls, 
#     #         name: str, 
#     #         option: 'sourdough.Design') -> None:
#     #     """Adds a design to 'design_options'.

#     #     Args:
#     #         name (str): key to use for storing 'option'.
#     #         option (sourdough.Design): the subclass to store in the 
#     #             'design_options' class attribute.

#     #     Raises:
#     #         TypeError: if 'option' is not a Design subclass.
            
#     #     """
#     #     if issubclass(option, sourdough.Design):
#     #         cls.design_options[name] = option
#     #     elif isinstance(option, sourdough.Design):
#     #         cls.designoptions[name] = option.__class__
#     #     else:
#     #         raise TypeError('option must be a Design subclass')
#     #     return cls  

#     """ Public Methods """
    
#     def add(self, *args, **kwargs) -> None:
#         """Adds passed arguments to the 'project' attribute.
        
#         This method delegates the addition to the current Stage instance. This
#         means that different arguments might need to be passed based upon the
#         current state of the workflow.
        
#         Args:
#             args and kwargs: arguments to pass to the delegated method.


#         """
#         self.project = self.contents[self.index].add(
#             self.project, *args, **kwargs)
#         return self
                 
#     def advance(self, stage: str = None) -> None:
#         """Advances to next item in 'contents' or to 'stage' argument.

#         This method only needs to be called manually if 'automatic' is False.
#         Otherwise, this method is automatically called when the class is 
#         instanced.

#         Args:
#             stage (str): name of item in 'contents'. Defaults to None. 
#                 If not passed, the method goes to the next item in contents.

#         Raises:
#             ValueError: if 'stage' is neither None nor in 'contents'.
#             IndexError: if 'advance' is called at the last stage in 'contents'.

#         """
#         if stage is None:
#             try:
#                 new_stage = self.contents[self.index + 1]
#             except IndexError:
#                 raise IndexError(f'{self.name} cannot advance further')
#         else:
#             try:
#                 new_stage = self.contents[stage]
#             except KeyError:
#                 raise ValueError(f'{stage} is not a recognized stage')
#         self.index += 1
#         self.previous_stage = self.stage
#         self.stage = new_stage
#         return self

#     def iterate(self, project: 'sourdough.Project') -> 'sourdough.Project':
#         """Advances to next stage and applies that stage to 'project'.

#         Args:
#             project (sourdough.Project): instance to apply the next stage's
#                 methods to.
                
#         Raises:
#             IndexError: if this instance is already at the last stage.

#         Returns:
#             sourdough.Project: with the last stage applied.
            
#         """
#         if self.index == len(self.contents) - 1:
#             raise IndexError(
#                 f'{self.name} is at the last stage and cannot further iterate')
#         else:
#             self.advance()
#             self.contents[self.index].apply(project = project)
#         return project
            
#     """ Dunder Methods """
    
#     def __iter__(self) -> Iterable:
#         """Returns iterable of methods of 'contents'.
        
#         Returns:
#             Iterable: 'apply' methods of 'contents'.
            
#         """
#         return iter([getattr(s, 'apply') for s in self.contents])

#     def __next__(self) -> Callable:
#         """Returns next method after method matching 'item'.
        
#         Returns:
#             Callable: next method corresponding to those listed in 
#                 'stage_options'.
            
#         """
#         if self.index < len(self.contents):
#             self.advance()
#             return getattr(self.contents[self.index], 'apply')
#         else:
#             raise StopIteration()
     
#     """ Private Methods """

#     def _initialize_stages(self, 
#             stages: Sequence[Union[str, 'sourdough.Stage']],
#             **kwargs) -> Sequence['sourdough.Stage']:
#         """Creates Stage instances, when necessary, in 'contents'

#         Args:
#             stages (MutableSequence[Union[str, sourdough.Stage]]): a list of strings 
#                 corresponding to keys in the 'stage_options' class attribute or 
#                 Stage subclass instances.
#             kwargs: any extra arguments to send to each created Stage instance.
#                 These will have no effect on Stage subclass instances already 
#                 stored in the 'stage_options' class attribute.

#         Raises:
#             KeyError: if 'stages' contains a string which does not match a key 
#                 in the 'stage_options' class attribute.
#             TypeError: if an item in 'stages' is neither a str nor Stage 
#                 subclass.
            
#         Returns:
#             Sequence[sourdough.Stage]: a list with only Stage subclass instances.
                  
#         """       
#         new_contents = []
#         for stage in stages:
#             if isinstance(stage, str):
#                 try:
#                     new_contents.append(self.stage_options[stage](**kwargs))
#                 except KeyError:
#                     KeyError(f'{stage} is not a recognized stage')
#             elif isinstance(stage, sourdough.Stage):
#                 new_contents.append(stage)
#             elif issubclass(stage, sourdough.Stage):
#                 new_contents.append(stage(**kwargs))
#             else:
#                 raise TypeError(f'{stage} must be a str or Stage type')
#         return new_contents
    
#     def _initialize_project(self, 
#             project: Union['sourdough.Project', str],
#             **kwargs) -> 'sourdough.Project':
#         """Creates or validates a Project or Project subclass instance.

#         Args:
#             project (Union[sourdough.Project, str]): either a Project instance,
#                 Project subclass, Project subclass instance, or str matching
#                 a key in 'project_options'.
#             kwargs: any extra arguments to send to the created Project instance.
#                 These will have no effect on Project instances already stored in 
#                 the 'project_options' class attribute.

#         Raises:
#             KeyError: if 'project' contains a string which does not match a key 
#                 in the 'project_options' class attribute.
#             TypeError: if an item in 'project' is neither a str nor Project 
#                 subclass or instance.
            
#         Returns:
#             sourdough.Project: a completed Project or subclass instance.
                  
#         """       
#         if isinstance(project, str):
#             try:
#                 instance = self.project_options[project](**kwargs)
#             except KeyError:
#                 KeyError(f'{project} is not a recognized project')
#         elif isinstance(project, sourdough.Project):
#             instance = project
#         elif issubclass(project, sourdough.Project):
#             instance = project(**kwargs)
#         else:
#             raise TypeError(f'{project} must be a str or Project type')
#         return instance
   
#     def _initialize_designs(self, **kwargs) -> Mapping[str, 'sourdough.Design']:
#         """Creates or validates 'design_options'.

#         Args:
#             kwargs: any extra arguments to send to the created Design instances.
            
#         Returns:
#             Mapping[str, sourdough.Design]: dictionary with str keys and values of
#                 Design instances that are available to use.
                  
#         """  
#         designs = {}
#         for key, value in self.design_options.items():
#             designs[key] = value(**kwargs)
#         return designs
                        
#     def _auto_contents(self, 
#             project: 'sourdough.Project') -> 'sourdough.Project':
#         """Automatically advances through and iterates stored Stage instances.

#         Args:
#             project (sourdough.Project): an instance containing any data for 
#                 the project methods to be applied to.
                
#         Returns:
#             sourdough.Project: modified by the stored Stage instance's 'apply' 
#                 methods.
            
#         """
#         for stage in self.contents:
#             self.iterate(project = project)
#         return project
