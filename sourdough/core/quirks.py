"""
quirks: sourdough mixin architecture
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Validator (Registry, Quirk, ABC): base class for type validators and 
        converters. The class provides a universal 'verify' method for type
        validation. All subclasses must have a 'convert' method for type 
        conversion.
    Loader (Quirk, ABC): lazy loader which uses a 'load' method to import python
        classes, functions, and other items at runtime. 
        
    # ValidatorFactory (Factory): returns sourdough.Validator subclass 
    #     instance which is used for type validation and conversion.
    # ProxyMixin (Quirk, ABC): mixin which creates a python property which 
    #     refers to another attribute by using the 'proxify' method.
    
"""
from __future__ import annotations
import abc
import dataclasses
# import inspect
from typing import (
    Any, Callable, ClassVar, Dict, Iterable, List, Mapping, Sequence, Union)

import sourdough


@dataclasses.dataclass
class Validator(abc.ABC):
    """Base class for type validation and/or conversion Quirks.
    
    Args:
        accepts (Union[Sequence[Any], Any]): type(s) accepted by the parent 
            class either as an individual item, in a Mapping, or in a Sequence.
        stores (Any): a single type stored by the parent class. Defaults to 
            None.
        library (ClassVar[sourdough.Catalog]): the instance which stores 
            subclasses.        
                        
    """
    accepts: Union[Sequence[Any], Any] = dataclasses.field(
        default_factory = list)
    stores: Any = None
    # library: ClassVar[sourdough.Catalog] = sourdough.Catalog()

    """ Initialization Methods """
    
    def __post_init__(self):
        """Registers an instance with 'contents'."""
        # Calls initialization method of other inherited classes.
        try:
            super().__post_init__()
        except AttributeError:
            pass

    """ Class Methods """

    @classmethod
    def inject(cls, item: Any) -> Any:
        return item

    """ Required Subclass Methods """
    
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
class Mapify(Validator, abc.ABC):
    """Type validator and converter for Mappings.
    
    Args:
        accepts (Union[Sequence[Any], Any]): type(s) accepted by the parent 
            class either as an individual item, in a Mapping, or in a Sequence.
            Defaults to sourdough.Element.
        stores (Any): a single type stored by the parent class. Defaults to 
            dict.
            
    """    
    accepts: Union[Sequence[Any], Any] = dataclasses.field(
        default_factory = lambda: sourdough.Element)
    stores: Any = dataclasses.field(default_factory = lambda: dict)
    
    """ Public Methods """
    
    def convert(self, 
            contents: Any) -> (
                Mapping[str, sourdough.Element]):
        """Converts 'contents' to a Mapping type.
        
        Args:
            contents (Any): an object containing one or 
                more Element subclasses or Element subclass instances.
        
        Raises:
            TypeError: if 'contents' is not an Any.
                
        Returns:
            Mapping[str, Element]: converted 'contents'.
            
        """
        converted = self.stores()
        contents = self.verify(contents = contents)
        if isinstance(contents, Mapping):
            converted = contents
        elif (isinstance(contents, Sequence) 
                or isinstance(contents, sourdough.Element)):
            for item in sourdough.tools.tuplify(contents):
                try:
                    converted[item.name] = item
                except AttributeError:
                    converted[item.get_name()] = item
        return converted
    

@dataclasses.dataclass    
class Sequencify(Validator, abc.ABC):
    """Type validator and converter for Sequences.
    
    Args:
        accepts (Union[Sequence[Any], Any]): type(s) accepted by the parent 
            class either as an individual item, in a Mapping, or in a Sequence.
            Defaults to sourdough.Element.
        stores (Any): a single type accepted by the parent class. Defaults to 
            list.
            
    """        
    accepts: Union[Sequence[Any], Any] = dataclasses.field(
        default_factory = lambda: sourdough.Element)
    stores: Any = dataclasses.field(default_factory = lambda: list)
    
    """ Public Methods """
       
    def convert(self, 
            contents: Any) -> (
                Sequence[sourdough.Element]):
        """Converts 'contents' to a Sequence type.
        
        Args:
            contents (Any): an object containing one or 
                more Element subclasses or Element subclass instances.
        
        Raises:
            TypeError: if 'contents' is not an Any.
                
        Returns:
            Sequence[Element]: converted 'contents'.
            
        """
        converted = self.stores()
        if isinstance(contents, Mapping):
            converted = converted.extend(contents.values())
        elif isinstance(contents, Sequence):
            converted = contents
        elif isinstance(contents, sourdough.Element):
            converted = converted.append(contents)
        return converted  
        

@dataclasses.dataclass
class Loader(abc.ABC):
    """ for lazy loading of python modules and objects.

    Args:
        modules Union[str, Sequence[str]]: name(s) of module(s) where object to 
            load is/are located. Defaults to an empty list.
        _loaded (ClassVar[Mapping[Any, Any]]): dict of str keys and previously
            loaded objects. This is checked first by the 'load' method to avoid
            unnecessary re-importation. Defaults to an empty dict.

    """
    modules: Union[str, Sequence[str]] = dataclasses.field(
        default_factory = list)
    _loaded: ClassVar[Mapping[Any, Any]] = {}

    """ Class Methods """

    @classmethod
    def inject(cls, item: Any) -> Any:
        return item
 
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



# @dataclasses.dataclass
# class ValidatorFactory(sourdough.Factory, abc.ABC):
#     """Factory for type validation and/or conversion class construction.
    
#     ValidatorFactory is primary used to convert Element subclasses to and from 
#     single instances, Mappings of instances, and Sequences of instances. 
    
#     Args:
#         product (Union[str, Sequence[str]]): name(s) of objects to return. 
#             'product' must correspond to key(s) in 'options.library'.
#         accepts (Union[Sequence[Any], Any]): type(s) accepted by the parent 
#             class either as an individual item, in a Mapping, or in a Sequence.
#         stores (Any): a single type stored by the parent class. Defaults 
#             to None.
#         options (ClassVar[sourdough.Options]): class which contains a 
#             'library' of alternatives for constructing objects.
            
#     """
#     product: Union[str, Sequence[str]]
#     accepts: Union[Sequence[Any], Any] = dataclasses.field(
#         default_factory = list)
#     stores: Any = None
#     options: ClassVar[sourdough.Options] = sourdough.Validator
    
  
# @dataclasses.dataclass
# class ProxyMixin(abc.ABC):
#     """ which creates a proxy name for a Element subclass attribute.

#     The 'proxify' method dynamically creates a property to access the stored
#     attribute. This allows class instances to customize names of stored
#     attributes while still maintaining the interface of the base sourdough
#     classes.

#     Only one proxy should be created per class. Otherwise, the created proxy
#     properties will all point to the same attribute.

#     Namespaces: 'proxify', '_proxy_getter', '_proxy_setter', 
#         '_proxy_deleter', '_proxify_attribute', '_proxify_method', the name of
#         the proxy property set by the user with the 'proxify' method.
       
#     To Do:
#         Add property to class instead of instance to prevent return of property
#             object.
#         Implement '__set_name__' in a secondary class to simplify the code and
#             namespace usage.
        
#     """

#     """ Public Methods """

#     def proxify(self,
#             proxy: str,
#             attribute: str,
#             default_value: Any = None,
#             proxify_methods: bool = True) -> None:
#         """Adds a proxy property to refer to class attribute.

#         Args:
#             proxy (str): name of proxy property to create.
#             attribute (str): name of attribute to link the proxy property to.
#             default_value (Any): default value to use when deleting 'attribute' 
#                 with '__delitem__'. Defaults to None.
#             proxify_methods (bool): whether to create proxy methods replacing 
#                 'attribute' in the original method name with the string passed 
#                 in 'proxy'. So, for example, 'add_chapter' would become 
#                 'add_recipe' if 'proxy' was 'recipe' and 'attribute' was
#                 'chapter'. The original method remains as well as the proxy.
#                 This does not change the rest of the signature of the method so
#                 parameter names remain the same. Defaults to True.

#         """
#         self._proxied_attribute = attribute
#         self._default_proxy_value = default_value
#         self._proxify_attribute(proxy = proxy)
#         if proxify_methods:
#             self._proxify_methods(proxy = proxy)
#         return self

#     """ Proxy Property Methods """

#     def _proxy_getter(self) -> Any:
#         """Proxy getter for '_proxied_attribute'.

#         Returns:
#             Any: value stored at '_proxied_attribute'.

#         """
#         return getattr(self, self._proxied_attribute)

#     def _proxy_setter(self, value: Any) -> None:
#         """Proxy setter for '_proxied_attribute'.

#         Args:
#             value (Any): value to set attribute to.

#         """
#         setattr(self, self._proxied_attribute, value)
#         return self

#     def _proxy_deleter(self) -> None:
#         """Proxy deleter for '_proxied_attribute'."""
#         setattr(self, self._proxied_attribute, self._default_proxy_value)
#         return self

#     """ Other Private Methods """

#     def _proxify_attribute(self, proxy: str) -> None:
#         """Creates proxy property for '_proxied_attribute'.

#         Args:
#             proxy (str): name of proxy property to create.

#         """
#         setattr(self, proxy, property(
#             fget = self._proxy_getter,
#             fset = self._proxy_setter,
#             fdel = self._proxy_deleter))
#         return self

#     def _proxify_methods(self, proxy: str) -> None:
#         """Creates proxy method with an alternate name.

#         Args:
#             proxy (str): name of proxy to repalce in method names.

#         """
#         for item in dir(self):
#             if (self._proxied_attribute in item
#                     and not item.startswith('__')
#                     and callable(item)):
#                 self.__dict__[item.replace(self._proxied_attribute, proxy)] = (
#                     getattr(self, item))
#         return self
 
      