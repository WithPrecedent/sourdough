"""
.. module:: repository
:synopsis: option storage made simple
:author: Corey Rayburn Yung
:copyright: 2019-2020
:license: Apache-2.0
"""

import collections.abc
import dataclasses
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Union

import sourdough


@dataclasses.dataclass
class Repository(sourdough.Component, collections.abc.MutableMapping):
    """Base class for wilcard-accepting dictionary.

    If a wildcard key or list of keys is sought using '__getitem__', a list of
    values is returned. If a string is sought a string is returned unless
    'always_return_list' is set to True.

    Args:
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. If the class instance
            needs settings from the shared Settings instance, 'name' should
            match the appropriate section name in that Settings instance. When
            subclassing, it is a good settings to use the same 'name' attribute
            as the base class for effective coordination between sourdough
            classes. Defaults to None or __class__.__name__.lower().
        contents (Optional[Dict[str, Any]]): stored dictionary. Defaults to an
            empty dictionary.
        defaults (Optional[List[str]]): a list of keys in 'contents' which
            will be used to return items when 'default' is sought. If not
            passed, 'default' will be set to all keys.
        always_return_list (Optional[bool]): whether to return a list even when
            the key passed is not a list (True) or to return a list in all cases
            (False). Defaults to False.

    """
    name: Optional[str] = None
    contents: Optional[Dict[str, Any]] = dataclasses.field(
        default_factory = dict)
    defaults: Optional[List[str]] = dataclasses.field(default_factory = list)
    always_return_list: Optional[bool] = False

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Sets 'name' to the default value if it is not passed.
        super().__post_init__()
        # Stores nested dictionaries as Repository instances.
        self.contents = self._nestify(contents = self.contents)
        # Sets 'default' to all keys of 'contents', if not passed.
        self.defaults = self.defaults or list(self.contents.keys())
        return self

    """ Public Methods """

    def add(self, contents: Union[Repository, Dict[str, Any]]) -> None:
        """Combines arguments with 'contents'.

        Args:
            contents (Union[Repository, Dict[str, Any]]): another
                Repository instance/subclass or a compatible dictionary.

        """
        self.contents.update(contents)
        self.contents = self._nestify(contents = self.contents)
        return self

    def subset(self, subset: Union[Any, List[Any]]) -> Repository:
        """Returns a subset of 'contents'.

        Args:
            subset (Union[Any, List[Any]]): key(s) to get key/value pairs from
                'dictionary'.

        Returns:
            Repository: with only keys in 'subset'.

        """
        return self.__class__(
            name = name,
            contents = sourdough.utilities.subsetify(
                dictionary = self.contents,
                subset = subset),
            defaults = self.defaults)

    """ Required ABC Methods """

    def __getitem__(self, key: Union[List[str], str]) -> Union[List[Any], Any]:
        """Returns value(s) for 'key' in 'contents'.

        The method searches for 'all', 'default', and 'none' matching wildcard
        options before searching for direct matches in 'contents'.

        Args:
            key (Union[List[str], str]): name(s) of key(s) in 'contents'.

        Returns:
            Union[List[Any], Any]: value(s) stored in 'contents'.

        """
        # Returns a list of all values if the 'all' key is sought.
        if key in ['all', ['all']]:
            return list(self.contents.values())
        # Returns a list of values for keys listed in 'defaults' attribute.
        elif key in ['default', ['default']]:
            return list({k: self.contents[k] for k in self.defaults}.values())
        # Returns an empty list if a null value is sought.
        elif key in ['none', ['none'], '', ['']]:
            return []
        else:
            if isinstance(key, list):
                try:
                    return [self.contents[k] for k in key if k in self.contents]
                except KeyError:
                    raise KeyError(f'{key} is not in {self.name}')
            else:
                try:
                    if self.always_return_list:
                        return [self.contents[key]]
                    else:
                        return self.contents[key]
                except KeyError:
                    raise KeyError(f'{key} is not in {self.name}')

    def __setitem__(self,
            key: Union[List[str], str],
            value: Union[List[Any], Any]) -> None:
        """Sets 'key' in 'contents' to 'value'.

        Args:
            key (Union[List[str], str]): name of key(s) to set in 'contents'.
            value (Union[List[Any], Any]): value(s) to be paired with 'key' in
                'contents'.

        """
        if key in ['default', ['default']]:
            self.defaults = value
        else:
            try:
                self.contents[key] = value
            except TypeError:
                self.contents.update(dict(zip(key, value)))
        return self

    def __delitem__(self, key: Union[List[str], str]) -> None:
        """Deletes 'key' in 'contents'.

        Args:
            key (Union[List[str], str]): name(s) of key(s) in 'contents' to
                delete the key/value pair.

        """
        self.contents = {
            i: self.contents[i]
            for i in self.contents if i not in sourdough.utilities.listify(key)}
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
            Integer: length of 'contents'.

        """
        return len(self.contents)

    """ Other Dunder Methods """

    def __add__(self,
            other: Union[Repository, Dict[str, Any]]) -> None:
        """Combines argument with 'contents'.

        Args:
            other (Union[Repository, Dict[str, Any]]): another
                Repository instance or compatible dictionary.

        """
        self.add(contents = other)
        return self

    def __iadd__(self,
            other: Union[Repository, Dict[str, Any]]) -> None:
        """Combines argument with 'contents'.

        Args:
            other (Union[Repository, Dict[str, Any]]): another
                Repository instance or compatible dictionary.

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
        """Returns default dictionary representation of contents.

        Returns:
            str: default dictionary representation of 'contents'.

        """
        return (
            f'{self.name} '
            f'contents: {self.contents.__str__()} '
            f'defaults: {self.defaults} ')

    """ Private Methods """

    def _nestify(self,
            contents: Union[
                Repository,
                Dict[str, Any]]) -> Repository:
        """Converts nested dictionaries to Repository instances.

        Args:
            contents (Union[Repository, Dict[str, Any]]): mutable
                mapping to be converted to a Repository instance.

        Returns:
            Repository: subclass instance with 'contents' stored.

        """
        new_repository = self.__new__()
        for key, value in contents.items():
            if isinstance(value, dict):
                new_repository.add(
                    contents = {key: self._nestify(contents = value)})
            else:
                new_repository.add(contents = {key: value})
        return new_repository