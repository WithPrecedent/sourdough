"""
components: sourdough composite objects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Structure (Sequencify, Hybrid, Component): type validated iterable in 
        sourdough composite objects. Structure instances can only contain
        Component instances (including other Structure instances). All structure
        subclasses must have 'iterate', 'activate', and 'finalize' methods.
    Technique (Component, Action): primitive object which performs some action.
    Step (Component, Action): wrapper for Technique which performs some action 
        (optional). Step can be useful when using Role subclasses with parallel
        structures such as Compare and Survey.

"""

from __future__ import annotations
import abc
import dataclasses
import itertools
import more_itertools
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union

import sourdough


@dataclasses.dataclass
class Overview(sourdough.base.Lexicon):
    """Dictionary of different Element types in a Structure instance.
    
    Args:
        contents (Mapping[Any, Any]]): stored dictionary. Defaults to an empty 
            dict.
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
    contents: Mapping[Any, Any] = dataclasses.field(default_factory = dict)
    name: str = None
    structure: sourdough.Structure = None
    
    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent initialization method(s).
        super().__post_init__()
        if self.structure.structure is not None:
            self.add({
                'name': self.structure.name, 
                'structure': self.structure.structure.name})
            for key, value in self.structure.structure.options.items():
                matches = self.structure.find(
                    self._get_type, 
                    element = value)
                if len(matches) > 0:
                    self.contents[f'{key}s'] = matches
        else:
            raise ValueError(
                'structure must be a Role for an overview to be created.')
        return self          
    
    """ Dunder Methods """
    
    def __str__(self) -> str:
        """Returns pretty string representation of an instance.
        
        Returns:
            str: pretty string representation of an instance.
            
        """
        new_line = '\n'
        representation = [f'sourdough {self.get_name}']
        for key, value in self.contents.items():
            if isinstance(value, Sequence):
                names = [v.name for v in value]
                representation.append(f'{key}: {", ".join(names)}')
            else:
                representation.append(f'{key}: {value}')
        return new_line.join(representation)    

    """ Private Methods """

    def _get_type(self, 
            item: sourdough.base.Element, 
            element: sourdough.base.Element) -> Sequence[sourdough.base.Element]: 
        """[summary]

        Args:
            item (self.stored_types): [description]
            self.stored_types (self.stored_types): [description]

        Returns:
            Sequence[self.stored_types]:
            
        """
        if isinstance(item, element):
            return [item]
        else:
            return []


@dataclasses.dataclass
class Structure(
        sourdough.quirks.Sequencify,
        sourdough.base.Hybrid,
        Component):
    """Base class for composite objects in sourdough projects.
    
    Structure differs from an ordinary Hybrid in 1 significant way:
        1) It is mixed in with Sequencify which allows for type validation and 
            conversion, using the 'verify' and 'convert' methods.
            
    Args:
        contents (Sequence[Union[str, Component]]): a list of str or Components. 
            Defaults to an empty list.
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
    contents: Sequence[Union[str, Component]] = dataclasses.field(
        default_factory = list)
    name: str = None

    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent initialization method(s).
        super().__post_init__()        
        # Initializes 'index' for iteration.
        self.index = -1
            
    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def iterate(self, **kwargs) -> Iterable:
        pass
    
    @abc.abstractmethod
    def activate(self, **kwargs) -> Iterable:
        pass    
    
    @abc.abstractmethod
    def finalize(self, **kwargs) -> Iterable:
        pass
  
    """ Dunder Methods """
    
    def __iter__(self) -> Iterable:
        if self.index + 1 < len(self.contents):
            self.index += 1
            yield self.iterate()
        else:
            raise StopIteration

    
@dataclasses.dataclass
class Aggregation(sourdough.Structure, sourdough.Component):
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
class SerialStructure(sourdough.Structure, sourdough.Component, abc.ABC):
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
    
    @abc.abstractmethod
    def iterate(self, **kwargs) -> Iterable:
        pass
    
    @abc.abstractmethod
    def activate(self, **kwargs) -> Iterable:
        pass    
    
    @abc.abstractmethod
    def finalize(self, **kwargs) -> Iterable:
        pass
            
    
@dataclasses.dataclass
class Pipeline(SerialStructure):
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
class ParallelStructure(sourdough.Structure, sourdough.Component, abc.ABC):
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
    
    @abc.abstractmethod
    def organize(self, **kwargs) -> Iterable:
        pass
    
    @abc.abstractmethod
    def iterate(self, **kwargs) -> Iterable:
        pass
    
    @abc.abstractmethod
    def activate(self, **kwargs) -> Iterable:
        pass    
    
    @abc.abstractmethod
    def finalize(self, **kwargs) -> Iterable:
        pass


@dataclasses.dataclass
class Contest(ParallelStructure):
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
class Study(ParallelStructure):
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
            structure (sourdough.Structure): [description]

        Returns:
            sourdough.Structure: [description]
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
        #         if isinstance(item, sourdough.Structure):
        #             self.organize()
        #     new_contents.append(instance)
        # self.contents = new_contents
        return self
        
    
@dataclasses.dataclass
class Survey(ParallelStructure):
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
        
        

# @dataclasses.dataclass
# class Graph(sourdough.Structure, sourdough.Component):
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
 
 
 
    
@dataclasses.dataclass
class Technique(sourdough.base.Loader, sourdough.Component):
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
class Step(sourdough.Component):
    """Wrapper for a Technique.

    Subclasses of Step can store additional methods and attributes to apply to 
    all possible technique instances that could be used. This is often useful 
    when creating 'comparative' Structure instances which test a variety of 
    strategies with similar or identical parameters and/or methods.

    A Step instance will try to return attributes from 'technique' if the
    attribute is not found in the Step instance. 

    Args:
        technique (Technique): technique object for this Structure in a sourdough
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
            'Structure' and 'manager'. 
                        
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
# class Edge(Component):
#     """An edge in a sourdough Graph.

#     'start' and 'stop' are the ends of the Edge. However, which value is 
#     assigned to each attribute only matters in a directional graph.

#     By default Edge is slotted so that no other attributes can be added. This
#     lowers memory consumption and increases speed. If you wish to add more 
#     functionality to your Graph edges, you should subclass Edge.

#     Args:
#         start (str): name of the Component where the edge starts.
#         stop (str): name of the Component where the edge ends.
#         directed (bool): whether this edge is directed (True). Defaults to 
#             False. 
#         weight (float): a weight value assigned to this edge. Defaults to None.

#     """
#     start: sourdough.Node = None
#     stop: sourdough.Node = None
#     directed: bool = False
#     weight: float = 1.0
#     name: str = None
    
#     """ Public Methods """

#     # def get_name(self) -> str:
#     #     """Returns 'name' based upon attached nodes.
        
#     #     Returns:
#     #         str: name of class for internal referencing.
        
#     #     """
#     #     return f'{self.start.name}_to_{self.stop.name}'


# @dataclasses.dataclass
# class Node(Component):
#     """An edge in a sourdough Graph.

#     'start' and 'stop' are the ends of the Edge. However, which value is 
#     assigned to each attribute only matters in a directional graph.

#     By default Edge is slotted so that no other attributes can be added. This
#     lowers memory consumption and increases speed. If you wish to add more 
#     functionality to your Graph edges, you should subclass Edge.

#     Args:
#         start (str): name of the Component where the edge starts.
#         stop (str): name of the Component where the edge ends.
#         directed (bool): whether this edge is directed (True). Defaults to 
#             False. 
#         weight (float): a weight value assigned to this edge. Defaults to None.

#     """

#     name: str = None
#     edges: Sequence['Edge'] = dataclasses.field(default_factory = list)


       