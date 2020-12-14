"""
quirks: sourdough mixin architecture
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Registrar (object): mixin for storing subclasses automatically.
    Librarian (object): mixin for storing subclass instances automatically.
    Loader (object): lazy loader which uses a 'load' method to import python
        classes, functions, and other items at runtime. 
        
    # Validator (Registry, Quirk, ABC): base class for type validators and 
    #     converters. The class provides a universal 'verify' method for type
    #     validation. All subclasses must have a 'convert' method for type 
    #     conversion. 
    # ProxyMixin (Quirk, ABC): mixin which creates a python property which 
    #     refers to another attribute by using the 'proxify' method.

ToDo:
    Add in Validator mixins.
    Fix ProxyMixin as explained in its docs.

"""
from __future__ import annotations
import abc
import copy
import dataclasses
import inspect
from sourdough.utilities.tools import deannotate
import typing
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import sourdough


@dataclasses.dataclass
class Element(object):
    """Allows a subclass to be stored by a Hybrid.
    
    An Element has a 'name' attribute for internal referencing and to allow 
    sourdough Hybrids storing them to function propertly. Element instances can 
    be used to create a variety of sourdough objects and composite structures 
    such as trees, cycles, contests, studies, and graphs.
    
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance.
            Defaults to None. 

    """
    name: str = None
    
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Sets 'name' attribute.
        if not hasattr(self, 'name') or self.name is None:  
            self.name = self._get_name()
        # Calls parent and/or mixin initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass

    """ Private Methods """
    
    def _get_name(self) -> str:
        """Returns snakecase of the class name.

        If a user wishes to use an alternate naming system, a subclass should
        simply override this method. 
        
        Returns:
            str: name of class for internal referencing and some access methods.
        
        """
        return sourdough.tools.snakify(self.__class__.__name__)

  
@dataclasses.dataclass
class Registrar(object):
    """Registry interface for core sourdough classes.
    
    This mixin automatically registers all concrete (non-abstract) subclasses
    using the 'registry' classmethod which must be provided by the class using
    this quirk.
    
    """
    registry: ClassVar[Mapping[str, Type]] = sourdough.types.Catalog()

    """ Initialization Methods """
    
    def __init_subclass__(cls, **kwargs):
        """Adds 'cls' to 'registry' if it is a concrete class."""
        super().__init_subclass__(**kwargs)
        if not abc.ABC in cls.__bases__:
            cls.register()
        
    """ Class Methods """

    @classmethod
    def register(cls) -> None:
        """Registers a subclass in a Catalog."""
        key = sourdough.tools.snakify(cls.__name__)
        cls.registry[key] = cls
        return cls

    @classmethod
    def acquire(cls, key: str) -> Any:
        """[summary]

        Args:
            key (str): [description]

        Returns:
            Any: [description]
            
        """
        return cls.registry.select(key)
    
    
@dataclasses.dataclass
class Librarian(object):
    """Library interface for core sourdough classes.
    
    This mixin automatically registers all subclass instances using the 
    'deposit' method which must be provided by the class using this quirk.
    
    """
    library: ClassVar[Mapping[str, object]] = sourdough.types.Catalog()

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent and/or mixin initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass
        # Stores subclass in Library.
        self.deposit()

    """ Public Methods """

    def deposit(self) -> None:
        """Stores a subclass instance in a Catalog."""
        try:
            self.library[self.name] = self
        except (AttributeError, TypeError):
            try:
                self.library[self.__name__] = self
            except (AttributeError, TypeError):
                self.library[self.__class__.__name__] = self 
        return self
    
    """ Class Methods """

    @classmethod
    def borrow(cls, key: str) -> Any:
        """
        """
        return copy.deepcopy(cls.library.select(key))


@dataclasses.dataclass
class Loader(object):
    """Allows loading of python modules and objects.

    Args:

    """
    import_path: str = None
 
    """ Public Methods """

    def importify(self, instance: bool = False, **kwargs) -> Union[object, Type]:
        """Returns object named by 'key'.

        Args:
            key (str): name of class, function, or variable to try to import 
                from modules listed in 'modules'.

        Returns:
            object: imported from a python module.

        """
        module, item = self._parse_import(name = self.import_path)
        imported = sourdough.tools.importify(module = module, key = item)
        if kwargs or instance:
            return imported(**kwargs)
        else:
            return imported

    """ Private Methods """
    
    def _parse_import(self, path: str) -> Tuple[str]:
        suffix = path.split('.')[-1]
        prefix = path[:-len(suffix) - 1]
        return prefix, suffix
    
# @dataclasses.dataclass
# class Validator(object):
#     """Base class for type validation and/or conversion Quirks.
    
#     To use this mixin, a base class must have a 'contents' attribute for the
#     items to be validated and/or converted.

#     Attributes:
#         accepts (Tuple[Any]): type(s) accepted by the parent class either as an 
#             individual item, in a Mapping, or in a Sequence.
#         stores (Any): a single type stored in 'contents'.
                          
#     """

#     """ Initialization Methods """
    
#     def __post_init__(self):
#         """Registers an instance with 'contents'."""
#         # Calls initialization method of other inherited classes.
#         try:
#             super().__post_init__()
#         except AttributeError:
#             pass
#         self.accepts = self.deannotate(
#             annotation = self.__annotations__['contents'])

#     """ Required Subclass Methods """
    
#     @abc.abstractmethod
#     def convert(self, contents: Any) -> Any:
#         """Converts 'contents' to appropriate type.
        
#         This method should convert every one of the types in 'accepts' to the
#         type in 'stores'.
        
#         Subclasses must provide their own methods.
        
#         """
#         pass   

#     @abc.abstractmethod
#     def verify(self, contents: Any) -> Any:
#         """Verifies 'contents' contains one of the types in 'accepts'.
        
#         Subclasses must provide their own methods.
        
#         """
#         pass  

#     def deannotate(self, annotation: Any) -> Tuple[Any]:
#         """Returns type annotations as a tuple.
        
#         This allows even complicated annotations with Union to be converted to a
#         form that fits with an isinstance call.

#         Args:
#             annotation (Any): type annotation.

#         Returns:
#             Tuple[Any]: base level of stored type in an annotation
        
#         """
#         origin = typing.get_origin(annotation)
#         args = typing.get_args(annotation)
#         if origin is Union:
#             accepts = tuple(deannotate(a)[0] for a in args)
#         else:
#             self.stores = origin
#             accepts = typing.get_args(annotation)
#         return accepts
        
#     def verify(self, contents: Any) -> Any:
#         """Verifies that 'contents' is one of the types in 'accepts'.
        
#         Args:
#             contents (Any): item(s) to be type validated.
            
#         Raises:
#             TypeError: if 'contents' is not one of the types in 'accepts'.
            
#         Returns:
#             Any: original contents if there is no TypeError.
        
#         """
#         if ((isinstance(contents, Mapping) 
#                 and all(isinstance(c, self.accepts) for c in contents.values()))
#             or (isinstance(contents, Sequence) 
#                 and all(isinstance(c, self.accepts) for c in contents))
#             or isinstance(contents, self.accepts)):
#             return contents   
#         else:
#             raise TypeError(
#                 f'contents must be or contain one of the following types: ' 
#                 f'{self.accepts}')        


# @dataclasses.dataclass
# class Mapify(Validator):
#     """Type validator and converter for Mappings.

#     Attributes:
#         accepts (Tuple[Any]): type(s) accepted by the parent class either as an 
#             individual item, in a Mapping, or in a Sequence.
#         stores (Any): a single type stored by the parent class. Set to dict.
            
#     """    

#     """ Initialization Methods """
    
#     def __post_init__(self):
#         """Registers an instance with 'contents'."""
#         # Calls initialization method of other inherited classes.
#         try:
#             super().__post_init__()
#         except AttributeError:
#             pass
#         self.stores = dict
    
#     """ Public Methods """
    
#     def convert(self, contents: Any) -> (Mapping[str, Any]):
#         """Converts 'contents' to a Mapping type.
        
#         Args:
#             contents (Any): an object containing item(s) with 'name' attributes.
                
#         Returns:
#             Mapping[str, Any]: converted 'contents'.
            
#         """
#         contents = self.verify(contents = contents)
#         converted = {}
#         if isinstance(contents, Mapping):
#             converted = contents
#         elif (isinstance(contents, Sequence) 
#                 and not isinstance(contents, str)
#                 and all(hasattr(i, 'name') for i in contents)):
#             for item in contents:
#                 try:
#                     converted[item.name] = item
#                 except AttributeError:
#                     converted[item.get_name()] = item
#         return converted
    

# @dataclasses.dataclass    
# class Sequencify(Validator):
#     """Type validator and converter for Sequences.
    
#     Args:
#         accepts (Union[Sequence[Any], Any]): type(s) accepted by the parent 
#             class either as an individual item, in a Mapping, or in a Sequence.
#             Defaults to sourdough.quirks.Element.
#         stores (Any): a single type accepted by the parent class. Defaults to 
#             list.
            
#     """        

#     """ Initialization Methods """
    
#     def __post_init__(self):
#         """Registers an instance with 'contents'."""
#         # Calls initialization method of other inherited classes.
#         try:
#             super().__post_init__()
#         except AttributeError:
#             pass
#         self.stores = list
    
#     """ Public Methods """
       
#     def convert(self, 
#             contents: Any) -> (
#                 Sequence[sourdough.quirks.Element]):
#         """Converts 'contents' to a Sequence type.
        
#         Args:
#             contents (Any): an object containing one or 
#                 more Element subclasses or Element subclass instances.
        
#         Raises:
#             TypeError: if 'contents' is not an Any.
                
#         Returns:
#             Sequence[Element]: converted 'contents'.
            
#         """
#         converted = self.stores()
#         if isinstance(contents, Mapping):
#             converted = converted.extend(contents.values())
#         elif isinstance(contents, Sequence):
#             converted = contents
#         elif isinstance(contents, sourdough.quirks.Element):
#             converted = converted.append(contents)
#         return converted  

#     def verify(self, contents: Any) -> Any:
#         """Verifies that 'contents' is one of the types in 'accepts'.
        
#         Args:
#             contents (Any): item(s) to be type validated.
            
#         Raises:
#             TypeError: if 'contents' is not one of the types in 'accepts'.
            
#         Returns:
#             Any: original contents if there is no TypeError.
        
#         """
#         if all(isinstance(c, self.accepts) for c in contents):
#             return contents
#         else:
#             raise TypeError(
#                 f'contents must be or contain one of the following types: ' 
#                 f'{self.accepts}')        


# @dataclasses.dataclass
# class ProxyMixin(object):
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
 
      