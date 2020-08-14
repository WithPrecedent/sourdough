"""
containers: storage classes for sourdough projects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:


"""
from __future__ import annotations
import abc
import dataclasses
import inspect
import textwrap
from typing import (Any, Callable, ClassVar, Container, Generic, Iterable, 
                    Iterator, Mapping, Sequence, Tuple, TypeVar, Union)

import sourdough


@dataclasses.dataclass
class Details(sourdough.Slate):
    """Basic characteristics of a group of sourdough Components.
    
    Args:
        contents (Mapping[Any, Any]]): stored dictionary. Defaults to an empty 
            dict.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Element is called, 'name' is set based upon
            the 'get_name' method in Element. If that method is not 
            overridden by a subclass instance, 'name' will be assigned to the 
            snake case version of the class name ('__class__.__name__'). 
        
    """
    contents: Sequence[str] = dataclasses.field(default_factory = list)
    generic: str = None
    structure: str = None
    attributes: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    name: str = None
    
    """ Public Methods """
    
    def validate(self, contents: Union[str, Sequence[str]]) -> Sequence[str]:
        """Validates 'contents' or converts 'contents' to a list.
        
        Args:
            contents (Sequence[str]): variable to validate as compatible with 
                an instance.
            
        Raises:
            TypeError: if 'contents' argument is not of a supported datatype.
            
        Returns:
            Sequence[str]: validated or converted argument that is compatible 
                with an instance.
        
        """
        if isinstance(contents, str):
            return sourdough.utilities.listify(contents)
        elif (isinstance(contents, Sequence) 
                and all(isinstance(c, str) for c in contents)):
            return contents
        else:
            raise TypeError('contents must be a str of list of str types')


@dataclasses.dataclass
class Outline(sourdough.Lexicon):
    """Base class for pieces of sourdough composite objects.
    
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Element is called, 'name' is set based upon
            the 'get_name' method in Element. If that method is not 
            overridden by a subclass instance, 'name' will be assigned to the 
            snake case version of the class name ('__class__.__name__'). 
        registry (ClassVar[sourdough.Inventory]): the instance which 
            automatically stores any subclass of Component.
              
    """
    contents: Mapping[str, Details] = dataclasses.field(default_factory = dict)
    generic: str = None
    name: str = None
        
    """ Public Methods """
    
    def validate(self, 
            contents: Mapping[str, Details]) -> Mapping[str, Details]:
        """Validates 'contents' or converts 'contents' to a dict.
        
        Args:
            contents (Mapping[str, Details]): variable to validate as compatible 
                with an instance.
            
        Raises:
            TypeError: if 'contents' argument is not of a supported datatype.
            
        Returns:
            Mapping[str, Details]: validated or converted argument that is 
                compatible with an instance.
        
        """
        if (isinstance(contents, Mapping) 
                and all(isinstance(c, Details) for c in contents.values())):
            return contents
        else:
            raise TypeError(
                'contents must be a dict type with Details type values')


@dataclasses.dataclass
class Inventory(sourdough.Catalog):
    """Catalog subclass with a more limiting 'validate' method.

    Args:
        contents (Union[Element, Sequence[Element], Mapping[Any, 
            Element]]): Element(s) to validate or convert to a dict. If 
            'contents' is a Sequence or a Element, the key for storing 
            'contents' is the 'name' attribute of each Element.
        defaults (Sequence[str]]): a list of keys in 'contents' which will be 
            used to return items when 'default' is sought. If not passed, 
            'default' will be set to all keys.
        always_return_list (bool]): whether to return a list even when
            the key passed is not a list or special access key (True) or to 
            return a list only when a list or special acces key is used (False). 
            Defaults to False.
        stored_types (Tuple[Callable]):
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Element is called, 'name' is set based upon
            the 'get_name' method in Element. If that method is not 
            overridden by a subclass instance, 'name' will be assigned to the 
            snake case version of the class name ('__class__.__name__').  
                     
    """
    contents: Mapping[Any, Any] = dataclasses.field(default_factory = dict)  
    defaults: Sequence[str] = dataclasses.field(default_factory = list)
    always_return_list: bool = False
    stored_types: Tuple[Callable] = (sourdough.Element)
    name: str = None
        
    """ Public Methods """

    def validate(self, 
            contents: Union[
                sourdough.Element,
                Mapping[Any, sourdough.Element],
                Sequence[sourdough.Element]]) -> Mapping[
                    str, sourdough.Element]:
        """Validates 'contents' or converts 'contents' to a dict.
        
        Args:
            contents (Union[Element, Mapping[Any, self.stored_types], 
                Sequence[Element]]): Element(s) to validate or convert to a 
                dict. If 'contents' is a Sequence or a Element, the key for 
                storing 'contents' is the 'name' attribute of each Element.
                
        Raises:
            TypeError: if 'contents' is neither a Element subclass, Sequence
                of Element subclasses, or Mapping with Elements subclasses
                as values.
                
        Returns:
            Mapping (str, self.stored_types): a properly typed dict derived
                from passed 'contents'.
            
        """
        if (isinstance(contents, Mapping)
            and (all(isinstance(c, self.stored_types) 
                    for c in contents.values())
                or all(issubclass(c, self.stored_types)
                         for c in contents.values()))):
            return contents
        elif isinstance(contents, self.stored_types):
            return {contents.name: contents}
        elif (inspect.isclass(contents) 
                and issubclass(contents, self.stored_types)):
            return {contents.get_name(): contents}
        elif isinstance(contents, Sequence):
            new_contents = {}
            for element in contents:
                if (isinstance(contents, self.stored_types) or 
                        (inspect.isclass(contents) 
                            and issubclass(contents, self.stored_types))):
                    try:
                        new_contents[element.name] = element
                    except AttributeError:
                        new_contents[element.get_name()] = element
                else:
                    raise TypeError(
                        'contents must contain all Element subclasses or '
                        'subclass instances')  
                
            return new_contents
        else:
            raise TypeError(
                f'contents must a dict with {self.stored_types} values, '
                f'{self.stored_types}, or a list of {self.stored_types}')    


@dataclasses.dataclass
class Overview(sourdough.Lexicon):
    """Dictionary of different Element types in a Worker instance.
    
    Args:
        contents (Mapping[Any, Any]]): stored dictionary. Defaults to an empty 
            dict.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Element is called, 'name' is set based upon
            the 'get_name' method in Element. If that method is not 
            overridden by a subclass instance, 'name' will be assigned to the 
            snake case version of the class name ('__class__.__name__').
              
    """
    contents: Mapping[Any, Any] = dataclasses.field(default_factory = dict)
    name: str = None
    worker: sourdough.Worker = None
    
    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent initialization method(s).
        super().__post_init__()
        if self.worker.structure is not None:
            self.add({
                'name': self.worker.name, 
                'structure': self.worker.structure.name})
            for key, value in self.worker.structure.options.items():
                matches = self.worker.find(
                    self._get_type, 
                    element = value)
                if len(matches) > 0:
                    self.contents[f'{key}s'] = matches
        else:
            raise ValueError(
                'structure must be a Role for an overview to be created.')
        return self          
    
    """ Dunder Methods """
    
    def __str__(self) -> str:
        """Returns pretty string representation of an instance.
        
        Returns:
            str: pretty string representation of an instance.
            
        """
        new_line = '\n'
        representation = [f'sourdough {self.get_name}']
        for key, value in self.contents.items():
            if isinstance(value, Sequence):
                names = [v.name for v in value]
                representation.append(f'{key}: {", ".join(names)}')
            else:
                representation.append(f'{key}: {value}')
        return new_line.join(representation)    

    """ Private Methods """

    def _get_type(self, 
            item: sourdough.Element, 
            element: sourdough.Element) -> Sequence[sourdough.Element]: 
        """[summary]

        Args:
            item (self.stored_types): [description]
            self.stored_types (self.stored_types): [description]

        Returns:
            Sequence[self.stored_types]:
            
        """
        if isinstance(item, element):
            return [item]
        else:
            return []
      