"""
.. module:: iterables
:synopsis: sourdough sequences
:author: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import abc
import collections.abc
import dataclasses
import importlib
import inspect
import itertools
import more_itertools
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union
import warnings

import sourdough


@dataclasses.dataclass
class Progression(sourdough.Component, collections.abc.MutableSequence):
    """Base class for sourdough sequenced iterables.
    
    A Progression differs from a python list in 6 ways:
        1) It includes a 'name' attribute which is used for internal referencing
            in sourdough.
        2) It includes an 'add' method which allows different datatypes to
            be passed and added to a Progression instance.
        3) It includes a 'subsetify' method which will return a Progression or
            Progression subclass instance with only the items with 'name'
            attributes matching items in the 'subset' parameter.
        4) It only stores items that have a 'name' attribute.
        5) Progression has an interface of both a dict and a list, but stores a 
            list. Progression does this by taking advantage of the 'name' 
            attribute in Component instances (although any instance with a 
            'name' attribute is compatiable with a Progression). A 'name' acts 
            as a key to create the facade of a dictionary with the items in the 
            stored list serving as values. This allows for duplicate keys for 
            storing class instances, easier iteration, and returning multiple 
            matching items. This design comes at the expense of lookup speed. As 
            a result, Progression should only be used if a high volumne of 
            access calls is not anticipated. Ordinarily, the loss of lookup 
            speed should have negligible effect on overall performance. 
        6) Iterating Plan iterates all contained iterables by using the
            'more_itertools.collapse' method. This orders all stored iterables 
            in a depth-first manner.      

    Args:
        contents (Sequence[sourdough.Component]]): stored iterable of 
            actions to apply in order. Defaults to an empty list.
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

    """
    contents: Sequence['sourdough.Component'] = dataclasses.field(
        default_factory = list)
    name: str = None

    """ Public Methods """
       
    def add(self, 
            items: Union[
                'sourdough.Component',
                str, 
                Sequence['sourdough.Component'],
                Sequence[str]]) -> None:
        """Appends 'items' to 'contents'.
        
        Args:
            items (Union[sourdough.Component, Sequence[sourdough.Component]]): 
                Component(s) to add to 'contents'.

        Raises:
            TypeError: if instances in 'items' are neither str type nor have a 
                name attribute.
            
        """
        if hasattr(component, 'name'):
            self.append(component)
        else:
            raise TypeError('component must have a name attribute')
        return self    

    def append(self, component: 'sourdough.Component') -> None:
        """Appends 'sourdough.Component' to 'contents'.
        
        Args:
            component (sourdough.Component): Component to add to 'contents'.

        Raises:
            TypeError: if 'sourdough.Component' does not have a name attribute
            
        """
        if hasattr(component, 'name'):
            self.contents.append(component)
        else:
            raise TypeError('component must have a name attribute')
        return self    
   
    def extend(self, component: 'sourdough.Component') -> None:
        """Extends 'sourdough.Component' to 'contents'.
        
        Args:
            component (sourdough.Component): Component to add to 'contents'.

        Raises:
            TypeError: if 'sourdough.Component' does not have a name attribute
            
        """
        if hasattr(component, 'name'):
            self.contents.extend(component)
        else:
            raise TypeError('component must have a name attribute')
        return self   
    
    def insert(self, index: int, component: 'sourdough.Component') -> None:
        """Inserts 'sourdough.Component' at 'index' in 'contents'.

        Args:
            index (int): index to insert 'sourdough.Component' at.
            component (sourdough.Component): object to be inserted.

        Raises:
            TypeError: if 'sourdough.Component' does not have a name attribute
            
        """
        if hasattr(component, 'name'):
            self.items.insert[index] = component
        else:
            raise TypeError('component must have a name attribute')
        return self
 
    def subsetify(self, subset: Union[str, Sequence[str]]) -> 'Plan':
        """Returns a subset of 'contents'.

        Args:
            subset (Union[str, Sequence[str]]): key(s) to get Component 
                instances with matching 'name' attributes from 'contents'.

        Returns:
            Plan: with only items with 'name' attributes in 'subset'.

        """
        subset = sourdough.tools.listify(subset)
        return self.__class__(
            name = self.name,
            contents = [c for c in self.contents if c.name in subset])    
     
    def update(self, components: Union[
            Mapping[str, 'sourdough.Component'], 
            Sequence['sourdough.Component']]) -> None:
        """Mimics the dict 'update' method.
        
        Args:
            components (Union[Mapping[str, sourdough.Component], Sequence[
                sourdough.Component]]): Component instances to add to 
                'contents'. If a Mapping is passed, the keys are ignored and
                the values are added to 'contents'. To mimic 'update', the
                passed 'components' are added to 'contents' by the 'extend'
                method.
 
        Raises:
            TypeError: if any of 'components' does not have a name attribute               
        
        """
        if isinstance(components, Mapping):
            components = list(components.values())
        if all(hasattr(c, 'name') for c in components):
            self.contents.extend(components)
        else:
            raise TypeError('components must all have a name attribute')
        return self
          
    """ Dunder Methods """

    def __getitem__(self, key: Union[str, int]) -> 'sourdough.Component':
        """Returns value(s) for 'key' in 'contents'.
        
        If 'key' is a str type, this method looks for a matching 'name'
        attribute in the stored instances.
        
        If 'key' is an int type, this method returns the stored component at the
        corresponding index.
        
        If only one match is found, a single Component instance is returned. If
        more are found, a Progression or Progression subclass with the matching
        'name' attributes is returned.

        Args:
            key (Union[str, int]): name or index to search for in 'contents'.

        Returns:
            sourdough.Component: value(s) stored in 'contents' that correspond 
                to 'key'. If there is more than one match, the return is a
                Progression or Progression subclass with that matching stored
                components.

        """
        if isinstance(key, int):
            return self.contents[key]
        else:
            matches = [c for c in self.contents if c.name == key]
            if len(matches) == 1:
                return matches[0]
            else:
                return self.__class__(name = self.name, contents = matches)

    def __setitem__(self, 
            key: Union[str, int], 
            value: 'sourdough.Component') -> None:
        """Sets 'key' in 'contents' to 'value'.

        Args:
            key (Union[str, int]): if key is a string, it is ignored (since the
                'name' attribute of the value will be acting as the key). In
                such a case, the 'value' is added to the end of 'contents'. If
                key is an int, 'value' is assigned at the that index number in
                'contents'.
            value (Any): value to be paired with 'key' in 'contents'.

        """
        if isinstance(key, int):
            self.contents[key] = value
        else:
            self.contents.add(value)
        return self

    def __delitem__(self, key: Union[str, int]) -> None:
        """Deletes item matching 'key' in 'contents'.

        If 'key' is a str type, this method looks for a matching 'name'
        attribute in the stored instances and deletes all such items. If 'key'
        is an int type, only the item at that index is deleted.

        Args:
            key (Union[str, int]): name or index in 'contents' to delete.

        """
        if isinstance(key, int):
            del self.contents[key]
        else:
            self.contents = [c for c in self.contents if c.name != key]
        return self

    def __iter__(self) -> Iterable:
        """Returns collapsed iterable of 'contents'.
     
        Returns:
            Iterable: using the itertools method which automatically iterates
                all stored iterables within 'contents'.Any
               
        """
        return iter(more_itertools.collapse(self.contents))

    def __len__(self) -> int:
        """Returns length of collapsed 'contents'.

        Returns:
            int: length of collapsed 'contents'.

        """
        return len(more_itertools.collapse(self.contents))
    
    def __add__(self, other: 'Plan') -> None:
        """Extends 'contents' with 'other'

        Args:
            other (Plan): another Plan instance.

        """
        self.contents.extend(other)
        return self
    
    def __repr__(self) -> str:
        """Returns '__str__' representation.

        Returns:
            str: default string representation of an instance.

        """
        return self.__str__()

    def __str__(self) -> str:
        """Returns default string representation of an instance.

        Returns:
            str: default string representation of an instance.

        """
        return (
            f'sourdough {self.__class__.__name__}\n'
            f'name: {self.name}\n'
            f'contents: {self.contents.__str__()}')   


@dataclasses.dataclass
class Plan(sourdough.OptionsMixin, Progression):
    """Base class for iterables storing Operator instances.

    Args:
        contents (Sequence[sourdough.Component]]): stored iterable of 
            actions to apply in order. Defaults to an empty list.
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
        options (ClassVar['sourdough.Catalog']): a sourdough dictionary of 
            available Operator instances available to use.
            
    """
    contents: Union[
        Sequence['sourdough.Operator'], 
        str] = dataclasses.field(default_factory = list)
    name: str = None
    options: ClassVar['sourdough.Catalog'] = sourdough.Catalog()

    """ Class Methods """
    
    @classmethod   
    def add_option(cls, 
            name: str, 
            option: 'sourdough.Operator') -> None:
        """Adds an operator to 'options'.

        Args:
            name (str): key to use for storing 'option'.
            option (sourdough.Operator): the subclass to store in the 'options' 
                class attribute.

        Raises:
            TypeError: if 'option' is not an Operator subclass
            
        """
        if issubclass(option, sourdough.Operator):
            cls.options[name] = option
        elif isinstance(option, sourdough.Operator):
            cls.options[name] = option.__class__
        else:
            raise TypeError('option must be an Operator subclass')
        return cls  

    """ Public Methods """
    
    def apply(self, data: object = None) -> object:
        """[summary]

        Args:
            data (object, optional): [description]. Defaults to None.

        Raises:

        Returns:
            object: [description]
            
        """
        if data is None:
            for operator in self.__iter__():
                self._get_operator(operator = operator).apply()
            return self
        else:
            for operator in self.__iter__():
                data = self._get_operator(operator = operator).apply(
                    data = data)
            return data

    """ Private Methods """
    
    def _get_operator(self, 
            operator: Union['sourdough.Operator', str]) -> 'sourdough.Operator':
        """[summary]

        Returns:
            [type]: [description]
        """
        try:
            return self.options[operator]
        except TypeError:
            return operator
       
        
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
#         project_options (ClassVar['sourdough.Catalog']): stores options for
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
    
#     project_options: ClassVar['sourdough.Catalog'] = sourdough.Catalog(
#         contents = {
#             'generic': Plan},
#         defaults = ['generic'])
#     stage_options: ClassVar['sourdough.Catalog'] = sourdough.Catalog(
#         contents = {
#             'draft': sourdough.Author,
#             'publish': sourdough.Publisher,
#             'apply': sourdough.Reader},
#         defaults = ['draft', 'edit', 'publish', 'apply'])
#     # design_options: ClassVar['sourdough.Catalog'] = sourdough.Catalog(
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
#         # Creates a dictionary of available designs for Worker instances.
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
