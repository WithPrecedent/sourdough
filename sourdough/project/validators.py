"""
types: sourdough type annotators, validators, and converters
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Validator (Container): class for type validation and conversion.

"""
from __future__ import annotations
import abc
import dataclasses
import inspect
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union

import sourdough


@dataclasses.dataclass
class Mapify(sourdough.base.ValidatorBase):
    
    
    """ Public Methods """

    def verify(
            contents: Union[Sequence[Callable], Callable]) -> sourdough.Elemental:
        """Verifies that 'contents' is or contains the type 'kind'.

        Args:
            contents (sourdough.Elemental): item to verify its type.
            kind (Element): the specific class type which 'contents' must be or 
                'contain'. Defaults to Element.

        Raises:
            TypeError: if 'contents' is not or does not contain 'kind'.

        Returns:
            sourdough.Elemental: the original 'contents'.
            
        """
        if not ((isinstance(contents, kind) 
                or (inspect.isclass(contents) and issubclass(contents, kind)))
            or (isinstance(contents, Sequence) 
                    and (all(isinstance(c, kind) for c in contents)
                or (all(inspect.isclass(c) for c in contents)
                    and all(issubclass(c, kind) for c in contents))))
            or (isinstance(contents, Mapping)
                    and (all(isinstance(c, kind) for c in contents.values())
                or (all(inspect.isclass(c) for c in contents.values())
                    and all(issubclass(c, kind) for c in contents.values()))))):
            raise TypeError(f'contents must be or conttain {kind} type(s)')  
        return contents
    
    def convert(self, 
            contents: sourdough.Elemental) -> Mapping[str, sourdough.Element]:
        """Converts 'contents' to a Mapping type.
        
        If 'stores' is not None, it must have a 'contents' attribute which is 
        where the converted 'contents' will be passed. If it is not passed, 
        'contents' will be converted to an ordinary dict.
        
        If 'contents' is already a Mapping, it is not converted. However, it 
        still will be placed inside a 'stores' instance if 'stores' is not None.
        
        Args:
            contents (sourdough.Elemental): an object containing one or more Element
                subclasses or Element subclass instances.
        
        Raises:
            TypeError: if 'contents' is not an sourdough.Elemental.
                
        Returns:
            Mapping[str, Element]: converted 'contents'.
            
        """
        if isinstance(contents, Mapping):
            converted = contents
        elif isinstance(contents, Sequence) or isinstance(contents, sourdough.Element):
            converted = {}
            for item in sourdough.tools.listify(contents):
                try:
                    converted[item.name] = item
                except AttributeError:
                    converted[item.get_name()] = item
        else:
            raise TypeError(f'contents must be {sourdough.Elemental} type')
        if self.stores:
            converted = self.stores(contents = converted)
        return converted
    

@dataclasses.dataclass    
class Sequencify(sourdough.base.ValidatorBase):
    

    def convert(self, contents: sourdough.Elemental) -> Sequence[Element]:
        """Converts 'contents' to a Sequence type.
        
        If 'stores' is not None, it must have a 'contents' attribute which is 
        where the converted 'contents' will be passed. If it is not passed, 
        'contents' will be converted to an ordinary list.
        
        If 'contents' is already a Sequence, it is not converted. However, it 
        still will be placed inside a 'stores' instance if 'stores' is not None.
        
        Args:
            contents (sourdough.Elemental): an object containing one or more Element
                subclasses or Element subclass instances.
        
        Raises:
            TypeError: if 'contents' is not an sourdough.Elemental.
                
        Returns:
            Sequence[Element]: converted 'contents'.
            
        """    
        if isinstance(contents, Mapping):
            converted = list(contents.values())
        elif isinstance(contents, Sequence):
            converted = contents
        elif isinstance(contents, sourdough.Element):
            converted = [contents]
        else:
            raise TypeError(f'contents must be {sourdough.Elemental} type')
        if self.stores:
            converted = self.stores(contents = converted)
        return converted  




    """ Public Methods """

    def convert(self, contents: sourdough.Elemental) -> Any:
        """Converts 'contents' to the appropriate type based on 'converters'.
        
        Args:
            contents (sourdough.Elemental): an object containing one or more Element
                subclasses or Element subclass instances.
        
        Raises:
            ValueError: if 'stores' is None.
            TypeError: if there is no converter method for the type in 'stores'.
              
        Returns:
            Any: converted 'contents'.
            
        """
        contents = self.verify(contents = contents, kind = self.stores)
        if self.stores is None:
            raise ValueError(
                'Validator cannot convert without a value for stores')
        try:
            return getattr(self, self.converters[self.stores])(
                contents = contents)
        except (KeyError, AttributeError):
            raise TypeError(f'no matching converter for {self.stroes}')  
