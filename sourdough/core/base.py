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
import itertools
from typing import (
    Any, Callable, ClassVar, Dict, Iterable, List, Optional, Tuple, Union)

import sourdough


@dataclasses.dataclass
class MappingBase(sourdough.Component, collections.abc.MutableMapping):
    """Base class for sourdough dictionar`ies.
    
    All subclasses must implement an 'add' method.
    
    Args:
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

    """ Public Methods """

    def add(self, key: str, value: str) -> NotImplementedError:
        """Adds 'key' and 'value' to 'contents'.
        
        The 'add' method should contain the default mechanism for adding new
        items to 'contents'. Users are still free to use the normal 'update' 
        method, which is made available by subclassing MutableMapping.
        
        Args:
            key (str): key to store 'value' at.
            value (str): value to store in 'contents'.
        
        """
        self.contents[key] = value
        return self
    
    def subsetify(self, subset: Union[str, List[str]]) -> 'MappingBase':
        """Returns a subset of 'contents'.

        Args:
            subset (Union[str, List[str]]): key(s) to get key/value pairs from
                'contents'.

        Returns:
            MappingBase: with only keys in 'subset'.

        """
        return self.__class__(
            name = self.name,
            contents = sourdough.utilities.subsetify(
                dictionary = self.contents,
                subset = subset))

    """ Dunder Methods """

    def __getitem__(self, key: str) -> Any:
        """Returns value for 'key' in 'contents'.

        Args:
            key (str): name of key in 'contents' for which value is sought.

        Returns:
            Any: value stored in 'contents'.

        """
        return self.contents[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Sets 'key' in 'contents' to 'value'.

        Args:
            key (str): name of key to set in 'contents'.
            value (Any): value to be paired with 'key' in 'contents'.

        """
        self.contents[key] = value
        return self

    def __delitem__(self, key: str) -> None:
        """Deletes 'key' in 'contents'.

        Args:
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

    def __add__(self, other: Union['MappingBase', Dict[str, Any]]) -> None:
        """Combines argument with 'contents'.

        Args:
            other ( Union['MappingBase', Dict[str, Any]]): another MappingBase 
                or compatiable dictionary.

        """
        self.contents.update(other)
        return self
    
    def __iadd__(self, other: 'MappingBase') -> None:
        """Combines argument with 'contents'.

        Args:
            other ( Union['MappingBase', Dict[str, Any]]): another MappingBase 
                or compatiable dictionary.
                
        """
        self.contents.update(other)
        return self

    def __repr__(self) -> str:
        """Returns '__str__' representation.

        Returns:
            str: default representation of 'contents'.

        """
        return self.__str__()

    def __str__(self) -> str:
        """Returns default representation of 'contents'.

        Returns:
            str: default representation of 'contents'.

        """
        return (
            f'sourdough {self.__class__.__name__}\n'
            f'name: {self.name}\n'
            f'contents: {self.contents.__str__()} ')   
    

@dataclasses.dataclass
class SequenceBase(sourdough.Component, collections.abc.MutableSequence):
    """Base class for iterables storing sourdough Component instances.
    
    SequenceBase has an interface of a dictionary but stores a list. 
    SequenceBase does this by taking advantage of the 'name' attribute in 
    Componentt instances. A 'name' acts as a key to create the facade of a 
    dictionary with the items in the stored list serving as values. This allows 
    for duplicate keys for storing class instances, easier iteration, and
    returning multiple matching items. This design comes at the expense of 
    lookup speed. As a result, SequenceBase should only be used if repeat 
    accesing of the stored 'contents' is not anticipated. Ordinarily, the loss 
    of lookup speed should have negligible effect on overall performance. 
    
    Iterating SequenceBase also iterates all contained iterables by using the
    'itertools.chain_from_iterable' method.

    Args:
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. If the class instance
            needs settings from the shared Settings instance, 'name' should
            match the appropriate section name in that Settings instance. When
            subclassing, it is a good settings to use the same 'name' attribute
            as the base class for effective coordination between sourdough
            classes. Defaults to None or __class__.__name__.lower().
        contents (Optional[List[Component]]): stored iterable of actions to take
            as part of the SequenceBase. Defaults to an empty list.

    """

    name: Optional[str] = None
    contents: Optional[List['sourdough.Component']] = dataclasses.field(
        default_factory = list)

    """ Public Methods """
       
    def add(self, component: 'sourdough.Component') -> None:
        """Appends 'component' to 'contents'.
        
        Args:
            component (sourdough.Component): Component to add to 'contents'.

        Raises:
            TypeError: if 'component' is not a Component instance.
            
        """
        if isinstance(component, sourdough.Component):
            self.append(component)
        else:
            raise TypeError('component must be a Component type')
        return self    

    def append(self, component: 'sourdough.Component') -> None:
        """Appends 'component' to 'contents'.
        
        Args:
            component (sourdough.Component): Component to add to 'contents'.

        """
        if isinstance(component, sourdough.Component):
            self.contents.append(component)
        else:
            raise TypeError('component must be a Component type')
        return self    
   
    def extend(self, component: 'sourdough.Component') -> None:
        """Extends 'component' to 'contents'.
        
        Args:
            component (sourdough.Component): Component to add to 'contents'.

        """
        if isinstance(component, sourdough.Component):
            self.contents.extend(component)
        else:
            raise TypeError('component must be a Component type')
        return self   
    
    def insert(self, index: int, component: 'sourdough.Component') -> None:
        """Inserts 'value' at 'index' in 'items'.

        Args:
            index (int): index to insert 'value' at.
            component (sourdough.Component): object to be inserted.

        """
        if isinstance(component, sourdough.Component):
            self.items.insert[index] = component
        else:
            raise TypeError('component must be a Component type')
        return self
 
    def subsetify(self, subset: Union[str, List[str]]) -> 'SequenceBase':
        """Returns a subset of 'contents'.

        Args:
            subset (Union[str, List[str]]): key(s) to get key/value pairs from
                'contents'.

        Returns:
            SequenceBase: with only items with 'name' attributes in 'subset'.

        """
        subset = sourdough.utilities.listify(subset)
        return self.__class__(
            name = self.name,
            contents = [c for c in self.contents if c.name in subset])    
        
    """ Dunder Methods """

    def __getitem__(self, key: Union[str, int]) -> 'sourdough.Component':
        """Returns value(s) for 'key' in 'contents'.
        
        If 'key' is a str type, this method looks for a matching 'name'
        attribute in the stored instances.

        Args:
            key (Union[str, int]): name or index to search for in 'contents'.

        Returns:
            Component: value stored in 'contents' that corresponder to 'key'.

        """
        if isinstance(key, int):
            return self.contents[key]
        else:
            matches = [c for c in self.contents if c.name == key]
            if len(matches) == 1:
                return matches[0]
            else:
                return self.__class__(name = self.name, contents = matches)

    def __setitem__(self, 
            key: Union[str, int], 
            value: 'sourdough.Component') -> None:
        """Sets 'key' in 'contents' to 'value'.

        Args:
            key (Union[str, int]): if key is a string, it is ignored (since the
                'name' attribute of the value will be acting as the key). In
                such a case, the 'value' is added to the end of 'contents'. If
                key is an int, 'value' is assigned at the that index number in
                'contents'.
            value (Any): value to be paired with 'key' in 'contents'.

        """
        if isinstance(key, int):
            self.contents[key] = value
        else:
            self.contents.add(value)
        return self

    def __delitem__(self, key: Union[str, int]) -> None:
        """Deletes item matching 'key' in 'contents'.

        If 'key' is a str type, this method looks for a matching 'name'
        attribute in the stored instances and deletes all such items. If 'key'
        is an integer, only the item at that index is deleted.

        Args:
            key (Union[str, int]): name or index in 'contents' to delete.

        """
        if isinstance(key, int):
            del self.contents[key]
        else:
            self.contents = [c for c in self.contents if c.name != key]
        return self

    def __iter__(self) -> Iterable:
        """Returns chained iterable of 'contents'.
     
        Returns:
            Iterable: using the itertools method which automatically iterates
                all stored iterables within 'contents'.Any
               
        """
        # return iter(itertools.chain.from_iterable(self.contents))
        return(iter(self.contents))

    def __len__(self) -> int:
        """Returns length of 'contents'.

        Returns:
            int: length of 'contents'.

        """
        return len(self.contents)
    
    def __add__(self, other: 'SequenceBase') -> None:
        """Extends 'contents' with 'other'

        Args:
            other (SequenceBase): another SequenceBase instance.

        """
        self.contents.extend(other)
        return self
    
    def __iadd__(self, other: 'MappingBase') -> None:
        """Extends 'contents' with 'other'

        Args:
            other (SequenceBase): another SequenceBase instance.

        """
        self.contents.extend(other)
        return self
    def __repr__(self) -> str:
        """Returns '__str__' representation.

        Returns:
            str: default representation of 'contents'.

        """
        return self.__str__()

    def __str__(self) -> str:
        """Returns default representation of 'contents'.

        Returns:
            str: default representation of 'contents'.

        """
        return (
            f'sourdough {self.__class__.__name__} '
            f'name: {self.name} '
            f'contents: {self.contents.__str__()} ')   


@dataclasses.dataclass
class FactoryBase(abc.ABC):
    """The Factory interface instances a class from available options.

    Args:
        product (Optional[str]): name of sourdough object to return. 'product' 
            must correspond to a key in 'options'. Defaults to None.
        default (ClassVar[str]): the name of the default object to instance. If 
            'product' is not passed, 'default' is used. 'default' must 
            correspond  to a key in 'options'. Defaults to None. If 'default'
            is to be used, it should be specified by a subclass, declared in an
            instance, or set via the class attribute.
        options (ClassVar[MutableMapping]): a dictionary or other mapping of 
            available options for object creation. Keys are the names of the 
            'product'. Values are the objects to create. Defaults to an 
            empty dictionary.

    Returns:
        Any: the factory uses the '__new__' method to return a different object 
            instance with kwargs as the parameters.

    """
    product: Optional[str] = None
    default: ClassVar[str] = None
    options: ClassVar[collections.abc.MutableMapping] = {}

    """ Initialization Methods """
    
    def __new__(cls, 
            product: Optional[str] = None, 
            **kwargs) -> Any:
        """Returns an instance from 'options'.

        Args:
            product (Optional[str]): name of sourdough object to return. 
                'product' must correspond to a key in 'options'. Defaults to 
                None. If not passed, the product listed in 'default' will be 
                used.
            kwargs (Dict[str, Any]): parameters to pass to the object being 
                created.

        Returns:
            Any: an instance of an object stored in 'options'.
        
        """
        if product:
            return cls.options[product](**kwargs) 
        else:
            return cls.options[cls.default](**kwargs)
    
    """ Class Methods """
    
    @classmethod
    def add(cls, key: str, option: 'sourdough.Component') -> None:
        """Adds 'option' to 'options' at 'key'.
        
        Args:
            key (str): name of key to link to 'option'.
            option (sourdough.Component): object to store in 'options'.
            
        """
        cls.options[key] = option
        return cls
        
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
            f'options: {str(self.options)}') 
        

@dataclasses.dataclass
class ImporterBase(abc.ABC):
    """Base class for lazy loading of python modules and objects.

    Args:
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

        Args:
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
        