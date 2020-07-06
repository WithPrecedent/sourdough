"""
.. module:: dictionaries
:synopsis: sourdough dictionaries
:author: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import collections.abc
import dataclasses
import inspect
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union

import sourdough


@dataclasses.dataclass
class Lexicon(collections.abc.MutableMapping):
    """Base class for sourdough dictionaries.

    Lexicon and its subclasses can serve as drop in replacements for dicts with 
    added features.
    
    A Lexicon differs from a python dict in 3 ways:
        1) It includes an 'add' method which allows different datatypes to
            be passed and added to a Lexicon instance. All of the normal 
            dictionary methods are also available. 'add' is available to set
            default or more complex methods of adding elements to the stored
            dict.
        2) It includes a 'subsetify' method which will return a Lexicon or
            Lexicon subclass instance with only the key/value pairs matching
            keys in the 'subset' parameter.
        3) It allows the '+' operator to be used to join a Lexicon instance
            with another Lexicon instance, a python dictionary, or a
            sourdough Component. The '+' operator calls the Lexicon 'add'
            method to implement how the added item(s) is/are added to the
            Lexicon instance.
    
    Args:
        contents (Mapping[str, Any]]): stored dictionary. Defaults to 
            en empty dict.
              
    """
    contents: Mapping[str, Any] = dataclasses.field(default_factory = dict)

    """ Public Methods """
    
    def add(self, 
            items: Union[
                'sourdough.Component',
                Sequence['sourdough.Component'],
                Mapping[str, 'sourdough.Component']]) -> None:
        """Adds 'items' to 'contents'.
        
        Args:
            items (Union[sourdough.Component, Sequence[sourdough.Component],
                Mapping[str, sourdough.Component]]): Component(s) to add to
                'contents'.

        Raises:
            TypeError: if 'sourdough.Component' is not a Component subclass
            
        """
        if isinstance(items, Mapping):
            self.contents.update(items)
        elif isinstance(items, Sequence):
            for item in items:
                self._add_item(item = item)
        else:
            self._add_item(item = items)
        return self
        
    def subsetify(self, 
            subset: Union[str, Sequence[str]], 
            **kwargs) -> 'Lexicon':
        """Returns a new instance with a subset of 'contents'.

        Args:
            subset (Union[str, Sequence[str]]): key(s) for which key/value pairs 
                from 'contents' should be returned.
            kwargs: allows subclasses to send additional parameters to this 
                method.

        Returns:
            Lexicon: with only keys in 'subset'.

        """
        return self.__class__(
            contents = sourdough.tools.subsetify(
                dictionary = self.contents,
                subset = subset),
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

    def __add__(self, 
            other: Union[
                'sourdough.Component',
                Sequence['sourdough.Component'],
                Mapping[str, 'sourdough.Component']]) -> None:
        """Combines argument with 'contents'.

        Args:
            other (Union[sourdough.Component, Sequence[sourdough.Component],
                Mapping[str, sourdough.Component]]): Component(s) to add to
                'contents'.

        """
        self.add(contents = other)
        return self

    def __repr__(self) -> str:
        """Returns '__str__' representation.

        Returns:
            str: default string representation of an instance.

        """
        return self.__str__()

    def __str__(self) -> str:
        """Returns default string representation of an instance.

        Returns:
            str: default string representation of an instance.

        """
        return (
            f'sourdough {self.__class__.__name__}\n'
            f'contents: {self.contents.__str__()}')   

    """ Private Methods """
    
    def _add_item(self, item: 'sourdough.Component') -> None:
        """[summary]

        Args:
            item (sourdough.Component): [description]

        Returns:
            [type]: [description]
            
        """
        if inspect.isclass(item):
            self.contents[sourdough.tools.snakify(item.__name__)] = item
        elif hasattr(self, 'name'):
            self.contents[item.name] = item
        else:
            self.contents[
                sourdough.tools.snakify(item.__class__.__name__)] = item            
        return self    


@dataclasses.dataclass
class Catalog(Lexicon):
    """Base class for a wildcard and list-accepting dictionary.

    A Catalog inherits the differences between a Lexicon and an ordinary python
    dict.

    A Catalog differs from a Lexicon in 5 ways:
        1) It recognizes an 'all' key which will return a list of all values
            stored in a Catalog instance.
        2) It recognizes a 'default' key which will return all values matching
            keys listed in the 'defaults' attribute. 'default' can also be set
            using the 'catalog['default'] = new_default' assignment. If 
            'defaults' is not passed when the instance is initialized, the 
            initial value of 'defaults' is 'all'
        3) It recognizes a 'none' key which will return an empty list.
        4) It supports a list of keys being accessed with the matching
            values returned. For example, 'catalog[['first_key', 'second_key']]' 
            will return the values for those keys in a list.
        5) If a single key is sought, a Catalog can either return the stored
            value or a stored value in a list (if 'always_return_list' is
            True). The latter option is available to make iteration easier
            when the iterator assumes a single datatype will be returned.

    Args:
        contents (Mapping[str, Any]]): stored dictionary. Defaults to 
            an empty dict.
        defaults (Sequence[str]]): a list of keys in 'contents' which
            will be used to return items when 'default' is sought. If not
            passed, 'default' will be set to all keys.
        always_return_list (bool]): whether to return a list even when
            the key passed is not a list or special access key (True) or to 
            return a list only when a list or special acces key is used (False). 
            Defaults to False.

    """
    contents: Mapping[str, Any] = dataclasses.field(default_factory = dict)    
    defaults: Sequence[str] = dataclasses.field(default_factory = list)
    always_return_list: bool = False

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Sets 'default' to all keys of 'contents', if not passed.
        self.defaults = self.defaults or 'all'
        return self

    """ Public Methods """
    
    def create(self, key: str, **kwargs) -> 'sourdough.Component':
        """Returns an instance of a stored subclass or instance.
        
        This method acts as a factory for instancing stored classes or returning
        instances.
        
        Args:
            key (str): key to desired Component in 'contents'.
            kwargs: arguments to pass to the selected Component when it is
                instanced.
                    
        Returns:
            sourdough.Component: that has been instanced with kwargs as 
                arguments if it was a stored class. Otherwise, the instance
                is returned as it was stored.
            
        """
        try:
            return self.contents[key](**kwargs)
        except TypeError:
            return self.contents[key] 
    
    def subsetify(self, subset: Union[str, Sequence[str]]) -> 'Catalog':
        """Returns a subset of 'contents'.

        Args:
            subset (Union[str, Sequence[str]]): key(s) to get key/value pairs 
                from 'contents'.

        Returns:
            Catalog: with only keys in 'subset'.

        """
        return super().subsetify(
            contents = self.contents,
            defaults = self.defaults,
            always_return_list = self.always_return_list)

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
        if key in ['default', ['default']]:
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

    def __str__(self) -> str:
        """Returns default string representation of an instance.

        Returns:
            str: default string representation of an instance.

        """
        return (
            f'sourdough {self.__class__.__name__}\n'
            f'contents: {self.contents.__str__()}\n'
            f'defaults: {self.defaults.__str__()}')


@dataclasses.dataclass
class MirrorDictionary(Lexicon):
    """Base class for a mirrored dictionary.

    MirrorDictionary access methods search keys and values for corresponding
    matched values and keys, respectively.

    Args:
        contents (Mapping[str, Any]]): stored dictionary. Defaults to 
            en empty dict.
              
    """
    contents: Mapping[str, Any] = dataclasses.field(default_factory = dict)

    def __post_init__(self) -> None:
        """Creates 'reversed_contents' from passed 'contents'."""
        self._create_reversed()
        return self

    """ Dunder Methods """

    def __getitem__(self, key: str) -> Any:
        """Returns match for 'key' in 'contents' or 'reversed_contents'.

        Args:
            key (str): name of key to find.

        Returns:
            Any: value stored in 'contents' or 'reversed_contents'.

        Raises:
            KeyError: if 'key' is neither found in 'contents' nor 
                'reversed_contents'.

        """
        try:
            return self.contents[key]
        except KeyError:
            try:
                return self.reversed_contents[key]
            except KeyError:
                raise KeyError(f'{key} is not in {self.__class__.__name__}')

    def __setitem__(self, key: str, value: Any) -> None:
        """Stores arguments in 'contents' and 'reversed_contents'.

        Args:
            key (str): name of key to set.
            value (Any): value to be paired with key.

        """
        self.contents[key] = value
        self.reversed_contents[value] = key
        return self

    def __delitem__(self, key: str) -> None:
        """Deletes key in the 'contents' and 'reversed_contents' dictionaries.

        Args:
            key (str): name of key to delete.

        """
        try:
            value = self.contents[key]
            del self.contents[key]
            del self.reversed_contents[value]
        except KeyError:
            try:
                value = self.reversed_contents[key]
                del self.reversed_contents[key]
                del self.contents[value]
            except KeyError:
                pass
        return self

    """ Private Methods """

    def _create_reversed(self) -> None:
        """Creates 'reversed_contents'."""
        self.reversed_contents = {
            value: key for key, value in self.contents.items()}
        return self
