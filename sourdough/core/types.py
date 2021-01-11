"""
types: sourdough base types
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Vessel (Iterable, ABC): abstract base class for sourdough iterables. All 
        subclasses must have an 'add' method as well as store their contents in 
        the 'contents' attribute.
    Progression (MutableSequence, Vessel): sourdough drop-in replacement for 
        list with additional functionality.
    Hybrid (Progression): iterable with both dict and list interfaces and 
        methods that stores items with a 'name' attribute.
    Lexicon (MutableMapping, Vessel): sourdough's drop-in replacement for 
        python dicts with some added functionality.
    Catalog (Lexicon): wildcard-accepting dict which is primarily intended for 
        storing different options and strategies. It also returns lists of 
        matches if a list of keys is provided.
    Configuration (Lexicon): stores configuration settings after either loading 
        them from disk or by the passed arguments.        
        
"""
from __future__ import annotations
import abc
import collections.abc
import configparser
import dataclasses
import importlib.util
import json
import pathlib
import toml
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import sourdough


@dataclasses.dataclass
class Vessel(collections.abc.Iterable, abc.ABC):
    """Abstract base class for sourdough iterables.
  
    A Vessel differs from a general python iterable in 3 ways:
        1) It must include an 'add' method which provides the default mechanism
            for adding new items to the iterable. All of the other appropriate
            methods for adding to a python iterable ('append', 'extend', 
            'update', etc.) remain, but 'add' allows a subclass to designate the
            preferred method of adding to the iterable's stored data.
        2) It allows the '+' operator to be used to join a Vessel subclass 
            instance of the same general type (Mapping, Sequence, Tuple, etc.). 
            The '+' operator calls the Vessel subclass 'add' method to implement 
            how the added item(s) is/are added to the Vessel subclass instance.
        3) The internally stored iterable is located in the 'contents' 
            attribute. This allows for consistent coordination among classes and
            mixins.
    
    Args:
        contents (Iterable[Any]): stored iterable. Defaults to None.
              
    """
    contents: Iterable[Any] = None

    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Initializes class instance.
        
        Although this method ordinarily does nothing, it makes the order of the
        inherited classes less important with multiple inheritance, such as when 
        adding sourdough quirks. 
        
        """
        # Calls parent initialization methods, if they exist.
        try:
            super().__post_init__()
        except AttributeError:
            pass
          
    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def add(self, item: Any) -> None:
        """Adds 'item' to 'contents' in the default manner.
        
        Subclasses must provide their own methods."""
        pass
    
    """ Dunder Methods """

    def __add__(self, other: Any) -> None:
        """Combines argument with 'contents' using the 'add' method.

        Args:
            other (Any): item to add to 'contents' using the 'add' method.

        """
        self.add(other)
        return self

    def __iter__(self) -> Iterable[Any]:
        """Returns iterable of 'contents'.

        Returns:
            Iterable: of 'contents'.

        """
        return iter(self.contents)


@dataclasses.dataclass
class Progression(collections.abc.MutableSequence, Vessel):
    """Basic sourdough list replacement.
    
    A Progression differs from an ordinary python list only in ways inherited
    from Vessel ('add' method, storage of data in 'contents', and allowing the
    '+' operator to join Progressions with other lists and Progressions).
    
    The 'add' method attempts to extend 'contents' with the item to be added.
    If this fails, it appends the item to 'contents'.
            
    Args:
        contents (Sequence[Any]): items to store in a list. Defaults to an empty 
            list.
        
    """
    contents: Sequence[Any] = dataclasses.field(default_factory = list)

    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Initializes class instance.
        
        Although this method ordinarily does nothing, it makes the order of the
        inherited classes less important with multiple inheritance, such as when 
        adding sourdough quirks. 
        
        """
        # Calls parent initialization methods, if they exist.
        try:
            super().__post_init__()
        except AttributeError:
            pass   
    
    """ Public Methods """

    def add(self, item: Sequence[Any], **kwargs) -> None:
        """Extends 'item' argument to 'contents' attribute.
        
        Args:
            item (Sequence[Any]): items to add to the 'contents' attribute.
            kwargs: creates a consistent interface even when subclasses have
                additional parameters.
        """
        try:
            self.contents.extend(item)
        except TypeError:
            self.contents.append(item)
        return self  

    def insert(self, index: int, item: Any) -> None:
        """Inserts 'item' at 'index' in 'contents'.

        Args:
            index (int): index to insert 'item' at.
            item (Any): object to be inserted.
            
        """
        self.contents.insert(index, item)
        return self
                        
    """ Dunder Methods """

    def __getitem__(self, key: int) -> Any:
        """Returns value(s) for 'key' in 'contents'.

        Args:
            key (int): index to search for in 'contents'.

        Returns:
            Any: item stored in 'contents' at key.

        """
        return self.contents[key]
            
    def __setitem__(self, key: int, value: Any) -> None:
        """Sets 'key' in 'contents' to 'value'.

        Args:
            key (int): index to set 'value' to in 'contents'.
            value (Any): value to be set at 'key' in 'contents'.

        """
        self.contents[key] = value

    def __delitem__(self, key: Union[Any, int]) -> None:
        """Deletes item at 'key' index in 'contents'.

        Args:
            key (int): index in 'contents' to delete.

        """
        del self.contents[key]

    def __iter__(self) -> Iterable[Any]:
        """Returns iterable of 'contents'.

        Returns:
            Iterable: of 'contents'.

        """
        return iter(self.contents)

    def __len__(self) -> int:
        """Returns length of iterable of 'contents'.

        Returns:
            int: length of iterable of 'contents'.

        """
        return len(self.contents)
    
   
@dataclasses.dataclass
class Hybrid(Progression):
    """Base class for ordered iterables in sourdough composite objects.
    
    Hybrid combines the functionality and interfaces of python dicts and lists.
    It allows duplicate keys and list-like iteration while supporting the easier
    access methods of dictionaries. In order to support this hybrid approach to
    iterables, Hybrid can only store items with a 'name' attribute or property.
    
    Hybrid is the primary iterable base class used in sourdough composite 
    objects.
    
    A Hybrid inherits the differences between a Progression and an ordinary 
    python list.
    
    A Hybrid differs from a Progression in 4 significant ways:
        1) It only store items with 'name' attributes or properties.
        2) Hybrid has an interface of both a dict and a list, but stores a list. 
            Hybrid does this by taking advantage of the 'name' attribute of 
            stored items. A 'name' acts as a key to create the facade of a dict
            with the items in the stored list serving as values. This allows for 
            duplicate keys for storing class instances, easier iteration, and 
            returning multiple matching items. This design comes at the expense 
            of lookup speed. As a result, Hybrid should only be used if a high 
            volume of access calls is not anticipated. Ordinarily, the loss of 
            lookup speed should have negligible effect on overall performance.
        3) It includes 'apply' and 'find' methods which traverse items in
            'contents' (recursively, if the 'recursive' argument is True), to
            either 'apply' a Callable or 'find' items matching criteria defined
            in a Callable. 
        4) It includes "excludify" and "subsetify" methods which return new
            instances with a subset of 'contents' based upon the 'subset'
            argument passed to the method. 'excludify' returns all 'contents'
            that do not have names matching items in the 'subset' argument.
            'subsetify' returns all 'contents' that have names matching items
            in the 'subset' argument.

    Args:
        contents (Sequence[Any]): items with 'name' attributes to store. If a 
            dict is passed, the keys will be ignored and only the values will be 
            added to 'contents'. If a single item is passed, it will be placed 
            in a list. Defaults to an empty list.
            
    """
    contents: Sequence[Any] = dataclasses.field(default_factory = list)
    
    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent and/or mixin initialization method(s), if they exist.
        try:
            super().__post_init__()
        except AttributeError:
            pass  
        # Sets initial default value for the 'get' method.
        self._default = None
        
    """ Public Methods """

    def append(self, item: List[Any]) -> None:
        """Appends 'item' to 'contents'.
        
        Args:
            items (List[Any]): items to append to 'contents'.

        """
        self.contents.append(item)
        return self    
    
    def apply(self, tool: Callable, recursive: bool = True, **kwargs) -> None:
        """Maps 'tool' to items stored in 'contents'.
        
        Args:
            tool (Callable): callable which accepts an object in 'contents' as
                its first argument and any other arguments in kwargs.
            recursive (bool): whether to apply 'tool' to nested items in
                'contents'. Defaults to True.
            kwargs: additional arguments to pass when 'tool' is used.
        
        """
        new_contents = []
        for child in iter(self.contents):
            if hasattr(child, 'apply') and recursive:
                new_child = child.apply(tool = tool, recursive = True, **kwargs)
            elif recursive:
                new_child = tool(child, **kwargs)
            else:
                new_child = child
            new_contents.append(new_child)
        self.contents = new_contents
        return self

    def clear(self) -> None:
        """Removes all items from 'contents'."""
        self.contents = []
        return self

    def excludify(self, subset: Union[Any, Sequence[Any]], 
                  **kwargs) -> Hybrid[Any]:
        """Returns a new instance without a subset of 'contents'.

        Args:
            subset (Union[Any, Sequence[Any]]): name(s) for which items from 
                'contents' should not be returned.
            kwargs: creates a consistent interface even when subclasses have
                additional parameters.

        Returns:
            Hybrid: with items without names in 'subset'.

        """
        subset = sourdough.tools.listify(subset)
        return self.__class__(
            contents = [c for c in self.contents if not c.name in subset])  
           
    def extend(self, item: Any) -> None:
        """Extends 'items' to 'contents'.
        
        Args:
            items (Any): instance(s) to add to the 'contents' attribute.

        Raises:
            TypeError: if 'item' does not have a name attribute.
            
        """
        self.contents.extend(item)
        return self  

    def find(self, tool: Callable, recursive: bool = True, 
             matches: Sequence[Any] = None, **kwargs) -> Sequence[Any]:
        """Finds items in 'contents' that match criteria in 'tool'.
        
        Args:
            tool (Callable): callable which accepts an object in 'contents' as
                its first argument and any other arguments in kwargs.
            recursive (bool): whether to apply 'tool' to nested items in
                'contents'. Defaults to True.
            matches (Sequence[Any]): items matching the criteria in 'tool'. This 
                should not be passed by an external call to 'find'. It is 
                included to allow recursive searching.
            kwargs: additional arguments to pass when 'tool' is used.
            
        Returns:
            Sequence[Any]: stored items matching the criteria in 'tool'. 
        
        """
        if matches is None:
            matches = []
        for item in iter(self.contents):
            matches.extend(sourdough.tools.listify(tool(item, **kwargs)))
            if isinstance(item, Iterable) and recursive:
                matches.extend(item.find(tool = tool, recursive = True,
                                         matches = matches, **kwargs))
        return matches
    
    def get(self, key: Union[Any, int]) -> Union[Any, Sequence[Any]]:
        """Returns value(s) in 'contents' or value in '_default' attribute.
        
        Args:
            key (Union[Any, int]): index or key for value in 'contents'.
                
        Returns:
            Union[Any, Sequence[Any]]: items in 'contents' or value in 
                '_default' attribute. 
        """
        try:
            return self[key]
        except KeyError:
            return self._default

    def items(self) -> Iterable:
        """Emulates python dict 'items' method.
        
        Returns:
            Iterable: tuple of Any names and Anys.
            
        """
        return tuple(zip(self.keys(), self.values()))

    def keys(self) -> Sequence[Any]:
        """Emulates python dict 'keys' method.
        
        Returns:
            Sequence[Any]: list of names of stored in 'contents'
            
        """
        return [c.name for c in self.contents]

    def pop(self, key: Union[Any, int]) -> Union[Any, Sequence[Any]]:
        """Pops item(s) from 'contents'.

        Args:
            key (Union[Any, int]): index or key for value in 'contents'.
                
        Returns:
            Union[Any, Sequence[Any]]: item(s) popped from 'contents'.
            
        """
        popped = self[key]
        del self[key]
        return popped
        
    def remove(self, key: Union[Any, int]) -> None:
        """Removes item(s) from 'contents'.

        Args:
            key (Union[Any, int]): index or key for value in 'contents'.
            
        """
        del self[key]
        return self
     
    def setdefault(self, value: Any) -> None:
        """Sets default value to return when 'get' method is used.
        
        Args:
            value (Any): default value to return.
            
        """
        self._default = value 
            
    def subsetify(self, subset: Union[Any, Sequence[Any]], 
                  **kwargs) -> Hybrid[Any]:
        """Returns a new instance with a subset of 'contents'.

        Args:
            subset (Union[Any, Sequence[Any]]): name(s) for which items from 
                'contents' should be returned.
            kwargs: creates a consistent interface even when subclasses have
                additional parameters.

        Returns:
            Hybrid: with items with names in 'subset'.

        """
        subset = sourdough.tools.listify(subset)
        return self.__class__(
            contents = [c for c in self.contents if c.name in subset])     
     
    def update(self, items: Any) -> None:
        """Mimics the dict 'update' method by appending 'items'.
        
        Args:
            items (Any): Any items to add to the 'contents' attribute. If a 
                Mapping is passed, the values are added to 'contents' and the 
                keys become the 'name' attributes of those values. To mimic 
                'update', the passed 'items' are added to 'contents' by the 
                'extend' method.           
        
        """
        if isinstance(items, Mapping):
            for key, value in items.items():
                new_item = value
                new_item.name = key
                self.extend(item = new_item)
        else:
            self.extend(item = items)
        return self

    def values(self) -> Sequence[Any]:
        """Emulates python dict 'values' method.
        
        Returns:
            Sequence[Any]: list of items stored in 'contents'
            
        """
        return self.contents
          
    """ Dunder Methods """

    def __getitem__(self, key: Union[Any, int]) -> Any:
        """Returns value(s) for 'key' in 'contents'.
        
        If 'key' is not an int type, this method looks for a matching 'name'
        attribute in the stored instances.
        
        If 'key' is an int type, this method returns the stored item at the
        corresponding index.
        
        If only one match is found, a single item is returned. If more are 
        found, a Hybrid or Hybrid subclass with the matching 'name' attributes 
        is returned.

        Args:
            key (Union[Any, int]): key or index to search for in 'contents'.

        Returns:
            Any: value(s) stored in 'contents' that correspond to 'key'. If 
                there is more than one match, the return is a Hybrid or Hybrid 
                subclass with that matching stored items.

        """
        if isinstance(key, int):
            return self.contents[key]
        else:
            matches = [c for c in self.contents if c.name == key]
            if len(matches) == 0:
                raise KeyError(f'{key} is not in {self.__class__.__name__}')
            elif len(matches) == 1:
                return matches[0]
            else:
                return self.__class__(contents = matches)
            
    def __setitem__(self, key: Union[Any, int], value: Any) -> None:
        """Sets 'key' in 'contents' to 'value'.

        Args:
            key (Union[Any, int]): if key isn't an int, it is ignored (since the
                'name' attribute of the value will be acting as the key). In
                such a case, the 'value' is added to the end of 'contents'. If
                key is an int, 'value' is assigned at the that index number in
                'contents'.
            value (Any): value to be paired with 'key' in 'contents'.

        """
        if isinstance(key, int):
            self.contents[key] = value
        else:
            self.add(value)
        return self

    def __delitem__(self, key: Union[Any, int]) -> None:
        """Deletes item matching 'key' in 'contents'.

        If 'key' is not an int type, this method looks for a matching 'name'
        attribute in the stored instances and deletes all such items. If 'key'
        is an int type, only the item at that index is deleted.

        Args:
            key (Union[Any, int]): name or index in 'contents' to delete.

        """
        if isinstance(key, int):
            del self.contents[key]
        else:
            self.contents = [c for c in self.contents if c.name != key]
        return self

    def __iter__(self) -> Iterable:
        """Returns iterable of 'contents'.

        Returns:
            Iterable: 'contents'.

        """
        return iter(self.contents)

    def __len__(self) -> int:
        """Returns length of iterable of 'contents'

        Returns:
            int: length of iterable 'contents'.

        """
        return len(self.__iter__())

 
@dataclasses.dataclass
class Lexicon(collections.abc.MutableMapping, Vessel):
    """Basic sourdough dict replacement.
    
    A Lexicon differs from an ordinary python dict in 1 additional way than
    a Vessel:
        1) It includes "excludify" and "subsetify" methods which return new
            instances with a subset of 'contents' based upon the 'subset'
            argument passed to the method. 'excludify' returns all 'contents'
            that do not have keys matching items in the 'subset' argument.
            'subsetify' returns all 'contents' that have keys matching items
            in the 'subset' argument.
    
    Args:
        contents (Mapping[Any, Any]]): stored dictionary. Defaults to an empty 
            dict.
              
    """
    contents: Mapping[Any, Any] = dataclasses.field(default_factory = dict)

    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Initializes class instance.
        
        Although this method ordinarily does nothing, it makes the order of the
        inherited classes less important with multiple inheritance, such as when 
        adding sourdough quirks. 
        
        """
        # Calls parent initialization methods, if they exist.
        try:
            super().__post_init__()
        except AttributeError:
            pass  
        
    """ Public Methods """
     
    def add(self, item: Mapping[Any, Any], **kwargs) -> None:
        """Adds 'item' to the 'contents' attribute.
        
        Args:
            item (Mapping[Any, Any]): items to add to 'contents' attribute.
            kwargs: creates a consistent interface even when subclasses have
                additional parameters.
                
        """
        self.contents.update(item)
        return self
       
    def excludify(self, subset: Union[Any, Sequence[Any]], **kwargs) -> Lexicon:
        """Returns a new instance without a subset of 'contents'.

        Args:
            subset (Union[Any, Sequence[Any]]): key(s) for which key/value pairs 
                from 'contents' should not be returned.
            kwargs: creates a consistent interface even when subclasses have
                additional parameters.

        Returns:
            Lexicon: with only key/value pairs with keys not in 'subset'.

        """
        subset = sourdough.tools.listify(subset)
        contents = {k: v for k, v in self.contents.items() if k not in subset}
        return self.__class__(contents = contents, **kwargs)
            
    def subsetify(self, subset: Union[Any, Sequence[Any]], **kwargs) -> Lexicon:
        """Returns a new instance with a subset of 'contents'.

        Args:
            subset (Union[Any, Sequence[Any]]): key(s) for which key/value pairs 
                from 'contents' should be returned.
            kwargs: creates a consistent interface even when subclasses have
                additional parameters.

        Returns:
            Lexicon: with only key/value pairs with keys in 'subset'.

        """
        subset = sourdough.tools.listify(subset)
        contents = {k: self.contents[k] for k in subset}
        return self.__class__(contents = contents, **kwargs)

    """ Dunder Methods """

    def __getitem__(self, key: Any) -> Any:
        """Returns value for 'key' in 'contents'.

        Args:
            key (Any): key in 'contents' for which a value is sought.

        Returns:
            Any: value stored in 'contents'.

        """
        return self.contents[key]

    def __setitem__(self, key: Any, value: Any) -> None:
        """Sets 'key' in 'contents' to 'value'.

        Args:
            key (Any): key to set in 'contents'.
            value (Any): value to be paired with 'key' in 'contents'.

        """
        self.contents[key] = value
        return self

    def __delitem__(self, key: Any) -> None:
        """Deletes 'key' in 'contents'.

        Args:
            key (Any): key in 'contents' to delete the key/value pair.

        """
        del self.contents[key]
        return self
    
    def __iter__(self) -> Iterable[Any]:
        """Returns iterable of 'contents'.

        Returns:
            Iterable: of 'contents'.

        """
        return iter(self.contents)

    def __len__(self) -> int:
        """Returns length of iterable of 'contents'

        Returns:
            int: length of iterable 'contents'.

        """
        return len(self.__iter__())


@dataclasses.dataclass
class Catalog(Lexicon):
    """Base class for a wildcard and list-accepting dictionary.

    A Catalog inherits the differences between a Lexicon and an ordinary python
    dict.

    A Catalog differs from a Lexicon in 6 significant ways:
        1) It recognizes an 'all' key which will return a list of all values
            stored in a Catalog instance.
        2) It recognizes a 'default' key which will return all values matching
            keys listed in the 'defaults' attribute. 'default' can also be set
            using the 'catalog['default'] = new_default' assignment. If 
            'defaults' is not passed when the instance is initialized, the 
            initial value of 'defaults' is 'all'.
        3) It recognizes a 'none' key which will return an empty list.
        4) It supports a list of keys being accessed with the matching values 
            returned. For example, 'catalog[['first_key', 'second_key']]' will 
            return the values for those keys in a list ['first_value',
            'second_value'].
        5) If a single key is sought, a Catalog can either return the stored
            value or a stored value in a list (if 'always_return_list' is
            True). The latter option is available to make iteration easier
            when the iterator assumes a single datatype will be returned.
        6) It includes a 'instance' and 'select' methods which return instances 
            or stored classes, respectively.

    Args:
        contents (Mapping[Any, Any]]): stored dictionary. Defaults to an empty 
            dict.
        defaults (Sequence[Any]]): a list of keys in 'contents' which will be 
            used to return items when 'default' is sought. If not passed, 
            'default' will be set to all keys.
        always_return_list (bool): whether to return a list even when the key 
            passed is not a list or special access key (True) or to return a 
            list only when a list or special access key is used (False). 
            Defaults to False.
                     
    """
    contents: Mapping[Any, Any] = dataclasses.field(default_factory = dict)  
    defaults: Sequence[Any] = dataclasses.field(default_factory = list)
    always_return_list: bool = False
    
    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Initializes class instance."""
        # Calls parent initialization methods, if they exist.
        try:
            super().__post_init__()
        except AttributeError:
            pass   
        # Sets 'default' to all keys of 'contents', if not passed.
        self.defaults = self.defaults or 'all'

    """ Public Methods """

    def instance(self, key: Union[Any, Sequence[Any]], **kwargs) -> Union[
                 Any, Sequence[Any]]:
        """Returns instance(s) of (a) stored class(es).
        
        This method acts as a factory for instancing stored classes.
        
        Args:
            key (Union[Any, Sequence[Any]]): key(s) in 'contents'.
            kwargs: arguments to pass to the selected item(s) when instanced.
                    
        Returns:
            Union[Any, Sequence[Any]]: stored value(s).
            
        """
        items = self[key]
        if isinstance(items, Sequence) and not isinstance(items, str):
            instances = []
            for item in items:
                instances.append(item(**kwargs))
        else:
            instances = items(**kwargs)
        return instances
 
    def select(self, key: Union[Any, Sequence[Any]]) -> Union[
               Any, Sequence[Any]]:
        """Returns value(s) stored in 'contents'.

        Args:
            key (Union[Any, Sequence[Any]]): key(s) in 'contents'.

        Returns:
            Union[Any, Sequence[Any]]: stored value(s).
            
        """
        return self[key] 

    def excludify(self, subset: Union[Any, Sequence[Any]], **kwargs) -> Catalog:
        """Returns a new instance without a subset of 'contents'.

        Args:
            subset (Union[Any, Sequence[Any]]): key(s) for which key/value pairs 
                from 'contents' should not be returned.
            kwargs: creates a consistent interface even when subclasses have
                additional parameters.

        Returns:
            Catalog: with only key/value pairs without keys in 'subset'.

        """
        if not isinstance(self.defaults, list):
            new_defaults = self.defaults
        else:
            new_defaults = [i for i in self.defaults if i not in subset] 
        return super().excludify(subset = subset, defaults = new_defaults,
                                 always_return_list = self.always_return_list,
                                 **kwargs)
                   
    def subsetify(self, subset: Union[Any, Sequence[Any]], **kwargs) -> Catalog:
        """Returns a new instance with a subset of 'contents'.

        Args:
            subset (Union[Any, Sequence[Any]]): key(s) for which key/value pairs 
                from 'contents' should be returned.
            kwargs: creates a consistent interface even when subclasses have
                additional parameters.

        Returns:
            Catalog: with only key/value pairs with keys in 'subset'.

        """
        if not isinstance(self.defaults, list):
            new_defaults = self.defaults
        else:
            new_defaults = [i for i in self.defaults if i in subset] 
        return super().subsetify(subset = subset, defaults = new_defaults,
                                 always_return_list = self.always_return_list,
                                 **kwargs)

    """ Dunder Methods """

    def __getitem__(self, key: Union[Any, Sequence[Any]]) -> Union[
                    Any, Sequence[Any]]:
        """Returns value(s) for 'key' in 'contents'.

        The method searches for 'all', 'default', and 'none' matching wildcard
        options before searching for direct matches in 'contents'.

        Args:
            key (Union[Any, Sequence[Any]]): key(s) in 'contents'.

        Returns:
            Union[Any, Sequence[Any]]: value(s) stored in 'contents'.

        """
        # Returns a list of all values if the 'all' key is sought.
        if key in ['all', ['all']]:
            return list(self.contents.values())
        # Returns a list of values for keys listed in 'defaults' attribute.
        elif key in ['default', ['default'], 'defaults', ['defaults']]:
            try:
                return self[self.defaults]
            except KeyError:
                return list(
                    {k: self.contents[k] for k in self.defaults}.values())
        # Returns an empty list if a null value is sought.
        elif key in ['none', ['none'], 'None', ['None']]:
            return []
        # Returns list of matching values if 'key' is list-like.        
        elif isinstance(key, Sequence) and not isinstance(key, str):
            return [self.contents[k] for k in key if k in self.contents]
        # Returns matching value if key is not a non-str Sequence or wildcard.
        else:
            try:
                if self.always_return_list:
                    return [self.contents[key]]
                else:
                    return self.contents[key]
            except KeyError:
                raise KeyError(f'{key} is not in {self.__class__.__name__}')

    def __setitem__(self,key: Union[Any, Sequence[Any]], 
                    value: Union[Any, Sequence[Any]]) -> None:
        """Sets 'key' in 'contents' to 'value'.

        Args:
            key (Union[Any, Sequence[Any]]): key(s) to set in 'contents'.
            value (Union[Any, Sequence[Any]]): value(s) to be paired with 'key' 
                in 'contents'.

        """
        if key in ['default', ['default'], 'defaults', ['defaults']]:
            self.defaults = sourdough.tools.listify(value)
        else:
            try:
                self.contents[key] = value
            except TypeError:
                self.contents.update(dict(zip(key, value)))
        return self

    def __delitem__(self, key: Union[Any, Sequence[Any]]) -> None:
        """Deletes 'key' in 'contents'.

        Args:
            key (Union[Any, Sequence[Any]]): name(s) of key(s) in 'contents' to
                delete the key/value pair.

        """
        self.contents = {
            i: self.contents[i] 
            for i in self.contents if i not in sourdough.tools.listify(key)}
        return self

 
@dataclasses.dataclass
class Configuration(sourdough.types.Lexicon):
    """Loads and Stores configuration settings.

    To create Configuration instance, a user can pass a:
        1) file path to a compatible file type;
        2) string containing a a file path to a compatible file type;
                                or,
        3) 2-level nested dict.

    If 'contents' is imported from a file, Configuration creates a dict and can 
    convert the dict values to appropriate datatypes. Currently, supported file 
    types are: ini, json, toml, and python.

    If 'infer_types' is set to True (the default option), str dict values are 
    automatically converted to appropriate datatypes (str, list, float, bool, 
    and int are currently supported). Type conversion is automatically disabled
    if the source file is a python module (assuming the user has properly set
    the types of the stored python dict).

    Because Configuration uses ConfigParser for .ini files, by default it stores 
    a 2-level dict. The desire for accessibility and simplicity dictated this 
    limitation. A greater number of levels can be achieved by having separate
    sections with names corresponding to the strings in the values of items in 
    other sections. This is implemented in the 'project' subpackage.

    Args:
        contents (Union[str, pathlib.Path, Mapping[Any, Mapping[Any, Any]]]): a 
            dict, a str file path to a file with settings, or a pathlib Path to
            a file with settings. Defaults to en empty dict.
        infer_types (bool]): whether values in 'contents' are converted to other 
            datatypes (True) or left alone (False). If 'contents' was imported 
            from an .ini file, a False value will leave all values as strings. 
            Defaults to True.
        defaults (Mapping[str, Mapping[str]]): any default options that should
            be used when a user does not provide the corresponding options in 
            their configuration settings. Defaults to an empty dict.

    """
    contents: Union[str,pathlib.Path, Mapping[str, Mapping[str, Any]]] = (
        dataclasses.field(default_factory = dict))
    infer_types: bool = True
    defaults: Mapping[str, Mapping[str, Any]] = dataclasses.field(
        default_factory = dict)

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent and/or mixin initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass
        self._initial_validation()
        # Infers types for values in 'contents', if the 'infer_types' option is 
        # selected.
        if self.infer_types:
            self.contents = self._infer_types(contents = self.contents)
        # Adds default settings as backup settings to 'contents'.
        self.contents = self._add_defaults(contents = self.contents)

    """ Public Methods """

    def validate(self, 
            contents: Union[
                str,
                pathlib.Path,
                Mapping[Any, Any]]) -> Mapping[Any, Any]:
        """Validates 'contents' or converts 'contents' to the proper type.

        Args:
            contents (Union[str, pathlib.Path, Mapping[Any, Any]]): a dict, a
                str file path to a file with settings, or a pathlib Path to a 
                file with settings.

        Raises:
            TypeError: if 'contents' is neither a str, dict, or Path.

        Returns:
            Mapping[Any, Any]: 'contents' in its proper form.

        """
        if isinstance(contents, Mapping):
            return contents
        elif isinstance(contents, (str, pathlib.Path)):
            extension = str(pathlib.Path(contents).suffix)[1:]
            load_method = getattr(self, f'_load_from_{extension}')
            return load_method(file_path = contents)
        elif contents is None:
            return {}
        else:
            raise TypeError(
                'contents must be None or a dict, Path, or str type')

    def add(self, 
            section: str, 
            contents: Mapping[Any, Any]) -> None:
        """Adds 'settings' to 'contents'.

        Args:
            section (str): name of section to add 'contents' to.
            contents (Mapping[Any, Any]): a dict to store in 'section'.

        """
        try:
            self[section].update(self.validate(contents = contents))
        except KeyError:
            self[section] = self.validate(contents = contents)
        return self

    def inject(self,
            instance: object,
            additional: Union[Sequence[str], str] = None,
            overwrite: bool = False) -> object:
        """Injects appropriate items into 'instance' from 'contents'.

        Args:
            instance (object): sourdough class instance to be modified.
            additional (Union[Sequence[str], str]]): other section(s) in 
                'contents' to inject into 'instance'. Defaults to None.
            overwrite (bool]): whether to overwrite a local attribute in 
                'instance' if there are values stored in that attribute. 
                Defaults to False.

        Returns:
            instance (object): sourdough class instance with modifications made.

        """
        sections = ['general']
        try:
            sections.append(instance.name)
        except AttributeError:
            pass
        if additional:
            sections.extend(sourdough.tools.listify(additional))
        for section in sections:
            try:
                for key, value in self.contents[section].items():
                    instance = self._inject(
                        instance = instance,
                        attribute = key,
                        value = value,
                        overwrite = overwrite)
            except KeyError:
                pass
        return instance

    """ Private Methods """

    def _initial_validation(self) -> None:
        """Validates passed 'contents' on class initialization."""
        self.contents = self.validate(contents = self.contents)
        return self

    def _load_from_ini(self, file_path: str) -> Mapping[Any, Any]:
        """Returns settings dictionary from an .ini file.

        Args:
            file_path (str): path to configparser-compatible .ini file.

        Returns:
            Mapping[Any, Any] of contents.

        Raises:
            FileNotFoundError: if the file_path does not correspond to a file.

        """
        try:
            contents = configparser.ConfigParser(dict_type = dict)
            contents.optionxform = lambda option: option
            contents.read(str(file_path))
            return dict(contents._sections)
        except FileNotFoundError:
            raise FileNotFoundError(f'settings file {file_path} not found')

    def _load_from_json(self, file_path: str) -> Mapping[Any, Any]:
        """Returns settings dictionary from an .json file.

        Args:
            file_path (str): path to configparser-compatible .json file.

        Returns:
            Mapping[Any, Any] of contents.

        Raises:
            FileNotFoundError: if the file_path does not correspond to a file.

        """
        try:
            with open(pathlib.Path(file_path)) as settings_file:
                settings = json.load(settings_file)
            return settings
        except FileNotFoundError:
            raise FileNotFoundError(f'settings file {file_path} not found')

    def _load_from_py(self, file_path: str) -> Mapping[Any, Any]:
        """Returns a settings dictionary from a .py file.

        Args:
            file_path (str): path to python module with '__dict__' dict
                defined.

        Returns:
            Mapping[Any, Any] of contents.

        Raises:
            FileNotFoundError: if the file_path does not correspond to a
                file.

        """
        # Disables type conversion if the source is a python file.
        self.infer_types = False
        try:
            file_path = pathlib.Path(file_path)
            import_path = importlib.util.spec_from_file_location(
                file_path.name,
                file_path)
            import_module = importlib.util.module_from_spec(import_path)
            import_path.loader.exec_module(import_module)
            return import_module.settings
        except FileNotFoundError:
            raise FileNotFoundError(f'settings file {file_path} not found')

    def _load_from_toml(self, file_path: str) -> Mapping[Any, Any]:
        """Returns settings dictionary from a .toml file.

        Args:
            file_path (str): path to configparser-compatible .toml file.

        Returns:
            Mapping[Any, Any] of contents.

        Raises:
            FileNotFoundError: if the file_path does not correspond to a file.

        """
        try:
            return toml.load(file_path)
        except FileNotFoundError:
            raise FileNotFoundError(f'settings file {file_path} not found')

    def _infer_types(self,
            contents: Mapping[Any, Mapping[Any, Any]]) -> Mapping[
                str, Mapping[Any, Any]]:
        """Converts stored values to appropriate datatypes.

        Args:
            contents (Mapping[Any, Mapping[Any, Any]]): a nested contents dict
                to review.

        Returns:
            Mapping[Any, Mapping[Any, Any]]: with the nested values converted to 
                the appropriate datatypes.

        """
        new_contents = {}
        for key, value in contents.items():
            if isinstance(value, dict):
                inner_bundle = {
                    inner_key: sourdough.tools.typify(inner_value)
                    for inner_key, inner_value in value.items()}
                new_contents[key] = inner_bundle
            else:
                new_contents[key] = sourdough.tools.typify(value)
        return new_contents

    def _add_defaults(self,
            contents: Mapping[Any, Mapping[Any, Any]]) -> Mapping[
                str, Mapping[Any, Any]]:
        """Creates a backup set of mappings for sourdough settings lookup.


        Args:
            contents (MutableMapping[Any, Mapping[Any, Any]]): a nested contents 
                dict to add defaults to.

        Returns:
            Mapping[Any, Mapping[Any, Any]]: with stored defaults added.

        """
        new_contents = self.defaults
        new_contents.update(contents)
        return new_contents

    def _inject(self,
            instance: object,
            attribute: str,
            value: Any,
            overwrite: bool) -> object:
        """Adds attribute to 'instance' based on conditions.

        Args:
            instance (object): sourdough class instance to be modified.
            attribute (str): name of attribute to inject.
            value (Any): value to assign to attribute.
            overwrite (bool]): whether to overwrite a local attribute
                in 'instance' if there are values stored in that attribute.
                Defaults to False.

        Returns:
            object: with attribute possibly injected.

        """
        if (not hasattr(instance, attribute)
                or not getattr(instance, attribute)
                or overwrite):
            setattr(instance, attribute, value)
        return instance

    """ Dunder Methods """

    def __setitem__(self, key: str, value: Mapping[Any, Any]) -> None:
        """Creates new key/value pair(s) in a section of the active dictionary.

        Args:
            key (str): name of a section in the active dictionary.
            value (MutableMapping): the dictionary to be placed in that section.

        Raises:
            TypeError if 'key' isn't a str or 'value' isn't a dict.

        """
        try:
            self.contents[key].update(value)
        except KeyError:
            try:
                self.contents[key] = value
            except TypeError:
                raise TypeError(
                    'key must be a str and value must be a dict type')
        return self

    def __missing__(self, key: str) -> 'Configuration':
        """Automatically creates a nested Configuration if 'key' is missing.
        
        This method implements autovivification.
        
        Args:
            key (str): name of key sought in this instance.
            
        Returns:
            Configuration: a new, nested settings at 'key'.
        
        """
        value = self[key] = type(self)(infer_types = False)
        return value
        