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
from typing import Any, ClassVar, Iterable, Mapping, Sequence, Tuple, Union

import sourdough


@dataclasses.dataclass
class Lexicon(collections.abc.MutableMapping):
    """Base class for sourdough dictionaries.
    
    A Lexicon differs from a python dict in 3 ways:
        1) It includes an 'add' method which allows different datatypes to
            be passed and added to a Lexicon instance.
        2) It includes a 'subsetify' method which will return a Lexicon or
            Lexicon subclass instance with only the key/value pairs listed
            in the 'subset' parameter.
        3) It allows the '+' operator to be used to join a Lexicon instance
            with another Lexicon instance, a python dictionary, or a
            sourdough Component. The '+' operator calls the Lexicon 'add'
            method to implement how the added item(s) is/are added to the
            Lexicon instance.
    
    Args:
        contents (Optional[Mapping[str, Any]]): stored dictionary. Defaults to 
            en empty dict.
              
    """
    contents: Optional[Mapping[str, Any]] = dataclasses.field(
        default_factory = dict)

    """ Public Methods """

    def add(self, 
            contents: Union[Mapping[str, Any], 'sourdough.Component']) -> None:
        """Combines arguments with 'contents'.

        Args:
            contents (Union[Mapping[str, Any], sourdough.Component]): a
                Mapping or sourdough Component to add to the 'contents' 
                attribute.
                
        Raises:
            TypeError: if 'contents' is not a Mapping, Component, or class.

        """
        if hasattr(contents, 'name'):
            self.contents[contents.name] = contents
        elif isinstance(contents, collections.abc.Mapping):
            self.contents.update(contents)
        elif inspect.isclass(contents):
            self.contents[
                sourdough.utilities.snakify(contents.__name__)] = contents
        else:
            raise TypeError('contents must be dict or Component type')
        return self
    
    def subsetify(self, 
            subset: Union[str, Sequence[str]], **kwargs) -> 'Lexicon':
        """Returns a subset of 'contents'.

        Args:
            subset (Union[str, Sequence[str]]): key(s) for which key/value pairs 
                from 'contents' should be returned.
            kwargs: allows subclasses to send additional parameters to this 
                method.

        Returns:
            Lexicon: with only keys in 'subset'.

        """
        return self.__class__(
            contents = sourdough.utilities.subsetify(
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
            other: Union[Mapping[str, Any], 'sourdough.Component']) -> None:
        """Combines argument with 'contents'.

        Args:
            contents (Union[Mapping[str, Any], sourdough.Component]): a
                Mapping or sourdough Component to add to the 'contents' 
                attribute.

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
            initial value of 'defaults' is set to all keys.
        3) It recognizes a 'none' key which will return an empty list.
        4) Catalog supports a list of keys being accessed with the matching
            values returned. 
        5) If a single key is sought, a Catalog can either return the stored
            value or a stored value in a list (if 'always_return_list' is
            True). The latter option is available to make iteration easier
            when a single datatype returned is presumed.

    Args:
        contents (Optional[Mapping[str, Any]]): stored dictionary. Defaults to 
            en empty dict.
        defaults (Optional[Sequence[str]]): a list of keys in 'contents' which
            will be used to return items when 'default' is sought. If not
            passed, 'default' will be set to all keys.
        always_return_list (Optional[bool]): whether to return a list even when
            the key passed is not a list (True) or to return a list in all cases
            (False). Defaults to False.

    """
    contents: Optional[Mapping[str, Any]] = dataclasses.field(
        default_factory = dict)    
    defaults: Optional[Sequence[str]] = dataclasses.field(
        default_factory = list)
    always_return_list: Optional[bool] = False

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Sets 'default' to all keys of 'contents', if not passed.
        self.defaults = self.defaults or list(self.contents.keys())
        return self

    """ Public Methods """

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
            name = self.name,
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
        elif key in ['default', ['default']]:
            return list({k: self.contents[k] for k in self.defaults}.values())
        # Returns an empty list if a null value is sought.
        elif key in ['none', ['none'], 'None', ['None'], '', ['']]:
            return []
        else:
            if isinstance(key, list):
                return [self.contents[k] for k in key if k in self.contents]
            else:
                try:
                    if self.always_return_list:
                        return [self.contents[key]]
                    else:
                        return self.contents[key]
                except KeyError:
                    raise KeyError(f'{key} is not in {self.name}')

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

    def __str__(self) -> str:
        """Returns default dictionary string representation of an instance.

        Returns:
            str: default dictionary string representation of an instance.

        """
        return (
            f'sourdough {self.__class__.__name__}\n'
            f'contents: {self.contents.__str__()}\n'
            f'defaults: {self.defaults.__str__()}')
