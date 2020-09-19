"""
validator: sourdough type annotators, validators, and converters
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    ValidatorFactory (Factory): returns sourdough.base.Validator subclass 
        instance which is used for type validation and conversion.

"""
from __future__ import annotations
import abc
import dataclasses
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union

import sourdough


@dataclasses.dataclass
class Mapify(sourdough.base.Validator):
    """Type validator and converter for Mappings.
    
    Args:
        accepts (Union[Sequence[Any], Any]): type(s) accepted by the parent 
            class either as an individual item, in a Mapping, or in a Sequence.
            Defaults to sourdough.base.Element.
        stores (Any): a single type stored by the parent class. Defaults 
            to dict.
            
    """    
    accepts: Union[Sequence[Any], Any] = dataclasses.field(
        default_factory = lambda: sourdough.base.Element)
    stores: Any = dataclasses.field(default_factory = lambda: dict)
    
    """ Public Methods """
    
    def convert(self, 
            contents: sourdough.base.Elemental) -> (
                Mapping[str, sourdough.base.Element]):
        """Converts 'contents' to a Mapping type.
        
        Args:
            contents (sourdough.base.Elemental): an object containing one or 
                more Element subclasses or Element subclass instances.
        
        Raises:
            TypeError: if 'contents' is not an sourdough.base.Elemental.
                
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
class Sequencify(sourdough.base.Validator):
    """Type validator and converter for Sequences.
    
    Args:
        accepts (Union[Sequence[Callable], Callable]): type(s) accepted by the
            parent class. Defaults to sourdough.base.Element.
        stores (Callable): a single type accepted by the parent class. Defaults 
            to None. If it is set to none, then an instance is only useful for 
            validation and does not convert types. Defaults to Sequence.
            
    """        
    accepts: Union[Sequence[Any], Any] = dataclasses.field(
        default_factory = lambda: sourdough.base.Element)
    stores: Any = dataclasses.field(default_factory = lambda: list)
    
    def convert(self, 
            contents: sourdough.base.Elemental) -> (
                Sequence[sourdough.base.Element]):
        """Converts 'contents' to a Sequence type.
        
        Args:
            contents (sourdough.base.Elemental): an object containing one or 
                more Element subclasses or Element subclass instances.
        
        Raises:
            TypeError: if 'contents' is not an sourdough.base.Elemental.
                
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


@dataclasses.dataclass
class ValidatorFactory(sourdough.base.Factory, abc.ABC):
    """Factory for type validation and/or conversion class construction.
    
    ValidatorFactory is primary used to convert Element subclasses to and from 
    single instances, Mappings of instances, and Sequences of instances. 
    
    Args:
        product (Union[str, Sequence[str]]): name(s) of objects to return. 
            'product' must correspond to key(s) in 'options.library'.
        accepts (Union[Sequence[Any], Any]): type(s) accepted by the parent 
            class either as an individual item, in a Mapping, or in a Sequence.
        stores (Any): a single type stored by the parent class. Defaults 
            to None.
        options (ClassVar[sourdough.base.Options]): class which contains a 
            'library' of alternatives for constructing objects.
            
    """
    product: Union[str, Sequence[str]]
    accepts: Union[Sequence[Any], Any] = dataclasses.field(
        default_factory = list)
    stores: Any = None
    options: ClassVar[sourdough.base.Options] = sourdough.base.Validator
     