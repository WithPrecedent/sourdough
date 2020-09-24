"""
validators: sourdough mixin type validators and converters
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Mapify (Validator):
    Sequencify (Validator):
    
"""
from __future__ import annotations
import abc
import dataclasses
from typing import (
    Any, Callable, ClassVar, Dict, Iterable, List, Mapping, Sequence, Union)

import sourdough


@dataclasses.dataclass
class Mapify(sourdough.quirks.Validator, abc.ABC):
    """Type validator and converter for Mappings.
    
    Args:
        accepts (Union[Sequence[Any], Any]): type(s) accepted by the parent 
            class either as an individual item, in a Mapping, or in a Sequence.
            Defaults to sourdough.base.Element.
        stores (Any): a single type stored by the parent class. Defaults to 
            dict.
            
    """    
    accepts: Union[Sequence[Any], Any] = dataclasses.field(
        default_factory = lambda: sourdough.base.Element)
    stores: Any = dataclasses.field(default_factory = lambda: dict)
    
    """ Public Methods """
    
    def convert(self, 
            contents: sourdough.Elemental) -> (
                Mapping[str, sourdough.base.Element]):
        """Converts 'contents' to a Mapping type.
        
        Args:
            contents (sourdough.Elemental): an object containing one or 
                more Element subclasses or Element subclass instances.
        
        Raises:
            TypeError: if 'contents' is not an sourdough.Elemental.
                
        Returns:
            Mapping[str, Element]: converted 'contents'.
            
        """
        converted = self.stores()
        contents = self.verify(contents = contents)
        if isinstance(contents, Mapping):
            converted = contents
        elif (isinstance(contents, Sequence) 
                or isinstance(contents, sourdough.base.Element)):
            for item in sourdough.tools.tuplify(contents):
                try:
                    converted[item.name] = item
                except AttributeError:
                    converted[item.get_name()] = item
        return converted
    

@dataclasses.dataclass    
class Sequencify(sourdough.quirks.Validator, abc.ABC):
    """Type validator and converter for Sequences.
    
    Args:
        accepts (Union[Sequence[Any], Any]): type(s) accepted by the parent 
            class either as an individual item, in a Mapping, or in a Sequence.
            Defaults to sourdough.base.Element.
        stores (Any): a single type accepted by the parent class. Defaults to 
            list.
            
    """        
    accepts: Union[Sequence[Any], Any] = dataclasses.field(
        default_factory = lambda: sourdough.base.Element)
    stores: Any = dataclasses.field(default_factory = lambda: list)
    
    """ Public Methods """
       
    def convert(self, 
            contents: sourdough.Elemental) -> (
                Sequence[sourdough.base.Element]):
        """Converts 'contents' to a Sequence type.
        
        Args:
            contents (sourdough.Elemental): an object containing one or 
                more Element subclasses or Element subclass instances.
        
        Raises:
            TypeError: if 'contents' is not an sourdough.Elemental.
                
        Returns:
            Sequence[Element]: converted 'contents'.
            
        """
        converted = self.stores()
        if isinstance(contents, Mapping):
            converted = converted.extend(contents.values())
        elif isinstance(contents, Sequence):
            converted = contents
        elif isinstance(contents, sourdough.base.Element):
            converted = converted.append(contents)
        return converted  
        