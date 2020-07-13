"""
.. module:: dictionaries
:synopsis: base sourdough dictionaries
:author: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import abc
import collections.abc
import dataclasses
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union

import sourdough


@dataclasses.dataclass
class Lexicon(collections.abc.MutableMapping, abc.ABC):
    """Base class for sourdough dictionaries.

    Lexicon subclasses can serve as drop in replacements for dicts with added
    features.
    
    A Lexicon differs from a python dict in 3 significant ways:
        1) It includes an 'add' method which allows different datatypes to
            be passed and added to a Lexicon instance. All of the normal dict 
            methods are also available. 'add' should be used to set default or 
            more complex methods of adding elements to the stored dict.
        2) It includes a 'subsetify' method which will return a Lexicon or
            Lexicon subclass instance with only the key/value pairs matching
            keys in the 'subset' parameter.
        3) It allows the '+' operator to be used to join a Lexicon instance
            with another Lexicon instance, a dict, or a Component. The '+' 
            operator calls the Lexicon 'add' method to implement how the added 
            item(s) is/are added to the Lexicon instance.
    
    All Lexicon subclasses must include a 'validate' method. Requirements for
    that method are described in the abstractmethod itself.
    
    Args:
        contents (Mapping[str, Any]]): stored dictionary. Defaults to an empty 
            dict.
              
    """
    contents: Mapping[str, Any] = dataclasses.field(default_factory = dict)

    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Validates 'contents' or converts it to a dict.
        self.contents = self.validate(contents = self.contents)
        
    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def validate(self, contents: Any) -> Mapping[Any, Any]:
        """Validates 'contents' or converts 'contents' to proper type.
        
        Subclasses must provide their own methods.
        
        The 'contents' argument should accept any supported datatype and either
        validate its type or convert it to a dict. This method is used to 
        validate or convert both the passed 'contents' and by the 'add' method
        to add new keys and values to the 'contents' attribute.
        
        """
        pass
    
    """ Public Methods """
    
    def add(self, contents: Any) -> None:
        """Adds 'contents' to the 'contents' attribute.
        
        Args:
            component (Union[sourdough.Component, 
                Sequence[sourdough.Component], Mapping[str, 
                sourdough.Component]]): Component(s) to add to
                'contents'. If 'component' is a Sequence or a Component, the 
                key for storing 'component' is the 'name' attribute of each 
                Component.

        """
        self.contents.update(self.validate(contents = contents))
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
        subset = sourdough.tools.listify(subset)
        return self.__class__(
            contents = {k: self.contents[k] for k in subset},
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
        """Combines argument with 'contents'.

        Args:
            other (Any): item to add to 'contents' using the 'add' method.

        """
        self.add(other)
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
class Corpus(Lexicon, abc.ABC):
    """Base class for 2-level nested dictionaries.
    
    A Corpus differs from a Lexicon in 3 significant ways:
        1) Its 'add' method requirements 2 arguments ('section' and 'contents') 
            due to the 2-level nature of the stored dict.
        2) It does not return an error if you attempt to delete a key that is
            not stored within 'contents'.
        3) If you try to find a key that does not correspond to a section in 
            'contents', a Corpus subclass instance will return the first 
            matching key within a section (iterated in stored order), if a
            match exists.
    
    The Corups 'add' method accounts for whether the 'section' passed already
    exists and adds the passed 'contents' appropriately.
    
    Args:
        contents (Mapping[str, Any]]): stored dictionary. Defaults to an empty 
            dict.
              
    """
    contents: Mapping[str, Mapping[str, Any]] = dataclasses.field(
        default_factory = dict)
        
    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def validate(self, contents: Any) -> Mapping[Any, Any]:
        """Validates 'contents' or converts 'contents' to proper type.
        
        Subclasses must provide their own methods.
        
        The 'contents' argument should accept any supported datatype and either
        validate its type or convert it to a dict. This method is used to 
        validate or convert both the passed 'contents' and by the 'add' method
        to add new keys and values to the 'contents' attribute.
        
        """
        pass

    """ Public Methods """

    def add(self, 
            section: str, 
            contents: Mapping[str, Any]) -> None:
        """Adds 'settings' to 'contents'.

        Args:
            section (str): name of section to add 'contents' to.
            contents (Mapping[str, Any]): a dict to store in 'section'.

        """
        try:
            self[section].update(self._validate(contents = contents))
        except KeyError:
            self[section] = self._validate(contents = contents)
        return self
    
    """ Dunder Methods """

    def __getitem__(self, key: str) -> Union[Mapping[str, Any], Any]:
        """Returns a section of the active dictionary or key within a section.

        Args:
            key (str): the name of the dictionary key for which the value is
                sought.

        Returns:
            Union[Mapping[str, Any], Any]: dict if 'key' matches a section in
                the active dictionary. If 'key' matches a key within a section,
                the value, which can be any of the supported datatypes is
                returned.

        """
        try:
            return self.contents[key]
        except KeyError:
            for section in list(self.contents.keys()):
                try:
                    return self.contents[section][key]
                except KeyError:
                    pass
            raise KeyError(f'{key} is not found in {self.__class__.__name__}')

    def __setitem__(self, key: str, value: Mapping[str, Any]) -> None:
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

    def __delitem__(self, key: str) -> None:
        """Deletes 'key' entry in 'contents'.

        Args:
            key (str): name of key in 'contents'.

        """
        try:
            del self.contents[key]
        except KeyError:
            pass
        return self


@dataclasses.dataclass
class Reflector(Lexicon):
    """Base class for a mirrored dictionary.

    Reflector access methods search keys and values for corresponding
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
        """Creates 'reversed_contents' from 'contents'."""
        self.reversed_contents = {
            value: key for key, value in self.contents.items()}
        return self
