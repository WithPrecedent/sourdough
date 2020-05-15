"""
.. module:: Registry
:synopsis: subclass registration made simple
:author: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import collections.abc
import dataclasses
import importlib
import inspect
import pathlib
import pyclbr
import re
from typing import (
    Any, Callable, ClassVar, Dict, Iterable, List, Optional, Tuple, Union)

import sourdough

   
@dataclasses.dataclass
class Library(collections.abc.MutableMapping): 
    """Stores subclass instances.
    
    Arguments:
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. If the class instance
            needs settings from the shared Settings instance, 'name' should
            match the appropriate section name in that Settings instance. When
            subclassing, it is a good settings to use the same 'name' attribute
            as the base class for effective coordination between sourdough
            classes. Defaults to None or __class__.__name__.lower().
        contents (Optional[Dict[str, Component]]): stored dictionary. Defaults 
            to an empty dictionary.
        base (object): related class for which matching subclasses and/or
            subclass instances should be stored.

    """
    name: Optional[str] = None
    contents: Optional[Dict[str, 'Component']] = dataclasses.field(
        default_factory = dict)
    base: Optional[object] = None

    """ Required ABC Methods """

    def __getitem__(self, key: str) -> Any:
        """Returns value for 'key' in 'contents'.

        Arguments:
            key (str): name of key in 'contents' for which value is sought.

        Returns:
            Any: value stored in 'contents'.

        """
        return self.contents[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Sets 'key' in 'contents' to 'value'.

        Arguments:
            key (str): name of key to set in 'contents'.
            value (Any): value to be paired with 'key' in 'contents'.

        """
        self.contents[key] = value
        return self

    def __delitem__(self, key: str) -> None:
        """Deletes 'key' in 'contents'.

        Arguments:
            key (str): name of key in 'contents' to delete the key/value pair.

        """
        del self.contents[key]
        return self

    def __iter__(self) -> Iterable:
        """Returns iterable of 'contents'.

        Returns:
            Iterable: of 'contents'.

        """
        return iter(self.contents)

    def __len__(self) -> int:
        """Returns length of 'contents'.

        Returns:
            int: length of 'contents'.

        """
        return len(self.contents)

    """ Other Dunder Methods """

    def __add__(self, other: 'MappingBase') -> None:
        """Combines argument with 'contents'.

        Arguments:
            other (MappingBase): another MappingBase or compatiable dictionary

        """
        self.add(contents = other)
        return self
    
    def __iadd__(self, other: 'MappingBase') -> None:
        """Combines argument with 'contents'.

        Arguments:
            other (MappingBase): another MappingBase or compatiable dictionary

        """
        self.add(contents = other)
        return self

    def __repr__(self) -> str:
        """Returns '__str__' representation.

        Returns:
            str: default dictionary representation of 'contents'.

        """
        return self.__str__()

    def __str__(self) -> str:
        """Returns default dictionary representation of 'contents'.

        Returns:
            str: default dictionary representation of 'contents'.

        """
        return (
            f'sourdough {self.__class__.__name__} '
            f'name: {self.name} '
            f'contents: {self.contents.__str__()} ')   
    

@dataclasses.dataclass
class Catalog(Library): 
    """Base class for storing Component subclasses.

    Arguments:
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. If the class instance
            needs settings from the shared Settings instance, 'name' should
            match the appropriate section name in that Settings instance. When
            subclassing, it is a good settings to use the same 'name' attribute
            as the base class for effective coordination between sourdough
            classes. Defaults to None or __class__.__name__.lower().
        contents (Optional[Dict[str, Component]]): stored dictionary. Defaults 
            to an empty dictionary.
        base (object): related class for which matching subclasses and/or
            subclass instances should be stored.

        auto_register (Optional[bool]): whether to walk through the current
            working directory and subfolders to search for classes to add to
            the Library (True). Defaults to True.
    
    """ 
    name: Optional[str] = None  
    contents: Optional[Dict[str, 'Component']] = dataclasses.field(
        default_factory = dict)
    base: Optional[object] = None
    auto_register: Optional[bool] = False
        
    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        self.base
        if self.auto_register:
            self.walk(folder = pathlib.Path.cwd())
        return self
        
    """ Public Methods """

    def add(self, component: 'Component') -> None:
        """Combines argument with 'contents'.
        

        """
        try:
            key = sourdough.utilities.snakify(component.__name__)
            self.contents[key] = component
        except AttributeError:
            key = sourdough.utilities.snakify(component.__class__.__name__)
            self.contents[key] = component.__class__
        return self
    
    def create(self, name: str, **kwargs) -> 'Component':
        """Returns an instance of a stored subclass.
        
        Arguments:
            name (str): key to desired Component in 'contents'.
            
        Returns:
            Component: that has been instanced with kwargs as arguments.
            
        """
        return self[name](**kwargs)
     
    def walk(self, 
            folder: Union[str, pathlib.Path], 
            recursive: Optional[bool] = True) -> None:
        """Adds Component subclasses for python files in 'folder'.
        
        If 'recursive' is True, subfolders are searched as well.
        
        Arguments:
            folder (Union[str, pathlib.Path]): folder to initiate search for 
                Component subclasses.
            recursive (Optional[bool]): whether to also search subfolders (True)
                or not (False). Defaults to True.
                
        """
        if recursive:
            glob_method = 'rglob'
        else:
            glob_method = 'glob'
        for file_path in getattr(pathlib.Path(folder), glob_method)('*.py'):
            module = self._import_from_path(file_path = file_path)
            subclasses = self._get_subclasses(module = module)
            for subclass in subclasses:
                self.add({
                    sourdough.utilities.snakify(subclass.__name__): subclass})    
        return self
       
    """ Private Methods """
    
    def _import_from_path(self, file_path: Union[pathlib.Path, str]) -> object:
        """Returns an imported module from a file path.
        
        Arguments:
            file_path (Union[pathlib.Path, str]): path of a python module.
        
        Returns:
            object: an imported python module. 
        
        """
        file_path = pathlib.Path(file_path)
        module_spec = importlib.util.spec_from_file_location(file_path)
        module = importlib.util.module_from_spec(module_spec)
        return module_spec.loader.exec_module(module)
    
    def _get_subclasses(self, module: object) -> List['Component']:
        """Returns a list of Component subclasses.
        
        Arguments:
            module (object): an import python module.
        
        Returns:
            List[Component]: list of subclasses of Component. If none are found,
                an empty list is returned.
                
        """
        matches = []
        for item in pyclbr.readmodule(module):
            # Adds direct subclasses.
            if inspect.issubclass(item, Component):
                matches.append[item]
            else:
                # Adds subclasses of other subclasses.
                for subclass in self.contents.values():
                    if subclass(item, subclass):
                        matches.append[item]
        return matches
