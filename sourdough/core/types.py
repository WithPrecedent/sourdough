"""
types: sourdough base types
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Receptable (Iterable, ABC): abstract base class for sourdough iterables. 
        All subclasses must have an 'add' method as well as store their contents 
        in the 'contents' attribute.
    Lexicon (MutableMapping, Receptable): sourdough's drop-in replacement for 
        python dicts with some added functionality.
    Catalog (Lexicon): wildcard-accepting dict which is primarily intended for 
        storing different options and strategies. It also returns lists of 
        matches if a list of keys is provided.
    Progression (MutableSequence, Receptable): sourdough drop-in replacement for list 
        with additional functionality.
    Hybrid (Progression): iterable with both dict and list interfaces and methods that 
        stores items with a 'name' attribute.
        
"""
from __future__ import annotations
import abc
import collections.abc
import dataclasses
import pprint
import textwrap
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Union)

import more_itertools

import sourdough

    
@dataclasses.dataclass
class Receptable(collections.abc.Iterable, abc.ABC):
    """Interface for sourdough iterables.
  
    A Receptable differs from a general python iterable in 3 ways:
        1) It must include an 'add' method which provides the default mechanism
            for adding new items to the iterable.
        2) It allows the '+' operator to be used to join a Receptable subclass 
            instance of the same general type (Mapping, Sequence, Tuple, etc.). 
            The '+' operator calls the Receptable subclass 'add' method to 
            implement how the added item(s) is/are added to the Receptable 
            subclass instance.
        3) The internally stored iterable must be located in the 'contents'
            attribute. This allows for consistent coordination among classes
            and mixins.
    
    Args:
        contents (Iterable[Any]): stored iterable.
              
    """
    contents: Iterable[Any] = None

    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Initializes class instance."""
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

    """ Public Methods """
    
    def convert(self, item: Any) -> Iterable:
        """Placeholder method for type conversion.
        
        Args:
            item (Any): item(s) to be type converted.
            
        Returns:
            Iterable: converted item(s).
        
        """
        return item
    
    def verify(self, item: Any) -> Iterable:
        """Placeholder method for type validation.
        
        Args:
            item (Any): item(s) to be type validated.
            
        Returns:
            Iterable: validated item(s).
        
        """
        return item
    
    """ Dunder Methods """

    def __add__(self, other: Any) -> None:
        """Combines argument with 'contents' using the 'add' method.

        Args:
            other (Any): item to add to 'contents' using the 'add' method.

        """
        self.add(other)
        return self


@dataclasses.dataclass
class Lexicon(collections.abc.MutableMapping, Receptable):
    """Basic sourdough dict replacement.
    
    Args:
        contents (Mapping[Any, Any]]): stored dictionary. Defaults to an empty 
            dict.
              
    """
    contents: Mapping[Any, Any] = dataclasses.field(default_factory = dict)

    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Initializes class instance."""
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
            kwargs: allows subclasses to send additional parameters to this 
                method.
                
        """
        # item = self.verify(item = item)
        # item = self.convert(item = item)
        self.contents.update(item)
        return self
                
    def subsetify(self, subset: Union[str, Sequence[str]], **kwargs) -> Lexicon:
        """Returns a new instance with a subset of 'contents'.

        Args:
            subset (Union[str, Sequence[str]]): key(s) for which key/value pairs 
                from 'contents' should be returned.
            kwargs: allows subclasses to send additional parameters to this 
                method.

        Returns:
            Lexicon: with only key/value pairs with keys in 'subset'.

        """
        subset = sourdough.tools.listify(subset)
        return self.__class__(
            contents = {k: self.contents[k] for k in subset},
            name = self.name,
            **kwargs)

    """ Dunder Methods """

    def __getitem__(self, key: str) -> Any:
        """Returns value for 'key' in 'contents'.

        Args:
            key (str): name of key in 'contents' for which a value is sought.

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
        # item = self.verify(item = value)
        # item = self.convert(item = item)
        self.contents[key] = value
        return self

    def __delitem__(self, key: str) -> None:
        """Deletes 'key' in 'contents'.

        Args:
            key (str): name of key in 'contents' to delete the key/value pair.

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
        defaults (Sequence[str]]): a list of keys in 'contents' which will be 
            used to return items when 'default' is sought. If not passed, 
            'default' will be set to all keys.
        always_return_list (bool): whether to return a list even when the key 
            passed is not a list or special access key (True) or to return a 
            list only when a list or special access key is used (False). 
            Defaults to False.
                     
    """
    contents: Mapping[Any, Any] = dataclasses.field(default_factory = dict)  
    defaults: Sequence[str] = dataclasses.field(default_factory = list)
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

    def instance(self, key: Union[str, Sequence[str]], **kwargs) -> Union[
                 object, Sequence[object]]:
        """Returns instance(s) of (a) stored class(es).
        
        This method acts as a factory for instancing stored classes.
        
        Args:
            key (Union[str, Sequence[str]]): name(s) of key(s) in 'contents'.
            kwargs: arguments to pass to the selected item(s) when instanced.
                    
        Returns:
            Union[object, Sequence[object]]: instance(s) of stored classes.
            
        """
        items = self[key]
        if isinstance(items, Sequence) and not isinstance(items, str):
            instances = []
            for item in items:
                instances.append(item(**kwargs))
        else:
            instances = items(**kwargs)
        return instances
 
    def select(self,key: Union[str, Sequence[str]]) -> Union[Any, Sequence[Any]]:
        """Returns value(s) stored in 'contents'.

        Args:
            key (Union[str, Sequence[str]]): name(s) of key(s) in 'contents'.

        Returns:
            Union[Any, Sequence[Any]]: stored value(s).
            
        """
        return self[key] 
            
    def subsetify(self, subset: Union[str, Sequence[str]], **kwargs) -> Catalog:
        """Returns a subset of 'contents'.

        Args:
            subset (Union[str, Sequence[str]]): key(s) to get key/value pairs 
                from 'contents'.
            kwargs: allows subclasses to send additional parameters to this 
                method.
                
        Returns:
            Catalog: with only keys in 'subset'.

        """
        if isinstance(self.defaults, str):
            new_defaults = self.defaults
        else:
            new_defaults = [i for i in self.defaults if i in subset] 
        return super().subsetify(
            subset = subset,
            defaults = new_defaults,
            always_return_list = self.always_return_list,
            **kwargs)

    """ Dunder Methods """

    def __getitem__(self, key: Union[str, Sequence[str]]) -> Union[
                    Any, Sequence[Any]]:
        """Returns value(s) for 'key' in 'contents'.

        The method searches for 'all', 'default', and 'none' matching wildcard
        options before searching for direct matches in 'contents'.

        Args:
            key (Union[str, Sequence[str]]): name(s) of key(s) in 'contents'.

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
        # Returns matching value if key is a str.
        else:
            try:
                if self.always_return_list:
                    return [self.contents[key]]
                else:
                    return self.contents[key]
            except KeyError:
                raise KeyError(f'{key} is not in {self.__class__.__name__}')

    def __setitem__(self,key: Union[str, Sequence[str]], 
                    value: Union[Any, Sequence[Any]]) -> None:
        """Sets 'key' in 'contents' to 'value'.

        Args:
            key (Union[str, Sequence[str]]): name of key(s) to set in 'contents'.
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

    def __delitem__(self, key: Union[str, Sequence[str]]) -> None:
        """Deletes 'key' in 'contents'.

        Args:
            key (Union[str, Sequence[str]]): name(s) of key(s) in 'contents' to
                delete the key/value pair.

        """
        self.contents = {
            i: self.contents[i]
            for i in self.contents if i not in sourdough.tools.listify(key)}
        return self

  
@dataclasses.dataclass
class Progression(collections.abc.MutableSequence, Receptable):
    """Basic sourdough list replacement.

    Args:
        contents (Sequence[Any]): items to store in a list. Defaults to an empty 
            list.
        
    """
    contents: Sequence[Any] = dataclasses.field(default_factory = list)

    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Initializes class instance."""
        # Calls parent initialization methods, if they exist.
        try:
            super().__post_init__()
        except AttributeError:
            pass   
    
    """ Public Methods """

    def add(self, item: Sequence[Any]) -> None:
        """Extends 'item' argument to 'contents' attribute.
        
        Args:
            item (Sequence[Any]): items to add to the 'contents' attribute.

        """
        # item = self.verify(item = item)
        # item = self.convert(item = item)
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
        # item = self.verify(item = item)
        # item = self.convert(item = item)
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
        # item = self.verify(item = value)
        # item = self.convert(item = item)
        self.contents[key] = value

    def __delitem__(self, key: Union[str, int]) -> None:
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
    
    A Hybrid differs from a Progression in 3 significant ways:
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
        # item = self.verify(item = item)
        # item = self.convert(item = item)
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
        for item in iter(self.contents):
            if isinstance(item, sourdough.Hybrid):
                if recursive:
                    new_item = item.apply(
                        tool = tool, 
                        recursive = True, 
                        **kwargs)
                else:
                    new_item = item
            else:
                new_item = tool(item, **kwargs)
            new_contents.append(new_item)
        self.contents = new_contents
        return self

    def clear(self) -> None:
        """Removes all items from 'contents'."""
        self.contents = []
        return self
    
    def extend(self, item: Any) -> None:
        """Extends 'items' to 'contents'.
        
        Args:
            items (Any): instance(s) to add to the 'contents' attribute.

        Raises:
            TypeError: if 'item' does not have a name attribute.
            
        """
        # item = self.verify(item = item)
        # item = self.convert(item = item)
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
            matches (Sequence[Any]): items matching the criteria
                in 'tool'. This should not be passed by an external call to
                'find'. It is included to allow recursive searching.
            kwargs: additional arguments to pass when 'tool' is used.
            
        Returns:
            Sequence[Any]: stored items matching the criteria
                in 'tool'. 
        
        """
        if matches is None:
            matches = []
        for item in iter(self.contents):
            matches.extend(sourdough.tools.listify(tool(item, **kwargs)))
            if isinstance(item, sourdough.Hybrid):
                if recursive:
                    matches.extend(item.find(
                        tool = tool, 
                        recursive = True,
                        matches = matches, 
                        **kwargs))
        return matches
    
    def get(self, key: Union[str, int]) -> Union[Any, Sequence[Any]]:
        """Returns value(s) in 'contents' or value in '_default' attribute.
        
        Args:
            key (Union[str, int]): index or stored Any name to get from
                'contents'.
                
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

    def keys(self) -> Sequence[str]:
        """Emulates python dict 'keys' method.
        
        Returns:
            Sequence[Any]: list of names of stored in 'contents'
            
        """
        return [c.name for c in self.contents]

    def pop(self, key: Union[str, int]) -> Union[Any, Sequence[Any]]:
        """Pops item(s) from 'contents'.

        Args:
            key (Union[str, int]): index or stored name to pop from 'contents'.
                
        Returns:
            Union[Any, Sequence[Any]]: item(s) popped from 'contents'.
            
        """
        popped = self[key]
        del self[key]
        return popped
        
    def remove(self, key: Union[str, int]) -> None:
        """Removes item(s) from 'contents'.

        Args:
            key (Union[str, int]): index or stored name to remove from
                'contents'.
            
        """
        del self[key]
        return self
     
    def setdefault(self, value: Any) -> None:
        """Sets default value to return when 'get' method is used.
        
        Args:
            value (Any): default value to return.
            
        """
        self._default = value 
     
    def subsetify(self, subset: Union[str, Sequence[str]]) -> Hybrid[Any]:
        """Returns a subset of 'contents'.

        Args:
            subset (Union[str, Sequence[str]]): key(s) to get items with 
                matching 'name' attributes from 'contents'.

        Returns:
            Hybrid[Any]: with only items with 'name' attributes in 'subset'.

        """
        subset = sourdough.tools.listify(subset)
        return self.__class__(
            name = self.name,
            contents = [c for c in self.contents if c.name in subset])     
     
    def update(self, items: Any) -> None:
        """Mimics the dict 'update' method by appending 'items'.
        
        Args:
            items (Any): Any items to add to the 'contents' attribute. If a 
                Mapping is passed, the values are added to 'contents' and the 
                keys become the 'name' attributes of those values. To mimic 
                'update', the passed 'items' are added to 'contents' by the 
                'extend' method.
 
        Raises:
            TypeError: if any of 'items' do not have a name attribute or
                if 'items is not a dict.               
        
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
            Sequence[Any]: list of Anys stored in 'contents'
            
        """
        return self.contents
          
    """ Dunder Methods """

    def __getitem__(self, key: Union[str, int]) -> Any:
        """Returns value(s) for 'key' in 'contents'.
        
        If 'key' is a str type, this method looks for a matching 'name'
        attribute in the stored instances.
        
        If 'key' is an int type, this method returns the stored item at the
        corresponding index.
        
        If only one match is found, a single item is returned. If more are 
        found, a Hybrid or Hybrid subclass with the matching 'name' attributes 
        is returned.

        Args:
            key (Union[str, int]): name or index to search for in 'contents'.

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
                return self.__class__(name = self.name, contents = matches)
            
    def __setitem__(self, key: Union[str, int], value: Any) -> None:
        """Sets 'key' in 'contents' to 'value'.

        Args:
            key (Union[str, int]): if key is a string, it is ignored (since the
                'name' attribute of the value will be acting as the key). In
                such a case, the 'value' is added to the end of 'contents'. If
                key is an int, 'value' is assigned at the that index number in
                'contents'.
            value (Any): value to be paired with 'key' in 'contents'.

        """
        # item = self.verify(item = value)
        # item = self.convert(item = item)
        if isinstance(key, int):
            self.contents[key] = value
        else:
            self.add(value)
        return self

    def __delitem__(self, key: Union[str, int]) -> None:
        """Deletes item matching 'key' in 'contents'.

        If 'key' is a str type, this method looks for a matching 'name'
        attribute in the stored instances and deletes all such items. If 'key'
        is an int type, only the item at that index is deleted.

        Args:
            key (Union[str, int]): name or index in 'contents' to delete.

        """
        if isinstance(key, int):
            del self.contents[key]
        else:
            self.contents = [c for c in self.contents if c.name != key]
        return self

    def __iter__(self) -> Iterable:
        """Returns  iterable of collapsed 'contents'.

        Returns:
            Iterable: collapsed 'contents'.

        """
        return more_itertools.collapse(self.contents)

    def __len__(self) -> int:
        """Returns length of iterable of 'contents'

        Returns:
            int: length of iterable 'contents'.

        """
        return len(self.__iter__())
