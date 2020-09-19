"""
base: sourdough base class for composite objects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Element (ABC): abstract base class for sourdough objects that are part of 
        composite structures.
    Elemental: annotation type for all classes that contain Elements. This
        includes any Element subclass, any Sequence of Elements or a Mapping
        with Element values.
    Slate (MutableSequence): sourdough drop-in replacement for list with 
        additional functionality.
    Lexicon (MutableMapping): sourdough's drop-in replacement for python dicts 
        with some added functionality.
    Hybrid (Element, Slate): iterable containing Element subclass instances 
        with both dict and list interfaces and methods.
    Catalog (Lexicon): wildcard-accepting dict which is primarily intended for 
        storing different options and strategies.
    Options (ABC): abstract base class for subclasses which store strategies 
        or other options in a 'library' attribute. It provides subclasses with
        a 'build' method for creating instances from stored options and a
        'select' method which returns stored items as they are stored. A 
        Options subclass can be linked to a Factory to automatically return
        a stored object when a Factory subclass is instanced.
    Registry (Options): abstract base class that automatically registers any 
        subclasses and stores them in the 'library' class attribute. 
    Repository (Options): abstract base class for automatically storing subclass
        instances in a 'library' class attribute.
    Validator (Registry): abstract base class for type validators and 
        converters. The class provides a universal 'verify' method for type
        validation. All subclasses must have a 'convert' method for type 
        conversion.
    Factory (ABC): object factory which returns instances of one or more 
        selected options. If multiple options are selected for creation, they 
        are returned in a list. Factory must be linked to an Options subclass
        via its 'options' attribute.
    Loader (ABC): lazy loader which uses a 'load' method to import python
        classes, functions, and other items at runtime on demand. 
    ProxyMixin (ABC): mixin which creates a python property which refers to 
        another attribute by using the 'proxify' method.
 
"""
from __future__ import annotations
import abc
import collections.abc
import copy
import dataclasses
import inspect
import pprint
import textwrap
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union

import more_itertools

import sourdough


@dataclasses.dataclass
class Element(abc.ABC):
    """Base class for parts of sourdough composite objects.

    A Element has a 'name' attribute for internal referencing and to allow 
    sourdough iterables to function propertly. Element instances can be used 
    to create a variety of composite data structures such as trees, cycles, 
    contests, studies, and graphs. 

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Element is called, 'name' is set based upon
            the 'get_name' method in Element. If that method is not overridden 
            by a subclass instance, 'name' will be assigned to the snake case 
            version of the class name ('__class__.__name__').
    
    """
    name: str = None

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Sets 'name' to the default value if it is not passed.
        self.name = self.name or self.get_name()

    """ Class Methods """

    @classmethod
    def get_name(cls) -> str:
        """Returns 'name' of class for use throughout sourdough.
        
        The method is a classmethod so that a 'name' can properly derived even
        before a class is instanced. It can also be called after a subclass is
        instanced (as is the case in '__post_init__').
        
        This method converts the class name from CapitalCase to snake_case.
        
        If a user wishes to use an alternate naming system, a subclass should
        simply override this method. 
        
        Returns:
            str: name of class for internal referencing and some access methods.
        
        """
        if isinstance(cls, Element):
            return cls.name
        elif inspect.isclass(cls):
            return sourdough.tools.snakify(cls.__name__)
        else:
            return sourdough.tools.snakify(cls.__class__.__name__)

    """ Dunder Methods """

    def __repr__(self) -> str:
        """Returns '__str__' representation.

        Returns:
            str: default string representation of an instance.

        """
        return self.__str__()
        
    def __str__(self) -> str:
        """Returns pretty string representation of an instance.
        
        Returns:
            str: pretty string representation of an instance.
            
        """
        new_line = '\n'
        representation = [f'sourdough {self.__class__.__name__}']
        attributes = [a for a in self.__dict__ if not a.startswith('_')]
        for attribute in attributes:
            value = getattr(self, attribute)
            if (isinstance(value, Element) 
                    and isinstance(value, (Sequence, Mapping))):
                representation.append(
                    f'''{attribute}:{new_line}{textwrap.indent(
                        str(value.contents), '    ')}''')            
            elif (isinstance(value, (Sequence, Mapping)) 
                    and not isinstance(value, str)):
                representation.append(
                    f'''{attribute}:{new_line}{textwrap.indent(
                        str(value), '    ')}''')
            else:
                representation.append(f'{attribute}: {str(value)}')
        return new_line.join(representation)    


Elemental = Union[Element, Mapping[str, Element], Sequence[Element]]


@dataclasses.dataclass
class Lexicon(collections.abc.MutableMapping):
    """Basic sourdough dict replacement.

    Lexicon subclasses can serve as drop in replacements for dicts with added
    features.
    
    A Lexicon differs from a python dict in 5 significant ways:
        1) It includes an 'add' method which allows different datatypes to
            be passed and added to a Lexicon instance. All of the normal dict 
            methods are also available. 'add' should be used to set default or 
            more complex methods of adding elements to the stored dict.
        2) It includes a 'subsetify' method which will return a Lexicon or
            Lexicon subclass instance with only the key/value pairs matching
            keys in the 'subset' argument.
        3) It allows the '+' operator to be used to join a Lexicon instance
            with another Lexicon instance or another Mapping. The '+' operator 
            calls the Lexicon 'add' method to implement how the added item(s) 
            is/are added to the Lexicon instance.
    
    Args:
        contents (Mapping[Any, Any]]): stored dictionary. Defaults to an empty 
            dict.
              
    """
    contents: Mapping[Any, Any] = dataclasses.field(default_factory = dict)
        
    """ Public Methods """
     
    def add(self, contents: Mapping[Any, Any], **kwargs) -> None:
        """Adds 'contents' to the 'contents' attribute.
        
        Args:
            contents (Mapping[Any, Any]): items to add to 'contents' attribute.
                Element.
            kwargs: allows subclasses to send additional parameters to this 
                method.
                
        """
        try:
            contents = self.convert(contents = contents)
        except AttributeError:
            pass
        self.contents.update(contents)
        return self
                
    def subsetify(self, 
            subset: Union[str, Sequence[str]], 
            **kwargs) -> Lexicon:
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

    def __add__(self, other: Any) -> None:
        """Combines argument with 'contents' using the 'add' method.

        Args:
            other (Any): item to add to 'contents' using the 'add' method.

        """
        self.add(other)
        return self

  
@dataclasses.dataclass
class Slate(collections.abc.MutableSequence):
    """Basic sourdough list replacement.
    
    A Slate differs from a python list in 3 significant ways:
        1) It includes a 'name' attribute which is used for internal referencing
            in sourdough. This is inherited from Element.
        2) It includes an 'add' method which allows different datatypes to be 
            passed and added to the 'contents' of a Slate instance. 

    Args:
        contents (Sequence[Any]): items to store in a list. Defaults to an empty 
            list.
        
    """
    contents: Sequence[Any] = dataclasses.field(default_factory = list)
        
    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent initialization method(s), if they exist.
        try:
            super().__post_init__()
        except AttributeError:
            pass     
    
    """ Public Methods """

    def add(self, contents: Sequence[Any]) -> None:
        """Extends 'contents' argument to 'contents' attribute.
        
        Args:
            contents (Sequence[Any]): items to add to the 'contents' attribute.

        """
        try:
            contents = self.convert(contents = contents)
        except AttributeError:
            pass
        self.contents.extend(contents)
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

    def __delitem__(self, key: Union[str, int]) -> None:
        """Deletes item at 'key' index in 'contents'.

        Args:
            key (int): index in 'contents' to delete.

        """
        del self.contents[key]

    def __iter__(self) -> Iterable:
        """Returns iterable of 'contents'.

        Returns:
            Iterable: generic ordered iterable of 'contents'.
               
        """
        return iter(self.contents)

    def __len__(self) -> int:
        """Returns length of 'contents'.

        Returns:
            int: length of 'contents'.

        """
        return len(self.contents)

    def __add__(self, other: Any) -> None:
        """Combines argument with 'contents'.

        Args:
            other (Any): item to add to 'contents' using the 'add' method.

        """
        self.add(other)
        return self

   
@dataclasses.dataclass
class Hybrid(Element, Slate):
    """Base class for ordered iterables in sourdough composite objects.
    
    Hybrid combines the functionality and interfaces of python dicts and lists.
    It allows duplicate keys and list-like iteration while supporting the easier
    access methods of dictionaries. In order to support this hybrid approach to
    iterables, Hybrid can only store Element subclasses.
    
    Hybrid is the primary iterable base class used in sourdough composite 
    objects.
    
    A Hybrid inherits the differences between a Slate and an ordinary python 
    list.
    
    A Hybrid differs from a Slate in 4 significant ways:
        1) It only stores Element subclasses or subclass instances.
        2) It includes a 'subsetify' method which will return a Hybrid or Hybrid 
            subclass instance with only the items with 'name' attributes 
            matching items in the 'subset' argument.
        3) Hybrid has an interface of both a dict and a list, but stores a list. 
            Hybrid does this by taking advantage of the 'name' attribute of 
            Element instances. A 'name' acts as a key to create the facade of 
            a dictionary with the items in the stored list serving as values. 
            This allows for duplicate keys for storing class instances, easier 
            iteration, and returning multiple matching items. This design comes 
            at the expense of lookup speed. As a result, Hybrid should only be 
            used if a high volume of access calls is not anticipated. 
            Ordinarily, the loss of lookup speed should have negligible effect 
            on overall performance.
        4) It includes 'apply' and 'find' methods which traverse items in
            'contents' (recursively, if the 'recursive' argument is True), to
            either 'apply' a callable or 'find' items matching criteria in a
            callable. 

    Args:
        contents (Elemental): Element subclasses or Element subclass 
            instances to store in a list. If a dict is passed, the keys will 
            be ignored and only the values will be added to 'contents'. If a
            single Element is passed, it will be placed in a list. Defaults to 
            an empty list.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Element is called, 'name' is set based 
            upon the '_get_name' method in Element. If that method is 
            not overridden by a subclass instance, 'name' will be assigned to 
            the snake case version of the class name ('__class__.__name__').
        
    Attributes:
        contents (Sequence[Element]): stored Element subclasses or 
            subclass instances.
            
    """
    contents: Elemental = dataclasses.field(default_factory = list)
    name: str = None 
    
    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent initialization method(s).
        super().__post_init__()        
        # Sets initial default value for the 'get' method.
        self._default = None
        
    """ Public Methods """

    def append(self, contents: Elemental) -> None:
        """Appends 'element' to 'contents'.
        
        Args:
            contents (Union[Element, Mapping[Any, Element], 
                Sequence[Element]]): Element instance(s) to add to the
                'contents' attribute.

        Raises:
            TypeError: if 'element' does not have a name attribute.
            
        """
        try:
            contents = self.convert(contents = contents)
        except AttributeError:
            pass
        self.contents.append(contents)
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
            if isinstance(item, sourdough.base.Hybrid):
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
   
    def extend(self, contents: Elemental) -> None:
        """Extends 'element' to 'contents'.
        
        Args:
            contents (Elemental): Elemental instance(s) to add to the 'contents' 
                attribute.

        Raises:
            TypeError: if 'element' does not have a name attribute.
            
        """
        try:
            contents = self.convert(contents = contents)
        except AttributeError:
            pass
        self.contents.extend(contents)
        return self  

    def find(self, 
            tool: Callable, 
            recursive: bool = True, 
            matches: Sequence[Element] = None,
            **kwargs) -> Sequence[Element]:
        """Finds items in 'contents' that match criteria in 'tool'.
        
        Args:
            tool (Callable): callable which accepts an object in 'contents' as
                its first argument and any other arguments in kwargs.
            recursive (bool): whether to apply 'tool' to nested items in
                'contents'. Defaults to True.
            matches (Sequence[Element]): items matching the criteria
                in 'tool'. This should not be passed by an external call to
                'find'. It is included to allow recursive searching.
            kwargs: additional arguments to pass when 'tool' is used.
            
        Returns:
            Sequence[Element]: stored items matching the criteria
                in 'tool'. 
        
        """
        if matches is None:
            matches = []
        for item in iter(self.contents):
            matches.extend(sourdough.tools.listify(tool(item, **kwargs)))
            if isinstance(item, sourdough.base.Hybrid):
                if recursive:
                    matches.extend(item.find(
                        tool = tool, 
                        recursive = True,
                        matches = matches, 
                        **kwargs))
        return matches
    
    def get(self, key: Union[str, int]) -> Union[Element, Sequence[Element]]:
        """Returns value(s) in 'contents' or value in '_default' attribute.
        
        Args:
            key (Union[str, int]): index or stored Element name to get from
                'contents'.
                
        Returns:
            Union[Element, Sequence[Element]]: items in 'contents' or value in 
                '_default' attribute. 
        """
        try:
            return self[key]
        except KeyError:
            return self._default
            
    def insert(self, index: int, element: Element) -> None:
        """Inserts 'element' at 'index' in 'contents'.

        Args:
            index (int): index to insert 'element' at.
            element (Element): object to be inserted.

        Raises:
            TypeError: if 'element' is not a Element type.
            
        """
        if isinstance(element, Element):
            self.contents.insert(index, element)
        else:
            raise TypeError('element must be a Element type')
        return self

    def items(self) -> Iterable:
        """Emulates python dict 'items' method.
        
        Returns:
            Iterable: tuple of Element names and Elements.
            
        """
        return tuple(zip(self.keys(), self.values()))

    def keys(self) -> Sequence[str]:
        """Emulates python dict 'keys' method.
        
        Returns:
            Sequence[Element]: list of names of Elements stored in 
                'contents'
            
        """
        try:
            return [c.name for c in self.contents]
        except AttributeError:
            return [c.get_name() for c in self.contents]

    def pop(self, key: Union[str, int]) -> Union[Element, Sequence[Element]]:
        """Pops item(s) from 'contents'.

        Args:
            key (Union[str, int]): index or stored Element name to pop from
                'contents'.
                
        Returns:
            Union[Element, Sequence[Element]]: items popped from 
                'contents'.
            
        """
        popped = self[key]
        del self[key]
        return popped
        
    def remove(self, key: Union[str, int]) -> None:
        """Removes item(s) from 'contents'.

        Args:
            key (Union[str, int]): index or stored Element name to remove from
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
     
    def subsetify(self, subset: Union[str, Sequence[str]]) -> Hybrid:
        """Returns a subset of 'contents'.

        Args:
            subset (Union[str, Sequence[str]]): key(s) to get Element 
                instances with matching 'name' attributes from 'contents'.

        Returns:
            Hybrid: with only items with 'name' attributes in 'subset'.

        """
        subset = sourdough.tools.listify(subset)
        try:
            return self.__class__(
                name = self.name,
                contents = [c for c in self.contents if c.name in subset])  
        except AttributeError:            
            return self.__class__(
                name = self.name,
                contents = [c for c in self.contents if c.get_name() in subset])    
     
    def update(self, contents: Elemental) -> None:
        """Mimics the dict 'update' method by appending 'contents'.
        
        Args:
            contents (Elemental): Elemental instances to add to the 'contents' 
                attribute. If a Mapping is passed, the values are added to 
                'contents' and the keys become the 'name' attributes of those 
                values. To mimic 'update', the passed 'elements' are added to 
                'contents' by the 'extend' method.
 
        Raises:
            TypeError: if any of 'elements' do not have a name attribute or
                if 'elements is not a dict.               
        
        """
        if isinstance(contents, Mapping):
            for key, value in contents.items():
                new_element = value
                new_element.name = key
                self.extend(contents = new_element)
        else:
            self.extend(contents = contents)
        return self

    def values(self) -> Sequence[Element]:
        """Emulates python dict 'values' method.
        
        Returns:
            Sequence[Element]: list of Elements stored in 'contents'
            
        """
        return self.contents
          
    """ Dunder Methods """

    def __getitem__(self, key: Union[str, int]) -> Element:
        """Returns value(s) for 'key' in 'contents'.
        
        If 'key' is a str type, this method looks for a matching 'name'
        attribute in the stored instances.
        
        If 'key' is an int type, this method returns the stored element at the
        corresponding index.
        
        If only one match is found, a single Element instance is returned. If
        more are found, a Hybrid or Hybrid subclass with the matching
        'name' attributes is returned.

        Args:
            key (Union[str, int]): name or index to search for in 'contents'.

        Returns:
            Element: value(s) stored in 'contents' that correspond 
                to 'key'. If there is more than one match, the return is a
                Hybrid or Hybrid subclass with that matching stored
                elements.

        """
        if isinstance(key, int):
            return self.contents[key]
        else:
            try:
                matches = [c for c in self.contents if c.name == key]
            except AttributeError:
                matches = [c for c in self.contents if c.get_name() == key]
            if len(matches) == 0:
                raise KeyError(f'{key} is not in {self.name}')
            elif len(matches) == 1:
                return matches[0]
            else:
                return self.__class__(name = self.name, contents = matches)
            
    def __setitem__(self, 
            key: Union[str, int], 
            value: Element) -> None:
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
            try:
                self.contents = [c for c in self.contents if c.name != key]
            except AttributeError:
                self.contents = [
                    c for c in self.contents if c.get_name() != key]
        return self

    def __len__(self) -> int:
        """Returns length of collapsed 'contents'.

        Returns:
            int: length of collapsed 'contents'.

        """
        return len(list(more_itertools.collapse(self.contents)))


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
        6) It includes a 'create' method which will either instance a stored
            class or return a stored instance.

    Args:
        contents (Mapping[str, Any]]): stored dictionary. Defaults to an empty 
            dict.
        defaults (Sequence[str]]): a list of keys in 'contents' which will be 
            used to return items when 'default' is sought. If not passed, 
            'default' will be set to all keys.
        always_return_list (bool]): whether to return a list even when
            the key passed is not a list or special access key (True) or to 
            return a list only when a list or special acces key is used (False). 
            Defaults to False.
                     
    """
    contents: Mapping[str, Any] = dataclasses.field(default_factory = dict)  
    defaults: Sequence[str] = dataclasses.field(default_factory = list)
    always_return_list: bool = False
    
    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Sets 'default' to all keys of 'contents', if not passed.
        self.defaults = self.defaults or 'all'

    """ Public Methods """

    def create(self, key: str, **kwargs) -> object:
        """Returns an instance of a stored subclass or instance.
        
        This method acts as a factory for instancing stored classes or returning
        instances.
        
        Args:
            key (str): key to desired item in 'contents'.
            kwargs: arguments to pass to the selected item when it is instanced.
                    
        Returns:
            object: that has been instanced with kwargs as arguments if it 
                was a stored class. Otherwise, the instance is returned as it 
                was stored.
            
        """
        try:
            return self.contents[key](**kwargs)
        except TypeError:
            return self.contents[key] 
        
    def subsetify(self, 
            subset: Union[str, Sequence[str]], 
            **kwargs) -> Catalog:
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

    def __getitem__(self, 
            key: Union[Sequence[str], str]) -> Union[Sequence[Any], Any]:
        """Returns value(s) for 'key' in 'contents'.

        The method searches for 'all', 'default', and 'none' matching wildcard
        options before searching for direct matches in 'contents'.

        Args:
            key (Union[Sequence[str], str]): name(s) of key(s) in 'contents'.

        Returns:
            Union[Sequence[Any], Any]: value(s) stored in 'contents'.

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

    def __setitem__(self,
            key: Union[Sequence[str], str],
            value: Union[Sequence[Any], Any]) -> None:
        """Sets 'key' in 'contents' to 'value'.

        Args:
            key (Union[Sequence[str], str]): name of key(s) to set in 
                'contents'.
            value (Union[Sequence[Any], Any]): value(s) to be paired with 'key' 
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

    def __delitem__(self, key: Union[Sequence[str], str]) -> None:
        """Deletes 'key' in 'contents'.

        Args:
            key (Union[Sequence[str], str]): name(s) of key(s) in 'contents' to
                delete the key/value pair.

        """
        self.contents = {
            i: self.contents[i]
            for i in self.contents if i not in sourdough.tools.listify(key)}
        return self


@dataclasses.dataclass
class Options(abc.ABC):
    """ Base class for stored options libraries.
    
    Options store strategies  or other options in a 'library' attribute. It 
    provides subclasses with a 'build' method for creating instances from stored
    options and a 'select' method which returns stored items as they are stored. 
    A Options subclass can be linked to a Factory to automatically return a 
    stored object when a Factory subclass is instanced.
    
    Args:
        library (ClassVar[Catalog]): the instance which stores 
            options or strategies in the 'library' class attribute.  
    
    Namespaces: 
        'library', 'register_from_disk', 'add_option', 'build'
        
    """
    library: ClassVar[Catalog] = Catalog()
    
    """ Class Methods """
    
    @classmethod
    def add_option(cls, key: str, value: Any) -> None:
        """Adds 'value' to 'library' at 'key'.
        
        Args:
            key (str): name of key to link to 'value'.
            value (Any): item to store in 'library'.
            
        """
        cls.library[key] = value
        return cls
    
    @classmethod
    def build(cls, key: Union[str, Sequence[str]], **kwargs) -> Any:
        """Creates instance(s) of a class(es) stored in 'library'.

        Args:
            key (Union[str, Sequence[str]]): name matching a key in 'library' 
                for which the value is sought.
            kwargs: arguments to pass to any selected items from the 'library'.

        Raises:
            TypeError: if 'key' is neither a str nor Sequence type.
            
        Returns:
            Any: instance(s) of a stored class(es) with kwargs passed as 
                arguments.
            
        """
        if isinstance(key, str):
            return cls.library.create(key = key, **kwargs)
        elif isinstance(key, Sequence):
            instances = []
            for item in key:
                instances.append(cls.library.create(key = item, **kwargs))
            return instances
        else:
            raise TypeError('key must be a str or list type')
 
    @classmethod
    def select(cls, key: Union[str, Sequence[str]]) -> object:
        """Returns a value stored in 'library'.

        Args:
            key (Union[str, Sequence[str]]): key(s) to values in 'library' to
                return.

        Returns:
            Any: value(s) stored in library.
            
        """
        return cls.library[key]       


@dataclasses.dataclass
class Registry(Options, abc.ABC):
    """ which stores subclasses in a 'library' class attribute.

    Args:
        register_from_disk (bool): whether to look in the current working
            folder and subfolders for subclasses of the Element class for 
            which this class is a mixin. Defaults to False.
        library (ClassVar[Catalog]): the instance which stores subclasses in a 
            Catalog instance.

    Namespaces: 
        'library', 'add_option', 'build', 'select', 'register_from_disk', 
        '_library_base', 'find_subclasses', '_import_from_path', 
        '_get_subclasses'
        
    To Do:
        Fix 'find_subclasses' and related classes. Currently, 
            importlib.util.module_from_spec returns None.
    
    """
    # register_from_disk: bool = False
    library: ClassVar[Catalog] = Catalog()
    
    """ Initialization Methods """
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not abc.ABC in cls.__bases__:
            try:
                name = cls.get_name()
            except AttributeError:
                name = sourdough.tools.snakify(cls.__name__)
            for item in cls.__mro__:    
                if Registry in item.__bases__:
                    item.library[name] = cls
                
    # def __init_subclass__(cls, **kwargs):
    #     super().__init_subclass__(**kwargs)
    #     # if cls.__mro__[1] == Registry:
    #     if Registry in cls.__bases__:
    #         cls._library_base = True
    #     try:
    #         name = cls.get_name()
    #     except AttributeError:
    #         name = sourdough.tools.snakify(cls.__name__)
    #     if not abc.ABC in cls.__bases__:
    #         for item in cls.__mro__:    
    #             try:
    #                 if item._library_base:
    #                     item.library[name] = cls
    #             except AttributeError:
    #                 pass

    # def __post_init__(self) -> None:
    #     """Initializes class instance attributes."""
    #     super().__post_init__()
    #     # Adds subclasses from disk to 'library' if 'register_from_disk'.
    #     if self.register_from_disk:
    #         self.find_subclasses(folder = pathlib.Path.cwd())

    # def find_subclasses(self, 
    #         folder: Union[str, pathlib.Path], 
    #         recursive: bool = True) -> None:
    #     """Adds Element subclasses for python files in 'folder'.
        
    #     If 'recursive' is True, subfolders are searched as well.
        
    #     Args:
    #         folder (Union[str, pathlib.Path]): folder to initiate search for 
    #             Element subclasses.
    #         recursive (bool]): whether to also search subfolders (True)
    #             or not (False). Defaults to True.
                
    #     """
    #     if recursive:
    #         glob_method = 'rglob'
    #     else:
    #         glob_method = 'glob'
    #     for file_path in getattr(pathlib.Path(folder), glob_method)('*.py'):
    #         if not file_path.name.startswith('__'):
    #             module = self._import_from_path(file_path = file_path)
    #             subclasses = self._get_subclasses(module = module)
    #             for subclass in subclasses:
    #                 self.add({
    #                     sourdough.tools.snakify(subclass.__name__): subclass})    
    #     return self
       
    # """ Private Methods """
    
    # def _import_from_path(self, file_path: Union[pathlib.Path, str]) -> object:
    #     """Returns an imported module from a file path.
        
    #     Args:
    #         file_path (Union[pathlib.Path, str]): path of a python module.
        
    #     Returns:
    #         object: an imported python module. 
        
    #     """
    #     # file_path = str(file_path)
    #     # file_path = pathlib.Path(file_path)
    #     print('test file path', file_path)
    #     module_spec = importlib.util.spec_from_file_location(file_path)
    #     print('test module_spec', module_spec)
    #     module = importlib.util.module_from_spec(module_spec)
    #     return module_spec.loader.exec_module(module)
    
    # def _get_subclasses(self, 
    #         module: object) -> Sequence[sourdough.base.Element]:
    #     """Returns a list of subclasses in 'module'.
        
    #     Args:
    #         module (object): an import python module.
        
    #     Returns:
    #         Sequence[Element]: list of subclasses of Element. If none are 
    #             found, an empty list is returned.
                
    #     """
    #     matches = []
    #     for item in pyclbr.readmodule(module):
    #         # Adds direct subclasses.
    #         if inspect.issubclass(item, sourdough.base.Element):
    #             matches.append[item]
    #         else:
    #             # Adds subclasses of other subclasses.
    #             for subclass in self.contents.values():
    #                 if subclass(item, subclass):
    #                     matches.append[item]
    #     return matches

   
@dataclasses.dataclass
class Repository(Options, abc.ABC):
    """ which stores subclass instances in a 'library' class attribute.

    In order to ensure that a subclass instance is added to the base 
    Catalog instance, super().__post_init__() should be called by 
    that subclass.

    Args:
        library (ClassVar[Catalog]): dict which stores subclass instances.
            
    Namespaces: 
        'library', 'register_from_disk', 'add_option', 'build'

    """
    library: ClassVar[Catalog] = Catalog()

    """ Initialization Methods """
    
    def __post_init__(self):
        """Registers an instance with 'library'."""
        # Calls initialization method of other inherited classes.
        try:
            super().__post_init__()
        except AttributeError:
            pass
        # Adds this instance to the 'library' class variable.
        self.library[self.name] = self


@dataclasses.dataclass
class Validator(abc.ABC):
    """Base class for type validation and/or conversion.
    
    Args:
        accepts (Union[Sequence[Any], Any]): type(s) accepted by the parent 
            class either as an individual item, in a Mapping, or in a Sequence.
        stores (Any): a single type stored by the parent class. Defaults to 
            None.
                        
    """
    accepts: Union[Sequence[Any], Any] = dataclasses.field(
        default_factory = list)
    stores: Any = None

    """ Initialization Methods """
    
    def __post_init__(self):
        """Registers an instance with 'library'."""
        # Calls initialization method of other inherited classes.
        try:
            super().__post_init__()
        except AttributeError:
            pass
        # Initializes 'contents' attribute.
        self._initial_validation()
        
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
       
    """ Private Methods """
    
    def _initial_validation(self) -> None:
        """Validates passed 'contents' on class initialization."""
        self.contents = self.convert(contents = self.contents)
        return self 
 

@dataclasses.dataclass
class Factory(abc.ABC):
    """Returns class(es) from options stored in 'options.library'.

    Args:
        product (Union[str, Sequence[str]]: name(s) of objects to return. 
            'product' must correspond to key(s) in 'options.library'.
        options (ClassVar[Options]): class which contains a 'library'.

    Raises:
        TypeError: if 'product' is neither a str nor Sequence of str.

    Returns:
        Any: the factory uses the '__new__' method to return a different object 
            product instance with kwargs as the parameters.

    """
    product: Union[str, Sequence[str]]
    options: ClassVar[Options] = Options

    """ Initialization Methods """
    
    def __new__(cls, product: Union[str, Sequence[str]], **kwargs) -> Any:
        """Returns an instance from 'options.library'.

        Args:
        product (Union[str, Sequence[str]]: name(s) of objects to return. 
            'product' must correspond to key(s) in 'options.library'.
            kwargs: parameters to pass to the object being created.

        Returns:
            Any: an instance of a Callable stored in 'options.library'.
        
        """
        return cls.options.build(key = product, **kwargs)
    
    """ Class Methods """
    
    @classmethod
    def add_option(cls, key: str, value: Any) -> None:
        """Adds 'value' to 'options.library' at 'key'.
        
        Args:
            key (str): name of key to link to 'value'.
            value (Any): item to store in 'options.library'.
            
        """
        cls.options.add_option(key = key, value = value)
        return cls
       
   
@dataclasses.dataclass
class ProxyMixin(abc.ABC):
    """ which creates a proxy name for a Element subclass attribute.

    The 'proxify' method dynamically creates a property to access the stored
    attribute. This allows class instances to customize names of stored
    attributes while still maintaining the interface of the base sourdough
    classes.

    Only one proxy should be created per class. Otherwise, the created proxy
    properties will all point to the same attribute.

    Namespaces: 'proxify', '_proxy_getter', '_proxy_setter', 
        '_proxy_deleter', '_proxify_attribute', '_proxify_method', the name of
        the proxy property set by the user with the 'proxify' method.
       
    To Do:
        Add property to class instead of instance to prevent return of property
            object.
        Implement '__set_name__' in a secondary class to simplify the code and
            namespace usage.
        
    """

    """ Public Methods """

    def proxify(self,
            proxy: str,
            attribute: str,
            default_value: Any = None,
            proxify_methods: bool = True) -> None:
        """Adds a proxy property to refer to class attribute.

        Args:
            proxy (str): name of proxy property to create.
            attribute (str): name of attribute to link the proxy property to.
            default_value (Any): default value to use when deleting 'attribute' 
                with '__delitem__'. Defaults to None.
            proxify_methods (bool): whether to create proxy methods replacing 
                'attribute' in the original method name with the string passed 
                in 'proxy'. So, for example, 'add_chapter' would become 
                'add_recipe' if 'proxy' was 'recipe' and 'attribute' was
                'chapter'. The original method remains as well as the proxy.
                This does not change the rest of the signature of the method so
                parameter names remain the same. Defaults to True.

        """
        self._proxied_attribute = attribute
        self._default_proxy_value = default_value
        self._proxify_attribute(proxy = proxy)
        if proxify_methods:
            self._proxify_methods(proxy = proxy)
        return self

    """ Proxy Property Methods """

    def _proxy_getter(self) -> Any:
        """Proxy getter for '_proxied_attribute'.

        Returns:
            Any: value stored at '_proxied_attribute'.

        """
        return getattr(self, self._proxied_attribute)

    def _proxy_setter(self, value: Any) -> None:
        """Proxy setter for '_proxied_attribute'.

        Args:
            value (Any): value to set attribute to.

        """
        setattr(self, self._proxied_attribute, value)
        return self

    def _proxy_deleter(self) -> None:
        """Proxy deleter for '_proxied_attribute'."""
        setattr(self, self._proxied_attribute, self._default_proxy_value)
        return self

    """ Other Private Methods """

    def _proxify_attribute(self, proxy: str) -> None:
        """Creates proxy property for '_proxied_attribute'.

        Args:
            proxy (str): name of proxy property to create.

        """
        setattr(self, proxy, property(
            fget = self._proxy_getter,
            fset = self._proxy_setter,
            fdel = self._proxy_deleter))
        return self

    def _proxify_methods(self, proxy: str) -> None:
        """Creates proxy method with an alternate name.

        Args:
            proxy (str): name of proxy to repalce in method names.

        """
        for item in dir(self):
            if (self._proxied_attribute in item
                    and not item.startswith('__')
                    and callable(item)):
                self.__dict__[item.replace(self._proxied_attribute, proxy)] = (
                    getattr(self, item))
        return self
 
 
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
            
 
""" 
Reflector is currently omitted from the sourdough build because I'm unsure
if it has a significant use case. The code below should still work, but it
isn't included in the uploaded package build. 
"""

# @dataclasses.dataclass
# class Reflector(Lexicon):
#     """Base class for a mirrored dictionary.

#     Reflector access methods search keys and values for corresponding
#     matched values and keys, respectively.

#     Args:
#         contents (Mapping[Any, Any]]): stored dictionary. Defaults to 
#             en empty dict.
              
#     """
#     contents: Mapping[Any, Any] = dataclasses.field(default_factory = dict)

#     def __post_init__(self) -> None:
#         """Creates 'reversed_contents' from passed 'contents'."""
#         self._create_reversed()
#         return self

#     """ Dunder Methods """

#     def __getitem__(self, key: str) -> Any:
#         """Returns match for 'key' in 'contents' or 'reversed_contents'.

#         Args:
#             key (str): name of key to find.

#         Returns:
#             Any: value stored in 'contents' or 'reversed_contents'.

#         Raises:
#             KeyError: if 'key' is neither found in 'contents' nor 
#                 'reversed_contents'.

#         """
#         try:
#             return self.contents[key]
#         except KeyError:
#             try:
#                 return self.reversed_contents[key]
#             except KeyError:
#                 raise KeyError(f'{key} is not in {self.__class__.__name__}')

#     def __setitem__(self, key: str, value: Any) -> None:
#         """Stores arguments in 'contents' and 'reversed_contents'.

#         Args:
#             key (str): name of key to set.
#             value (Any): value to be paired with key.

#         """
#         self.contents[key] = value
#         self.reversed_contents[value] = key
#         return self

#     def __delitem__(self, key: str) -> None:
#         """Deletes key in the 'contents' and 'reversed_contents' dictionaries.

#         Args:
#             key (str): name of key to delete.

#         """
#         try:
#             value = self.contents[key]
#             del self.contents[key]
#             del self.reversed_contents[value]
#         except KeyError:
#             try:
#                 value = self.reversed_contents[key]
#                 del self.reversed_contents[key]
#                 del self.contents[value]
#             except KeyError:
#                 pass
#         return self

#     """ Private Methods """

#     def _create_reversed(self) -> None:
#         """Creates 'reversed_contents' from 'contents'."""
#         self.reversed_contents = {
#             value: key for key, value in self.contents.items()}
#         return self


   