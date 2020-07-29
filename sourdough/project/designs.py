"""
dedigndesdeiignes for sourdough projects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    DLsignoader): base class for defining composite dedignn 
        sourdough.

"""
import abc
import dataclasses
import itertools
import textwrap
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union

import more_itertools

import sourdough

 
@dataclasses.dataclass
class Design(sourdough.Loader):
    """Contains default types for composite dedigno be loaded.
    
    Args:  
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
        modules Union[str, Sequence[str]]: name(s) of module(s) where object to 
            load is/are located. use is located. Defaults to an empty list.
        components (Mapping[str, str]): dict with keys as the type of composite
            class and values as the names of classes in 'modules'. Defaults to
            an empty dict.
        iterator (str, Callable): name of a method to iterator through a
            composite object or a function for iteration. Defaults to iter.
        _loaded (Mapping[str, Any]): dictionary of str keys and previously
            loaded objects. This is checked first by the 'load' method to avoid
            unnecessary re-importation. Defaults to an empty dict.
         
    """
    name: str = None
    modules: Union[str, Sequence[str]] = dataclasses.field(
        default_factory = list)
    components: Mapping[str, str] = dataclasses.field(default_factory = dict)
    iterator: Union[str, Callable] = iter  
    _loaded: Mapping[str, Any] = dataclasses.field(default_factory = dict)    
    
    """ Public Methods """

    def load(self, key: str) -> object:
        """Returns object named in 'key'.

        Args:
            key (str): name of key in 'components' that corresponds to the 
                class, function, or variable to try to import from modules 
                listed in 'modules'.

        Returns:
            object: imported from a python module.

        """
        return super().load(key = self.components[key])
        

@dataclasses.dataclass
class Chained(Tree):
    """Contains default types for composite dedigno be loaded.
    
    Args:  
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
        modules Union[str, Sequence[str]]: name(s) of module(s) where object to 
            load is/are located. use is located. Defaults to an empty list.
        components (Mapping[str, str]): dict with keys as the type of composite
            class and values as the names of classes in 'modules'. Defaults to
            an empty dict.
        iterator (str, Callable): name of a method to iterator through a
            composite object or a function for iteration. Defaults to iter.
        _loaded (Mapping[str, Any]): dictionary of str keys and previously
            loaded objects. This is checked first by the 'load' method to avoid
            unnecessary re-importation. Defaults to an empty dict.
         
    """    
    name: str = None
    modules: str = dataclasses.field(
        default_factory = lambda: [
            'sourdough.project.workers',
            'sourdough.project.components'])
    components: Mapping[str, str] = dataclasses.field(
        default_factory = lambda: {
            'root': 'Manager',
            'workers': 'Worker',
            'tasks': 'Task',
            'techniques': 'Technique'})
    iterator: Union[str, Callable] = iter  
    _loaded: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    
      
@dataclasses.dataclass
class Comparative(Tree):
    """Contains default types for composite dedigno be loaded.
    
    Args:  
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
        modules Union[str, Sequence[str]]: name(s) of module(s) where object to 
            load is/are located. use is located. Defaults to an empty list.
        components (Mapping[str, str]): dict with keys as the type of composite
            class and values as the names of classes in 'modules'. Defaults to
            an empty dict.
        iterator (str, Callable): name of a method to iterator through a
            composite object or a function for iteration. Defaults to iter.
        _loaded (Mapping[str, Any]): dictionary of str keys and previously
            loaded objects. This is checked first by the 'load' method to avoid
            unnecessary re-importation. Defaults to an empty dict.
         
    """    
    name: str = None
    modules: str = dataclasses.field(
        default_factory = lambda: [
            'sourdough.project.workers',
            'sourdough.project.components'])
    components: Mapping[str, str] = dataclasses.field(
        default_factory = lambda: {
            'root': 'Manager',
            'workers': 'Worker',
            'tasks': 'Task',
            'techniques': 'Technique'})
    iterator: Union[str, Callable] = itertools.product  
    _loaded: Mapping[str, Any] = dataclasses.field(default_factory = dict)   


@dataclasses.dataclass
class Flat(Tree):
    """Contains default types for composite dedigno be loaded.
    
    Args:  
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
        modules Union[str, Sequence[str]]: name(s) of module(s) where object to 
            load is/are located. use is located. Defaults to an empty list.
        components (Mapping[str, str]): dict with keys as the type of composite
            class and values as the names of classes in 'modules'. Defaults to
            an empty dict.
        iterator (str, Callable): name of a method to iterator through a
            composite object or a function for iteration. Defaults to iter.
        _loaded (Mapping[str, Any]): dictionary of str keys and previously
            loaded objects. This is checked first by the 'load' method to avoid
            unnecessary re-importation. Defaults to an empty dict.
         
    """    
    name: str = None
    modules: str = dataclasses.field(
        default_factory = lambda: [
            'sourdough.project.workers',
            'sourdough.project.components'])
    components: Mapping[str, str] = dataclasses.field(
        default_factory = lambda: {
            'root': 'Manager',
            'workers': 'Worker',
            'tasks': 'Task',
            'techniques': 'Technique'})
    iterator: Union[str, Callable] = more_itertools.collapse  
    _loaded: Mapping[str, Any] = dataclasses.field(default_factory = dict) 
    

@dataclasses.dataclass
class Graph(Design):
    """Contains default types for composite dedigno be loaded.
    
    Args:  
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
        modules Union[str, Sequence[str]]: name(s) of module(s) where object to 
            load is/are located. use is located. Defaults to an empty list.
        components (Mapping[str, str]): dict with keys as the type of composite
            class and values as the names of classes in 'modules'. Defaults to
            an empty dict.
        iterator (str, Callable): name of a method to iterator through a
            composite object or a function for iteration. Defaults to iter.
        _loaded (Mapping[str, Any]): dictionary of str keys and previously
            loaded objects. This is checked first by the 'load' method to avoid
            unnecessary re-importation. Defaults to an empty dict.
         
    """   
    name: str = None
    modules: str = dataclasses.field(
        default_factory = lambda: [
            'sourdough.project.graphs',
            'sourdough.project.components'])
    components: Mapping[str, str] = dataclasses.field(
        default_factory = lambda: {
            'root': 'Node',
            'node': 'Node',
            'edges': 'Edge',
            'task': 'Task',
            'techniques': 'Technique'})
    iterator: Union[str, Callable] = itertools.product
    _loaded: Mapping[str, Any] = dataclasses.field(default_factory = dict)   
 
 
@dataclasses.dataclass
class Cycle(Design):
    """Contains default types for composite dedigno be loaded.
    
    Args:  
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
        modules Union[str, Sequence[str]]: name(s) of module(s) where object to 
            load is/are located. use is located. Defaults to an empty list.
        components (Mapping[str, str]): dict with keys as the type of composite
            class and values as the names of classes in 'modules'. Defaults to
            an empty dict.
        iterator (str, Callable): name of a method to iterator through a
            composite object or a function for iteration. Defaults to iter.
        _loaded (Mapping[str, Any]): dictionary of str keys and previously
            loaded objects. This is checked first by the 'load' method to avoid
            unnecessary re-importation. Defaults to an empty dict.
         
    """ 
    name: str = None
    modules: Union[str, Sequence[str]] = dataclasses.field(
        default_factory = list)
    components: Mapping[str, str] = dataclasses.field(default_factory = dict)
    iterator: Union[str, Callable] = itertools.cycle
    _loaded: Mapping[str, Any] = dataclasses.field(default_factory = dict)       
    