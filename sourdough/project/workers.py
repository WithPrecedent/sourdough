"""
workers: structured iterables in sourdough projects
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
class Aggregation(sourdough.Worker):
    """Aggregates unordered objects.
    
    Distinguishing characteristics of an Aggregation:
        1) Order doesn't matter.
        2) Stored Components do not need to be connected. If attributes of the
            stored Components created connections, those connections will be 
            left in tact.
        
    Args:
        contents (Sequence[Union[str, Component]]): a list of str or Components. 
            Defaults to an empty set.
        name (str): property which designates the internal reference of a class 
            instance that is used throughout sourdough. For example, if a 
            sourdough instance needs options from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            Defaults to None. If 'name' is None, it will be assigned to the 
            snake case version of the class name ('__name__' or 
            '__class__.__name__').
    
    """
    contents: Sequence[Union[str, sourdough.Component]] = dataclasses.field(
        default_factory = set)
    name: str = None
       

@dataclasses.dataclass
class SerialWorker(sourdough.Worker, abc.ABC):
    """Base class for serially structures Workers in sourdough projects.
        
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
class Cycle(SerialWorker):
    """Ordered sourdough Components which will be repetitively called.

    Distinguishing characteristics of a Pipeline:
        1) Follows a sequence of instructions (serial structure).
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
class Pipeline(SerialWorker):
    """Ordered sourdough Components without branching.

    Distinguishing characteristics of a Pipeline:
        1) Follows a sequence of instructions (serial structure).
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
class ParallelWorker(sourdough.Worker, abc.ABC):
    """Base class for parallelly structured Workers in sourdough projects.
        
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
class Contest(ParallelWorker):
    """Stores Workers in a comparative parallel structure and chooses best.

    Distinguishing characteristics of a Contest:
        1) Repeats a Pipeline with different options (parallel structure).
        2) Chooses the best option based upon selected criteria.
        3) Each stored Component is only attached to the Contest with exactly 
            one connection (these connections are not defined separately - they
            are simply part of the parallel structure).
        
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
class Study(ParallelWorker):
    """Stores Workers in a comparative parallel structure.

    Distinguishing characteristics of a Study:
        1) Repeats a Pipeline with different options (parallel structure).
        2) Maintains all of the repetitions without selecting or averaging the 
            results.
        3) Each stored Component is only attached to the Study with exactly 
            one connection (these connections are not defined separately - they
            are simply part of the parallel structure).
                      
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

    """ Public Methods """
    
    def organize(self, settings: sourdough.Settings) -> None:
        """[summary]

        Args:
            structure (sourdough.Worker): [description]

        Returns:
            sourdough.Worker: [description]
        """
        # new_contents = []
        # steps = list(self.contents.keys())
        # possible = list(self.contents.values())
        # permutations = list(map(list, itertools.product(*possible)))
        # for pipeline in permutations:
        #     instance = Pipeline()
        #     for item in pipeline:
        #         if isinstance(item, Sequence):
                    
        #         else:
                    
        #         component = self._get_component(
        #             key = item, 
        #             generic = self.contents.generic)
        #         if isinstance(item, sourdough.Worker):
        #             self.organize()
        #     new_contents.append(instance)
        # self.contents = new_contents
        return self
        
    
@dataclasses.dataclass
class Survey(ParallelWorker):
    """Stores Workers in a comparative parallel structure and averages results.

    Distinguishing characteristics of a Survey:
        1) Repeats a Pipeline with different options (parallel structure).
        2) Averages or otherwise combines the results based upon selected 
            criteria.
        3) Each stored Component is only attached to the Survey with exactly 
            one connection (these connections are not defined separately - they
            are simply part of the parallel structure).    
                    
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
#         sourdough.quirks.Registry, 
#         sourdough.Element, 
#         abc.ABC):
#     """Base class related to constructing and iterating Worker instances.
    
#     """
#     name: str = None
#     workflow: sourdough.Workflow = None
#     iterations: int = 1
#     library: ClassVar[sourdough.Catalog] = sourdough.Catalog(
#         stored_types = ('Role'))

#     """ Initialization Methods """
    
#     def __post_init__(self) -> None:
#         """Initializes class instance attributes."""
#         # Calls parent and/or mixin initialization method(s).
#         super().__post_init__()
#         # Sets 'index' for current location in 'Worker' for the iterator.
#         self.index: int = -1

#     """ Required Subclass Methods """

#     @abc.abstractmethod
#     def organize(self, Worker: sourdough.Worker) -> sourdough.Worker:
#         pass
 
#     @abc.abstractmethod
#     def finalize(self, Worker: sourdough.Worker) -> sourdough.Worker:
#         pass
    
#     """ Class Methods """

#     @classmethod
#     def validate(cls, Worker: sourdough.Worker) -> sourdough.Worker:
#         """Returns a Role instance based upon 'structure'.
        
#         Args:
#             Worker (sourdough.Worker): Hybrid instance with 'structure' attribute
#                 to be validated.
                
#         Raises:
#             TypeError: if 'Worker.structure' is neither a str nor Role type.
            
#         Returns:
#             sourdough.Worker: with a validated 'structure' attribute.
            
#         """
#         if isinstance(Worker.structure, str):
#             Worker.structure = cls.library[Worker.structure]()
#         elif (inspect.isclass(Worker.structure) 
#                 and issubclass(Worker.structure, cls)):
#             Worker.structure = Worker.structure() 
#         elif isinstance(Worker.structure, cls):
#             Worker.structure.__post_init__()
#         else:
#             raise TypeError(
#                 f'The structure attribute of Worker must be a str or {cls} type')
#         return Worker

#     """ Public Methods """
    
#     def iterate(self, Worker: sourdough.Worker) -> Iterable:
#         return more_itertools.collapse(Worker.contents)

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
#         structures = {}
#         for key in project.components.inventory.keys():
#             suffix = f'_{key}s'
#             structures[key] = {
#                 k: v for k, v in settings.items() if k.endswith(suffix)} 
            
#         return {k: v for k, v in project.components.inventory.items()}
    
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
#             print('test wrapped', wrapped)
#             for item in wrapped:
#                 print('test item in wrapped', item)
#                 kwargs.update({generic.contains: key})
#                 component = project.component.instance(key = key, **kwargs)
#                 self.Worker.add(component) 
#         # Otherwise uses the appropriate generic type.
#         else:
#             for item in wrapped:
#                 kwargs.update({'name': key, generic.contains: key})
#                 self.Worker.add(generic(**kwargs)) 
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
#         self.Worker.add(component)
#         return self  
           
      
# @dataclasses.dataclass
# class Obey(Role):
    
#     name: str = None
#     workflow: sourdough.Workflow = None
#     iterations: int = 1
    
#     """ Public Methods """

#     def organize(self, Worker: sourdough.Worker) -> sourdough.Worker:
#         pass

#     def finalize(self, Worker: sourdough.Worker) -> sourdough.Worker:
#         pass

      
# @dataclasses.dataclass
# class Repeat(Role):
    
#     name: str = None
#     workflow: sourdough.Workflow = None
#     iterations: int = 2
    
#     """ Public Methods """

#     def organize(self, Worker: sourdough.Worker) -> sourdough.Worker:
#         pass
    
#     def iterate(self, Worker: sourdough.Worker) -> Iterable:
#         return itertools.repeat(Worker.contents, self.iterations)
        
#     def finalize(self, Worker: sourdough.Worker) -> sourdough.Worker:
#         pass
       
         
# @dataclasses.dataclass
# class Compare(Role):
    
#     name: str = None
#     workflow: sourdough.Workflow = None
#     iterations: int = 1

#     """ Public Methods """

#     def organize(self, Worker: sourdough.Worker) -> sourdough.Worker:
#         """[summary]

#         Args:
#             Worker (sourdough.Worker): [description]

#         Returns:
#             sourdough.Worker: [description]
#         """
#         steps = components.pop([components.keys()[0]])
#         possible = list(components.values())
#         permutations = list(map(list, itertools.product(*possible)))
#         for i, contained in enumerate(permutations):
#             instance = sourdough.Worker(
#                 _components = tuple(zip(steps, contained)))
#         return Worker
    
#     def finalize(self, Worker: sourdough.Worker) -> sourdough.Worker:
#         pass

         
# @dataclasses.dataclass
# class Judge(Role):
    
#     name: str = None
#     workflow: sourdough.Workflow = None
#     iterations: int = 10

#     """ Public Methods """

#     def organize(self, Worker: sourdough.Worker) -> sourdough.Worker:
#         pass
    
#     def finalize(self, Worker: sourdough.Worker) -> sourdough.Worker:
#         pass
    

# @dataclasses.dataclass
# class Survey(Role):
    
#     name: str = None
#     workflow: sourdough.Workflow = None
#     iterations: int = 10
    
#     """ Public Methods """

#     def organize(self, Worker: sourdough.Worker) -> sourdough.Worker:
#         pass
    
#     def finalize(self, Worker: sourdough.Worker) -> sourdough.Worker:
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
#     Worker: sourdough.Worker = None
#     iterator: Union[str, Callable] = more_itertools.collapse
#     options: ClassVar[sourdough.Catalog] = sourdough.Catalog(
#         contents = {
#             'task': sourdough.Step,
#             'technique': sourdough.Technique,
#             'Worker': sourdough.Worker})
