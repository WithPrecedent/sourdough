"""
structures: common design patterns and structures adapted to sourdough
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:

    
"""
from __future__ import annotations
import abc
import collections.abc
import dataclasses
import itertools
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import sourdough


""" Builder Structure """


@dataclasses.dataclass
class Constructor(abc.ABC):
    """Abstract base class for sourdough builders.
    
    Subclasses must have a 'create' method.
    
    """

    @abc.abstractmethod
    def create(self, **kwargs) -> Any:
        """Subclasses must provide their own methods."""
        pass
    

@dataclasses.dataclass
class Builder(sourdough.types.Lexicon, Constructor):
    """Builds complex class instances.

    For any parameters which require further construction code, a subclass
    should include a method named '_get_{name of a key in 'contents'}'. That
    method should return the value for the named parameter.

    Args:
        contents (Mapping[Any, Any]): keys are the names of the parameters to
            pass when an object is created. Values are the defaults to use when
            there is not a method named with this format: '_get_{key}'. Keys
            are iterated in order when the 'create' method is called. Defaults
            to an empty dict.
        base (Type): a class that can either be a class to create an instance
            from or a class with a 'registry' attribute that holds stored
            classes. If a user intends to get a class stored in the 'registry'
            attribute, they need to pass a 'name' argument to the 'create' 
            method which corresponds to a key in the registry. Defaults to None.
        
    """
    contents: Mapping[Any, Any] = dataclasses.field(default_factory = dict)
    base: Type = None

    def create(self, name: str = None, **kwargs) -> object:
        """Builds and returns an instance based on 'name' and 'kwargs'.

        Args:
            name (str): name of a class stored in 'base.registry.' If there is
                no registry, 'name' is None, or 'name' doesn't match a key in
                'base.registry', then an instance of 'base' is returned.
            kwargs (Dict[Any, Any]): any specific parameters that a user wants
                passed to a class when an instance is created.

        Returns:
            object: an instance of a stored class.
            
        """
        for parameter in self.contents.keys():
            if parameter not in kwargs:
                try:
                    method = getattr(self, f'_get_{parameter}')
                    kwargs[parameter] = method(name = name, **kwargs)
                except KeyError:
                    kwargs[parameter] = self.contents[parameter]
        product = self.get_product(name = name, **kwargs)
        return product(**kwargs) 
    
    def get_product(self, name: str) -> Type:
        """Returns a class stored in 'base.registry' or 'base'.

        Args:
            name (str): the name of the sought class corresponding to a key in
                'base.registry'. If 'name' is None or doesn't match a key in
                'base.registry', the class listed in 'base' is returned instead.

        Returns:
            Type: a stored class.
            
        """
        try:
            product = self.base.registry.acquire(key = name)
        except (KeyError, AttributeError, TypeError):
            product = self.base
        return product  
    

@dataclasses.dataclass  
class Director(sourdough.types.Lexicon, Constructor):
    """Directs and stores objects created by a builder.
    
    A Director is not necessary, but provides a convenient way to store objects
    created by a sourdough builder.
    
    Args:
        contents (Mapping[str, object]): keys are names of objects stored and 
            values are the stored object. Defaults to an empty dict.
        builder (Abstract Builder): related builder which constructs objects to
            be stored in 'contents'.
    
    """
    contents: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    builder: Constructor = None
    
    """ Public Methods """
    
    def create(self, name: str = None, **kwargs) -> None:
        """Builds and stores an instance based on 'name' and 'kwargs'.

        Args:
            name (str): name of a class stored in 'builder.base.registry.' If 
                there is no registry, 'name' is None, or 'name' doesn't match a 
                key in 'builder.base.registry', then an instance of 
                'builder.base' is instanced and stored.
            kwargs (Dict[Any, Any]): any specific parameters that a user wants
                passed to a class when an instance is created.
            
        """
        self.contents[name] = self.builder.create(name = name, **kwargs)
        return self


""" Composite Structures """


@dataclasses.dataclass
class Element(collections.abc.Container, abc.ABC):
    """Provides a 'name' attribute to a part of a composite structure.

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Configuration instance, 
            'name' should match the appropriate section name in a Configuration 
            instance. Defaults to None. 

    """
    contents: collections.abc.Container = None
    name: str = None
    
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Sets 'name' attribute.
        if not hasattr(self, 'name') or self.name is None:  
            self.name = self._get_name()
        # Calls parent and/or mixin initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass

    """ Private Methods """
    
    def _get_name(self) -> str:
        """Returns snakecase of the class name.

        If a user wishes to use an alternate naming system, a subclass should
        simply override this method. 
        
        Returns:
            str: name of class for internal referencing and some access methods.
        
        """
        return sourdough.tools.snakify(self.__class__.__name__)

    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def apply(self, data: Any = None, **kwargs) -> Any:
        """Subclasses must provide their own methods."""
        pass 
    

@dataclasses.dataclass
class Node(Element, sourdough.types.Lexicon):

    contents: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    name: str = None

    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def apply(self, data: Any = None, **kwargs) -> Any:
        """Subclasses must provide their own methods."""
        pass 


@dataclasses.dataclass
class Component(Element, sourdough.types.Hybrid):
    
    contents: Sequence[Element] = dataclasses.field(default_factory = list) 
    name: str = None
    
    """ Public Methods """
    
    def apply(self, data: Any = None, **kwargs) -> Any:
        """[summary]

        Args:
            data (Any, optional): [description]. Defaults to None.

        Returns:
            Any: [description]
        """
        for node in self.contents:
            if data is None:
                node.apply(data = data, **kwargs)
            else:
                data = node.apply(data = data, **kwargs)
        if data is None:
            return self
        else:
            return data
        
    
@dataclasses.dataclass
class Leaf(Element, collections.abc.Container):

    contents: Callable = None 
    name: str = None
    
    """ Public Methods """
    
    def apply(self, data: Any = None, **kwargs) -> Any:
        """[summary]

        Args:
            data (Any, optional): [description]. Defaults to None.

        Returns:
            Any: [description]
        """
        return self.contents(data = data, **kwargs)


@dataclasses.dataclass
class Graph(Element, sourdough.types.Lexicon):
    """Stores a directed acyclic graph (DAG).
    
    Internally, the graph nodes are stored in 'contents'. And the edges are
    stored as an adjacency list in 'edges' with the 'name' attributes of the
    nodes in 'contents' acting as the starting and stopping nodes in 'edges'.
    
    
    """  
    contents: Mapping[str, Node] = dataclasses.field(default_factory = dict)
    name: str = None
    edges: Mapping[str, Sequence[str]] = dataclasses.field(
        default_factory = dict)

    """ Properties """
    
    @property
    def root(self) -> str:
        """[summary]

        Raises:
            ValueError: [description]
            ValueError: [description]

        Returns:
            str: [description]
        """
        descendants = itertools.chain(self.edges.values())
        roots = [k for k in self.edges.keys() if k not in descendants]
        if len(roots) > 1:
            raise ValueError('Graph is not acyclic - it has more than 1 root')
        elif len(roots) == 0:
            raise ValueError('Graph is not acyclic - it has no root')
        else:
            return roots[0]
           
    @property
    def end(self) -> str:
        """[summary]

        Raises:
            ValueError: [description]
            ValueError: [description]

        Returns:
            str: [description]
        """
        ends = [k for k in self.edges.keys() if not self.edges[k]]
        if len(ends) > 1:
            return ends
        elif len(ends) == 0:
            raise ValueError('Graph is not acyclic - it has no endpoint')
        else:
            return ends[0]
            
    @property
    def permutations(self) -> List[List[str]]:
        """
        """
        return self._find_all_paths(start = self.root, end = self.end)
        
    """ Public Methods """
          
    def add_node(self, node: Node) -> None:
        """Adds a node to the graph.
            
        """
        self.contents[node.name] = node
        return self

    def add_edge(self, start: str, stop: str) -> None:
        """[summary]

        Args:
            start (str): [description]
            stop (str): [description]
            
        """
        self.edges[start] = stop
        return self

    def delete_node(self, name: str) -> None:
        """Deletes node from graph.
        
        """
        del self.contents[name]
        del self.edges[name]
        for key in self.contents.keys():
            if name in self.edges[key]:
                self.edges[key].remove(name)
        return self

    def delete_edge(self, start: str, stop: str) -> None:
        """[summary]

        Args:
            start (str): [description]
            stop (str): [description]
            
        """
        self.edges[start].remove(stop)
        return self
   
    
    """ Private Methods """
    
    def _find_all_paths(self, start: str, end: str, path: List[str] = []):
        """[summary]

        The code here is adapted from: https://www.python.org/doc/essays/graphs/
        
        Args:
            start (str): [description]
            end (str): [description]
            path (List[str], optional): [description]. Defaults to [].

        Returns:
            [type]: [description]
            
        """
        path = path + [start]
        if start == end:
            return [path]
        if start not in self.edges:
            return []
        paths = []
        for node in self.edges[start]:
            if node not in path:
                new_paths = self._find_all_paths(
                    start = node, 
                    end = end, 
                    path = path)
                for new_path in new_paths:
                    paths.append(new_path)
        return paths

    """ Dunder Methods """
    
    def __iter__(self) -> Iterable:
        """Returns iterable of sorted graph.
        
        Returns:
            Iterable: based upon the 'get_sorted' method of a subclass.
        
        """
        return iter(self.permutations)
          