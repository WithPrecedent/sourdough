"""
.. module:: graphs
:synopsis: sourdough graphs
:publisher: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

""" 
sourdough graphs are still a work in progress. They are not used by the default
projects structure, but are made available here for users to subclass as they
wish.

Each node/vertex in a sourdough Graph should be a Component subclass instance
or a str type.
All edges should be Edge or Edge subclass instances.

"""

import abc
import collections
import copy
import dataclasses
import itertools
from typing import Any, ClassVar, Iterable, Mapping, Sequence, Tuple, Union

import sourdough

    
@dataclasses.dataclass
class Edge(object):
    """An edge in a sourdough Graph.

    'start' and 'stop' are the ends of the Edge. However, which value is 
    assigned to each attribute only matters in a directional graph.

    By default Edge is slotted so that no other attributes can be added. This
    lowers memory consumption and increases speed. If you wish to add more 
    functionality to your Graph edges, you should subclass Edge.

    Args:
        start (str): name of the Component where the edge starts.
        stop (str): name of the Component where the edge ends.
        directed (bool): whether this edge is directed (True). Defaults to 
            False. 
        weight (float): a weight value assigned to this edge. Defaults to None.

    """
    __slots__ = ['start', 'stop', 'directed', 'weight']

    start: str
    stop: str
    directed: Optional[bool] = False
    weight: Optional[float] = None
 
 
@dataclasses.dataclass
class Graph(sourdough.Progression, abc.ABC):
    """Base class for sourdough graphs.
    
    Args:
        contents (Optional[Union[Sequence['sourdough.Component'], Sequence[Tuple[str]], 
            Mapping[str, Sequence[str]]]]): a list of contents, an adjacency list, or
            an adjacency matrix. Whatever structure is passed, it will be 
            converted to a list of contents. Defaults to an empty list.
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. If the class instance
            needs settings from the shared Settings instance, 'name' should
            match the appropriate section name in that Settings instance. When
            subclassing, it is a good settings to use the same 'name' attribute
            as the base class for effective coordination between sourdough
            classes. Defaults to None or __class__.__name__.lower().
        edges ()

    
    """
    contents: Sequence[Union['sourdough.Component', str]] = dataclasses.field(
        default_factory = list)
    name: str = None
    edges: Union[Sequence['Edge'],
        Sequence[Tuple[str]], 
        Mapping[str, Sequence[str]]] = dataclasses.field(default_factory = list)

    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls inherited initialization method.
        super().__post_init__()
        # Converts 'contents' to the proper structure.
        if isinstance(self.edges, dict):
            adjacency = copy.deepcopy(self.contents)
            self.contents = []
            self.from_dict(adjacency = adjacency)
        elif any(self.edges, tuple):
            adjacency = copy.deepcopy(self.contents)
            self.contents = []
            self.from_list(adjacency = adjacency)
        
    """ Required Subclass Methods """

    @abc.abstractmethod
    def get_sorted(self,
            graph: Optional['sourdough.Plan'] = None,
            return_components: Optional[bool] = False) -> None:
        """Subclasses must provide their own methods."""

    @abc.abstractmethod
    def validate(self, 
            graph: Optional['sourdough.Plan'] = None) -> None:
        """Subclasses must provide their own methods."""
           
    """ Public Methods """
    
    def from_dict(self, adjacency: Mapping[str, Sequence[str]]) -> None:
        """[summary]

        Args:
            adjacency (MutableMapping[str, Sequence[str]]): [description]

        Returns:
            [type]: [description]
        """
        for key, value in adjacency.items():
            self.add_node(name = key)
            self.add_edge(start = value[0], stop = value[1])
        return self

    def from_list(self, adjacency: Sequence[Union[str]]) -> None:
        """[summary]

        Args:
            adjacency (MutableSequence[Union[str]]): [description]

        Returns:
            [type]: [description]
        """
        for item in adjacency:
            if item not in self.contents:
                self.add_node(name = item)
            self.add_edge(start = item[0], stop = item[1])
        return self
          
    def add_node(self,
            name: str = None,
            component: Optional['sourdough.Component'] = None) -> None:
        """Adds a node to the graph."""
        if component and not name:
            name = component.name
        elif not name:
            raise ValueError('component or name must be passed to add_node')
        node = sourdough.Component(name = name, component = component)
        self.contents.append(node)
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
        if start not in self.contents:
            raise KeyError(f'{start} is not in the graph')
        if stop not in self.contents:
            raise KeyError(f'{stop} is not in the graph')
        test_graph = copy.deepcopy(self.contents)
        test_graph[start].descendents.append(stop)
        test_graph[stop].predecessors.append(start)
        self._validate_graph(graph = test_graph)     
        self.contents[start].descendents.append(stop)
        self.contents[stop].predecessors.append(start)
        return self

    def delete_node(self, name: str) -> None:
        """Deletes node from graph.
        
        """
        del self.contents[name]
        for node in self.contents:
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
            self.contents[start].descendants.remove(stop)
            self.contents[stop].predecessors.remove(start)
        except KeyError:
            raise KeyError(f'edge not found in the graph')
        return self

    def predecessors(self, 
            name: str,
            recursive: Optional[bool] = False) -> Sequence[str]:
        """[summary]

        Args:
            name ([type]): [description]

        Returns:
            [type]: [description]
            
        ToDo:
            Add recursive functionality.
            
        """
        return self.contents[name].predecessors
                 
    def descendants(self, 
            name: str,
            recursive: Optional[bool] = False) -> Sequence[str]:
        """[summary]

        Args:
            node ([type]): [description]

        Returns:
            [type]: [description]
            
        ToDo:
            Add recursive functionality.
            
        """
        return self.contents[name].descendents

    """ Dunder Methods """
    
    def __iter__(self) -> Iterable:
        """Returns iterable of sorted graph.
        
        Returns:
            Iterable: based upon the 'get_sorted' method of a subclass.
        
        """
        return iter(self.get_sorted(return_components = True))
    
    """ Private Methods """
    
    def _topological_sort(self, 
            graph: 'sourdough.Plan') -> Sequence['sourdough.Component']:
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
            graph: 'sourdough.Plan', 
            node: 'sourdough.Component',
            searched: list[str]) -> Sequence['sourdough.Component']: 
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
    
    def _dfs_sort(self, graph: 'sourdough.Plan') -> Sequence['sourdough.Component']:
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
            graph: 'sourdough.Plan', 
            node: 'sourdough.Component',
            searched: list[str]) -> Sequence['sourdough.Component']: 
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
    

@dataclasses.dataclass
class DAGraph(Graph):
    """Base class for directed acyclic graph.
    
     Args:
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. If the class instance
            needs settings from the shared Settings instance, 'name' should
            match the appropriate section name in that Settings instance. When
            subclassing, it is a good settings to use the same 'name' attribute
            as the base class for effective coordination between sourdough
            classes. Defaults to None or __class__.__name__.lower().
        contents (Optional[Union[Sequence['sourdough.Component'], Sequence[Tuple[str]], 
            Mapping[str, Sequence[str]]]]): a list of contents, an adjacency list, or
            an adjacency matrix. Whatever structure is passed, it will be 
            converted to a list of contents. Defaults to an empty list.   
    
    """
    name: str = None
    contents: Optional[Union[
        Sequence['sourdough.Component'], 
        Sequence[Tuple[str]], 
        Mapping[str, Sequence[str]]]] = dataclasses.field(default_factory = list)

    """ Properties """
    
    @property
    def root(self) -> 'sourdough.Component':
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
    def endpoints(self) -> Sequence['sourdough.Component']:
        """[summary]

        Returns:
            [type]: [description]
            
        """
        return [v for v in self.contents if not v.descendents]

    """ Public Methods """
        
    def get_sorted(self, 
            graph: Optional['sourdough.Plan'] = None,
            return_components: Optional[bool] = False) -> Sequence[Union[
                Component, 
                'sourdough.Component']]:
        """Performs a topological sort on 'graph'.
        
        If 'graph' is not passed, the 'contents' attribute is used instead.
        
        Args:
            graph:
        """
        if graph is None:
            graph = self.contents
        sorted_queue = self._topological_sort(graph = graph)
        if return_components:
            return [v.component for v in sorted_queue]
        else:
            return sorted_queue

    def validate(self, graph: 'sourdough.Plan') -> None:
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
    