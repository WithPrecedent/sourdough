"""
containers: storage classes for sourdough projects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:


"""
import abc
import dataclasses
import inspect
import textwrap
from typing import (
    Any, Callable, ClassVar, Iterable, Mapping, Sequence, Tuple, Union)

import sourdough


@dataclasses.dataclass
class Outline(sourdough.Lexicon):
    
    contents: Mapping[str, Sequence[str]] = dataclasses.field(
        default_factory = dict)
    generics: Mapping[str, str] = dataclasses.field(default_factory = dict)
    name: str = None
        
    """ Public Methods """
    
    def validate(self, 
            contents: Mapping[str, Sequence[str]]) -> Mapping[
                str, 
                Sequence[str]]:
        """Validates 'contents' or converts 'contents' to a dict.
        
        Args:
            contents (Any): variable to validate as compatible with an instance.
            
        Raises:
            TypeError: if 'contents' argument is not of a supported datatype.
            
        Returns:
            Mapping[Any, Any]: validated or converted argument that is 
                compatible with an instance.
        
        """
        if (isinstance(contents, Mapping) 
                and all(isinstance(c, Sequence) for c in contents.values())):
            return contents
        else:
            raise TypeError('contents must be a dict type with list values')


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
                'sourdough.Element',
                Mapping[Any, 'sourdough.Element'],
                Sequence['sourdough.Element']]) -> Mapping[
                    str, 'sourdough.Element']:
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
    worker: 'sourdough.Worker' = None
    
    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent initialization method(s).
        super().__post_init__()
        if self.worker.role is not None:
            self.add({
                'name': self.worker.name, 
                'role': self.worker.role.name})
            for key, value in self.worker.role.options.items():
                matches = self.worker.find(
                    self._get_type, 
                    element = value)
                if len(matches) > 0:
                    self.contents[f'{key}s'] = matches
        else:
            raise ValueError(
                'role must be a Role for an overview to be created.')
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
            item: 'sourdough.Element', 
            element: 'sourdough.Element') -> Sequence[
                'sourdough.Element']: 
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


# @dataclasses.dataclass
# class SmartOptionsMixin(abc.ABC):
#     """Mixin which stores classes or instances in a dynamically-named attribute.
    
#     In contrast to the typical OptionsMixin, the SmartOptionsMixin searches the
#     MRO for the first Element subclass and uses its name to create a class
#     attribute.

#     Namespaces: 'options', 'select', '{snakify(compenent_class.snakify)}s',
#         '_set_options_attribute', '_options_attribute'.

#     """
    
#     """ Initialization Methods """
    
#     def __post_init__(self):
#         """Registers an instance with 'library'."""
#         # Calls initialization method of other inherited classes.
#         try:
#             super().__post_init__()
#         except AttributeError:
#             pass
#         # Creates class attribute storing an Inventory instance.
#         self._set_options_attribute()
        
#     """ Public Methods """
        
#     def select(self, key: Union[str, Sequence[str]], **kwargs) -> Union[
#             object, Sequence[object]]:
#         """Creates instance(s) of a class(es) stored in 'options'.

#         Args:
#             key (str): name matching a key in 'options' for which the value
#                 is sought.

#         Raises:
#             TypeError: if 'option' is neither a str nor Sequence type.
            
#         Returns:
#             Union[object, Sequence[object]]: instance(s) of a stored value(s).
            
#         """
#         def _select_item(single_key: str) -> object:
#             """Nested function to return a single value in 'options'.
        
#             A nested function is used to avoid cluttering the namespace of a
#             an object using the OptionsMixin.
            
#             Args:
#                 single_key (str): name of key for value to be returned.
                
#             Returns:
#                 object: instance of a stored value.
            
#             """
#             if kwargs:
#                 return getattr(
#                     self, self._options_attribute)[single_key](**kwargs)
#             else:
#                 return getattr(self, self._options_attribute)[single_key]
            
#         if isinstance(key, str):
#             return _select_item(single_key = key)
#         elif isinstance(key, Sequence):
#             instances = []
#             for k in key:
#                 instances.append(_select_item(single_key = k))
#             return instances
#         else:
#             raise TypeError('option must be a str or list type')
        
#     """ Private Methods """
    
#     def _set_options_attribute(self) -> None:
#         """Assigns Inventory instance to dynamically named attribute.
        
#         The name of the attribute is the snake_case name of the first Element
#         subclass found in the MRO.
        
#         """
#         base = [issubclass(c, sourdough.Element) for c in self.__mro__()][0]
#         base = f'{sourdough.utilities.snakify(base.__name__)}s'
#         self._options_attribute = base
#         setattr(self, base, sourdough.Inventory(always_return_list = True))
#         return self
            