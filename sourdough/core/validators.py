"""
validator: sourdough type validator and converter.
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Validator (Container): class for type validation and conversion.

"""
from __future__ import annotations
import abc
import collections.abc
import copy
import dataclasses
import inspect
import textwrap
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union

import sourdough


@dataclasses.dataclass
class Validator(sourdough.creators.Factory):
    """Validates and/or converts object types.
    
    Validator is primary used to convert Element subclasses to and from single
    instances, Mappings of instances, and Sequences of instances. However, with
    additional conversion methods, it can be extended to any validation or 
    converstion task.
    
    Args:
        accepts (Any): a Union of types or a single type.
        stores (Callable): a single type. Defaults to None. If it is set to 
            none, then an instance is only useful for validation and does not 
            convert types.
            
    """
    products: str
    accepts: Union[Sequence[Callable], Callable] = dataclasses.field(
        default_factory = list)
    stores: Callable = None
    options: ClassVar[Mapping[Any, str]] = {
        'mapping': 'mapify', 
        'sequence': 'sequencify'}

    """ Public Methods """

    def convert(self, element: sourdough.Elemental) -> Any:
        """Converts 'element' to the appropriate type based on 'converters'.
        
        Args:
            element (sourdough.Elemental): an object containing one or more Element
                subclasses or Element subclass instances.
        
        Raises:
            ValueError: if 'stores' is None.
            TypeError: if there is no converter method for the type in 'stores'.
              
        Returns:
            Any: converted 'element'.
            
        """
        element = self.verify(element = element, kind = self.stores)
        if self.stores is None:
            raise ValueError(
                'Validator cannot convert without a value for stores')
        try:
            return getattr(self, self.converters[self.stores])(
                element = element)
        except (KeyError, AttributeError):
            raise TypeError(f'no matching converter for {self.stroes}')
        
    def mapify(self, element: sourdough.Elemental) -> Mapping[str, Element]:
        """Converts 'element' to a Mapping type.
        
        If 'stores' is not None, it must have a 'contents' attribute which is 
        where the converted 'element' will be passed. If it is not passed, 
        'element' will be converted to an ordinary dict.
        
        If 'element' is already a Mapping, it is not converted. However, it 
        still will be placed inside a 'stores' instance if 'stores' is not None.
        
        Args:
            element (sourdough.Elemental): an object containing one or more Element
                subclasses or Element subclass instances.
        
        Raises:
            TypeError: if 'element' is not an sourdough.Elemental.
                
        Returns:
            Mapping[str, Element]: converted 'element'.
            
        """
        if isinstance(element, Mapping):
            converted = element
        elif isinstance(element, Sequence) or isinstance(element, Element):
            converted = {}
            for item in sourdough.tools.listify(element):
                try:
                    converted[item.name] = item
                except AttributeError:
                    converted[item.get_name()] = item
        else:
            raise TypeError(f'element must be {sourdough.Elemental} type')
        if self.stores:
            converted = self.stores(contents = converted)
        return converted

    def sequencify(self, element: sourdough.Elemental) -> Sequence[Element]:
        """Converts 'element' to a Sequence type.
        
        If 'stores' is not None, it must have a 'contents' attribute which is 
        where the converted 'element' will be passed. If it is not passed, 
        'element' will be converted to an ordinary list.
        
        If 'element' is already a Sequence, it is not converted. However, it 
        still will be placed inside a 'stores' instance if 'stores' is not None.
        
        Args:
            element (sourdough.Elemental): an object containing one or more Element
                subclasses or Element subclass instances.
        
        Raises:
            TypeError: if 'element' is not an sourdough.Elemental.
                
        Returns:
            Sequence[Element]: converted 'element'.
            
        """    
        if isinstance(element, Mapping):
            converted = list(element.values())
        elif isinstance(element, Sequence):
            converted = element
        elif isinstance(element, Element):
            converted = [element]
        else:
            raise TypeError(f'element must be {sourdough.Elemental} type')
        if self.stores:
            converted = self.stores(contents = converted)
        return converted

    def verify(
            element: sourdough.Elemental, 
            kind: sourdough.Element = sourdough.Element) -> sourdough.Elemental:
        """Verifies that 'element' is or contains the type 'kind'.

        Args:
            element (sourdough.Elemental): item to verify its type.
            kind (Element): the specific class type which 'element' must be or 
                'contain'. Defaults to Element.

        Raises:
            TypeError: if 'element' is not or does not contain 'kind'.

        Returns:
            sourdough.Elemental: the original 'element'.
            
        """
        if not ((isinstance(element, kind) 
                or (inspect.isclass(element) and issubclass(element, kind)))
            or (isinstance(element, Sequence) 
                    and (all(isinstance(c, kind) for c in element)
                or (all(inspect.isclass(c) for c in element)
                    and all(issubclass(c, kind) for c in element))))
            or (isinstance(element, Mapping)
                    and (all(isinstance(c, kind) for c in element.values())
                or (all(inspect.isclass(c) for c in element.values())
                    and all(issubclass(c, kind) for c in element.values()))))):
            raise TypeError(f'element must be or conttain {kind} type(s)')  
        return element
       
    """ Dunder Methods """
    
    def __contains__(self, item: Callable) -> bool:
        """Returns whether 'item' is in 'stores'.
        
        Args:
            item (Callable): item to check.
            
        Returns:
            bool: if item is in the 'stores' attribute.
            
        """
        return item in self.stores    
    
    