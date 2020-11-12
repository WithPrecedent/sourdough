"""
workflows: iterables in sourdough projects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:

"""
from __future__ import annotations
import abc
import dataclasses
import itertools
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Union)

import more_itertools

import sourdough


@dataclasses.dataclass
class Aggregation(sourdough.Component, sourdough.types.Hybrid):
    """Aggregates unordered objects.
    
    Distinguishing characteristics of an Aggregation:
        1) Order doesn't matter.
        2) Stored Components do not need to be connected. If attributes of the
            stored Components created connections, those connections will be 
            left in tact.
        
    Args:
        contents (Sequence[Union[str, Component]]): a list of str or Components. 
            Defaults to an empty set.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. 
    
    """
    contents: Sequence[Union[str, sourdough.Component]] = dataclasses.field(
        default_factory = set)
    name: str = None
       

@dataclasses.dataclass
class SerialFlow(sourdough.Component, sourdough.types.Hybrid, abc.ABC):
    """Base class for serially workflows Flows in sourdough projects.
        
    Args:
        contents (Sequence[Union[str, Component]]): a list of str or Components. 
            Defaults to an empty list.
        name (str): property which designates the internal reference of a class 
            instance that is used throughout sourdough. For example, if a 
            sourdough instance needs options from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            Defaults to None. If 'name' is None, it will be assigned to the 
            snake case version of the class name ('__name__' or 
            '__class__.__name__').
    
    """
    contents: Sequence[Union[str, sourdough.Component]] = dataclasses.field(
        default_factory = list)
    name: str = None
    branches: ClassVar[bool] = False   

    
@dataclasses.dataclass
class Cycle(SerialFlow):
    """Ordered sourdough Components which will be repetitively called.

    Distinguishing characteristics of a Pipeline:
        1) Follows a sequence of instructions (serial workflow).
        2) It may pass data or other arguments to the next step in the sequence.
        3) Only one connection or path exists between each object.
        4) It repeats the number of times set in the 'iterations' attribute.
            If 'iteratations' is 'infinite', the loop will repeat until stopped
            by a condition set in 'criteria'.
        
    Args:
        contents (Sequence[Union[str, sourdough.Component]]): a set of str or
            Components. 
        name (str): property which designates the internal reference of a class 
            instance that is used throughout sourdough. For example, if a 
            sourdough instance needs options from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            Defaults to None. If 'name' is None, it will be assigned to the 
            snake case version of the class name ('__name__' or 
            '__class__.__name__').
    
    """
    contents: Sequence[Union[str, sourdough.Component]] = dataclasses.field(
        default_factory = list)
    name: str = None
    iterations: int = 10
    criteria: str = None
    

@dataclasses.dataclass
class Pipeline(SerialFlow):
    """Ordered sourdough Components without branching.

    Distinguishing characteristics of a Pipeline:
        1) Follows a sequence of instructions (serial workflow).
        2) It may pass data or other arguments to the next step in the sequence.
        3) Only one connection or path exists between each object. There is no
            branching or looping.
        
    Args:
        contents (Sequence[Union[str, Component]]): a list of str or Components. 
            Defaults to an empty list.
        name (str): property which designates the internal reference of a class 
            instance that is used throughout sourdough. For example, if a 
            sourdough instance needs options from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            Defaults to None. If 'name' is None, it will be assigned to the 
            snake case version of the class name ('__name__' or 
            '__class__.__name__').
    
    """
    contents: Sequence[Union[str, sourdough.Component]] = dataclasses.field(
        default_factory = list)
    name: str = None    


@dataclasses.dataclass
class ParallelFlow(sourdough.Component, sourdough.types.Hybrid, abc.ABC):
    """Base class for parallelly workflowd Flows in sourdough projects.
        
    Args:
        contents (Sequence[Union[str, Component]]): a list of str or Components. 
            Defaults to an empty list.
        name (str): property which designates the internal reference of a class 
            instance that is used throughout sourdough. For example, if a 
            sourdough instance needs options from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            Defaults to None. If 'name' is None, it will be assigned to the 
            snake case version of the class name ('__name__' or 
            '__class__.__name__').
    
    """
    contents: Sequence[Union[str, sourdough.Component]] = dataclasses.field(
        default_factory = list)
    name: str = None
    iterations: int = 1
    criteria: str = None
    branches: ClassVar[bool] = True
          
    """ Required Subclass Methods """
    
    # @abc.abstractmethod
    # def organize(self, **kwargs) -> Iterable:
    #     pass
    
    # @abc.abstractmethod
    # def iterate(self, **kwargs) -> Iterable:
    #     pass
    
    # @abc.abstractmethod
    # def activate(self, **kwargs) -> Iterable:
    #     pass    
    
    # @abc.abstractmethod
    # def finalize(self, **kwargs) -> Iterable:
    #     pass


@dataclasses.dataclass
class Contest(ParallelFlow):
    """Stores Flows in a comparative parallel workflow and chooses best.

    Distinguishing characteristics of a Contest:
        1) Repeats a Pipeline with different options (parallel workflow).
        2) Chooses the best option based upon selected criteria.
        3) Each stored Component is only attached to the Contest with exactly 
            one connection (these connections are not defined separately - they
            are simply part of the parallel workflow).
        
    Args:
        contents (Sequence[Union[str, Component]]): a list of str or Components. 
            Defaults to an empty list.
        name (str): property which designates the internal reference of a class 
            instance that is used throughout sourdough. For example, if a 
            sourdough instance needs options from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            Defaults to None. If 'name' is None, it will be assigned to the 
            snake case version of the class name ('__name__' or 
            '__class__.__name__').
    
    """
    contents: Sequence[sourdough.Pipeline] = dataclasses.field(
        default_factory = list)
    iterations: int = 10
    criteria: str = None
    name: str = None
    
    
@dataclasses.dataclass
class Study(ParallelFlow):
    """Stores Flows in a comparative parallel workflow.

    Distinguishing characteristics of a Study:
        1) Repeats a Pipeline with different options (parallel workflow).
        2) Maintains all of the repetitions without selecting or averaging the 
            results.
        3) Each stored Component is only attached to the Study with exactly 
            one connection (these connections are not defined separately - they
            are simply part of the parallel workflow).
                      
    Args:
        contents (Sequence[Union[str, Component]]): a list of str or Components. 
            Defaults to an empty list.
        name (str): property which designates the internal reference of a class 
            instance that is used throughout sourdough. For example, if a 
            sourdough instance needs options from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            Defaults to None. If 'name' is None, it will be assigned to the 
            snake case version of the class name ('__name__' or 
            '__class__.__name__').
    
    """
    contents: Union[
        sourdough.Outline,
        sourdough.Pipeline] = dataclasses.field(default_factory = list)
    iterations: int = None
    name: str = None
        
    
@dataclasses.dataclass
class Survey(ParallelFlow):
    """Stores Flows in a comparative parallel workflow and averages results.

    Distinguishing characteristics of a Survey:
        1) Repeats a Pipeline with different options (parallel workflow).
        2) Averages or otherwise combines the results based upon selected 
            criteria.
        3) Each stored Component is only attached to the Survey with exactly 
            one connection (these connections are not defined separately - they
            are simply part of the parallel workflow).    
                    
    Args:
        contents (Sequence[Union[str, Component]]): a list of str or Components. 
            Defaults to an empty list.
        name (str): property which designates the internal reference of a class 
            instance that is used throughout sourdough. For example, if a 
            sourdough instance needs options from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            Defaults to None. If 'name' is None, it will be assigned to the 
            snake case version of the class name ('__name__' or 
            '__class__.__name__').
    
    """
    contents: Sequence[sourdough.Pipeline] = dataclasses.field(
        default_factory = list)
    iterations: int = 10
    criteria: str = None
    name: str = None
        


# @dataclasses.dataclass
# class Role(
#         sourdough.Registry, 
#         sourdough.Element, 
#         abc.ABC):
#     """Base class related to constructing and iterating Flow instances.
    
#     """
#     name: str = None
#     director: sourdough.Director = None
#     iterations: int = 1
#     library: ClassVar[sourdough.types.Catalog] = sourdough.types.Catalog(
#         stored_types = ('Role'))

#     """ Initialization Methods """
    
#     def __post_init__(self) -> None:
#         """Initializes class instance attributes."""
#         # Calls parent and/or mixin initialization method(s).
#         super().__post_init__()
#         # Sets 'index' for current location in 'Flow' for the iterator.
#         self.index: int = -1

#     """ Required Subclass Methods """

#     @abc.abstractmethod
#     def organize(self, Flow: sourdough.Component, sourdough.types.Hybrid) -> sourdough.Component, sourdough.types.Hybrid:
#         pass
 
#     @abc.abstractmethod
#     def finalize(self, Flow: sourdough.Component, sourdough.types.Hybrid) -> sourdough.Component, sourdough.types.Hybrid:
#         pass
    
#     """ Class Methods """

#     @classmethod
#     def validate(cls, Flow: sourdough.Component, sourdough.types.Hybrid) -> sourdough.Component, sourdough.types.Hybrid:
#         """Returns a Role instance based upon 'workflow'.
        
#         Args:
#             Flow (sourdough.Component, sourdough.types.Hybrid): Hybrid instance with 'workflow' attribute
#                 to be validated.
                
#         Raises:
#             TypeError: if 'Flow.workflow' is neither a str nor Role type.
            
#         Returns:
#             sourdough.Component, sourdough.types.Hybrid: with a validated 'workflow' attribute.
            
#         """
#         if isinstance(Flow.workflow, str):
#             Flow.workflow = cls.library[Flow.workflow]()
#         elif (inspect.isclass(Flow.workflow) 
#                 and issubclass(Flow.workflow, cls)):
#             Flow.workflow = Flow.workflow() 
#         elif isinstance(Flow.workflow, cls):
#             Flow.workflow.__post_init__()
#         else:
#             raise TypeError(
#                 f'The workflow attribute of Flow must be a str or {cls} type')
#         return Flow

#     """ Public Methods """
    
#     def iterate(self, Flow: sourdough.Component, sourdough.types.Hybrid) -> Iterable:
#         return more_itertools.collapse(Flow.contents)

#     """ Private Methods """
  
#     def _get_settings_suffixes(self, 
#             settings: Mapping[str, Sequence[str]]) -> Sequence[str]: 
#         """[summary]

#         Args:
#             settings (Mapping[str, Sequence[str]]): [description]

#         Returns:
#             Sequence[str]: [description]
#         """
#         suffixes = [k.split('_')[-1] for k in settings.keys()]
#         return sourdough.tools.deduplicate(suffixes)
    
#     def _get_suffixes(self, 
#             settings: Mapping[str, Sequence[str]], 
#             project: sourdough.Project) -> Mapping[
#                 str, Mapping[str, Sequence[str]]]:
#         """[summary]

#         Args:
#             settings (Mapping[str, Sequence[str]]): [description]
#             project (sourdough.Project): [description]

#         Returns:
#             Mapping[ str, Mapping[str, Sequence[str]]]: [description]
            
#         """
#         workflows = {}
#         for key in project.components.resources.keys():
#             suffix = f'_{key}s'
#             workflows[key] = {
#                 k: v for k, v in settings.items() if k.endswith(suffix)} 
            
#         return {k: v for k, v in project.components.resources.items()}
    
#     def _build_wrapper(self,
#             key: str, 
#             generic: sourdough.Component,
#             wrapped: Mapping[str, Sequence[str]],
#             project: sourdough.Project,
#             **kwargs) -> None:
#         """[summary]

#         Args:
#             wrapper (str): [description]
#             wrapped (Mapping[str, Sequence[str]]): [description]
#             wrapped_type (str):
#             generic_wrapper (Callable): [description]

#         Returns:
#             [type]: [description]
#         """
#         # Checks if special prebuilt class exists.
#         if key in project.component.library:
#             for item in wrapped:
#                 kwargs.update({generic.contains: key})
#                 component = project.component.instance(key = key, **kwargs)
#                 self.Flow.add(component) 
#         # Otherwise uses the appropriate generic type.
#         else:
#             for item in wrapped:
#                 kwargs.update({'name': key, generic.contains: key})
#                 self.Flow.add(generic(**kwargs)) 
#         return self   

#     def _build_component(self,
#             key: str, 
#             generic: sourdough.Component,
#             project: sourdough.Project,
#             **kwargs) -> None:
#         """[summary]
#         """
#         # Checks if special prebuilt class exists.
#         try:
#             component = project.component.instance(key = key, **kwargs)
#         # Otherwise uses the appropriate generic type.
#         except KeyError:
#             kwargs.update({'name': key})
#             component = generic(**kwargs)
#         self.Flow.add(component)
#         return self  
           
      
# @dataclasses.dataclass
# class Obey(Role):
    
#     name: str = None
#     director: sourdough.Director = None
#     iterations: int = 1
    
#     """ Public Methods """

#     def organize(self, Flow: sourdough.Component, sourdough.types.Hybrid) -> sourdough.Component, sourdough.types.Hybrid:
#         pass

#     def finalize(self, Flow: sourdough.Component, sourdough.types.Hybrid) -> sourdough.Component, sourdough.types.Hybrid:
#         pass

      
# @dataclasses.dataclass
# class Repeat(Role):
    
#     name: str = None
#     director: sourdough.Director = None
#     iterations: int = 2
    
#     """ Public Methods """

#     def organize(self, Flow: sourdough.Component, sourdough.types.Hybrid) -> sourdough.Component, sourdough.types.Hybrid:
#         pass
    
#     def iterate(self, Flow: sourdough.Component, sourdough.types.Hybrid) -> Iterable:
#         return itertools.repeat(Flow.contents, self.iterations)
        
#     def finalize(self, Flow: sourdough.Component, sourdough.types.Hybrid) -> sourdough.Component, sourdough.types.Hybrid:
#         pass
       
         
# @dataclasses.dataclass
# class Compare(Role):
    
#     name: str = None
#     director: sourdough.Director = None
#     iterations: int = 1

#     """ Public Methods """

#     def organize(self, Flow: sourdough.Component, sourdough.types.Hybrid) -> sourdough.Component, sourdough.types.Hybrid:
#         """[summary]

#         Args:
#             Flow (sourdough.Component, sourdough.types.Hybrid): [description]

#         Returns:
#             sourdough.Component, sourdough.types.Hybrid: [description]
#         """
#         steps = components.pop([components.keys()[0]])
#         possible = list(components.values())
#         permutations = list(map(list, itertools.product(*possible)))
#         for i, contained in enumerate(permutations):
#             instance = sourdough.Component, sourdough.types.Hybrid(
#                 _components = tuple(zip(steps, contained)))
#         return Flow
    
#     def finalize(self, Flow: sourdough.Component, sourdough.types.Hybrid) -> sourdough.Component, sourdough.types.Hybrid:
#         pass

         
# @dataclasses.dataclass
# class Judge(Role):
    
#     name: str = None
#     director: sourdough.Director = None
#     iterations: int = 10

#     """ Public Methods """

#     def organize(self, Flow: sourdough.Component, sourdough.types.Hybrid) -> sourdough.Component, sourdough.types.Hybrid:
#         pass
    
#     def finalize(self, Flow: sourdough.Component, sourdough.types.Hybrid) -> sourdough.Component, sourdough.types.Hybrid:
#         pass
    

# @dataclasses.dataclass
# class Survey(Role):
    
#     name: str = None
#     director: sourdough.Director = None
#     iterations: int = 10
    
#     """ Public Methods """

#     def organize(self, Flow: sourdough.Component, sourdough.types.Hybrid) -> sourdough.Component, sourdough.types.Hybrid:
#         pass
    
#     def finalize(self, Flow: sourdough.Component, sourdough.types.Hybrid) -> sourdough.Component, sourdough.types.Hybrid:
#         pass



# @dataclasses.dataclass
# class LazyIterable(collections.abc.Iterable, sourdough.Component, abc.ABC):
    
    
#     @abc.abstractmethod
#     def generator(self, *args) -> Iterable:
#         pass
        
    

# @dataclasses.dataclass
# class Compare(LazyIterable):
    
    
#     def generator(self, *args) -> sourdough.Element:
#         pools = [tuple(pool) for pool in args]
#         result = [[]]
#         for pool in pools:
#             result = [x + [y] for x in result for y in pool]
#         for product in result:
#             yield tuple(product)

# @dataclasses.dataclass
# class Tree(Role):
    
#     name: str = None
#     Flow: sourdough.Component, sourdough.types.Hybrid = None
#     iterator: Union[str, Callable] = more_itertools.collapse
#     options: ClassVar[sourdough.types.Catalog] = sourdough.types.Catalog(
#         contents = {
#             'task': sourdough.Step,
#             'technique': sourdough.Technique,
#             'Flow': sourdough.Component, sourdough.types.Hybrid})
