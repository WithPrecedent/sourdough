"""
structures: common composite structures adapted to sourdough
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
                    Optional, Sequence, Tuple, Type, Union)

import sourdough


@dataclasses.dataclass
class Node(sourdough.base.Component, abc.ABC):
    """ 
    
    """
    name: str = None

    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def apply(self, data: Any = None, **kwargs) -> Any:
        """Subclasses must provide their own methods."""
        pass 
     
    
@dataclasses.dataclass
class Technique(Node, sourdough.types.Proxy):

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
class Pipeline(Node, sourdough.types.Progression):
    """
    
    """
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
class Graph(Node, sourdough.types.Lexicon):
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

    def apply(self) -> object:
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
    
    def _find_all_paths(self, start: str, end: str, 
                        path: List[str] = []) -> List[List[str]]:
        """Returns all paths in graph from 'start' to 'end'.

        The code here is adapted from: https://www.python.org/doc/essays/graphs/
        
        Args:
            start (str): name of Node instance to start paths from.
            end (str): name of Node instance to end paths.
            path (List[str]): a path from 'start' to 'end'. Defaults to an empty 
                list. 

        Returns:
            List[List[str]]: a list of possible paths (each path is a list of
                Node names) from 'start' to 'end'
            
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


@dataclasses.dataclass
class Tree(Node, sourdough.types.Hybrid):
    """
    
    """
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
class Parameters(sourdough.types.Lexicon):
    """
    """
    contents: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    name: str = None
    base: Union[Type, str] = None
    required: Sequence[str] = dataclasses.field(default_factory = list)
    runtime: Mapping[str, str] = dataclasses.field(default_factory = dict)
    selected: Sequence[str] = dataclasses.field(default_factory = list)
    default: ClassVar[Mapping[str, Any]] = {}
    
    """ Public Methods """
    
    def create(self, creator: sourdough.project.Creator, **kwargs) -> None:
        """[summary]

        Args:
            creator (sourdough.project.Creator): [description]

        """
        if not kwargs:
            kwargs = self.default
        for kind in ['settings', 'required', 'runtime', 'selected']:
            kwargs = getattr(self, f'_get_{kind}')(creator = creator, **kwargs)
        self.contents = kwargs
        return self
    
    """ Private Methods """
    
    def _get_settings(self, creator: sourdough.project.Creator, 
                      **kwargs) -> Dict[str, Any]:
        """[summary]

        Args:
            creator (sourdough.project.Creator): [description]

        Returns:
            Dict[str, Any]: [description]
            
        """
        try:
            kwargs.update(creator.settings[f'{self.name}_parameters'])
        except KeyError:
            pass
        return kwargs
    
    def _get_required(self, creator: sourdough.project.Creator, 
                      **kwargs) -> Dict[str, Any]:
        """[summary]

        Args:
            creator (sourdough.project.Creator): [description]

        Returns:
            Dict[str, Any]: [description]
            
        """
        for item in self.required:
            if item not in kwargs:
                kwargs[item] = self.default[item]
        return kwargs
    
    def _get_runtime(self, creator: sourdough.project.Creator, 
                      **kwargs) -> Dict[str, Any]:
        """[summary]

        Args:
            creator (sourdough.project.Creator): [description]

        Returns:
            Dict[str, Any]: [description]
            
        """
        for parameter, attribute in self.runtime.items():
            try:
                kwargs[parameter] = getattr(creator, attribute)
            except AttributeError:
                pass
        return kwargs

    def _get_selected(self, creator: sourdough.project.Creator, 
                      **kwargs) -> Dict[str, Any]:
        """[summary]

        Args:
            creator (sourdough.project.Creator): [description]

        Returns:
            Dict[str, Any]: [description]
            
        """
        if self.selected:
            kwargs = {k: kwargs[k] for k in self.selected}
        return kwargs
  