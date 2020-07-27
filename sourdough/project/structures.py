"""
structures: structure classes for sourdough projects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Project (OptionsMixin, Inventory): iterable which contains the needed
        information and data for constructing and executing tree objects.

"""
import abc
import dataclasses
import itertools
import textwrap
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union

import more_itertools

import sourdough

 
@dataclasses.dataclass
class Structure(sourdough.Loader):
    """Contains default types for composite structures to be loaded.
    
    Args:  
        modules Union[str, Sequence[str]]: name(s) of module(s) where object to 
            load is/are located. use is located. Defaults to an empty list.
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
        components (Mapping[str, str]): dict with keys as the type of composite
            class and values as the names of classes in 'modules'. Defaults to
            an empty dict.
        iterator (str, Callable): name of a method to iterator through a
            composite object or a function for iteration. Defaults to iter.
        _loaded (Mapping[str, Any]): dictionary of str keys and previously
            loaded objects. This is checked first by the 'load' method to avoid
            unnecessary re-importation. Defaults to an empty dict.
         
    """
    modules: Union[str, Sequence[str]] = dataclasses.field(
        default_factory = lambda: list)
    name: str = None
    components: Mapping[str, str] = dataclasses.field(
        default_factory = lambda: dict)
    iterator: Union[str, Callable] = iter  
    _loaded: Mapping[str, Any] = dataclasses.field(
        default_factory = lambda: dict)

    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent initialization method(s).
        super().__post_init__() 
        # Imports the modules        


@dataclasses.dataclass
class Tree(Structure, abc.ABC):
    """Contains default types for tree structures to be loaded.
    
    Args:  
        modules Union[str, Sequence[str]]: name(s) of module(s) where object to 
            load is/are located. use is located. Defaults to an empty list.
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
        components (Mapping[str, str]): dict with keys as the type of composite
            class and values as the names of classes in 'modules'. Defaults to
            an empty dict.
        iterator (str, Callable): name of a method to iterator through a
            composite object or a function for iteration. Defaults to iter.
        _loaded (Mapping[str, Any]): dictionary of str keys and previously
            loaded objects. This is checked first by the 'load' method to avoid
            unnecessary re-importation. Defaults to an empty dict.
         
    """    
    modules: str = dataclasses.field(
        default_factory = lambda: [
            'sourdough.project.workers',
            'sourdough.project.actions'])
    name: str = None
    components: Mapping[str, str] = dataclasses.field(
        default_factory = lambda: {
            'root': 'Manager',
            'workers': 'Worker',
            'tasks': 'Task',
            'techniques': 'Technique'})
    iterator: Union[str, Callable] = iter 
    _loaded: Mapping[str, Any] = dataclasses.field(
        default_factory = lambda: dict) 
        

@dataclasses.dataclass
class Chained(Tree):
    """Contains default types for composite structures to be loaded.
    
    Args:  
        modules Union[str, Sequence[str]]: name(s) of module(s) where object to 
            load is/are located. use is located. Defaults to an empty list.
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
        components (Mapping[str, str]): dict with keys as the type of composite
            class and values as the names of classes in 'modules'. Defaults to
            an empty dict.
        iterator (str, Callable): name of a method to iterator through a
            composite object or a function for iteration. Defaults to iter.
        _loaded (Mapping[str, Any]): dictionary of str keys and previously
            loaded objects. This is checked first by the 'load' method to avoid
            unnecessary re-importation. Defaults to an empty dict.
         
    """    
    modules: str = dataclasses.field(
        default_factory = lambda: [
            'sourdough.project.workers',
            'sourdough.project.actions'])
    name: str = None
    components: Mapping[str, str] = dataclasses.field(
        default_factory = lambda: {
            'root': 'Manager',
            'workers': 'Worker',
            'tasks': 'Task',
            'techniques': 'Technique'})
    iterator: Union[str, Callable] = iter  
    _loaded: Mapping[str, Any] = dataclasses.field(
        default_factory = lambda: dict)
    
      
@dataclasses.dataclass
class Comparative(Tree):
    """Contains default types for composite structures to be loaded.
    
    Args:  
        modules Union[str, Sequence[str]]: name(s) of module(s) where object to 
            load is/are located. use is located. Defaults to an empty list.
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
        components (Mapping[str, str]): dict with keys as the type of composite
            class and values as the names of classes in 'modules'. Defaults to
            an empty dict.
        iterator (str, Callable): name of a method to iterator through a
            composite object or a function for iteration. Defaults to iter.
        _loaded (Mapping[str, Any]): dictionary of str keys and previously
            loaded objects. This is checked first by the 'load' method to avoid
            unnecessary re-importation. Defaults to an empty dict.
         
    """   
    modules: str = dataclasses.field(
        default_factory = lambda: [
            'sourdough.project.workers',
            'sourdough.project.actions'])
    name: str = None
    components: Mapping[str, str] = dataclasses.field(
        default_factory = lambda: {
            'root': 'Manager',
            'workers': 'Worker',
            'tasks': 'Task',
            'techniques': 'Technique'})
    iterator: Union[str, Callable] = itertools.product
    _loaded: Mapping[str, Any] = dataclasses.field(
        default_factory = lambda: dict)      


@dataclasses.dataclass
class Flat(Tree):
    """Contains default types for composite structures to be loaded.
    
    Args:  
        modules Union[str, Sequence[str]]: name(s) of module(s) where object to 
            load is/are located. use is located. Defaults to an empty list.
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
        components (Mapping[str, str]): dict with keys as the type of composite
            class and values as the names of classes in 'modules'. Defaults to
            an empty dict.
        iterator (str, Callable): name of a method to iterator through a
            composite object or a function for iteration. Defaults to iter.
        _loaded (Mapping[str, Any]): dictionary of str keys and previously
            loaded objects. This is checked first by the 'load' method to avoid
            unnecessary re-importation. Defaults to an empty dict.
         
    """
    modules: str = dataclasses.field(
        default_factory = lambda: [
            'sourdough.project.workers',
            'sourdough.project.actions'])
    name: str = None
    components: Mapping[str, str] = dataclasses.field(
        default_factory = lambda: {
            'root': 'Manager',
            'workers': 'Worker',
            'tasks': 'Task',
            'techniques': 'Technique'})
    iterator: Union[str, Callable] = more_itertools.collapse
    _loaded: Mapping[str, Any] = dataclasses.field(
        default_factory = lambda: dict)   
    

@dataclasses.dataclass
class Graph(Structure):
    """Contains default types for composite structures to be loaded.
    
    Args:  
        modules Union[str, Sequence[str]]: name(s) of module(s) where object to 
            load is/are located. use is located. Defaults to an empty list.
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
        components (Mapping[str, str]): dict with keys as the type of composite
            class and values as the names of classes in 'modules'. Defaults to
            an empty dict.
        iterator (str, Callable): name of a method to iterator through a
            composite object or a function for iteration. Defaults to iter.
        _loaded (Mapping[str, Any]): dictionary of str keys and previously
            loaded objects. This is checked first by the 'load' method to avoid
            unnecessary re-importation. Defaults to an empty dict.
         
    """   
    modules: str = dataclasses.field(
        default_factory = lambda: [
            'sourdough.project.graphs',
            'sourdough.project.actions'])
    name: str = None
    components: Mapping[str, str] = dataclasses.field(
        default_factory = lambda: {
            'root': 'Node',
            'node': 'Node',
            'edges': 'Edge',
            'task': 'Task',
            'techniques': 'Technique'})
    iterator: Union[str, Callable] = itertools.product
    _loaded: Mapping[str, Any] = dataclasses.field(
        default_factory = lambda: dict)   
 
 
@dataclasses.dataclass
class Cycle(Structure):
    """Contains default types for composite structures to be loaded.
    
    Args:  
        modules Union[str, Sequence[str]]: name(s) of module(s) where object to 
            load is/are located. use is located. Defaults to an empty list.
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
        components (Mapping[str, str]): dict with keys as the type of composite
            class and values as the names of classes in 'modules'. Defaults to
            an empty dict.
        iterator (str, Callable): name of a method to iterator through a
            composite object or a function for iteration. Defaults to iter.
        _loaded (Mapping[str, Any]): dictionary of str keys and previously
            loaded objects. This is checked first by the 'load' method to avoid
            unnecessary re-importation. Defaults to an empty dict.
         
    """ 
    modules: Union[str, Sequence[str]] = dataclasses.field(
        default_factory = lambda: list)
    name: str = None
    components: Mapping[str, str] = dataclasses.field(
        default_factory = lambda: dict)
    iterator: Union[str, Callable] = itertools.cycle
    _loaded: Mapping[str, Any] = dataclasses.field(
        default_factory = lambda: dict)       