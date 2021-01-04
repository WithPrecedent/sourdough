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
class AbstractBuilder(abc.ABC):
    """Abstract base class for sourdough builders.
    
    Subclasses must have a 'create' method.
    
    """

    @abc.abstractmethod
    def create(self, **kwargs) -> Any:
        """Subclasses must provide their own methods."""
        pass
    

@dataclasses.dataclass
class Builder(sourdough.types.Lexicon, AbstractBuilder):
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
                    kwargs[parameter] = value
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
class Director(sourdough.types.Lexicon, AbstractBuilder):
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
    builder: AbstractBuilder = None
    
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
class Node(sourdough.quirks.Element):

    contents: Any = None 
    name: str = None

    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def apply(self, data: Any = None, **kwargs) -> Any:
        """Subclasses must provide their own methods."""
        pass 


@dataclasses.dataclass
class Composite(Node, sourdough.types.Hybrid):
    
    contents: Sequence[Node] = dataclasses.field(default_factory = list) 
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
class Leaf(Node, collections.abc.Container):

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
class Graph(sourdough.types.Lexicon):
    """Stores a directed acyclic graph (DAG).
    
    Internally, the DAG is stored as an adjacency list in 'contents'.
    

    
    """  
    contents: Mapping[str, Node] = dataclasses.field(default_factory = dict)
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
            raise ValueError('Graph has more than 1 endpoint')
        elif len(ends) == 0:
            raise ValueError('Graph is not acyclic - it has no endpoint')
        else:
            return ends[0]
            
    @property
    def permutations(self) -> List[str]:
        return self._find_all_paths(start = self.root, end = self.end)
        
    """ Public Methods """
    
    def find_all_paths(self, start: str, end: str, path: List[str] = []):
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
          
    def add_node(self,
            name: str = None,
            element: sourdough.Component = None) -> None:
        """Adds a node to the graph."""
        if element and not name:
            name = element.name
        elif not name:
            raise ValueError('element or name must be passed to add_node')
        node = sourdough.Component(name = name, element = element)
        self.children.append(node)
        return self

    def add_edge(self, start: str, stop: str) -> None:
        """[summary]

        Args:
            start (str): [description]
            stop (str): [description]

        Raises:
            KeyError: [description]
            KeyError: [description]

        Returns:
            [type]: [description]
            
        """
        if start not in self.children:
            raise KeyError(f'{start} is not in the graph')
        if stop not in self.children:
            raise KeyError(f'{stop} is not in the graph')
        test_graph = copy.deepcopy(self.children)
        test_graph[start].descendents.append(stop)
        test_graph[stop].predecessors.append(start)
        self._validate_graph(graph = test_graph)     
        self.children[start].descendents.append(stop)
        self.children[stop].predecessors.append(start)
        return self

    def delete_node(self, name: str) -> None:
        """Deletes node from graph.
        
        """
        del self.children[name]
        for node in self.children:
            node.predecessors = [p for p in node.predecessors if p != name]
            node.descendents = [d for d in node.descendents if d != name]
        return self

    def delete_edge(self, 
            start: str, stop: str) -> None:
        """[summary]

        Args:
            start (str): [description]
            stop (str): [description]

        Raises:
            KeyError: [description]

        Returns:
            [type]: [description]
        """
        try:
            self.children[start].descendants.remove(stop)
            self.children[stop].predecessors.remove(start)
        except KeyError:
            raise KeyError(f'edge not found in the graph')
        return self

    def predecessors(self, 
            name: str,
            recursive: bool = False) -> Sequence[str]:
        """[summary]

        Args:
            name ([type]): [description]

        Returns:
            [type]: [description]
            
        ToDo:
            Add recursive functionality.
            
        """
        return self.children[name].predecessors
                 
    def descendants(self, 
            name: str,
            recursive: bool = False) -> Sequence[str]:
        """[summary]

        Args:
            node ([type]): [description]

        Returns:
            [type]: [description]
            
        ToDo:
            Add recursive functionality.
            
        """
        return self.children[name].descendents

    """ Dunder Methods """
    
    def __iter__(self) -> Iterable:
        """Returns iterable of sorted graph.
        
        Returns:
            Iterable: based upon the 'get_sorted' method of a subclass.
        
        """
        return iter(self.get_sorted(return_elements = True))
    
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
        return '\n'.join([textwrap.dedent(f'''
            sourdough {self.__class__.__name__}
            name: {self.name}
            nodes:'''),
            f'''{textwrap.indent(str(self.children), '    ')}
            edges:
            {textwrap.indent(str(self.edges), '    ')}'''])   
         
    """ Private Methods """
    
    def _topological_sort(self, 
            graph: sourdough.products.Workflow) -> Sequence[sourdough.Component]:
        """[summary]

        Returns:
            [type]: [description]
            
        """
        searched = []
        return self._topological_descend(
            graph = graph, 
            node = graph.root,
            searched = searched)
        
    def _topological_descend(self, 
            graph: sourdough.products.Workflow, 
            node: sourdough.Component,
            searched: list[str]) -> Sequence[sourdough.Component]: 
        """[summary]

        Returns:
            [type]: [description]
            
        """
        sorted_queue = []      
        for descendent in node.descendents:
            if graph[descendent] not in searched:
                searched.insert(descendent, 0)
                sorted_queue.extend(self._dfs_descend(
                    graph = graph,
                    node = graph[descendent],
                    searched = searched))
        return sorted_queue    
    
    def _dfs_sort(self, 
            graph: sourdough.products.Workflow) -> Sequence[sourdough.Component]:
        """[summary]

        Returns:
            [type]: [description]
            
        """
        searched = []
        return self._dfs_descend(
            graph = graph, 
            node = graph.root,
            searched = searched)
        
    def _dfs_descend(self, 
            graph: sourdough.products.Workflow, 
            node: sourdough.Component,
            searched: list[str]) -> Sequence[sourdough.Component]: 
        """[summary]

        Returns:
            [type]: [description]
        """
        sorted_queue = []      
        for descendent in node.descendents:
            if graph[descendent] not in searched:
                searched.append(descendent)
                sorted_queue.extend(self._dfs_descend(
                    graph = graph,
                    node = graph[descendent],
                    searched = searched))
        return sorted_queue    
        """ Properties """
    
    @property
    def root(self) -> sourdough.Component:
        """[summary]

        Raises:
            ValueError: [description]
            ValueError: [description]

        Returns:
            [type]: [description]
        """
        rootless = [v for v in self.nodees if not self.predecessors]
        if len(rootless) > 1:
            raise ValueError('graph is not acyclic - it has more than 1 root')
        elif len(rootless) == 0:
            raise ValueError('graph is not acyclic - it has no root')
        else:
            return rootless[0]
 
    @property
    def endpoints(self) -> Sequence[sourdough.Component]:
        """[summary]

        Returns:
            [type]: [description]
            
        """
        return [v for v in self.children if not v.descendents]

    """ Public Methods """
        
    def get_sorted(self, 
            graph: sourdough.products.Workflow = None,
            return_elements: bool = False) -> Sequence[sourdough.Component]:
        """Performs a topological sort on 'graph'.
        
        If 'graph' is not passed, the 'children' attribute is used instead.
        
        Args:
            graph:
        """
        if graph is None:
            graph = self.children
        sorted_queue = self._topological_sort(graph = graph)
        if return_elements:
            return [v.element for v in sorted_queue]
        else:
            return sorted_queue

    def validate(self, graph: sourdough.products.Workflow) -> None:
        """
        

        Args:
            graph ([type]): [description]

        Raises:
            ValueError: if topological sort fails.
            ValueError: if the root check fails.
            
        """
        try:
            self.get_sorted(graph = graph)
        except ValueError:
            raise ValueError(f'graph failed the topological sort test')
        test_root = self.root()
        return self
