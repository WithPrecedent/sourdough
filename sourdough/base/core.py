"""
elements: sourdough core base classes
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Element: abstract base class for core sourdough objects.
    Action (Element): abstract base class for storing action methods. Action 
        subclasses must have a 'perform' method.
    Lexicon (Element, MutableMapping): sourdough drop-in replacement for dict
        with additional functionality.
    Catalog (Lexicon): list and wildcard accepting dict replacement with a 
        'create' method for instancing and/or validating stored objects.
    Slate (Element, MutableSequence): sourdough drop-in replacement for list
        with additional functionality.
    Hybrid (Slate): iterable containing Element subclass instances with both 
        dict and list interfaces and methods.

"""
from __future__ import annotations
import abc
import collections.abc
import copy
import dataclasses
import inspect
import more_itertools
import textwrap
from typing import (Any, Callable, ClassVar, Container, Generic, Iterable, 
                    Iterator, Mapping, Sequence, Tuple, TypeVar, Union)

import sourdough


@dataclasses.dataclass
class Element(abc.ABC):
    """Base class for core sourdough objects.

    A Element has a 'name' attribute for internal referencing and to allow 
    sourdough iterables to function propertly. Element instances can be used 
    to create a variety of tree data designs such as trees and graphs. 

    The mixins included with sourdough are all compatible, individually and
    collectively, with Element and its subclasses.

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Element is called, 'name' is set based upon
            the 'get_name' method in Element. If that method is not 
            overridden by a subclass instance, 'name' will be assigned to the 
            snake case version of the class name ('__class__.__name__').
    
    """
    name: str = None

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Sets 'name' to the default value if it is not passed.
        self.name = self.get_name()

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
        if inspect.isclass(cls):
            return sourdough.utilities.snakify(cls.__name__)
        elif cls.name is None:
            return sourdough.utilities.snakify(cls.__class__.__name__)
        else:
            return cls.name

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


@dataclasses.dataclass
class Action(Element, abc.ABC):
    """Base class for performing actions on other objects in sourdough.
    
    All Action subclasses must have 'perform' methods.
    
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Element is called, 'name' is set based upon
            the 'get_name' method in Element. If that method is not 
            overridden by a subclass instance, 'name' will be assigned to the 
            snake case version of the class name ('__class__.__name__').
    
    """
    name: str = None
    
    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def perform(self, item: object = None, **kwargs) -> object:
        """Performs some action, possibly related to passed 'item'.
        
        Subclasses must provide their own methods.
        
        """
        pass
    

@dataclasses.dataclass
class Lexicon(Element, collections.abc.MutableMapping):
    """Basic sourdough dict replacement.

    Lexicon subclasses can serve as drop in replacements for dicts with added
    features.
    
    A Lexicon differs from a python dict in 4 significant ways:
        1) It includes a 'name' attribute which is used for internal referencing
            in sourdough. This is inherited from Element.
        2) It includes an 'add' method which allows different datatypes to
            be passed and added to a Lexicon instance. All of the normal dict 
            methods are also available. 'add' should be used to set default or 
            more complex methods of adding elements to the stored dict.
        3) It uses a 'validate' method to validate or convert the passed 
            'contents' argument. It will convert all supported datatypes to 
            a dict. The 'validate' method is automatically called when a
            Lexicon is instanced and when the 'add' method is called.
        4) It includes a 'subsetify' method which will return a Lexicon or
            Lexicon subclass instance with only the key/value pairs matching
            keys in the 'subset' argument.
        5) It allows the '+' operator to be used to join a Lexicon instance
            with another Lexicon instance or another Mapping. The '+' operator 
            calls the Lexicon 'add' method to implement how the added item(s) 
            is/are added to the Lexicon instance.
    
    Args:
        contents (Mapping[Any, Any]]): stored dictionary. Defaults to an empty 
            dict.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Element is called, 'name' is set based upon
            the 'get_name' method in Element. If that method is not 
            overridden by a subclass instance, 'name' will be assigned to the 
            snake case version of the class name ('__class__.__name__').
              
    """
    contents: Mapping[Any, Any] = dataclasses.field(default_factory = dict)
    name: str = None
      
    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent initialization method(s).
        super().__post_init__()    
        # Validates 'contents' or converts it to appropriate iterable.
        self._initial_validation()  
        
    """ Public Methods """
    
    def validate(self, contents: Any) -> Mapping[Any, Any]:
        """Validates 'contents' or converts 'contents' to a dict.
        
        This method simply confirms that 'contents' is a Mapping. Subclasses
        should overwrite this method to support more datatypes and implement
        any type conversion techniques that are necessary.
        
        Args:
            contents (Any): variable to validate as compatible with an instance.
            
        Raises:
            TypeError: if 'contents' argument is not of a supported datatype.
            
        Returns:
            Mapping[Any, Any]: validated or converted argument that is 
                compatible with an instance.
        
        """
        if isinstance(contents, Mapping):
            return contents
        else:
            raise TypeError('contents must be a dict type')
     
    def add(self, contents: Mapping[Any, Any], **kwargs) -> None:
        """Adds 'contents' to the 'contents' attribute.
        
        Args:
            contents (Mapping[Any, Any]): items to add to 'contents' attribute.
                Element.
            kwargs: allows subclasses to send additional parameters to this 
                method.
                
        """
        contents = self.validate(contents = contents)
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
        subset = sourdough.utilities.listify(subset)
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

    """ Private Methods """
    
    def _initial_validation(self) -> None:
        """Validates passed 'contents' on class initialization."""
        new_contents = copy.deepcopy(self.contents)
        new_contents = self.validate(contents = new_contents)
        self.contents = {}
        self.add(contents = new_contents)
        return self
    

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
        contents (Mapping[Any, Any]]): stored dictionary. Defaults to an empty 
            dict.
        defaults (Sequence[str]]): a list of keys in 'contents' which will be 
            used to return items when 'default' is sought. If not passed, 
            'default' will be set to all keys.
        always_return_list (bool]): whether to return a list even when
            the key passed is not a list or special access key (True) or to 
            return a list only when a list or special acces key is used (False). 
            Defaults to False.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Element is called, 'name' is set based upon
            the 'get_name' method in Element. If that method is not 
            overridden by a subclass instance, 'name' will be assigned to the 
            snake case version of the class name ('__class__.__name__').  
                     
    """
    contents: Mapping[Any, Any] = dataclasses.field(default_factory = dict)  
    defaults: Sequence[str] = dataclasses.field(default_factory = list)
    always_return_list: bool = False
    name: str = None
    
    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent initialization method(s).
        super().__post_init__()
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
            **kwargs) -> 'Catalog':
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
            self.defaults = sourdough.utilities.listify(value)
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
            for i in self.contents if i not in sourdough.utilities.listify(key)}
        return self

        
@dataclasses.dataclass
class Slate(Element, collections.abc.MutableSequence):
    """Basic sourdough list replacement.
    
    A Slate differs from a python list in 3 significant ways:
        1) It includes a 'name' attribute which is used for internal referencing
            in sourdough. This is inherited from Element.
        2) It includes an 'add' method which allows different datatypes to be 
            passed and added to the 'contents' of a Slate instance. 
        3) It uses a 'validate' method to validate or convert the passed 
            'contents' argument. It will convert all supported datatypes to 
            a list. The 'validate' method is automatically called when a
            Slate is instanced and when the 'add' method is called.

    Args:
        contents (Sequence[Any]): items to store in a list. Defaults to an empty 
            list.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Element is called, 'name' is set based upon
            the '_get_name' method in Element. If that method is not 
            overridden by a subclass instance, 'name' will be assigned to the 
            snake case version of the class name ('__class__.__name__').
        
    """
    contents: Sequence[Any] = dataclasses.field(default_factory = list)
    name: str = None
  
    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent initialization method(s).
        super().__post_init__()        
        # Validates 'contents' or converts it to appropriate iterable.
        self._initial_validation()  
    
    """ Public Methods """
    
    def validate(self, contents: Sequence[Any]) -> Sequence[Any]:
        """Validates 'contents' or converts 'contents' to proper type.
        
        Args:
            contents (Sequence[Any]): items to validate or convert to a list.
            
        Raises:
            TypeError: if 'contents' argument is not of a supported datatype.
            
        Returns:
            Sequence[Any]: validated or converted argument that is compatible 
                with an instance.
        
        """
        if isinstance(contents, Sequence):
            return contents
        else:
            raise TypeError('contents must be a list')

    def add(self, contents: Sequence[Any]) -> None:
        """Extends 'contents' argument to 'contents' attribute.
        
        Args:
            contents (Sequence[Any]): items to add to the 'contents' attribute.

        """
        contents = self.validate(contents = contents)
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

    """ Private Methods """
    
    def _initial_validation(self) -> None:
        """Validates passed 'contents' on class initialization."""
        new_contents = copy.deepcopy(self.contents)
        new_contents = self.validate(contents = new_contents)
        self.contents = []
        self.add(contents = new_contents)
        return self
    
    
@dataclasses.dataclass
class Hybrid(Slate):
    """Base class for ordered iterables in sourdough.
    
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
        contents (Union[Element, Mapping[Any, Element], Sequence[Element]]): 
            Element subclasses or Element subclass instances to store in a list. 
            If a dict is passed, the keys will be ignored and only the values 
            will be added to 'contents'. Defaults to an empty list.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Element is called, 'name' is set based upon
            the '_get_name' method in Element. If that method is not 
            overridden by a subclass instance, 'name' will be assigned to the 
            snake case version of the class name ('__class__.__name__').
        
    """
    contents: Union[
        Element,
        Mapping[Any, Element], 
        Sequence[Element]] = dataclasses.field(default_factory = list)
    name: str = None
    
    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent initialization method(s).
        super().__post_init__()        
        # Sets initial default value for the 'get' method.
        self._default = None
        
    """ Public Methods """
    
    def validate(self, 
            contents: Union[
                Element,
                Mapping[Any, Element], 
                Sequence[Element]]) -> Sequence[Element]:
        """Validates 'contents' or converts 'contents' to proper type.
        
        Args:
            contents (Union[Element, Mapping[Any, Element], Sequence[Element]]): 
                items to validate or convert to a list of Element instances.
            
        Raises:
            TypeError: if 'contents' argument is not of a supported datatype.
            
        Returns:
            Sequence[Element]: validated or converted argument that is 
                compatible with an instance.
        
        """
        if (isinstance(contents, Element) or 
                (inspect.isclass(contents) 
                    and issubclass(contents, Element))):
            if isinstance(contents, Sequence):
                return contents
            else:
                return [contents]
        elif (isinstance(contents, Sequence) 
            and (all(isinstance(c, Element) for c in contents)
                or (all(inspect.isclass(c) for c in contents)
                    and all(issubclass(c, Element) for c in contents)))):
            return contents
        elif (isinstance(contents, Mapping)
            and (all(isinstance(c, Element) for c in contents.values())
                or (all(inspect.isclass(c) for c in contents.values())
                    and all(
                        issubclass(c, Element) for c in contents.values())))):
            return list(contents.values())
        else:
            raise TypeError(
                'contents must be a list of Elements, dict with Element values,'
                'or Element type')

    def add(self, 
            contents: Union[
                Element,
                Mapping[Any, Element], 
                Sequence[Element]]) -> None:
        """Extends 'contents' argument to 'contents' attribute.
        
        Args:
            contents (Union[Element, Mapping[Any, Element], Sequence[Element]]): 
                Element instance(s) to add to the 'contents' attribute.

        """
        contents = self.validate(contents = contents)
        self.contents.extend(contents)
        return self    

    def append(self, 
            contents: Union[
                Element,
                Mapping[Any, Element], 
                Sequence[Element]]) -> None:
        """Appends 'element' to 'contents'.
        
        Args:
            contents (Union[Element, Mapping[Any, Element], 
                Sequence[Element]]): Element instance(s) to add to the
                'contents' attribute.

        Raises:
            TypeError: if 'element' does not have a name attribute.
            
        """
        contents = self.validate(contents = contents)
        if (isinstance(contents, Sequence)
                and not isinstance(contents, Element)):
            contents = self.__class__(contents)
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
   
    def extend(self, 
            contents: Union[
                Element,
                Mapping[Any, Element], 
                Sequence[Element]]) -> None:
        """Extends 'element' to 'contents'.
        
        Args:
            contents (Union[Element, Mapping[Any, Element], 
                Sequence[Element]]): Element instance(s) to add to the
                'contents' attribute.

        Raises:
            TypeError: if 'element' does not have a name attribute.
            
        """
        contents = self.validate(contents = contents)
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
            matches.extend(sourdough.utilities.listify(tool(item, **kwargs)))
            if isinstance(item, sourdough.Hybrid):
                if recursive:
                    matches.extend(item.find(
                        tool = tool, 
                        recursive = True,
                        matches = matches, 
                        **kwargs))
        return matches
    
    def get(self, 
            key: Union[str, int]) -> Union[
                Element, 
                Sequence[Element]]:
        """Returns value(s) in 'contents' or value in '_default' attribute.
        
        Args:
            key (Union[str, int]): index or stored Element name to get from
                'contents'.
                
        Returns:
            Union[Element, Sequence[Element]]: items in 'contents' or 
                value in '_default' attribute. 
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

    def items(self) -> Tuple[str, Element]:
        """Emulates python dict 'items' method.
        
        Returns:
            Tuple[str, Element]: tuple of Element names and Elements.
            
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

    def pop(self, 
            key: Union[str, int]) -> Union[
                Element, 
                Sequence[Element]]:
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
     
    def subsetify(self, subset: Union[str, Sequence[str]]) -> 'Hybrid':
        """Returns a subset of 'contents'.

        Args:
            subset (Union[str, Sequence[str]]): key(s) to get Element 
                instances with matching 'name' attributes from 'contents'.

        Returns:
            Worker: with only items with 'name' attributes in 'subset'.

        """
        subset = sourdough.utilities.listify(subset)
        try:
            return self.__class__(
                name = self.name,
                contents = [c for c in self.contents if c.name in subset])  
        except AttributeError:            
            return self.__class__(
                name = self.name,
                contents = [c for c in self.contents if c.get_name() in subset])    
     
    def update(self, 
            contents: Union[
                Mapping[Any, Element], 
                Sequence[Element]]) -> None:
        """Mimics the dict 'update' method by appending 'contents'.
        
        Args:
            contents (Union[Mapping[Any, Element], Sequence[Element]]): 
                Element instances to add to the 'contents' attribute. If a 
                Mapping is passed, the values are added to 'contents' and the
                keys become the 'name' attributes of those avalues. To mimic 
                'update', the passed 'elements' are added to 'contents' by the 
                'extend' method.
 
        Raises:
            TypeError: if any of 'elements' do not have a name attribute or
                if 'elements is not a dict.               
        
        """
        if isinstance(contents, Mapping):
            for key, value in contents.items():
                new_element = value
                new_element.name = key
                self.extend(contents = new_element)
        elif all(isinstance(c, Element) for c in contents):
            self.extend(contents = contents)
        else:
            raise TypeError(
                'elements must be a dict or list containing Elements')
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

""" 
Factory is currently omitted from the sourdough build because its design doesn't
presently fit with the sourdough workflow. However, the code should still work.
"""

# @dataclasses.dataclass
# class Factory(Element, abc.ABC):
#     """The Factory interface instances a class from available options.

#     Args:
#         element (Union[str, Sequence[str]]: name of sourdough element(s) to 
#             return. 'element' must correspond to key(s) in 'options'. Defaults 
#             to None.
#         options (ClassVar[sourdough.Catalog]): a dict of available options 
#             for object creation. Defaults to an empty Catalog instance.

#     Raises:
#         TypeError: if 'element' is neither a str nor Sequence of str.

#     Returns:
#         Any: the factory uses the '__new__' method to return a different object 
#             product instance with kwargs as the parameters.

#     """
#     element: Union[str, Sequence[str]] = None
#     options: ClassVar['Catalog'] = Catalog()
#     name: str = None

#     """ Initialization Methods """
    
#     def __new__(cls, element: str = None, **kwargs) -> Any:
#         """Returns an instance from 'options'.

#         Args:
#             element (str): name of sourdough element(s) to return. 
#                 'element' must correspond to key(s) in 'options'. Defaults to 
#                 None.
#             kwargs (MutableMapping[Any, Any]): parameters to pass to the object 
#                 being created.

#         Returns:
#             Any: an instance of an object stored in 'options'.
        
#         """
#         if isinstance(element, str):
#             return cls.options[element](**kwargs)
#         elif isinstance(element, Sequence):
#             instances = []
#             for match in cls.options[element]:
#                 instances.append(match(**kwargs))
#             return instances
#         else:
#             raise TypeError('element must be a str or list type')
    
#     """ Class Methods """
    
#     @classmethod
#     def add(cls, key: str, option: Any) -> None:
#         """Adds 'option' to 'options' at 'key'.
        
#         Args:
#             key (str): name of key to link to 'option'.
#             option (Any): object to store in 'options'.
            
#         """
#         cls.options[key] = option
#         return cls
   