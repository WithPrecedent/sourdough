"""
composites: lightweight composite structures adapted to sourdough
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Composite (Base, ABC): base class for all sourdough composite structures.
        All subclasses must have 'apply' and 'find' methods. Its 'library'
        class attribute stores all subclasses.
    Graph (Lexicon, Composite): a lightweight directed acyclic graph (DAG).
    Pipeline (Hybrid, Composite): a simple serial pipeline data structure.
    Tree (Hybrid, Composite): a general tree data structure.
    
"""
from __future__ import annotations
import abc
import dataclasses
import itertools
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import sourdough


@dataclasses.dataclass
class Composite(abc.ABC):
    """Base class for sourdough's composite objects.

    Subclasses must have 'apply' and 'find' methods that follow the criteria
    described in the docstrings for those methods.

    """

    @abc.abstractmethod
    def apply(self, tool: Callable, **kwargs) -> None:
        """Applies 'tool' to each element in 'contents'.
        
        Subclasses must provide their own methods.

        Args:
            tool (Callable): callable which accepts an object in 'contents' as
                its first argument and any other arguments in kwargs.
            kwargs: additional arguments to pass when 'tool' is used.
            
        """
        pass        
    
    @abc.abstractmethod 
    def find(self, tool: Callable, **kwargs) -> Sequence[Any]:
        """Finds items in 'contents' that match criteria in 'tool'.
        
        Args:
            tool (Callable): callable which accepts an object in 'contents' as
                its first argument and any other arguments in kwargs.
            kwargs: additional arguments to pass when 'tool' is used.
            
        Returns:
            Sequence[Any]: stored items matching the criteria in 'tool'. 
        
        """
        pass


@dataclasses.dataclass
class Graph(sourdough.types.Lexicon, Composite):
    """Stores a directed acyclic graph (DAG).
    
    Internally, the graph elements are stored in 'contents'. And the edges are
    stored as an adjacency list in 'edges' with the 'name' attributes of the
    elements in 'contents' acting as the starting and stopping elements in 
    'edges'.
    
    Although based on the sourdough dict replacement, Lexicon, a Graph differs
    from it in too many ways to list here.
    
    Args:
        contents (Mapping[str, sourdough.quirks.Element]): keys are the names 
            of Element instances that are stored in values.
        edges (Mapping[str, Sequence[str]]): an adjacency list where the keys
            are the names of elements and the values are names of elements 
            which the key is connected to.
            
    """  
    contents: Mapping[str, sourdough.quirks.Element] = dataclasses.field(
        default_factory = dict)
    edges: Mapping[str, Sequence[str]] = dataclasses.field(
        default_factory = dict)

    """ Properties """
    
    @property
    def root(self) -> str:
        """Returns name of root element in 'contents'.

        Raises:
            ValueError: if there is more than 1 root or no roots.

        Returns:
            str: name of root element in contents'
            
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
        """Returns name of endpoint element in 'contents'.

        Raises:
            ValueError: if there is more than 1 endpoint or no endpoints.

        Returns:
            str: name of endpoint element in 'contents'.
            
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
        """Returns all paths through graph in list of lists form.
        
        Returns:
            List[List[str]]: returns all paths from 'root' to 'end' in a list
                of lists of names of elements.
                
        """
        return self._find_all_paths(start = self.root, end = self.end)
        
    """ Public Methods """
    
    def add(self, item: Union[sourdough.quirks.Element, Tuple[str]]) -> None:
        """Adds a item to 'contents' or 'edges' depending on type.
        
        Args:
            item (Union[sourdough.quirks.Element, Tuple[str]]): either a 
                Element or a tuple containing the names of elements for an 
                edge to be created.
        
        """
        if isinstance(item, sourdough.quirks.Element):
            self.add_element(element = item)
        elif isinstance(item, tuple) and len(item) == 2:
            self.add_edge(start = item[0], stop = item[1])
        return self

    def add_element(self, element: sourdough.quirks.Element) -> None:
        """Adds a element to 'contents'.
        
        Args:
            element (Element): element with a name attribute to add to 
                'contents'.
        
        """
        self.contents[element.name] = element
        return self

    def add_edge(self, start: str, stop: str) -> None:
        """Adds an edge to 'edges'.

        Args:
            start (str): name of element for edge to start.
            stop (str): name of element for edge to stop.
            
        """
        self.edges[start] = stop
        return self

    def apply(self, tool: Callable, **kwargs) -> None:
        """Applies 'tool' to each element in 'contents'.

        Args:
            tool (Callable): callable which accepts an object in 'contents' as
                its first argument and any other arguments in kwargs.
            kwargs: additional arguments to pass when 'tool' is used.
            
        """
        new_contents = {}
        for name, element in self.contents:
            new_contents[name] = tool(element, **kwargs)
        self.contents = new_contents
        return self        
        
    def delete_element(self, name: str) -> None:
        """Deletes element from graph.
        
        Args:
            name (str): name of element to delete from 'contents' and 'edges'.
            
        """
        del self.contents[name]
        del self.edges[name]
        for key in self.contents.keys():
            if name in self.edges[key]:
                self.edges[key].remove(name)
        return self

    def delete_edge(self, start: str, stop: str) -> None:
        """Deletes edge from graph.

        Args:
            start (str): name of starting element for the edge to delete.
            stop (str): name of ending element for the edge to delete.
            
        """
        self.edges[start].remove(stop)
        return self

    def find(self, tool: Callable, **kwargs) -> Sequence[Any]:
        """Finds items in 'contents' that match criteria in 'tool'.
        
        Args:
            tool (Callable): callable which accepts an object in 'contents' as
                its first argument and any other arguments in kwargs.
            kwargs: additional arguments to pass when 'tool' is used.
            
        Returns:
            Sequence[Any]: stored items matching the criteria in 'tool'. 
        
        """
        matches = []
        for element in self.contents.values():
            matches.extend(sourdough.tools.listify(tool(element, **kwargs)))
        return matches
   
    """ Private Methods """
    
    def _find_all_paths(self, start: str, end: str, 
                        path: List[str] = []) -> List[List[str]]:
        """Returns all paths in graph from 'start' to 'end'.

        The code here is adapted from: https://www.python.org/doc/essays/graphs/
        
        Args:
            start (str): name of Element instance to start paths from.
            end (str): name of Element instance to end paths.
            path (List[str]): a path from 'start' to 'end'. Defaults to an empty 
                list. 

        Returns:
            List[List[str]]: a list of possible paths (each path is a list of
                Element names) from 'start' to 'end'
            
        """
        path = path + [start]
        if start == end:
            return [path]
        if start not in self.edges:
            return []
        paths = []
        for element in self.edges[start]:
            if element not in path:
                new_paths = self._find_all_paths(
                    start = element, 
                    end = end, 
                    path = path)
                for new_path in new_paths:
                    paths.append(new_path)
        return paths
   

@dataclasses.dataclass
class Pipeline(sourdough.types.Hybrid, Composite):
    """Stores a linear pipeline data structure.
    
    A Pipeline differs from a Hybrid in 2 significant ways:
        1) It only stores Element subclasses.
        2) It includes 'apply' and 'find' methods which traverse items in
            'contents' to either 'apply' a Callable or 'find' items matching 
            criteria defined in a Callable.

    Args:
        contents (Sequence[Element]): items with 'name' attributes to store. 
            If a dict is passed, the keys will be ignored and only the values 
            will be added to 'contents'. If a single item is passed, it will be 
            placed in a list. Defaults to an empty list.
                         
    """
    contents: Sequence[sourdough.quirks.Element] = dataclasses.field(
        default_factory = list) 
    
    """ Public Methods """

    def add(self, item: Sequence[Any], **kwargs) -> None:
        """Appends 'item' argument to 'contents' attribute.
        
        Args:
            item (Sequence[Any]): items to add to the 'contents' attribute.
            kwargs: creates a consistent interface even when subclasses have
                additional parameters.
                
        """
        self.contents.append(item)
        return self  

    def apply(self, tool: Callable, **kwargs) -> None:
        """Applies 'tool' to each element in 'contents'.

        Args:
            tool (Callable): callable which accepts an object in 'contents' as
                its first argument and any other arguments in kwargs.
            kwargs: additional arguments to pass when 'tool' is used.
            
        """
        new_contents = []
        for element in self.contents:
            new_contents.append(tool(element, **kwargs))
        self.contents = new_contents
        return self        
       
    def find(self, tool: Callable, **kwargs) -> Sequence[Any]:
        """Finds items in 'contents' that match criteria in 'tool'.
        
        Args:
            tool (Callable): callable which accepts an object in 'contents' as
                its first argument and any other arguments in kwargs.
            kwargs: additional arguments to pass when 'tool' is used.
            
        Returns:
            Sequence[Any]: stored items matching the criteria in 'tool'. 
        
        """
        matches = []
        for element in self.contents:
            matches.extend(sourdough.tools.listify(tool(element, **kwargs)))
        return matches

    def reorder(self, order: Sequence[str]) -> None:
        """

        Args:
            order (Sequence[str]): [description]

        Returns:
            [type]: [description]
        """
        new_contents = []
        for item in order:
            new_contents.append(self[item])
        self.contents = new_contents
        return self      
        
        
@dataclasses.dataclass
class Tree(sourdough.types.Hybrid, Composite):
    """Stores a general tree data structure.
    
    A Tree differs from a Hybrid in 3 significant ways:
        1) It only stores Element subclasses.
        2) It has a nested structure with children descending from items in
            'contents'. Consequently, all relevant methods include a 'recursive'
            parameter which determines whether the method should apply to all
            levels of the tree.
        3) It includes 'apply' and 'find' methods which traverse items in
            'contents' (recursively, if the 'recursive' argument is True), to
            either 'apply' a Callable or 'find' items matching criteria defined
            in a Callable.

    Args:
        contents (Sequence[Element]): items with 'name' attributes to store. 
            If a dict is passed, the keys will be ignored and only the values 
            will be added to 'contents'. If a single item is passed, it will be 
            placed in a list. Defaults to an empty list.
                         
    """
    contents: Sequence[sourdough.quirks.Element] = dataclasses.field(
        default_factory = list) 
    
    """ Public Methods """

    def add(self, item: Sequence[Any], **kwargs) -> None:
        """Appends 'item' argument to 'contents' attribute.
        
        Args:
            item (Sequence[Any]): items to add to the 'contents' attribute.
            kwargs: creates a consistent interface even when subclasses have
                additional parameters.
                
        """
        self.contents.append(item)
        return self  

    def apply(self, tool: Callable, recursive: bool = True, **kwargs) -> None:
        """Maps 'tool' to items stored in 'contents'.
        
        Args:
            tool (Callable): callable which accepts an object in 'contents' as
                its first argument and any other arguments in kwargs.
            recursive (bool): whether to apply 'tool' to nested items in
                'contents'. Defaults to True.
            kwargs: additional arguments to pass when 'tool' is used.
        
        """
        new_contents = []
        for child in iter(self.contents):
            if hasattr(child, 'apply') and recursive:
                new_child = child.apply(tool = tool, recursive = True, **kwargs)
            elif recursive:
                new_child = tool(child, **kwargs)
            else:
                new_child = child
            new_contents.append(new_child)
        self.contents = new_contents
        return self

    def find(self, tool: Callable, recursive: bool = True, 
             matches: Sequence[Any] = None, **kwargs) -> Sequence[Any]:
        """Finds items in 'contents' that match criteria in 'tool'.
        
        Args:
            tool (Callable): callable which accepts an object in 'contents' as
                its first argument and any other arguments in kwargs.
            recursive (bool): whether to apply 'tool' to nested items in
                'contents'. Defaults to True.
            matches (Sequence[Any]): items matching the criteria in 'tool'. This 
                should not be passed by an external call to 'find'. It is 
                included to allow recursive searching.
            kwargs: additional arguments to pass when 'tool' is used.
            
        Returns:
            Sequence[Any]: stored items matching the criteria in 'tool'. 
        
        """
        if matches is None:
            matches = []
        for item in iter(self.contents):
            matches.extend(sourdough.tools.listify(tool(item, **kwargs)))
            if isinstance(item, Iterable) and recursive:
                matches.extend(item.find(tool = tool, recursive = True,
                                         matches = matches, **kwargs))
        return matches
     