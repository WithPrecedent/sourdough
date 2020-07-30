"""
structures: general composite object types
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:

"""

import abc
import copy
import dataclasses
import itertools
import more_itertools
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union

import sourdough
  
    
@dataclasses.dataclass
class Structure(sourdough.OptionsMixin, sourdough.Component, abc.ABC):

    name: str = None
    worker: 'sourdough.Worker' = None
    iterator: Union[str, Callable] = iter    
    options: ClassVar['sourdough.Catalog'] = sourdough.Catalog()
    
    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent initialization method(s).
        super().__post_init__()
        # Sets current 'stage' and 'index' for that 'stage'.
        self.index: int = -1
    
    """ Dunder Methods """
    
    def __iter__(self) -> Iterable:
        """Returns iterable of 'contents' based upon 'structure'.
        
        Returns:
            Iterable: of 'contents'.
            
        """
        if isinstance(self.iterator, str):
            return getattr(self, self.iterator)()
        else:
            return self.iterator(self.worker.contents)

    def __next__(self) -> Union[Callable, 'sourdough.Component']:
        """Returns next method after method matching 'item'.
        
        Returns:
            Callable: next method corresponding to those listed in 'options'.
            
        """
        if self.index < len(self.worker.contents):
            self.index += 1
            if isinstance(self.worker[self.index], sourdough.Action):
                return self.worker[self.index].perform
            else:
                return self.worker[self.index]
        else:
            raise StopIteration()


@dataclasses.dataclass
class Creator(Structure):
    
    name: str = None
    worker: 'sourdough.Worker' = None
    iterator: Union[str, Callable] = itertools.chain
    options: ClassVar['sourdough.Catalog'] = sourdough.Catalog(
        contents = {
            'author': sourdough.project.creators.Author,
            'publisher': sourdough.project.creators.Publisher,
            'reader': sourdough.project.creators.Reader},
        defaults = ['author', 'publisher', 'reader'])


@dataclasses.dataclass
class Cycle(Structure):
    
    name: str = None
    worker: 'sourdough.Worker' = None
    iterator: Union[str, Callable] = itertools.cycle   
    options: ClassVar['sourdough.Catalog'] = sourdough.Catalog(
        contents = {
            'task': sourdough.project.actions.Task,
            'technique': sourdough.project.actions.Technique,
            'worker': sourdough.project.project.Worker})
        
      
@dataclasses.dataclass
class Progression(Structure):
    
    name: str = None
    worker: 'sourdough.Worker' = None
    iterator: Union[str, Callable] = itertools.chain
    options: ClassVar['sourdough.Catalog'] = sourdough.Catalog(
        contents = {
            'task': sourdough.project.actions.Task,
            'technique': sourdough.project.actions.Technique,
            'worker': sourdough.project.project.Worker})
  
  
@dataclasses.dataclass
class Study(Structure):
    
    name: str = None
    worker: 'sourdough.Worker' = None
    iterator: Union[str, Callable] = itertools.product   
    options: ClassVar['sourdough.Catalog'] = sourdough.Catalog(
        contents = {
            'task': sourdough.project.actions.Task,
            'technique': sourdough.project.actions.Technique,
            'worker': sourdough.project.project.Worker})
           
    
@dataclasses.dataclass
class Tree(Structure):
    
    name: str = None
    worker: 'sourdough.Worker' = None
    iterator: Union[str, Callable] = more_itertools.collapse
    options: ClassVar['sourdough.Catalog'] = sourdough.Catalog(
        contents = {
            'task': sourdough.project.actions.Task,
            'technique': sourdough.project.actions.Technique,
            'worker': sourdough.project.project.Worker})
  

@dataclasses.dataclass
class Graph(Structure):
    
    name: str = None
    worker: 'sourdough.Worker' = None
    iterator: Union[str, Callable] = 'iterator'    
    options: ClassVar['sourdough.Catalog'] = sourdough.Catalog(
        contents = {
            'edge': sourdough.project.components.Edge,
            'node': sourdough.project.components.Node})
        
    # contents: Sequence[Union['sourdough.Component', str]] = dataclasses.field(
    #     default_factory = list)
    # design: str = 'chained'
    # identification: str = None
    # data: Any = None    
    # edges: Union[Sequence['sourdough.Edge'],
    #     Sequence[Sequence[str]], 
    #     Mapping[str, Sequence[str]]] = dataclasses.field(default_factory = list)
    # options: ClassVar['sourdough.Catalog'] = sourdough.Catalog()  

    # """ Initialization Methods """
    
    # def __post_init__(self) -> None:
    #     """Initializes class instance attributes."""
    #     # Calls parent initialization method(s).
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
    
    # def from_dict(self, adjacency: Mapping[str, Sequence[str]]) -> None:
    #     """[summary]

    #     Args:
    #         adjacency (MutableMapping[str, Sequence[str]]): [description]

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
    #         component: 'sourdough.Component' = None) -> None:
    #     """Adds a node to the graph."""
    #     if component and not name:
    #         name = component.name
    #     elif not name:
    #         raise ValueError('component or name must be passed to add_node')
    #     node = sourdough.Component(name = name, component = component)
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
    #     return iter(self.get_sorted(return_components = True))
    
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
    #         graph: 'sourdough.Worker') -> Sequence['sourdough.Component']:
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
    #         graph: 'sourdough.Worker', 
    #         node: 'sourdough.Component',
    #         searched: list[str]) -> Sequence['sourdough.Component']: 
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
    #         graph: 'sourdough.Worker') -> Sequence['sourdough.Component']:
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
    #         graph: 'sourdough.Worker', 
    #         node: 'sourdough.Component',
    #         searched: list[str]) -> Sequence['sourdough.Component']: 
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
    # def root(self) -> 'sourdough.Component':
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
    # def endpoints(self) -> Sequence['sourdough.Component']:
    #     """[summary]

    #     Returns:
    #         [type]: [description]
            
    #     """
    #     return [v for v in self.contents if not v.descendents]

    # """ Public Methods """
        
    # def get_sorted(self, 
    #         graph: 'sourdough.Worker' = None,
    #         return_components: bool = False) -> Sequence['sourdough.Component']:
    #     """Performs a topological sort on 'graph'.
        
    #     If 'graph' is not passed, the 'contents' attribute is used instead.
        
    #     Args:
    #         graph:
    #     """
    #     if graph is None:
    #         graph = self.contents
    #     sorted_queue = self._topological_sort(graph = graph)
    #     if return_components:
    #         return [v.component for v in sorted_queue]
    #     else:
    #         return sorted_queue

    # def validate(self, graph: 'sourdough.Worker') -> None:
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
