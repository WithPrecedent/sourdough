"""
graphs: classes for flexible workflows
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:



"""
from __future__ import annotations
import collections.abc
import dataclasses
import multiprocessing
import textwrap
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import sourdough


@dataclasses.dataclass
class Node(sourdough.quirks.Registar, sourdough.quirks.Element, 
           collections.abc.MutableSequence):
    """Base container class for sourdough composite objects.
    
    A Node has a 'name' attribute for internal referencing and to allow 
    sourdough iterables to function propertly. Node instances can be used 
    to create a variety of composite workflows such as trees, cycles, contests, 
    studies, and graphs.
    
    Args:
        children (Any): item(s) contained by a Node instance.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Configuration instance, 'name' 
            should match the appropriate section name in the Configuration instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. 
        parameters (Mapping[Any, Any]]): parameters to be attached to 'children' 
            when the 'apply' method is called. Defaults to an empty dict.
        iterations (Union[int, str]): number of times the 'apply' method should 
            be called. If 'iterations' is 'infinite', the 'apply' method will
            continue indefinitely unless the method stops further iteration.
            Defaults to 1.
        criteria (str): after iteration is complete, a 'criteria' determines
            what should be outputted. This should correspond to a key in the
            'algorithms' Catalog for the corresponding sourdough Manager. 
            Defaults to None.
        parallel (ClassVar[bool]): whether the 'children' contain other 
            iterables (True) or static objects (False). If True, a subclass
            should include a custom iterable for navigating the stored 
            iterables. Defaults to False.
            
    """
    name: str = None
    parent: Node = None
    children: Sequence[Node] = dataclasses.field(default_factory = list)
    parameters: Mapping[Any, Any] = dataclasses.field(default_factory = dict)

    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent and/or mixin initialization method(s), if they exist.
        try:
            super().__post_init__()
        except AttributeError:
            pass  
        # Sets initial default value for the 'get' method.
        self._default = None
        
    """ Properties """

    @property
    def descendants(self) -> Sequence[Node]:
        pass
    
    @property
    def predecessors(self) -> Sequence[Node]:
        pass   
    
    @property
    def leaves(self) -> Sequence[Node]:
        pass   
    
    @property
    def root(self) -> Node:
        pass   
    
    @property
    def is_leaf(self) -> bool:
        return len(self.descendants) < 2
    
    @property
    def is_root(self) -> bool:
        return self.parent is None
    
    """ Public Methods """
    
    def add(self, node: Union[Node, str]) -> None:
        """Appends 'node' to 'children'.
        
        Args:
            node (Union[str, Node]): a Node instance, a Node subclass, or a str
                matching a stored Node in the Node registry.

        """
        self.children.append(node)
        return self

    def append(self, item: List[Any]) -> None:
        """Appends 'item' to 'children'.
        
        Args:
            items (List[Any]): items to append to 'children'.

        """
        self.children.append(item)
        return self   
        
    def apply(self, tool: Callable, recursive: bool = True, **kwargs) -> None:
        """Maps 'tool' to items stored in 'children'.
        
        Args:
            tool (Callable): callable which accepts an object in 'children' as
                its first argument and any other arguments in kwargs.
            recursive (bool): whether to apply 'tool' to nested items in
                'children'. Defaults to True.
            kwargs: additional arguments to pass when 'tool' is used.
        
        """
        new_children = []
        for child in iter(self.children):
            if isinstance(child, Iterable):
                if recursive:
                    new_child = child.apply(tool = tool, recursive = True, 
                                            **kwargs)
                else:
                    new_child = child
            else:
                new_child = tool(child, **kwargs)
            new_children.append(new_child)
        self.children = new_children
        return self

    def clear(self) -> None:
        """Makes 'children' an empty list."""
        self.children = []
        return self
    
    def finalize(self, recursive: bool = True) -> None:
        """[summary]

        Args:
            recursive (bool, optional): [description]. Defaults to True.

        Returns:
            [type]: [description]
        """
        
        new_children = []
        for child in self.children:
            new_child = self._instancify(node = child)
            if recursive and isinstance(new_child, Iterable):
                new_child = new_child.finalize(recursive = recursive)
            new_children.append(new_child)
        self.children = new_children
        return self 
    
    def find(self, tool: Callable, recursive: bool = True, 
             matches: Sequence[Any] = None, **kwargs) -> Sequence[Node]:
        """Finds items in 'children' that match criteria in 'tool'.
        
        Args:
            tool (Callable): callable which accepts an object in 'children' as
                its first argument and any other arguments in kwargs.
            recursive (bool): whether to apply 'tool' to nested items in
                'children'. Defaults to True.
            matches (Sequence[Any]): items matching the criteria in 'tool'. This 
                should not be passed by an external call to 'find'. It is 
                included to allow recursive searching.
            kwargs: additional arguments to pass when 'tool' is used.
            
        Returns:
            Sequence[Any]: stored items matching the criteria in 'tool'. 
        
        """
        if matches is None:
            matches = []
        for item in iter(self.children):
            matches.extend(sourdough.tools.listify(tool(item, **kwargs)))
            if isinstance(item, Iterable):
                if recursive:
                    matches.extend(item.find(tool = tool, recursive = True,
                                             matches = matches, **kwargs))
        return matches
    
    def from_matrix(self, matrix: Mapping[Any, Sequence[str]],
                    clear: bool = True) -> None:
        """[summary]

        Args:
            adjacency (MutableMapping[Any, Sequence[str]]): [description]

        Returns:
            [type]: [description]
        """
        if clear:
            self.clear()
        for key, value in matrix.items():
            self.add(node = key, children = value[1])
        return self
         
    def implement(self, data: Any = None, **kwargs) -> Any:
        """[summary]

        Args:
            data (Any): [description]

        Returns:
            Any: [description]
        """
        if data is not None:
            kwargs['data'] = data
        try:
            self.children.implement(**kwargs)
        except AttributeError:
            raise AttributeError('stored object in Node lacks implement method')

    def insert(self, index: int, item: Any) -> None:
        """Inserts 'item' at 'index' in 'children'.

        Args:
            index (int): index to insert 'item' at.
            item (Any): object to be inserted.
            
        """
        self.children.insert(index, item)
        return self

    def items(self) -> Iterable:
        """Emulates python dict 'items' method.
        
        Returns:
            Iterable: tuple of Any names and Anys.
            
        """
        return tuple(zip(self.keys(), self.values()))

    def keys(self) -> Sequence[Any]:
        """Emulates python dict 'keys' method.
        
        Returns:
            Sequence[Any]: list of names of stored in 'children'
            
        """
        return [c.name for c in self.children]

    def pop(self, key: Union[Any, int]) -> Union[Any, Sequence[Any]]:
        """Pops item(s) from 'children'.

        Args:
            key (Union[Any, int]): index or key for value in 'children'.
                
        Returns:
            Union[Any, Sequence[Any]]: item(s) popped from 'children'.
            
        """
        popped = self[key]
        del self[key]
        return popped
        
    def remove(self, key: Union[Any, int]) -> None:
        """Removes item(s) from 'children'.

        Args:
            key (Union[Any, int]): index or key for value in 'children'.
            
        """
        del self[key]
        return self
     
    def setdefault(self, value: Any) -> None:
        """Sets default value to return when 'get' method is used.
        
        Args:
            value (Any): default value to return.
            
        """
        self._default = value 
     
    def subsetify(self, subset: Union[Any, Sequence[Any]], 
                  **kwargs) -> Node[Any]:
        """Returns a subset of 'children'.

        Args:
            subset (Union[Any, Sequence[Any]]): key(s) to get items with 
                matching 'name' attributes from 'children'.
            kwargs: creates a consistent interface even when subclasses have
                additional parameters.
                
        Returns:
            Node[Any]: with only items with 'name' attributes in 'subset'.

        """
        subset = sourdough.tools.listify(subset)
        return self.__class__(
            name = self.name,
            children = [c for c in self.children if c.name in subset])     
     
    def update(self, items: Any) -> None:
        """Mimics the dict 'update' method by appending 'items'.
        
        Args:
            items (Any): Any items to add to the 'children' attribute. If a 
                Mapping is passed, the values are added to 'children' and the 
                keys become the 'name' attributes of those values. To mimic 
                'update', the passed 'items' are added to 'children' by the 
                'extend' method.           
        
        """
        if isinstance(items, Mapping):
            for key, value in items.items():
                new_item = value
                new_item.name = key
                self.extend(item = new_item)
        else:
            self.extend(item = items)
        return self

    def values(self) -> Sequence[Any]:
        """Emulates python dict 'values' method.
        
        Returns:
            Sequence[Any]: list of items stored in 'children'
            
        """
        return self.children                

    """ Private Methods """

    def _instancify(self, node: Union[str, Node], **kwargs) -> Node:
        """Returns a Node instance based on 'node' and kwargs.

        Args:
            node (Union[str, Node]): a Node instance, a Node subclass, or a str
                matching a stored Node in the Node registry.

        Raises:
            KeyError: if 'node' is a str, but doesn't match a stored Node in the
                Node registry.
            TypeError: if 'node' is neither a str, a Node subclass, or a Node
                instance.

        Returns:
            Node: an instance with all kwargs added as attributes.
            
        """
        if isinstance(node, Node):
            for key, value in kwargs.items():
                setattr(node, key, value)
        else:
            if isinstance(node, str):
                try:
                    node = Node.registry.acquire(key = node)
                except KeyError:
                    raise KeyError('node not found in the Node registry ')
            elif issubclass(node, Node):
                pass
            else:
                raise TypeError('node must be a Node or str')
            node = node(**kwargs)
        return node 
     
    """ Dunder Methods """
  
    def __getitem__(self, key: Union[Any, int]) -> Any:
        """Returns value(s) for 'key' in 'children'.
        
        If 'key' is not an int type, this method looks for a matching 'name'
        attribute in the stored instances.
        
        If 'key' is an int type, this method returns the stored item at the
        corresponding index.
        
        If only one match is found, a single item is returned. If more are 
        found, a Node or Node subclass with the matching 'name' attributes 
        is returned.

        Args:
            key (Union[Any, int]): key or index to search for in 'children'.

        Returns:
            Any: value(s) stored in 'children' that correspond to 'key'. If 
                there is more than one match, the return is a Node or Node 
                subclass with that matching stored items.

        """
        if isinstance(key, int):
            return self.children[key]
        else:
            matches = [c for c in self.children if c.name == key]
            if len(matches) == 0:
                raise KeyError(f'{key} is not in {self.__class__.__name__}')
            elif len(matches) == 1:
                return matches[0]
            else:
                return self.__class__(name = self.name, children = matches)
            
    def __setitem__(self, key: Union[Any, int], value: Any) -> None:
        """Sets 'key' in 'children' to 'value'.

        Args:
            key (Union[Any, int]): if key isn't an int, it is ignored (since the
                'name' attribute of the value will be acting as the key). In
                such a case, the 'value' is added to the end of 'children'. If
                key is an int, 'value' is assigned at the that index number in
                'children'.
            value (Any): value to be paired with 'key' in 'children'.

        """
        if isinstance(key, int):
            self.children[key] = value
        else:
            self.add(value)
        return self

    def __delitem__(self, key: Union[Any, int]) -> None:
        """Deletes item matching 'key' in 'children'.

        If 'key' is not an int type, this method looks for a matching 'name'
        attribute in the stored instances and deletes all such items. If 'key'
        is an int type, only the item at that index is deleted.

        Args:
            key (Union[Any, int]): name or index in 'children' to delete.

        """
        if isinstance(key, int):
            del self.children[key]
        else:
            self.children = [c for c in self.children if c.name != key]
        return self

    def __iter__(self) -> Iterable:
        """Returns iterable of 'children'.

        Returns:
            Iterable: 'children'.

        """
        return iter(self.children)

    def __len__(self) -> int:
        """Returns length of iterable of 'children'

        Returns:
            int: length of iterable 'children'.

        """
        return len(self.__iter__())
  
    def __contains__(self, name: str) -> bool:
        """[summary]

        Args:
            name (str): [description]

        Returns:
            bool: [description]
            
        """
        if isinstance(self.children, (list, tuple, dict)):
            return name in self.children
        else:
            try:
                return name == self.children.name
            except (AttributeError, TypeError):
                return name == self.children

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
    

@dataclasses.dataclass
class Worker(sourdough.quirks.Registar, sourdough.quirks.Element, 
             collections.abc.MutableSequence):
    """Base container class for sourdough composite objects.
    
    A Node has a 'name' attribute for internal referencing and to allow 
    sourdough iterables to function propertly. Node instances can be used 
    to create a variety of composite workflows such as trees, cycles, contests, 
    studies, and graphs.
    
    Args:
        children (Any): item(s) contained by a Node instance.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Configuration instance, 'name' 
            should match the appropriate section name in the Configuration instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. 
        parameters (Mapping[Any, Any]]): parameters to be attached to 'children' 
            when the 'apply' method is called. Defaults to an empty dict.
        iterations (Union[int, str]): number of times the 'apply' method should 
            be called. If 'iterations' is 'infinite', the 'apply' method will
            continue indefinitely unless the method stops further iteration.
            Defaults to 1.
        criteria (str): after iteration is complete, a 'criteria' determines
            what should be outputted. This should correspond to a key in the
            'algorithms' Catalog for the corresponding sourdough Manager. 
            Defaults to None.
        parallel (ClassVar[bool]): whether the 'children' contain other 
            iterables (True) or static objects (False). If True, a subclass
            should include a custom iterable for navigating the stored 
            iterables. Defaults to False.
            
    """ 
    name: str = None
    parent: Node = None
    children: Sequence[Node] = dataclasses.field(default_factory = list)
    parameters: Mapping[Any, Any] = dataclasses.field(default_factory = dict)
    iterations: Union[int, str] = 1
    criteria: Union[str, Callable, Sequence[Union[Callable, str]]] = None
    parallel: ClassVar[bool] = False
    
    """ Public Methods """

    def implement(self, data: Any) -> Any:
        """[summary]

        Args:
            data (Any): [description]

        Returns:
            Any: [description]
        """
        datasets = []
        for i in self.iterations:
            if self.parallel:
                if sourdough.settings.parallelize:
                    datasets.append(self.implementation(data = data))
            else:
                data = self.implementation(data = data)
        return data     

    """ Private Methods """

    def _implement_parallel(self, data: Any) -> Any:
        """Applies 'implementation' to data.
        
        Args:
            data (Any): any item needed for the class 'implementation' to be
                applied.
                
        Returns:
            Any: item after 'implementation has been applied.

        """  
        return data 

    def _implement_parallel_in_parallel(self, data: Any) -> Any:
        """Applies 'implementation' to data.
        
        Args:
            data (Any): any item needed for the class 'implementation' to be
                applied.
                
        Returns:
            Any: item after 'implementation has been applied.

        """
        all_data = []  
        multiprocessing.set_start_method('spawn')
        with multiprocessing.Pool() as pool:
            all_data = pool.starmap(self.implementation, data)
        return all_data  
    
    def _implement_parallel_in_serial(self, data: Any) -> Any:
        """Applies 'implementation' to data.
        
        Args:
            data (Any): any item needed for the class 'implementation' to be
                applied.
                
        Returns:
            Any: item after 'implementation has been applied.

        """  
        all_data = []
        all_data.append(self.implementation(data = data))
        return data   
                    

@dataclasses.dataclass
class Contest(Worker):
    """Stores Workflows in a comparative parallel workflow and chooses the best.

    Distinguishing characteristics of a Contest:
        1) Applies different components in parallel.
        2) Chooses the best stored Component based upon 'criteria'.
        3) Each stored Component is only attached to the Contest with exactly 
            one connection (these connections are not defined separately - they
            are simply part of the parallel workflow).
        
    Args:
        children (Sequence[Component]): Component subclass instances. Defaults 
            to an empty list.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Configuration instance, 'name' 
            should match the appropriate section name in the Configuration instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes.
        iterations (Union[int, str]): number of times the 'apply' method should 
            be called. If 'iterations' is 'infinite', the 'apply' method will
            continue indefinitely unless the method stops further iteration.
            Defaults to 1.
        criteria (str): after iteration is complete, a 'criteria' determines
            what should be outputted. This should correspond to a key in the
            'algorithms' Catalog for the sourdough manager.project. Defaults to None.
        parallel (ClassVar[bool]): whether the 'children' contain other 
            iterables (True) or static objects (False). If True, a subclass
            should include a custom iterable for navigating the stored 
            iterables. Defaults to True.
                            
    """
    children: Sequence[sourdough.Component] = dataclasses.field(
        default_factory = list)
    name: str = None
    iterations: Union[int, str] = 1
    criteria: str = None
    parallel: ClassVar[bool] = True
    
    
@dataclasses.dataclass
class Study(Worker):
    """Stores Flows in a comparative parallel workflow.

    Distinguishing characteristics of a Study:
        1) Applies different components and creates new branches of the overall
            Project workflow.
        2) Maintains all of the repetitions without selecting or averaging the 
            results.
        3) Each stored Component is only attached to the Study with exactly 
            one connection (these connections are not defined separately - they
            are simply part of the parallel workflow).
                      
    Args:
        children (Sequence[Component]): Component subclass instances. Defaults 
            to an empty list.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Configuration instance, 'name' 
            should match the appropriate section name in the Configuration instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes.
        iterations (Union[int, str]): number of times the 'apply' method should 
            be called. If 'iterations' is 'infinite', the 'apply' method will
            continue indefinitely unless the method stops further iteration.
            Defaults to 1.
        criteria (str): after iteration is complete, a 'criteria' determines
            what should be outputted. This should correspond to a key in the
            'algorithms' Catalog for the sourdough manager.project. Defaults to None.
        parallel (ClassVar[bool]): whether the 'children' contain other 
            iterables (True) or static objects (False). If True, a subclass
            should include a custom iterable for navigating the stored 
            iterables. Defaults to True.
                            
    """
    children: Sequence[sourdough.Component] = dataclasses.field(
        default_factory = list)
    name: str = None
    iterations: Union[int, str] = 1
    criteria: str = None
    parallel: ClassVar[bool] = True
        
    
@dataclasses.dataclass
class Survey(Worker):
    """Stores Flows in a comparative parallel workflow and averages results.

    Distinguishing characteristics of a Survey:
        1) Applies different components in parallel.
        2) Averages or otherwise combines the results based upon selected 
            criteria.
        3) Each stored Component is only attached to the Survey with exactly 
            one connection (these connections are not defined separately - they
            are simply part of the parallel workflow).    
                    
    Args:
        children (Sequence[Component]): Component subclass instances. Defaults 
            to an empty list.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Configuration instance, 'name' 
            should match the appropriate section name in the Configuration instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes.
        iterations (Union[int, str]): number of times the 'apply' method should 
            be called. If 'iterations' is 'infinite', the 'apply' method will
            continue indefinitely unless the method stops further iteration.
            Defaults to 1.
        criteria (str): after iteration is complete, a 'criteria' determines
            what should be outputted. This should correspond to a key in the
            'algorithms' Catalog for the sourdough manager.project. Defaults to None.
        parallel (ClassVar[bool]): whether the 'children' contain other 
            iterables (True) or static objects (False). If True, a subclass
            should include a custom iterable for navigating the stored 
            iterables. Defaults to True.
                            
    """
    children: Sequence[sourdough.Component] = dataclasses.field(
        default_factory = list)
    name: str = None
    iterations: Union[int, str] = 1
    criteria: str = None
    parallel: ClassVar[bool] = True   
       
       
# @dataclasses.dataclass
# class Graph(sourdough.products.Workflow):
#     """Base class for composite objects in sourdough projects.

#     Distinguishing characteristics of a Graph:
#         1) Iteration is not defined by ordering of children.
#         2) Incorporates Edges as part of its workflow.
#         3) All Components must be connected (sourdough does not presently
#             support graphs with unconnected graphs).
            
#     Args:
#         children (Sequence[Union[str, sourdough.Component]]): a list of str or
#             Components. 
#         name (str): designates the name of a class instance that is used for 
#             internal referencing throughout sourdough. For example if a 
#             sourdough instance needs settings from a Configuration instance, 'name' 
#             should match the appropriate section name in the Configuration instance. 
#             When subclassing, it is sometimes a good idea to use the same 'name' 
#             attribute as the base class for effective coordination between 
#             sourdough classes. Defaults to None. If 'name' is None and 
#             '__post_init__' of Element is called, 'name' is set based upon
#             the 'get_name' method in Element. If that method is not 
#             overridden by a subclass instance, 'name' will be assigned to the 
#             snake case version of the class name ('__class__.__name__').
    
#     """
#     children: Sequence[Union[str, sourdough.Component]] = dataclasses.field(
#         default_factory = list)
#     name: str = None



# @dataclasses.dataclass
# class Graph(Role):
    
#     name: str = None
#     Flow: sourdough.products.Workflow = None
#     iterator: Union[str, Callable] = 'iterator'    
#     options: ClassVar[sourdough.types.Catalog] = sourdough.types.Catalog(
#         children = {
#             'edge': sourdough.Edge,
#             'node': sourdough.Node})
        
    # children: Sequence[Union[sourdough.Component, str]] = dataclasses.field(
    #     default_factory = list)
    # design: str = 'chained'
    # identification: str = None
    # data: Any = None    
    # edges: Union[Sequence[sourdough.Edge],
    #     Sequence[Sequence[str]], 
    #     Mapping[Any, Sequence[str]]] = dataclasses.field(default_factory = list)
    # options: ClassVar[sourdough.types.Catalog] = sourdough.types.Catalog()  

    # """ Initialization Methods """
    
    # def __post_init__(self) -> None:
    #     """Initializes class instance attributes."""
    #     # Calls parent and/or mixin initialization method(s).
    #     super().__post_init__()
    #     # Converts 'children' to the proper design.
    #     if isinstance(self.edges, dict):
    #         adjacency = copy.deepcopy(self.children)
    #         self.children = []
    #         self.from_dict(adjacency = adjacency)
    #     elif any(self.edges, tuple):
    #         adjacency = copy.deepcopy(self.children)
    #         self.children = []
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
    #         if item not in self.children:
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
    #     self.children.append(node)
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
    #     if start not in self.children:
    #         raise KeyError(f'{start} is not in the graph')
    #     if stop not in self.children:
    #         raise KeyError(f'{stop} is not in the graph')
    #     test_graph = copy.deepcopy(self.children)
    #     test_graph[start].descendents.append(stop)
    #     test_graph[stop].predecessors.append(start)
    #     self._validate_graph(graph = test_graph)     
    #     self.children[start].descendents.append(stop)
    #     self.children[stop].predecessors.append(start)
    #     return self

    # def delete_node(self, name: str) -> None:
    #     """Deletes node from graph.
        
    #     """
    #     del self.children[name]
    #     for node in self.children:
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
    #         self.children[start].descendants.remove(stop)
    #         self.children[stop].predecessors.remove(start)
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
    #     return self.children[name].predecessors
                 
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
    #     return self.children[name].descendents

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
    #         f'''{textwrap.indent(str(self.children), '    ')}
    #         edges:
    #         {textwrap.indent(str(self.edges), '    ')}'''])   
         
    # """ Private Methods """
    
    # def _topological_sort(self, 
    #         graph: sourdough.products.Workflow) -> Sequence[sourdough.Component]:
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
    #         graph: sourdough.products.Workflow, 
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
    #         graph: sourdough.products.Workflow) -> Sequence[sourdough.Component]:
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
    #         graph: sourdough.products.Workflow, 
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
    #     return [v for v in self.children if not v.descendents]

    # """ Public Methods """
        
    # def get_sorted(self, 
    #         graph: sourdough.products.Workflow = None,
    #         return_elements: bool = False) -> Sequence[sourdough.Component]:
    #     """Performs a topological sort on 'graph'.
        
    #     If 'graph' is not passed, the 'children' attribute is used instead.
        
    #     Args:
    #         graph:
    #     """
    #     if graph is None:
    #         graph = self.children
    #     sorted_queue = self._topological_sort(graph = graph)
    #     if return_elements:
    #         return [v.element for v in sorted_queue]
    #     else:
    #         return sorted_queue

    # def validate(self, graph: sourdough.products.Workflow) -> None:
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
