"""
.. module:: plan
:synopsis: sourdough project iterable
:author: Corey Rayburn Yung
:copyright: 2019-2020
:license: Apache-2.0
"""

import collections.abc
import dataclasses
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Union

import sourdough


@dataclasses.dataclass
class Plan(sourdough.Component, collections.abc.MutableSequence):
    """Base class for iterating Component instances.

    A Plan stores a list of items with 'name' attributes. Each 'name'
    acts as a key to create the facade of a dictionary with the items in the
    stored list serving as values. This allows for duplicate keys and the
    storage of class instances at the expense of lookup speed. Since normal
    use cases do not include repeat accessing of Plan instances, the
    loss of lookup speed should have negligible effect on overall performance.

    Args:
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. If the class instance
            needs settings from the shared Settings instance, 'name' should
            match the appropriate section name in that Settings instance. When
            subclassing, it is a good settings to use the same 'name' attribute
            as the base class for effective coordination between sourdough
            classes. Defaults to None or __class__.__name__.lower().
        contents (Optional[List[Component]]): stored list. Defaults to an
            empty list.
        extender (Optional[bool]): whether to extend (True) 'contents' when
            using the 'add' method or '+' (True) or append (False) when using
            those methods. Defaults to True

    """
    name: Optional[str] = None
    contents: Optional[List[sourdough.Component]] = dataclasses.field(
        default_factory = list)
    extender: Optional[bool] = True

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        super().__post_init__()
        if self.__class__ == Plan:
            if self.extender:
                return Extender(name = self.name, contents = self.contents)
            else:
                return Appended(name = self.name, contents = self.contents)
        return self

    """ Required ABC Methods """

    def insert(self, index: int, value: sourdough.Component) -> None:
        """Inserts 'value' at 'index' in 'contents'.

        Args:
            index (int): index to insert 'value' at.
            value (Component): object to be inserted.

        """
        self.contents.insert[index] = value
        return self

    def __getitem__(self, key: str) -> List[sourdough.Component]:
        """Returns value(s) for 'key' in 'contents' as a list.

        Args:
            key (str): name to search for in 'contents'.

        Returns:
            List[Component]: value(s) stored in 'contents'.

        """
        return [c for c in self.contents if c.name == key]

    def __setitem__(self, key: str, value: sourdough.Component) -> None:
        """Adds 'value' to 'contents' if 'key' matches 'value.name'.

        Args:
            key (str): name of key(s) to set in 'contents'.
            value (Component): value(s) to be added at the end of
                'contents'.

        Raises:
            TypeError: if 'name' attribute in value either doesn't exist or
                doesn't match 'key'.

        """
        if hasattr(value, name) and value.name in [key]:
            self.add(contents = contents)
        else:
            raise TypeError(
                f'{self.name} requires a value with a name atttribute')
        return self

    def __delitem__(self, key: str) -> None:
        """Deletes 'key' in 'contents'.

        Args:
            key (str): name(s) of key(s) in 'contents' to
                delete the key/value pair.

        """
        try:
            self.contents = [item for item in self.contents if item.name != key]
        except AttributeError:
            raise TypeError(
                f'{self.name} requires a value with a name atttribute')
        return self

    def __len__(self) -> int:
        """Returns length of 'contents'.

        Returns:
            Integer: length of 'contents'.

        """
        return len(self.contents)

    """ Other Dunder Methods """

    def __add__(self,
            other: Union[
                List[sourdough.Component],
                sourdough.Component]) -> None:
        """Combines argument with 'contents'.

        Args:
            other (Union[List[Component], Component]):
                Component(s) to add to 'contents'.

        """
        self.add(contents = other)
        return self

    def __iadd__(self,
            other: Union[
                List[sourdough.Component],
                sourdough.Component]) -> None:
        """Combines argument with 'contents'.

        Args:
            other (Union[List[Component], Component]):
                Component(s) to add to 'contents'.

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
        """Returns representation of 'contents'.

        Returns:
            str: representation of 'contents'.

        """
        return (
            f'sourdough {self.name} '
            f'contents: {self.contents} ')


@dataclasses.dataclass
class Appender(Plan):
    """Plan subclass which appends its contents by default.

    'Contents' is appended by the 'add' method and when using '+' to join a
    Plan with another object.

    Args:
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. If the class instance
            needs settings from the shared Settings instance, 'name' should
            match the appropriate section name in that Settings instance. When
            subclassing, it is a good settings to use the same 'name' attribute
            as the base class for effective coordination between sourdough
            classes. Defaults to None or __class__.__name__.lower().
        contents (Optional[List[Component]]): stored list. Defaults to an
            empty list.

    """
    name: Optional[str] = None
    contents: Optional[List[sourdough.Component]] = dataclasses.field(
        default_factory = list)

    """ Public Methods """

    def add(self,
            contents: Union[
                List[sourdough.Component],
                sourdough.Component]) -> None:
        """Appends arguments to 'contents'.

        Args:
            contents (Union[List[Component], Component]): Component(s) to add
                to 'contents'.

        """
        self.contents.append(contents)
        return self


@dataclasses.dataclass
class Extender(Plan):
    """Plan subclass which extends its contents by default.

    'Contents' is extended by the 'add' method and when using '+' to join a
    Plan with another object.

    Args:
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. If the class instance
            needs settings from the shared Settings instance, 'name' should
            match the appropriate section name in that Settings instance. When
            subclassing, it is a good settings to use the same 'name' attribute
            as the base class for effective coordination between sourdough
            classes. Defaults to None or __class__.__name__.lower().
        contents (Optional[List[Component]]): stored list. Defaults to an
            empty list.

    """
    name: Optional[str] = None
    contents: Optional[List[sourdough.Component]] = dataclasses.field(
        default_factory = list)

    """ Public Methods """

    def add(self,
            contents: Union[
                List[sourdough.Component],
                sourdough.Component]) -> None:
        """Extends 'contents' with argument, if possible.

        If the argument can not be used to extend 'contents', it is appended
        instead.

        Args:
            contents (Union[List[Component], Component]): Component(s) to add to
                'contents'.

        """
        try:
            self.contents.extend(contents)
        except TypeError:
            self.contents.append(contents)
        return self