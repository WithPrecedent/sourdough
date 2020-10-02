"""
structures: sourdough iterables in composite objects
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
    """Base class for composite objects in sourdough projects.
    
    Distinguishing characteristics of an Aggregation:
        1) Order doesn't matter.
        2) All stored Components must be of the same type.
        3) Stored Components do not need to be connected.
        
    Args:
        contents (Sequence[Union[str, sourdough.Component]]): a list of str or
            Components. 
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Element is called, 'name' is set based upon
            the 'get_name' method in Element. If that method is not overridden 
            by a subclass instance, 'name' will be assigned to the snake case 
            version of the class name ('__class__.__name__').
    
    """
    contents: Sequence[Union[str, sourdough.Component]] = dataclasses.field(
        default_factory = list)
    name: str = None
       

@dataclasses.dataclass
class SerialWorker(sourdough.Worker, abc.ABC):
    """Base class for serial composite objects in sourdough projects.
        
    Args:
        contents (Sequence[Union[str, sourdough.Component]]): a list of str or
            Components. 
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Element is called, 'name' is set based upon
            the 'get_name' method in Element. If that method is not overridden 
            by a subclass instance, 'name' will be assigned to the snake case 
            version of the class name ('__class__.__name__').
    
    """
    contents: Sequence[Union[str, sourdough.Component]] = dataclasses.field(
        default_factory = list)
    name: str = None
             
    """ Required Subclass Methods """
    
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
class Pipeline(SerialWorker):
    """Base class for composite objects in sourdough projects.

    Distinguishing characteristics of a Contest:
        1) Follows a sequence of instructions (serial structure).
        2) It may pass data or other arguments to the next step in the sequence.
        3) Only one connection or path exists between each object.
        
    Args:
        contents (Sequence[Union[str, sourdough.Component]]): a list of str or
            Components. 
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Element is called, 'name' is set based upon
            the 'get_name' method in Element. If that method is not overridden 
            by a subclass instance, 'name' will be assigned to the snake case 
            version of the class name ('__class__.__name__').
    
    """
    contents: Sequence[Union[str, sourdough.Component]] = dataclasses.field(
        default_factory = list)
    name: str = None
            

@dataclasses.dataclass
class ParallelWorker(sourdough.Worker, abc.ABC):
    """Base class for parallel composite objects in sourdough projects.
        
    Args:
        contents (Sequence[Union[str, sourdough.Component]]): a list of str or
            Components. 
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Element is called, 'name' is set based upon
            the 'get_name' method in Element. If that method is not overridden 
            by a subclass instance, 'name' will be assigned to the snake case 
            version of the class name ('__class__.__name__').
    
    """
    contents: Sequence[Union[str, sourdough.Component]] = dataclasses.field(
        default_factory = list)
    iterations: int = 10
    criteria: str = None
    name: str = None
            
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
    """Base class for composite objects in sourdough projects.

    Distinguishing characteristics of a Contest:
        1) Repeats a Pipeline with different options (parallel structure).
        2) Chooses the best option based upon selected criteria.
        3) Each stored Component is only attached to the Contest with exactly 
            one connection (these connections are not defined separately - they
            are simply part of the parallel structure).
        
    Args:
        contents (Sequence[Union[str, sourdough.Component]]): a list of str or
            Components. 
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Element is called, 'name' is set based upon
            the 'get_name' method in Element. If that method is not overridden 
            by a subclass instance, 'name' will be assigned to the snake case 
            version of the class name ('__class__.__name__').
    
    """
    contents: Sequence[sourdough.Pipeline] = dataclasses.field(
        default_factory = list)
    iterations: int = 10
    criteria: str = None
    name: str = None
    
    
@dataclasses.dataclass
class Study(ParallelWorker):
    """Base class for composite objects in sourdough projects.

    Distinguishing characteristics of a Study:
        1) Repeats a Pipeline with different options (parallel structure).
        2) Maintains all of the repetitions without selecting or averaging the 
            results.
        3) Each stored Component is only attached to the Study with exactly 
            one connection (these connections are not defined separately - they
            are simply part of the parallel structure).
                      
    Args:
        contents (Sequence[Union[str, sourdough.Component]]): a list of str or
            Components. 
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Element is called, 'name' is set based upon
            the 'get_name' method in Element. If that method is not overridden 
            by a subclass instance, 'name' will be assigned to the snake case 
            version of the class name ('__class__.__name__').
    
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
    """Base class for composite objects in sourdough projects.

    Distinguishing characteristics of a Survey:
        1) Repeats a Pipeline with different options (parallel structure).
        2) Averages or otherwise combines the results based upon selected 
            criteria.
        3) Each stored Component is only attached to the Survey with exactly 
            one connection (these connections are not defined separately - they
            are simply part of the parallel structure).    
                    
    Args:
        contents (Sequence[Union[str, sourdough.Component]]): a list of str or
            Components. 
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Element is called, 'name' is set based upon
            the 'get_name' method in Element. If that method is not overridden 
            by a subclass instance, 'name' will be assigned to the snake case 
            version of the class name ('__class__.__name__').
    
    """
    contents: Sequence[sourdough.Pipeline] = dataclasses.field(
        default_factory = list)
    iterations: int = 10
    criteria: str = None
    name: str = None
        


@dataclasses.dataclass
class Technique(sourdough.quirks.Loader, sourdough.Element):
    """Base class for primitive objects in a sourdough composite object.
    
    The 'contents' and 'parameters' attributes are combined at the last moment
    to allow for runtime alterations.
    
    Args:
        contents (object): core object used by the 'perform' method. Defaults 
            to None.
        parameters (Mapping[Any, Any]]): parameters to be attached to
            'contents' when the 'perform' method is called. Defaults to an 
            empty dict.
        modules Union[str, Sequence[str]]: name(s) of module(s) where the 
            contents to load is/are located. Defaults to an empty list.
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
        _loaded (ClassVar[Mapping[Any, Any]]): dict of str keys and previously
            loaded objects. This is checked first by the 'load' method to avoid
            unnecessary re-importation. Defaults to an empty dict.
                                    
    """
    contents: object = None
    parameters: Mapping[Any, Any] = dataclasses.field(default_factory = dict)
    modules: Union[str, Sequence[str]] = dataclasses.field(
        default_factory = list)
    name: str = None
    _loaded: ClassVar[Mapping[Any, Any]] = {}

    """ Initialization Methods """
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Adds new subclass to 'library'.
        if not hasattr(cls, '_base'):
            cls._base = cls

    """ Properties """
    
    @property
    def algorithm(self) -> Union[object, str]:
        return self.contents
    
    @algorithm.setter
    def algorithm(self, value: Union[object, str]) -> None:
        self.contents = value
        return self
    
    @algorithm.deleter
    def algorithm(self) -> None:
        self.contents = None
        return self
        
    """ Public Methods """
    
    def perform(self, data: object = None, **kwargs) -> object:
        """Applies stored 'contents' with 'parameters'.
        
        Args:
            data (object): optional object to apply 'contents' to. Defaults to
                None.
                
        Returns:
            object: with any modifications made by 'contents'. If data is not
                passed, nothing is returned.        
        
        """
        self.contents = self.load(key = self.name)
        if data is None:
            self.contents.perform(**self.parameters, **kwargs)
            return self
        else:
            return self.contents.perform(data, **self.parameters, **kwargs)

             
@dataclasses.dataclass
class Step(sourdough.Element):
    """Wrapper for a Technique.

    Subclasses of Step can store additional methods and attributes to apply to 
    all possible technique instances that could be used. This is often useful 
    when creating 'comparative' Worker instances which test a variety of 
    strategies with similar or identical parameters and/or methods.

    A Step instance will try to return attributes from 'technique' if the
    attribute is not found in the Step instance. 

    Args:
        technique (Technique): technique object for this Worker in a sourdough
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
        contains (ClassVar[Sequence[str]]): list of snake-named base class
            types that can be stored in this component. Defaults to a list
            containing 'technique'.
        containers (ClassVar[Sequence[str]]): list of snake-named base class
            types that can store this component. Defaults to a list containing
            'Worker' and 'manager'. 
                        
    """
    contents: Union['Technique', str] = None
    name: str = None

    """ Initialization Methods """
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Adds new subclass to 'library'.
        if not hasattr(cls, '_base'):
            cls._base = cls
                
    """ Properties """
    
    @property
    def technique(self) -> Union['Technique', str]:
        return self.contents
    
    @technique.setter
    def technique(self, value: Union['Technique', str]) -> None:
        self.contents = value
        return self
    
    @technique.deleter
    def technique(self) -> None:
        self.contents = None
        return self
    
    """ Public Methods """
    
    def perform(self, data: object = None, **kwargs) -> object:
        """Subclasses must provide their own methods.
        
        The code below outlines a basic method that a subclass should build on
        for a properly functioning Step.
        
        Applies stored 'contents' with 'parameters'.
        
        Args:
            data (object): optional object to apply 'contents' to. Defaults to
                None.
                
        Returns:
            object: with any modifications made by 'contents'. If data is not
                passed, nothing is returned.        
        
        """
        if data is None:
            self.contents.perform(**kwargs)
            return self
        else:
            return self.contents.perform(item = data, **kwargs)

    """ Dunder Methods """

    def __getattr__(self, attribute: str) -> Any:
        """Looks for 'attribute' in 'contents'.

        Args:
            attribute (str): name of attribute to return.

        Raises:
            AttributeError: if 'attribute' is not found in 'contents'.

        Returns:
            Any: matching attribute.

        """
        try:
            return getattr(self.contents, attribute)
        except AttributeError:
            raise AttributeError(
                f'{attribute} neither found in {self.name} nor '
                f'{self.contents}') 

        

# @dataclasses.dataclass
# class Graph(sourdough.Worker, sourdough.Component):
#     """Base class for composite objects in sourdough projects.

#     Distinguishing characteristics of a Graph:
#         1) Iteration is not defined by ordering of contents.
#         2) Incorporates Edges as part of its structure.
#         3) All Components must be connected (sourdough does not presently
#             support graphs with unconnected graphs).
            
#     Args:
#         contents (Sequence[Union[str, sourdough.Component]]): a list of str or
#             Components. 
#         name (str): designates the name of a class instance that is used for 
#             internal referencing throughout sourdough. For example if a 
#             sourdough instance needs settings from a Settings instance, 'name' 
#             should match the appropriate section name in the Settings instance. 
#             When subclassing, it is sometimes a good idea to use the same 'name' 
#             attribute as the base class for effective coordination between 
#             sourdough classes. Defaults to None. If 'name' is None and 
#             '__post_init__' of Element is called, 'name' is set based upon
#             the 'get_name' method in Element. If that method is not 
#             overridden by a subclass instance, 'name' will be assigned to the 
#             snake case version of the class name ('__class__.__name__').
    
#     """
#     contents: Sequence[Union[str, sourdough.Component]] = dataclasses.field(
#         default_factory = list)
#     name: str = None


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
#         for key in project.components.library.keys():
#             suffix = f'_{key}s'
#             structures[key] = {
#                 k: v for k, v in settings.items() if k.endswith(suffix)} 
            
#         return {k: v for k, v in project.components.library.items()}
    
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
  

# @dataclasses.dataclass
# class Graph(Role):
    
#     name: str = None
#     Worker: sourdough.Worker = None
#     iterator: Union[str, Callable] = 'iterator'    
#     options: ClassVar[sourdough.Catalog] = sourdough.Catalog(
#         contents = {
#             'edge': sourdough.Edge,
#             'node': sourdough.Node})
        
    # contents: Sequence[Union[sourdough.Component, str]] = dataclasses.field(
    #     default_factory = list)
    # design: str = 'chained'
    # identification: str = None
    # data: Any = None    
    # edges: Union[Sequence[sourdough.Edge],
    #     Sequence[Sequence[str]], 
    #     Mapping[Any, Sequence[str]]] = dataclasses.field(default_factory = list)
    # options: ClassVar[sourdough.Catalog] = sourdough.Catalog()  

    # """ Initialization Methods """
    
    # def __post_init__(self) -> None:
    #     """Initializes class instance attributes."""
    #     # Calls parent and/or mixin initialization method(s).
    #     super().__post_init__()
    #     # Converts 'contents' to the proper design.
    #     if isinstance(self.edges, dict):
    #         adjacency = copy.deepcopy(self.contents)
    #         self.contents = []
    #         self.from_dict(adjacency = adjacency)
    #     elif any(self.edges, tuple):
    #         adjacency = copy.deepcopy(self.contents)
    #         self.contents = []
    #         self.from_list(adjacency = adjacency)
           
    # """ Public Methods """
    
    # def from_dict(self, adjacency: Mapping[Any, Sequence[str]]) -> None:
    #     """[summary]

    #     Args:
    #         adjacency (MutableMapping[Any, Sequence[str]]): [description]

    #     Returns:
    #         [type]: [description]
    #     """
    #     for key, value in adjacency.items():
    #         self.add_node(name = key)
    #         self.add_edge(start = value[0], stop = value[1])
    #     return self

    # def from_list(self, adjacency: Sequence[Union[str]]) -> None:
    #     """[summary]

    #     Args:
    #         adjacency (MutableSequence[Union[str]]): [description]

    #     Returns:
    #         [type]: [description]
    #     """
    #     for item in adjacency:
    #         if item not in self.contents:
    #             self.add_node(name = item)
    #         self.add_edge(start = item[0], stop = item[1])
    #     return self
          
    # def add_node(self,
    #         name: str = None,
    #         element: sourdough.Component = None) -> None:
    #     """Adds a node to the graph."""
    #     if element and not name:
    #         name = element.name
    #     elif not name:
    #         raise ValueError('element or name must be passed to add_node')
    #     node = sourdough.Component(name = name, element = element)
    #     self.contents.append(node)
    #     return self

    # def add_edge(self, start: str, stop: str) -> None:
    #     """[summary]

    #     Args:
    #         start (str): [description]
    #         stop (str): [description]

    #     Raises:
    #         KeyError: [description]
    #         KeyError: [description]

    #     Returns:
    #         [type]: [description]
            
    #     """
    #     if start not in self.contents:
    #         raise KeyError(f'{start} is not in the graph')
    #     if stop not in self.contents:
    #         raise KeyError(f'{stop} is not in the graph')
    #     test_graph = copy.deepcopy(self.contents)
    #     test_graph[start].descendents.append(stop)
    #     test_graph[stop].predecessors.append(start)
    #     self._validate_graph(graph = test_graph)     
    #     self.contents[start].descendents.append(stop)
    #     self.contents[stop].predecessors.append(start)
    #     return self

    # def delete_node(self, name: str) -> None:
    #     """Deletes node from graph.
        
    #     """
    #     del self.contents[name]
    #     for node in self.contents:
    #         node.predecessors = [p for p in node.predecessors if p != name]
    #         node.descendents = [d for d in node.descendents if d != name]
    #     return self

    # def delete_edge(self, 
    #         start: str, stop: str) -> None:
    #     """[summary]

    #     Args:
    #         start (str): [description]
    #         stop (str): [description]

    #     Raises:
    #         KeyError: [description]

    #     Returns:
    #         [type]: [description]
    #     """
    #     try:
    #         self.contents[start].descendants.remove(stop)
    #         self.contents[stop].predecessors.remove(start)
    #     except KeyError:
    #         raise KeyError(f'edge not found in the graph')
    #     return self

    # def predecessors(self, 
    #         name: str,
    #         recursive: bool = False) -> Sequence[str]:
    #     """[summary]

    #     Args:
    #         name ([type]): [description]

    #     Returns:
    #         [type]: [description]
            
    #     ToDo:
    #         Add recursive functionality.
            
    #     """
    #     return self.contents[name].predecessors
                 
    # def descendants(self, 
    #         name: str,
    #         recursive: bool = False) -> Sequence[str]:
    #     """[summary]

    #     Args:
    #         node ([type]): [description]

    #     Returns:
    #         [type]: [description]
            
    #     ToDo:
    #         Add recursive functionality.
            
    #     """
    #     return self.contents[name].descendents

    # """ Dunder Methods """
    
    # def __iter__(self) -> Iterable:
    #     """Returns iterable of sorted graph.
        
    #     Returns:
    #         Iterable: based upon the 'get_sorted' method of a subclass.
        
    #     """
    #     return iter(self.get_sorted(return_elements = True))
    
    # def __repr__(self) -> str:
    #     """Returns '__str__' representation.

    #     Returns:
    #         str: default string representation of an instance.

    #     """
    #     return self.__str__()
    
    # def __str__(self) -> str:
    #     """Returns default string representation of an instance.

    #     Returns:
    #         str: default string representation of an instance.

    #     """
    #     return '\n'.join([textwrap.dedent(f'''
    #         sourdough {self.__class__.__name__}
    #         name: {self.name}
    #         nodes:'''),
    #         f'''{textwrap.indent(str(self.contents), '    ')}
    #         edges:
    #         {textwrap.indent(str(self.edges), '    ')}'''])   
         
    # """ Private Methods """
    
    # def _topological_sort(self, 
    #         graph: sourdough.Worker) -> Sequence[sourdough.Component]:
    #     """[summary]

    #     Returns:
    #         [type]: [description]
            
    #     """
    #     searched = []
    #     return self._topological_descend(
    #         graph = graph, 
    #         node = graph.root,
    #         searched = searched)
        
    # def _topological_descend(self, 
    #         graph: sourdough.Worker, 
    #         node: sourdough.Component,
    #         searched: list[str]) -> Sequence[sourdough.Component]: 
    #     """[summary]

    #     Returns:
    #         [type]: [description]
            
    #     """
    #     sorted_queue = []      
    #     for descendent in node.descendents:
    #         if graph[descendent] not in searched:
    #             searched.insert(descendent, 0)
    #             sorted_queue.extend(self._dfs_descend(
    #                 graph = graph,
    #                 node = graph[descendent],
    #                 searched = searched))
    #     return sorted_queue    
    
    # def _dfs_sort(self, 
    #         graph: sourdough.Worker) -> Sequence[sourdough.Component]:
    #     """[summary]

    #     Returns:
    #         [type]: [description]
            
    #     """
    #     searched = []
    #     return self._dfs_descend(
    #         graph = graph, 
    #         node = graph.root,
    #         searched = searched)
        
    # def _dfs_descend(self, 
    #         graph: sourdough.Worker, 
    #         node: sourdough.Component,
    #         searched: list[str]) -> Sequence[sourdough.Component]: 
    #     """[summary]

    #     Returns:
    #         [type]: [description]
    #     """
    #     sorted_queue = []      
    #     for descendent in node.descendents:
    #         if graph[descendent] not in searched:
    #             searched.append(descendent)
    #             sorted_queue.extend(self._dfs_descend(
    #                 graph = graph,
    #                 node = graph[descendent],
    #                 searched = searched))
    #     return sorted_queue    
    #     """ Properties """
    
    # @property
    # def root(self) -> sourdough.Component:
    #     """[summary]

    #     Raises:
    #         ValueError: [description]
    #         ValueError: [description]

    #     Returns:
    #         [type]: [description]
    #     """
    #     rootless = [v for v in self.nodees if not self.predecessors]
    #     if len(rootless) > 1:
    #         raise ValueError('graph is not acyclic - it has more than 1 root')
    #     elif len(rootless) == 0:
    #         raise ValueError('graph is not acyclic - it has no root')
    #     else:
    #         return rootless[0]
 
    # @property
    # def endpoints(self) -> Sequence[sourdough.Component]:
    #     """[summary]

    #     Returns:
    #         [type]: [description]
            
    #     """
    #     return [v for v in self.contents if not v.descendents]

    # """ Public Methods """
        
    # def get_sorted(self, 
    #         graph: sourdough.Worker = None,
    #         return_elements: bool = False) -> Sequence[sourdough.Component]:
    #     """Performs a topological sort on 'graph'.
        
    #     If 'graph' is not passed, the 'contents' attribute is used instead.
        
    #     Args:
    #         graph:
    #     """
    #     if graph is None:
    #         graph = self.contents
    #     sorted_queue = self._topological_sort(graph = graph)
    #     if return_elements:
    #         return [v.element for v in sorted_queue]
    #     else:
    #         return sorted_queue

    # def validate(self, graph: sourdough.Worker) -> None:
    #     """
        

    #     Args:
    #         graph ([type]): [description]

    #     Raises:
    #         ValueError: if topological sort fails.
    #         ValueError: if the root check fails.
            
    #     """
    #     try:
    #         self.get_sorted(graph = graph)
    #     except ValueError:
    #         raise ValueError(f'graph failed the topological sort test')
    #     test_root = self.root()
    #     return self
