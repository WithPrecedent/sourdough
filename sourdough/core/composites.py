"""
structures: lightweight composite structures adapted to sourdough
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Structure (Base, ABC): base class for all sourdough composite structures.
        All subclasses must have 'apply' and 'find' methods. Its 'library'
        class attribute stores all subclasses.
    Graph (Lexicon, Structure): a lightweight directed acyclic graph (DAG).
    Pipeline (Hybrid, Structure): a simple serial pipeline data structure.
    Tree (Hybrid, Structure): a general tree data structure.
    
"""
from __future__ import annotations
import abc
import dataclasses
import itertools
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import sourdough


@dataclasses.dataclass
class Graph(sourdough.types.Lexicon):
    """Stores a directed acyclic graph (DAG) as an adjacency list.

    Despite being called an adjacency "list," the typical and most efficient
    way to store one is using a python dict. A sourdough Graph inherits from
    a Lexicon in order to allow use of its extra functionality over a plain
    dict.
    
    Graph also supports autovivification where a list is created as a value for
    a missing key. This means that a Graph need not inherit from defaultdict.
    
    The Graph does not actually store Node instances. Rather, it maintains the
    string names of Nodes which can then be used to create and iterate over
    Nodes.
    
    Args:
        contents (Dict[str, List[str]]): an adjacency list where the keys are 
            the names of nodes and the values are names of nodes which the key 
            is connected to. Defaults to an empty dict.
        default (Any): default value to use when a key is missing and a new
            one is automatically corrected. Defaults to an empty list.
          
    """  
    contents: Dict[str, List[str]] = dataclasses.field(default_factory = dict)
    default: Any = dataclasses.field(default_factory = list)

    """ Properties """
           
    @property
    def endpoints(self) -> List[str]:
        """Returns endpoint nodes in the Graph.

        Raises:
            ValueError: if there is more than 1 endpoint or no endpoints.

        Returns:
            str: name of endpoint node in 'nothing'.
            
        """
        ends = [k for k in self.contents.keys() if not self.contents[k]]
        if len(ends) > 0:
            return ends
        elif len(ends) == 0:
            raise ValueError('Graph is not acyclic - it has no endpoints')
              
    @property
    def nodes(self) -> List[str]:
        """Returns all nodes in the Graph.

        Returns:
            List[str]: all nodes.
            
        """
        return list(self.keys())

    @property
    def paths(self) -> List[List[str]]:
        """Returns all paths through graph in list of lists form.
        
        Returns:
            List[List[str]]: returns all paths from 'roots' to 'end' in a list
                of lists of names of nodes.
                
        """
        return self._find_all_permutations(
            starts = self.roots, 
            ends = self.endpoints)
       
    @property
    def roots(self) -> List[str]:
        """Returns root nodes in the Graph.

        Raises:
            ValueError: if there are no roots.

        Returns:
            List[str]: root nodes.
            
        """
        stops = list(itertools.chain.from_iterable(self.contents.values()))
        roots = [k for k in self.contents.keys() if k not in stops]
        if len(roots) > 0:
            return roots
        else:
            raise ValueError('Graph is not acyclic - it has no roots')
    
    """ Class Methods """
       
    @classmethod
    def from_adjacency(cls, adjacency: Dict[str, List[str]]) -> Graph:
        """Creates a Graph instance from an adjacency list.

        Args:
            adjacency (Dict[str, List[str]]): adjacency list used to create a
                Graph instance.
            
        """
        return cls(contents = adjacency)
    
    @classmethod
    def from_edges(cls, edges: List[Sequence[str]]) -> Graph:
        """Creates a Graph instance from an edge list.

        Args:
            edges (List[Sequence[str]]): Edge list used to create a Graph 
                instance.
            
        """
        contents = {}
        for edge_pair in edges:
            if edge_pair[0] not in contents:
                contents[edge_pair[0]] = [edge_pair[1]]
            else:
                contents[edge_pair[0]].append(edge_pair[1])
            if edge_pair[1] not in contents:
                contents[edge_pair[1]] = []
        return cls(contents = contents)
    
    @classmethod
    def from_matrix(cls, matrix: List[List[int]], names: List[str]) -> Graph:
        """Creates a Graph instance from an adjacency matrix

        Args:
            matrix (matrix: List[List[int]]): adjacency matrix used to create a 
                Graph instance. The values in the matrix should be 1 
                (indicating an edge) and 0 (indicating no edge).
            names (List[str]): names of nodes in the order of the rows and
                columns in 'matrix'.
            
        """
        name_mapping = dict(zip(range(len(matrix)), names))
        raw_adjacency = {
            i: [j for j, adjacent in enumerate(row) if adjacent] 
            for i, row in enumerate(matrix)}
        contents = {}
        for key, value in raw_adjacency.items():
            new_key = name_mapping[key]
            new_values = []
            for edge in value:
                new_values.append(name_mapping[edge])
            contents[new_key] = new_values
        return cls(contents = contents)
    
    """ Public Methods """
    
    def add(self, item: Union[str, Tuple[str]]) -> None:
        """Adds a node or edge to 'contents' depending on type.
        
        Args:
            item (Union[str, Tuple[str]]): either a str name or a tuple 
                containing the names of nodes for an edge to be created.
        
        Raises:
            TypeError: if 'item' is neither a str or a tuple of two strings.
            
        """
        if isinstance(item, str):
            self.add_node(node = item)
        elif isinstance(item, tuple) and len(item) == 2:
            self.add_edge(start = item[0], stop = item[1])
        else:
            raise TypeError('item must be a str for adding a node or a tuple '
                            'of two strings for adding an edge')
        return self

    def add_edge(self, start: str, stop: str) -> None:
        """Adds an edge to 'contents'.

        Args:
            start (str): node for edge to start.
            stop (str): node for edge to stop.
            
        Raises:
            ValueError: if 'start' is the same as 'stop'.
            
        """
        if start == stop:
            raise ValueError(
                'The start of an edge cannot be the same as the stop')
        else:
            if stop not in self.contents:
                self.add_node(node = stop)
            if start not in self.contents:
                self.add_node(node = start)
            if stop not in self.contents[start]:
                self.contents[start].append(stop)
        return self

    def add_node(self, node: str) -> None:
        """Adds a node to 'contents'.
        
        Args:
            node (str): node to add to the graph.
            
        Raises:
            ValueError: if 'node' is already in 'contents'.
        
        """
        if node in self.contents:
            raise ValueError(f'{node} already exists in the graph')
        else:
            self.contents[node] = []
        return self

    def combine(self, graph: Graph) -> None:
        """Adds 'other' Graph to this Graph.

        Combining creates an edge between every endpoint of this instance's
        Graph and the every root of 'graph'.

        Args:
            graph (Graph): a second Graph to combine with this one.
            
        Raises:
            ValueError: if 'graph' has nodes that are also in 'contents'.
            TypeError: if 'graph' is not a Graph type.
            
        """
        if isinstance(graph, Graph):
            if self.contents:
                current_endpoints = self.endpoints
                self.contents.update(graph.contents)
                for endpoint in current_endpoints:
                    for root in graph.roots:
                        self.add_edge(start = endpoint, stop = root)
            else:
                self.contents = graph.contents
        else:
            raise TypeError('graph must be a Graph type to combine')
        return self

    def delete_edge(self, start: str, stop: str) -> None:
        """Deletes edge from graph.

        Args:
            start (str): starting node for the edge to delete.
            stop (str): ending node for the edge to delete.
        
        Raises:
            KeyError: if 'start' is not a node in the Graph.
            ValueError: if 'stop' does not have an edge with 'start'.

        """
        try:
            self.contents[start].remove(stop)
        except KeyError:
            raise KeyError(f'{start} does not exist in the graph')
        except ValueError:
            raise ValueError(f'{stop} is not connected to {start}')
        return self
       
    def delete_node(self, node: str) -> None:
        """Deletes node from graph.
        
        Args:
            node (str): node to delete from 'contents'.
        
        Raises:
            KeyError: if 'node' is not in 'contents'.
            
        """
        try:
            del self.contents[node]
        except KeyError:
            raise KeyError(f'{node} does not exist in the graph')
        return self

    def extend(self, nodes: Sequence[str]) -> None:
        """[summary]

        Args:
            nodes (Sequence[str]): [description]
            
        """
        try:
            for endpoint in self.endpoints:
                self.add_edge(start = endpoint, stop = nodes[0])
        except ValueError:
            pass
        previous_node = None
        for node in sourdough.tools.listify(nodes):
            if previous_node is not None:
                self.add_edge(start = previous_node, stop = node)
            previous_node = node
        return self
    
    def search(self, start: str = None, depth_first: bool = True) -> List[str]:
        """Returns a path through the Graph.

        Args:
            start (str): node to start the path from. If None, it is assigned to
                the first root in the Graph. Defaults to None.
            depth_first (bool): whether the search should be depth first (True)
                or breadth first (False). Defaults to True.

        Returns:
            List[str]: nodes in a path through the Graph.
            
        """        
        if start is None:
            start = self.roots[0]
        if depth_first:
            visited = self._depth_first_search(node = start, visited = [])
        else:
            visited = self._breadth_first_search(node = start)
        return visited

    """ Private Methods """

    def _breadth_first_search(self, node: str) -> List[str]:
        """Returns a breadth first search path through the Graph.

        Args:
            node (str): node to start the search from.

        Returns:
            List[str]: nodes in a path through the Graph.
            
        """        
        visited = set()
        queue = [node]
        while queue:
            vertex = queue.pop(0)
            if vertex not in visited:
                visited.add(vertex)
                queue.extend(set(self[vertex]) - visited)
        return list(visited)
       
    def _depth_first_search(self, node: str, visited: List[str]) -> List[str]:
        """Returns a depth first search path through the Graph.

        Args:
            node (str): node to start the search from.
            visited (List[str]): list of visited nodes.

        Returns:
            List[str]: nodes in a path through the Graph.
            
        """  
        if node not in visited:
            visited.append(node)
            for edge in self[node]:
                self._depth_first_search(node = edge, visited = visited)
        return visited
    
    def _find_all_paths(self, start: str, end: str, 
                        path: List[str] = []) -> List[List[str]]:
        """Returns all paths in graph from 'start' to 'end'.

        The code here is adapted from: https://www.python.org/doc/essays/graphs/
        
        Args:
            start (str): node to start paths from.
            end (str): node to end paths.
            path (List[str]): a path from 'start' to 'end'. Defaults to an empty 
                list. 

        Returns:
            List[List[str]]: a list of possible paths (each path is a list of
                Element names) from 'start' to 'end'
            
        """
        path = path + [start]
        if start == end:
            return [path]
        if start not in self.contents:
            return []
        paths = []
        for node in self.contents[start]:
            if node not in path:
                new_paths = self._find_all_paths(
                    start = node, 
                    end = end, 
                    path = path)
                for new_path in new_paths:
                    paths.append(new_path)
        return paths
       
    def _find_all_permutations(self, 
            starts: Union[str, Sequence[str]],
            ends: Union[str, Sequence[str]]) -> List[List[str]]:
        """[summary]

        Args:
            start (Union[str, Sequence[str]]): starting points for paths through
                the Graph.
            ends (Union[str, Sequence[str]]): endpoints for paths through the
                Graph.

        Returns:
            List[List[str]]: list of all paths through the Graph from all
                'starts' to all 'ends'.
            
        """
        all_permutations = []
        for start in sourdough.tools.listify(starts):
            for end in sourdough.tools.listify(ends):
                paths = self._find_all_paths(
                    start = start, 
                    end = end)
                if paths:
                    if all(isinstance(path, str) for path in paths):
                        all_permutations.append(paths)
                    else:
                        all_permutations.extend(paths)
        return all_permutations

    """ Dunder Methods """

    def __add__(self, other: Graph) -> None:
        """Adds 'other' Graph to this Graph.

        Graph adding uses the 'combine' method. Read its docstring for further
        details about how the graphs are added together.
        
        Args:
            other (Graph): a second Graph to combine with this one.
            
        """
        self.combine(graph = other)        
        return self

    def __iadd__(self, other: Any) -> None:
        """Adds 'other' Graph to this Graph.

        Graph adding uses the 'combine' method. Read its docstring for further
        details about how the graphs are added together.
        
        Args:
            other (Graph): a second Graph to combine with this one.
            
        """
        self.combine(graph = other)        
        return self
       
    def __missing__(self, key: str) -> List:
        """Returns an empty list when a missing 'key' is sought.

        Args:
            key (str): node sought by an access call.

        Returns:
            List: empty list of edges.
            
        """
        return self.default


# @dataclasses.dataclass
# class Pipeline(sourdough.types.Hybrid):
#     """Stores a linear pipeline data structure.
    
#     A Pipeline differs from a Hybrid in 2 significant ways:
#         1) It only stores Element subclasses.
#         2) It includes 'apply' and 'find' methods which traverse items in
#             'contents' to either 'apply' a Callable or 'find' items matching 
#             criteria defined in a Callable.

#     Args:
#         contents (Sequence[Element]): items with 'name' attributes to store. 
#             If a dict is passed, the keys will be ignored and only the values 
#             will be added to 'contents'. If a single item is passed, it will be 
#             placed in a list. Defaults to an empty list.
                         
#     """
#     contents: Sequence[sourdough.quirks.Element] = dataclasses.field(
#         default_factory = list) 
    
#     """ Public Methods """

#     def add(self, item: Sequence[Any], **kwargs) -> None:
#         """Appends 'item' argument to 'contents' attribute.
        
#         Args:
#             item (Sequence[Any]): items to add to the 'contents' attribute.
#             kwargs: creates a consistent interface even when subclasses have
#                 additional parameters.
                
#         """
#         self.contents.append(item)
#         return self  

#     def apply(self, tool: Callable, **kwargs) -> None:
#         """Applies 'tool' to each node in 'contents'.

#         Args:
#             tool (Callable): callable which accepts an object in 'contents' as
#                 its first argument and any other arguments in kwargs.
#             kwargs: additional arguments to pass when 'tool' is used.
            
#         """
#         new_contents = []
#         for node in self.contents:
#             new_contents.append(tool(node, **kwargs))
#         self.contents = new_contents
#         return self        
       
#     def find(self, tool: Callable, **kwargs) -> Sequence[Any]:
#         """Finds items in 'contents' that match criteria in 'tool'.
        
#         Args:
#             tool (Callable): callable which accepts an object in 'contents' as
#                 its first argument and any other arguments in kwargs.
#             kwargs: additional arguments to pass when 'tool' is used.
            
#         Returns:
#             Sequence[Any]: stored items matching the criteria in 'tool'. 
        
#         """
#         matches = []
#         for node in self.contents:
#             matches.extend(sourdough.tools.listify(tool(node, **kwargs)))
#         return matches

#     def reorder(self, order: Sequence[str]) -> None:
#         """

#         Args:
#             order (Sequence[str]): [description]

#         Returns:
#             [type]: [description]
#         """
#         new_contents = []
#         for item in order:
#             new_contents.append(self[item])
#         self.contents = new_contents
#         return self      
        
        
# @dataclasses.dataclass
# class Tree(sourdough.types.Hybrid, Structure):
#     """Stores a general tree data structure.
    
#     A Tree differs from a Hybrid in 3 significant ways:
#         1) It only stores Element subclasses.
#         2) It has a nested structure with children descending from items in
#             'contents'. Consequently, all relevant methods include a 'recursive'
#             parameter which determines whether the method should apply to all
#             levels of the tree.
#         3) It includes 'apply' and 'find' methods which traverse items in
#             'contents' (recursively, if the 'recursive' argument is True), to
#             either 'apply' a Callable or 'find' items matching criteria defined
#             in a Callable.

#     Args:
#         contents (Sequence[Element]): items with 'name' attributes to store. 
#             If a dict is passed, the keys will be ignored and only the values 
#             will be added to 'contents'. If a single item is passed, it will be 
#             placed in a list. Defaults to an empty list.
                         
#     """
#     contents: Sequence[sourdough.quirks.Element] = dataclasses.field(
#         default_factory = list) 
    
#     """ Public Methods """

#     def add(self, item: Sequence[Any], **kwargs) -> None:
#         """Appends 'item' argument to 'contents' attribute.
        
#         Args:
#             item (Sequence[Any]): items to add to the 'contents' attribute.
#             kwargs: creates a consistent interface even when subclasses have
#                 additional parameters.
                
#         """
#         self.contents.append(item)
#         return self  

#     def apply(self, tool: Callable, recursive: bool = True, **kwargs) -> None:
#         """Maps 'tool' to items stored in 'contents'.
        
#         Args:
#             tool (Callable): callable which accepts an object in 'contents' as
#                 its first argument and any other arguments in kwargs.
#             recursive (bool): whether to apply 'tool' to nested items in
#                 'contents'. Defaults to True.
#             kwargs: additional arguments to pass when 'tool' is used.
        
#         """
#         new_contents = []
#         for child in iter(self.contents):
#             if hasattr(child, 'apply') and recursive:
#                 new_child = child.apply(tool = tool, recursive = True, **kwargs)
#             elif recursive:
#                 new_child = tool(child, **kwargs)
#             else:
#                 new_child = child
#             new_contents.append(new_child)
#         self.contents = new_contents
#         return self

#     def find(self, tool: Callable, recursive: bool = True, 
#              matches: Sequence[Any] = None, **kwargs) -> Sequence[Any]:
#         """Finds items in 'contents' that match criteria in 'tool'.
        
#         Args:
#             tool (Callable): callable which accepts an object in 'contents' as
#                 its first argument and any other arguments in kwargs.
#             recursive (bool): whether to apply 'tool' to nested items in
#                 'contents'. Defaults to True.
#             matches (Sequence[Any]): items matching the criteria in 'tool'. This 
#                 should not be passed by an external call to 'find'. It is 
#                 included to allow recursive searching.
#             kwargs: additional arguments to pass when 'tool' is used.
            
#         Returns:
#             Sequence[Any]: stored items matching the criteria in 'tool'. 
        
#         """
#         if matches is None:
#             matches = []
#         for item in iter(self.contents):
#             matches.extend(sourdough.tools.listify(tool(item, **kwargs)))
#             if isinstance(item, Iterable) and recursive:
#                 matches.extend(item.find(tool = tool, recursive = True,
#                                          matches = matches, **kwargs))
#         return matches
     