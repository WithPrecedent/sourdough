"""
quirks: sourdough mixin architecture
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

sourdough quirks are not technically mixins because some have required 
attributes. Traditionally, mixins do not have any attributes and only add 
functionality. quirks are designed for multiple inheritance and easy addition
to other classes. Despite not meeting the traditional definition of "mixin,"
they are internally referred to as "mixins" because their design and goals are
otherwise similar to mixins.

Although python doesn't require the separation of interfaces in the same way
that more structured languages do, some of the includes quirks in this module
are designed to make it clearer for users trying to expand sourdough's 
functionality. These quirks show the required and included methods for core
classes in sourdough. So, whether you intend to directly subclass or write 
alternate classes for use in sourdough, these quirks show how to survive 
static type-checkers and other internal checks made by sourdough.

Contents:
    Quirk (Base, ABC): base class for all sourdough quirks (described above). 
        Its 'library' class attribute stores all subclasses.
    Element (Quirk): quirk for sourdough containers used in composite 
        structures. It automatically assigns a 'name' attribute if none is 
        passed. Subclasses must have an 'apply' method. 
    # Coordinator (Quirk): quirk for directing other classes to perform actions. 
    #     It provides generic 'advance' and 'complete' methods. Subclasses must 
    #     provide a 'validate' methods to check and/or convert attribute values.
    # Registrar (Quirk): quirk for storing subclasses automatically.
    # Librarian (Quirk): quirk for storing subclass instances automatically.
    # Loader (Quirk): quirk enabling lazy loadin to import python classes, 
    #     functions, and other items at runtime. 

ToDo:
    Add in Validator mixins.
    Fix ProxyMixin as explained in its docs.

"""
from __future__ import annotations
import abc
import copy
import dataclasses
import types
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union, get_args, 
                    get_origin)

import sourdough


@dataclasses.dataclass
class Library(sourdough.Catalog):
    """Stores Base subclasses in a dictionary.

    A Library inherits the differences between a Catalog and a Lexicon.
    
    A Library differs from a Catalog in 2 significant ways:
        1) It should only store Base subclasses as values.
        2) It includes methods for accessing, building, customizing, and 
            instancing the stored subclasses.
        
    Args:
        contents (Mapping[Any, Type[Base]]): stored dictionary with only Base 
            subclasses as values. Defaults to an empty dict.
        defaults (Sequence[Any]]): a list of keys in 'contents' which will be 
            used to return items when 'default' is sought. If not passed, 
            'default' will be set to all keys.
        always_return_list (bool): whether to return a list even when the key 
            passed is not a list or special access key (True) or to return a 
            list only when a list or special access key is used (False). 
            Defaults to False.       
    """
    contents: Mapping[Any, Type[Base]] = dataclasses.field(
        default_factory = dict)
    default: Any = None
    defaults: Sequence[Any] = dataclasses.field(default_factory = list)
    always_return_list: bool = False

    """ Properties """
    
    @property
    def suffixes(self) -> Tuple[str]:
        """
        """
        return tuple(key + 's' for key in self.contents.keys())
    
    """ Public Methods """

    def borrow(self, name: Union[str, Sequence[str]]) -> Type[Base]:
        """Returns a stored subclass unchanged.

        Args:
            name (str): key to accessing subclass in 'contents'.

        Returns:
            Type[Base]: corresponding Base subclass.
            
        """
        match = self.default
        for item in more_itertools.always_iterable(name):
            try:
                match = self.contents[item]
                break
            except KeyError:
                pass
        return match

    def build(self, name: str, 
              quirks: Union[str, Sequence[str]] = None) -> Type[Base]:
        """Returns subclass matching 'name' with selected quirks.

        Args:
            name (str): key name of stored class in 'contents' to returned.
            quirks (Union[str, Sequence[str]]): names of Quirk subclasses to
                add to the custom built class. Defaults to None.

        Returns:
            Type: stored class.
            
        """
        bases = []
        if quirks is not None:
            bases.extend(more_itertools.always_iterable(
                sourdough.base.Quirk.library.select(name = quirks)))
        bases.append(self.select(name = name))
        return dataclasses.dataclass(type(name, tuple(bases), {}))
    
    def instance(self, name: str, quirks: Union[str, Sequence[str]] = None, 
                 **kwargs) -> object:
        """Returns the stored class instance matching 'name'.
        
        If 'quirks' are also passed, they will be added to the returned class
        inheritance.

        Args:
            name (str): key name of stored class in 'contents' to returned.
            quirks (Union[str, Sequence[str]]): names of Quirk subclasses to
                add to the custom built class. Defaults to None.
            kwargs: parameters and arguments to pass to the instanced class.

        Returns:
            object: stored class instance or custom built class with 'quirks'.
            
        """
        if quirks is None:
            return self.select(name = name)(**kwargs)
        else:
            return self.build(name = name, quirks = quirks)(**kwargs)


@dataclasses.dataclass
class Bases(types.SimpleNamespace):
    """Base classes for a sourdough projects.
    
    Changing the attributes on a Bases instance allows users to specify 
    different base classes for a sourdough project in the necessary categories.
    Project will automatically use the base classes in the Bases instance 
    passed to it.
    
    Attribute values can either be classes or strings of the import path of 
    classes. In the latter case, the base classes will be lazily loaded when 
    called.
            
    """

    """ Public Methods """
    
    def add(self, name: str, base: Union[str, Type]) -> None:
        setattr(self, name, base)
        return self
        
    def delete(self, name: str) -> None:
        delattr(self, name)
        return self

    """ Public Methods """

    def importify(self, path: str, instance: bool = False) -> Type:
        """Returns object named by 'key'.

        Args:
            key (str): name of class, function, or variable to try to import 
                from modules listed in 'modules'.

        Returns:
            object: imported from a python module.

        """
        item = path.split('.')[-1]
        module = path[:-len(item) - 1]
        return sourdough.tools.importify(module = module, key = item)

    """ Dunder Methods """

    def __getattribute__(self, name: str) -> Any:
        """Converts stored import paths into the corresponding objects.

        If an import path is stored, that attribute is permanently converted
        from a str to the imported object or class.
        
        Args:
            name (str): name of attribute sought.

        Returns:
            Any: the stored value or, if the value is an import path, the
                class or object stored at the designated import path.
            
        """
        value = super().__getattribute__(name)
        if (isinstance(value, str) and '.' in value):
            value = self.importify(path = value)
            super().__setattr__(name, value)
        return value


@dataclasses.dataclass
class Base(abc.ABC):
    """Abstract base class for connecting a base class to a Library.
    
    Any subclass will automatically store itself in the class attribute 
    'library' using the snakecase name of the class as the key.
    
    Args:
        library (ClassVar[Library]): related Library instance that will store
            subclasses and allow runtime construction and instancing of those
            stored subclasses.
        
    """
    library: ClassVar[Library] = Library()
    bases: ClassVar[Bases] = Bases()
    
    """ Initialization Methods """
    
    def __init_subclass__(cls, **kwargs):
        """Adds 'cls' to 'library' if it is a concrete class."""
        super().__init_subclass__(**kwargs)
        # Creates a snakecase key of the class name.
        key = sourdough.tools.snakify(cls.__name__)
        # Adds base classes to 'bases' using 'key'.
        if Base in cls.__bases__:
            cls.bases.add(name = key, base = cls)
        # Adds concrete subclasses to 'library' using 'key'.
        elif not abc.ABC in cls.__bases__:
            cls.library[key] = cls
           
           
@dataclasses.dataclass
class Quirk(Base, abc.ABC):
    """Base class for sourdough quirks (mixin-approximations).
    
    Args:
        library (ClassVar[Library]): related Library instance that will store
            subclasses and allow runtime construction and instancing of those
            stored subclasses.
        
    """
    library: ClassVar[sourdough.Library] = sourdough.Library()
    

@dataclasses.dataclass
class Element(Quirk):
    """Mixin for classes that need a 'name' attribute.
    
    Automatically provides a 'name' attribute to a subclass, if it isn't 
    otherwise passed. This is important for parts of sourdough composite objects 
    like trees and graphs.

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Configuration instance, 
            'name' should match the appropriate section name in a Configuration 
            instance. Defaults to None. 

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
class Validator(Quirk):
    """Mixin for calling validation methods

    Args:
        validations (List[str]): a list of attributes that need validating.
            Each item in 'validations' should also have a corresponding
            method named f'_validate_{item}'. Defaults to an empty list. 
               
    """
    validations: ClassVar[Sequence[str]] = []

    """ Public Methods """

    def validate(self, validations: Sequence[str] = None) -> None:
        """Validates or converts stored attributes.
        
        Args:
            validations (List[str]): a list of attributes that need validating.
                Each item in 'validations' should also have a corresponding
                method named f'_validate_{item}'. If not passed, the
                'validations' attribute will be used instead. Defaults to None. 
        
        """
        if validations is None:
            validations = self.validations
        # Calls validation methods based on items listed in 'validations'.
        for item in validations:
            if hasattr(self, f'_validate_{item}'):
                kwargs = {item: getattr(self, item)}
                setattr(self, item, getattr(
                    self, f'_validate_{item}')(**kwargs))
        return self     

 
@dataclasses.dataclass
class Registrar(Quirk):
    """Registry interface for core sourdough classes.
    
    A Registrar automatically registers all concrete (non-abstract) subclasses
    using the 'registry' class attribute which must be provided by the class 
    using this quirk.

    Namespaces: 'registry', 'register', 'acquire'

    Args:
        registry (ClassVar[Mapping[str, Type]]):
    
    """
    registry: ClassVar[Mapping[str, Type]] = sourdough.Catalog()

    """ Initialization Methods """
    
    def __init_subclass__(cls, **kwargs):
        """Adds 'cls' to 'registry' if it is a concrete class."""
        super().__init_subclass__(**kwargs)
        if not abc.ABC in cls.__bases__:
            cls.register()
        
    """ Class Methods """

    @classmethod
    def register(cls) -> None:
        """Registers a subclass in a Catalog.
        
        The default 'register' method uses the snake-case name of the class as
        the key for the stored subclass.
        
        """
        key = sourdough.tools.snakify(cls.__name__)
        cls.registry[key] = cls
        return cls

    @classmethod
    def acquire(cls, key: str) -> Any:
        """Returns the stored class matching 'key'.

        Args:
            key (str): name of stored class to returned, as defined by the
                'register' method.

        Returns:
            Any: stored subclass.
            
        """
        return cls.registry.select(key = key)
    
    
@dataclasses.dataclass
class Librarian(Quirk):
    """Store interface for core sourdough classes.
    
    Librarian automatically registers all subclass instances using the 'deposit' 
    method which stores the subclass instances in 'store'.
    
    To use this quirk, the '__post_init__' method must be called.
    
    """
    store: ClassVar[Mapping[str, object]] = sourdough.Catalog()

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent and/or mixin initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass
        # Stores subclass in Store.
        self.deposit()

    """ Public Methods """

    def deposit(self) -> None:
        """Stores a subclass instance in a Catalog.
        
        The 'deposit' method with use the 'name' attribute of an instance, if
        it exists. Otherwise, it will use the snake-case '__name__' or 
        '__class_name__' of the instance.
        
        """
        try:
            self.store[self.name] = self
        except (AttributeError, TypeError):
            try:
                self.store[sourdough.tools.snakify(self.__name__)] = self
            except (AttributeError, TypeError):
                self.store[sourdough.tools.snakify(
                    self.__class__.__name__)] = self 
        return self
    
    """ Class Methods """

    @classmethod
    def borrow(cls, key: str) -> object:
        """Returns the stored class matching 'key'.

        Args:
            key (str): name of stored subclass instance to be returned, as 
                defined by the 'deposit' method.

        Returns:
            object: stored subclass isntance.
            
        """
        return copy.deepcopy(cls.store.select(key))


@dataclasses.dataclass
class Loader(Quirk):
    """Faciliates lazy loading from modules.

    Subclasses with attributes storing strings containing import paths 
    (indicated by having a '.' in their text) will automatically have those
    attribute values turned into the corresponding stored classes.

    The 'load' method also allows this process to be performed manually.

    Subclasses should not have custom '__getattribute__' methods or properties
    to avoid errors.

    Namespaces: 'load', '__getattribute__'
    
    """
 
    """ Public Methods """

    def load(self, path: str, instance: bool = False, 
             **kwargs) -> Union[object, Type]:
        """Returns object named by 'key'.

        Args:
            key (str): name of class, function, or variable to try to import 
                from modules listed in 'modules'.

        Returns:
            object: imported from a python module.

        """
        item = path.split('.')[-1]
        module = path[:-len(item) - 1]
        imported = sourdough.tools.importify(module = module, key = item)
        if kwargs or instance:
            return imported(**kwargs)
        else:
            return imported

    """ Dunder Methods """

    def __getattribute__(self, name: str) -> Any:
        """Converts stored import paths into the corresponding objects.

        If an import path is stored, that attribute is permanently converted
        from a str to the imported object or class.
        
        Args:
            name (str): name of attribute sought.

        Returns:
            Any: the stored value or, if the value is an import path, the
                class or object stored at the designated import path.
            
        """
        value = super().__getattribute__(name)
        if (isinstance(value, str) and '.' in value):
            value = self.load(path = value)
            super().__setattr__(name, value)
        return value

  
# @dataclasses.dataclass
# class Validator(object):
#     """Mixin for type validation and/or conversion Quirks.
    
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
#         origin = get_origin(annotation)
#         args = get_args(annotation)
#         if origin is Union:
#             accepts = tuple(self.deannotate(a)[0] for a in args)
#         else:
#             self.stores = origin
#             accepts = get_args(annotation)
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
 
      