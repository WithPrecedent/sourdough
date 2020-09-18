"""
types: sourdough type annotators, validators, and converters
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    ValidatorOptions (Registry): abstract base class for any type validators 
        and converters. All subclasses must have 'verify' and 'convert' methods.
    Validator (Factory): returns ValidatorOption subclass instance which is used
        for type validation and conversion.

"""
from __future__ import annotations
import abc
import dataclasses
import typing
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union

import sourdough

 
@dataclasses.dataclass
class ValidatorOption(sourdough.base.Registry):
    """Base class for type validation and/or conversion.
    
    Args:
        accepts (Union[Sequence[Any], Any]): type(s) accepted by the parent 
            class.
        stores (Any): a single type accepted by the parent class. Defaults 
            to None. If it is set to none, then an instance is only useful for 
            validation and does not convert types.
            
    """
    accepts: Union[Sequence[Any], Any] = dataclasses.field(
        default_factory = list)
    stores: Any = None
    library: ClassVar[sourdough.base.Catalog] = sourdough.base.Catalog()
            
    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def verify(self, contents: Any) -> Any:
        pass
    
    @abc.abstractmethod
    def convert(self, contents: Any) -> Any:
        pass   


@dataclasses.dataclass
class Validator(sourdough.base.Factory, abc.ABC):
    """Factory for type validation and/or conversion class construction.
    
    Validator is primary used to convert Element subclasses to and from single
    instances, Mappings of instances, and Sequences of instances. However, with
    additional conversion methods, it can be extended to any validation or 
    converstion task.
    
    Args:
        accepts (Union[Sequence[Callable], Callable]): type(s) accepted by the
            parent class.
        stores (Callable): a single type accepted by the parent class. Defaults 
            to None. If it is set to none, then an instance is only useful for 
            validation and does not convert types.
            
    """
    products: Union[str, Sequence[str]]
    accepts: Union[Sequence[Any], Any] = dataclasses.field(
        default_factory = list)
    stores: Any = None
    options: ClassVar[sourdough.base.Options] = ValidatorOption
           

@dataclasses.dataclass
class Mapify(ValidatorOption):
    
    accepts: Union[Sequence[Any], Any] = dataclasses.field(
        default = lambda: [Mapping, Sequence, sourdough.base.Element])
    stores: Any = dataclasses.field(default = lambda: Mapping)
    
    """ Public Methods """

    def verify(contents: sourdough.base.Elemental) -> sourdough.base.Elemental:
        """Verifies that 'contents' is or contains the type 'kind'.

        Args:
            contents (sourdough.base.Elemental): item to verify its type.
            kind (Element): the specific class type which 'contents' must be or 
                'contain'. Defaults to Element.

        Raises:
            TypeError: if 'contents' is not or does not contain 'kind'.

        Returns:
            sourdough.base.Elemental: the original 'contents'.
            
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
            contents: sourdough.base.Elemental) -> Mapping[str, sourdough.base.Element]:
        """Converts 'contents' to a Mapping type.
        
        If 'stores' is not None, it must have a 'contents' attribute which is 
        where the converted 'contents' will be passed. If it is not passed, 
        'contents' will be converted to an ordinary dict.
        
        If 'contents' is already a Mapping, it is not converted. However, it 
        still will be placed inside a 'stores' instance if 'stores' is not None.
        
        Args:
            contents (sourdough.base.Elemental): an object containing one or more Element
                subclasses or Element subclass instances.
        
        Raises:
            TypeError: if 'contents' is not an sourdough.base.Elemental.
                
        Returns:
            Mapping[str, Element]: converted 'contents'.
            
        """
        if isinstance(contents, Mapping):
            converted = contents
        elif isinstance(contents, Sequence) or isinstance(contents, sourdough.base.Element):
            converted = {}
            for item in sourdough.tools.listify(contents):
                try:
                    converted[item.name] = item
                except AttributeError:
                    converted[item.get_name()] = item
        else:
            raise TypeError(f'contents must be {sourdough.base.Elemental} type')
        if self.stores:
            converted = self.stores(contents = converted)
        return converted
    

@dataclasses.dataclass    
class Sequencify(ValidatorOption):
    
    accepts: Union[Sequence[Any], Any] = dataclasses.field(
        default = lambda: [Mapping, Sequence, sourdough.base.Element])
    stores: Any = dataclasses.field(default = lambda: Sequence)
    
    def convert(self, contents: sourdough.base.Elemental) -> Sequence[Element]:
        """Converts 'contents' to a Sequence type.
        
        If 'stores' is not None, it must have a 'contents' attribute which is 
        where the converted 'contents' will be passed. If it is not passed, 
        'contents' will be converted to an ordinary list.
        
        If 'contents' is already a Sequence, it is not converted. However, it 
        still will be placed inside a 'stores' instance if 'stores' is not None.
        
        Args:
            contents (sourdough.base.Elemental): an object containing one or more Element
                subclasses or Element subclass instances.
        
        Raises:
            TypeError: if 'contents' is not an sourdough.base.Elemental.
                
        Returns:
            Sequence[Element]: converted 'contents'.
            
        """    
        if isinstance(contents, Mapping):
            converted = list(contents.values())
        elif isinstance(contents, Sequence):
            converted = contents
        elif isinstance(contents, sourdough.base.Element):
            converted = [contents]
        else:
            raise TypeError(f'contents must be {sourdough.base.Elemental} type')
        if self.stores:
            converted = self.stores(contents = converted)
        return converted  




    """ Public Methods """

    def convert(self, contents: sourdough.base.Elemental) -> Any:
        """Converts 'contents' to the appropriate type based on 'converters'.
        
        Args:
            contents (sourdough.base.Elemental): an object containing one or more Element
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
