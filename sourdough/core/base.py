"""
base: sourdough base class for composite objects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Element: abstract base class for sourdough objects that are part of 
        composite structures.
    Elemental: annotation type for all classes that contain Elements.

"""
from __future__ import annotations
import abc
import collections.abc
import dataclasses
import inspect
# import pathlib
# import pyclbr
import pprint
import textwrap
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union

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


Elemental = Union['Element', Mapping[str, 'Element'], Sequence['Element']]


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
                sourdough.Element.
            kwargs: allows subclasses to send additional parameters to this 
                method.
                
        """
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
class Factory(abc.ABC):
    """Instances a class from available Callables stored in 'options'.

    Args:
        products (Union[str, Sequence[str]]: name(s) of objects to return. 
            'products' must correspond to key(s) in 'options'.
        options (Mapping[str, Callable]): a dict of available options for object 
            creation. Defaults to an empty dict.

    Raises:
        TypeError: if 'products' is neither a str nor Sequence of str.

    Returns:
        Any: the factory uses the '__new__' method to return a different object 
            product instance with kwargs as the parameters.

    """
    products: Union[str, Sequence[str]]
    options: ClassVar[Mapping[str, Any]] = {}

    """ Initialization Methods """
    
    def __new__(cls, products: str, **kwargs) -> Any:
        """Returns an instance from 'options'.

        Args:
            products (str): name of sourdough products(s) to return. 'products' 
                must correspond to key(s) in 'options'.
            kwargs: parameters to pass to the object being created.

        Returns:
            Any: an instance of a Callable stored in 'options'.
        
        """
        if isinstance(products, str):
            return cls.options[products](**kwargs)
        elif isinstance(products, Sequence):
            instances = []
            for match in cls.options[products]:
                instances.append(match(**kwargs))
            return instances
        else:
            raise TypeError('products must be a str or list type')
    
    """ Class Methods """
    
    @classmethod
    def add(cls, key: str, value: Any) -> None:
        """Adds 'option' to 'options' at 'key'.
        
        Args:
            key (str): name of key to link to 'value'.
            value (Any): object to store in 'options'.
            
        """
        cls.options[key] = value
        return cls
    

@dataclasses.dataclass
class Validator(Factory, abc.ABC):
    """Factory for type validation and/or conversion class construction.
    
    Validator is primary used to convert Element subclasses to and from single
    instances, Mappings of instances, and Sequences of instances. However, with
    additional conversion methods, it can be extended to any validation or 
    converstion task.
    
    Args:
        accepts (Union[Sequence[Callable], Callable]): type(s) accepted by the
            parent class.
        stores (Callable): a single type accepted by the parent class. Defaults 
            to None. If it is set to none, then an instance is only useful for 
            validation and does not convert types.
            
    """
    products: Union[str, Sequence[str]]
    accepts: Union[Sequence[Callable], Callable] = dataclasses.field(
        default_factory = list)
    stores: Callable = None
    options: ClassVar[Catalog] = Catalog()


@dataclasses.dataclass
class ValidatorBase(abc.ABC):
    """Base class for type validation and/or conversion.
    
    Args:
        accepts (Union[Sequence[Callable], Callable]): type(s) accepted by the
            parent class.
        stores (Callable): a single type accepted by the parent class. Defaults 
            to None. If it is set to none, then an instance is only useful for 
            validation and does not convert types.
            
    """
    accepts: Union[Sequence[Callable], Callable] = dataclasses.field(
        default_factory = list)
    stores: Callable = None
            
    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def verify(self, contents: Any) -> Any:
        pass
    
    @abc.abstractmethod
    def convert(self, contents: Any) -> Any:
        pass   
    