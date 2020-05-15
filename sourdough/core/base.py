"""
.. module:: base
:synopsis: sourdough base classes
:author: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import abc
import collections.abc
import dataclasses
import importlib
import inspect
from typing import (
    Any, Callable, ClassVar, Dict, Iterable, List, Optional, Tuple, Union)

import sourdough


@dataclasses.dataclass
class MappingBase(sourdough.Component, collections.abc.MutableMapping):
    """Base class for sourdough dictionaries.
    
    All subclasses must implement an 'add' method.
    
    Arguments:
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. For example if a 
            class instance needs settings from the shared Settings instance, 
            'name' should match the appropriate section name in that Settings 
            instance. When subclassing, it is sometimes a good idea to use the 
            same 'name' attribute as the base class for effective coordination 
            between sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Component is called, 'name' is set to a snake 
            case version of the class name ('__class__.__name__').
        contents (Optional[Dict[str, Any]]): stored dictionary. Defaults to an
            empty dictionary.
            
    """
    name: Optional[str] = None
    contents: Optional[Dict[str, Any]] = dataclasses.field(
        default_factory = dict)

    """ Required Subclass Methods """

    @abc.abstractmethod
    def add(self, *args, **kwargs) -> NotImplementedError:
        """Subclasses must implement their own methods.
        
        The 'add' method should contain the default mechanism for adding new
        items to 'contents'. Users are still free to use the normal 'update' 
        method, which is made available by subclassing MutableMapping.
        
        """
        pass
        
    """ Public Methods """
    
    def subsetify(self, subset: Union[str, List[str]]) -> 'MappingBase':
        """Returns a subset of 'contents'.

        Arguments:
            subset (Union[str, List[str]]): key(s) to get key/value pairs from
                'contents'.

        Returns:
            MappingBase: with only keys in 'subset'.

        """
        return self.__class__(
            name = name,
            contents = sourdough.utilities.subsetify(
                dictionary = self.contents,
                subset = subset))

    """ Required ABC Methods """

    def __getitem__(self, key: str) -> Any:
        """Returns value for 'key' in 'contents'.

        Arguments:
            key (str): name of key in 'contents' for which value is sought.

        Returns:
            Any: value stored in 'contents'.

        """
        return self.contents[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Sets 'key' in 'contents' to 'value'.

        Arguments:
            key (str): name of key to set in 'contents'.
            value (Any): value to be paired with 'key' in 'contents'.

        """
        self.contents[key] = value
        return self

    def __delitem__(self, key: str) -> None:
        """Deletes 'key' in 'contents'.

        Arguments:
            key (str): name of key in 'contents' to delete the key/value pair.

        """
        del self.contents[key]
        return self

    def __iter__(self) -> Iterable:
        """Returns iterable of 'contents'.

        Returns:
            Iterable: of 'contents'.

        """
        return iter(self.contents)

    def __len__(self) -> int:
        """Returns length of 'contents'.

        Returns:
            int: length of 'contents'.

        """
        return len(self.contents)

    """ Other Dunder Methods """

    def __add__(self, other: 'MappingBase') -> None:
        """Combines argument with 'contents'.

        Arguments:
            other (MappingBase): another MappingBase or compatiable dictionary

        """
        self.add(contents = other)
        return self
    
    def __iadd__(self, other: 'MappingBase') -> None:
        """Combines argument with 'contents'.

        Arguments:
            other (MappingBase): another MappingBase or compatiable dictionary

        """
        self.add(contents = other)
        return self

    def __repr__(self) -> str:
        """Returns '__str__' representation.

        Returns:
            str: default dictionary representation of 'contents'.

        """
        return self.__str__()

    def __str__(self) -> str:
        """Returns default dictionary representation of 'contents'.

        Returns:
            str: default dictionary representation of 'contents'.

        """
        return (
            f'sourdough {self.__class__.__name__} '
            f'name: {self.name} '
            f'contents: {self.contents.__str__()} ')   
    

@dataclasses.dataclass
class SequenceBase(sourdough.Component, collections.abc.MutableSequence):
    """Base class for sourdough lists.
    
    All subclasses must implement an 'add' method.
    
    Arguments:
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. If the class instance
            needs settings from the shared Settings instance, 'name' should
            match the appropriate section name in that Settings instance. When
            subclassing, it is a good settings to use the same 'name' attribute
            as the base class for effective coordination between sourdough
            classes. Defaults to None or __class__.__name__.lower().
        items (Optional[List[Any]]): stored list. Defaults to an empty list.

    """

    name: Optional[str] = None
    items: Optional[List[Any]] = dataclasses.field(default_factory = list)
    
    """ Required Subclass Methods """

    @abc.abstractmethod
    def add(self, *args, **kwargs) -> NotImplementedError:
        """Subclasses must implement their own methods.
        
        The 'add' method should contain the default mechanism for adding new
        items to 'items'. Users are still free to use the 'extend' and 
        'append' methods which are made available by subclassing 
        MutableSequence.
        
        """
        pass
    
    """ ABC Public Methods """
    
    def insert(self, index: int, value: Any) -> None:
        """Inserts 'value' at 'index' in 'items'.

        Arguments:
            index (int): index to insert 'value' at.
            value (sourdough.Component): object to be inserted.

        """
        self.items.insert[index] = value
        return self

    """ ABC Dunder Methods """

    def __getitem__(self, index: int) -> Any:
        """Returns value at 'index' in 'items'.

        Arguments:
            index (int): location of object in 'items' to return.

        Returns:
            Any: object located at 'index'.

        """
        return self.items[index]
    
    def __setitem__(self, index: int, value: Any) -> None:
        """Sets item at 'index' to 'value'.

        Arguments:
            index (int): location of item to set in 'items'.
            value (Any): value to be set at 'index' in 'items'.
        """
        self.items[index] = value

    def __delitem__(self, index: int) -> None:
        """Deletes item at 'index' in 'items'.

        Arguments:
            index (int): location of item in 'items' to delete.

        """
        del self.items[index]
        return self

    def __len__(self) -> int:
        """Returns length of 'items'.

        Returns:
            int: length of 'items'.

        """
        return len(self.items)

    """ Other Dunder Methods """

    def __repr__(self) -> str:
        """Returns '__str__' representation.

        Returns:
            str: default list representation of 'items'.

        """
        return self.__str__()

    def __str__(self) -> str:
        """Returns default list representation of 'items'.

        Returns:
            str: default list representation of 'items'.

        """
        return (
            f'sourdough {self.__class__.__name__} '
            f'name: {self.name} '
            f'items: {self.items.__str__()} ')   


@dataclasses.dataclass
class FactoryBase(abc.ABC):
    """The Factory interface instances a class from available options.

    Arguments:
        product (Optional[str]): name of sourdough object to return. 'product' 
            must correspond to a key in 'products'. Defaults to None.
        default (ClassVar[str]): the name of the default object to instance. If 
            'product' is not passed, 'default' is used. 'default' must 
            correspond  to a key in 'products'. Defaults to None. If 'default'
            is to be used, it should be specified by a subclass, declared in an
            instance, or set via the class attribute.
        products (ClassVar[MutableMapping]): a dictionary or other mapping of 
            available options for object creation. Keys are the names of the 
            'product'. Values are the objects to create. Defaults to an 
            empty dictionary.

    Returns:
        Any: the factory uses the '__new__' method to return a different object 
            instance with kwargs as the parameters.

    """
    product: Optional[str] = None
    default: ClassVar[str] = None
    products: ClassVar[collections.abc.MutableMapping] = {}

    """ Initialization Methods """
    
    def __new__(cls, 
            product: Optional[str] = None, 
            **kwargs) -> Any:
        """Returns an instance from 'products'.

        Arguments:
            product (Optional[str]): name of sourdough object to return. 
                'product' must correspond to a key in 'products'. Defaults to 
                None. If not passed, the product listed in 'default' will be 
                used.
            kwargs (Dict[str, Any]): parameters to pass to the object being 
                created.

        Returns:
            Any: an instance of an object stored in 'products'.
        
        """
        if product:
            return cls.products[product](**kwargs) 
        else:
            return cls.products[cls.default](**kwargs)
        
    """ Dunder Methods """
    
    def __repr__(self) -> str:
        """Returns '__str__' representation.

        Returns:
            str: default representation of a class instance.

        """
        return self.__str__()

    def __str__(self) -> str:
        """Returns default representation of a class instance.

        Returns:
            str: default representation of a class instance.

        """
        return (
            f'sourdough {self.__class__.__name__} '
            f'product: {self.product} '
            f'default: {self.default} '
            f'products: {str(self.products)}') 
        

@dataclasses.dataclass
class ImporterBase(abc.ABC):
    """Base class for lazy loading of python modules and objects.

    Arguments:
        module (Optional[str]): name of module where object to use is located
            (can either be a sourdough or non-sourdough module). Defaults to
            'sourdough'.
        default_module (Optional[str]): a backup name of module where object to
            use is located (can either be a sourdough or non-sourdough module).
            Defaults to 'sourdough'.

    """
    module: Optional[str] = dataclasses.field(
        default_factory = lambda: 'sourdough')
    default_module: Optional[str] = dataclasses.field(
        default_factory = lambda: 'sourdough')

    """ Public Methods """

    def load(self, attribute: str) -> object:
        """Returns object named in 'attribute'.

        If 'attribute' is not a str, it is assumed to have already been loaded
        and is returned as is.

        The method searches both 'module' and 'default_module' for the named
        'attribute'. It also checks to see if the 'attribute' is directly
        loadable from the module or if it is the name of a local attribute that
        has a value of a loadable object in the module.

        Arguments:
            attribute (str): name of attribute to load from 'module' or
                'default_module'.

        Returns:
            object: from 'module' or 'default_module'.

        """
        # If 'attribute' is a string, attempts to load from 'module' or, if not
        # found there, 'default_module'.
        if isinstance(getattr(self, attribute), str):
            try:
                return getattr(importlib.import_module(self.module), attribute)
            except (ImportError, AttributeError):
                try:
                    return getattr(
                        importlib.import_module(self.module),
                        getattr(self, attribute))
                except (ImportError, AttributeError):
                    try:
                        return getattr(
                            importlib.import_module(self.module), attribute)
                    except (ImportError, AttributeError):
                        try:
                            return getattr(
                                importlib.import_module(self.default_module),
                                getattr(self, attribute))
                        except (ImportError, AttributeError):
                            raise ImportError(
                                f'{attribute} is neither in \
                                {self.module} nor {self.default_module}')
        # If 'attribute' is not a string, it is returned as is.
        else:
            return getattr(self, attribute)
        