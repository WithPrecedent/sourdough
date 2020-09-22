"""
quirks: sourdough quirks architecture
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Validator (Registry, Quirk): abstract base class for type validators and 
        converters. The class provides a universal 'verify' method for type
        validation. All subclasses must have a 'convert' method for type 
        conversion.
    ValidatorFactory (Factory): returns sourdough.base.Validator subclass 
        instance which is used for type validation and conversion.
    Loader (Quirk): lazy loader which uses a 'load' method to import python
        classes, functions, and other items at runtime on demand. 
 
"""
from __future__ import annotations
import abc
import dataclasses
import inspect
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union

import sourdough


@dataclasses.dataclass
class Validator(sourdough.base.Registry, sourdough.base.Quirk, abc.ABC):
    """Base class for type validation and/or conversion.
    
    Args:
        accepts (Union[Sequence[Any], Any]): type(s) accepted by the parent 
            class either as an individual item, in a Mapping, or in a Sequence.
        stores (Any): a single type stored by the parent class. Defaults to 
            None.
                        
    """
    element: sourdough.base.Element
    accepts: Union[Sequence[Any], Any] = dataclasses.field(
        default_factory = list)
    stores: Any = None

    """ Initialization Methods """
    
    def __post_init__(self):
        """Registers an instance with 'contents'."""
        # Calls initialization method of other inherited classes.
        try:
            super().__post_init__()
        except AttributeError:
            pass
        # Initializes 'contents' attribute.
        self.element.contents = self.apply(contents = self.element.contents)
        
    """ Required Subclass Methods """
    
    def apply(self, contents: Any) -> Any:
        """[summary]

        Args:
            contents (Any): [description]

        Returns:
            Any: [description]
        """
        contents = self.verify(contents = contents)
        return self.convert(contents = contents)
    
    @abc.abstractmethod
    def convert(self, contents: Any) -> Any:
        """Submodules must provide their own methods.
        
        This method should convert every one of the types in 'accepts' to the
        type in 'stores'.
        
        """
        pass   

    """ Public Methods """
    
    def verify(self, contents: Any) -> Any:
        """Verifies that 'contents' is one of the types in 'accepts'.
        
        Args:
            contents (Any): item(s) to be type validated.
            
        Raises:
            TypeError: if 'contents' is not one of the types in 'accepts'.
            
        Returns:
            Any: original contents if there is no TypeError.
        
        """
        accepts = sourdough.tools.tuplify(self.accepts)
        if all(isinstance(c, accepts) for c in contents):
            return contents
        else:
            raise TypeError(
                f'contents must be or contain one of the following types: ' 
                f'{self.accepts}')

@dataclasses.dataclass
class Mapify(Validator):
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
class Sequencify(Validator):
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
        

@dataclasses.dataclass
class Loader(sourdough.base.Quirk):
    """ for lazy loading of python modules and objects.

    Args:
        modules Union[str, Sequence[str]]: name(s) of module(s) where object to 
            load is/are located. Defaults to an empty list.
        _loaded (ClassVar[Mapping[Any, Any]]): dict of str keys and previously
            loaded objects. This is checked first by the 'load' method to avoid
            unnecessary re-importation. Defaults to an empty dict.

    """
    element: sourdough.base.Element
    modules: Union[str, Sequence[str]] = dataclasses.field(
        default_factory = list)
    _loaded: ClassVar[Mapping[Any, Any]] = {}
    
    """ Public Methods """

    def load(self, 
            key: str, 
            check_attributes: bool = False, 
            **kwargs) -> object:
        """Returns object named by 'key'.

        Args:
            key (str): name of class, function, or variable to try to import 
                from modules listed in 'modules'.

        Returns:
            object: imported from a python module.

        """
        imported = None
        if key in self._loaded:
            imported = self._loaded[key]
        else:
            if check_attributes:
                try:
                    key = getattr(self, key)
                except AttributeError:
                    pass
            for module in sourdough.tools.listify(self.modules):
                try:
                    imported = sourdough.tools.importify(
                        module = module, 
                        key = key)
                    break
                except (AttributeError, ImportError):
                    pass
        if imported is None:
            raise ImportError(f'{key} was not found in {self.modules}')
        elif kwargs:
            self._loaded[key] = imported(**kwargs)
            return self._loaded[key]
        else:
            self._loaded[key] = imported
            return self._loaded[key]
             