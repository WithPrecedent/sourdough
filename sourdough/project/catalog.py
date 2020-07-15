"""
.. module:: catalog
:synopsis: dictionary for storing strategies
:author: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import dataclasses
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union

import sourdough


@dataclasses.dataclass
class Corpus(sourdough.Lexicon):
    """Base class for a wildcard and list-accepting dictionary.

    A Corpus inherits the differences between a Lexicon and an ordinary python
    dict.

    A Corpus differs from a Lexicon in 5 significant ways:
        1) It recognizes an 'all' key which will return a list of all values
            stored in a Corpus instance.
        2) It recognizes a 'default' key which will return all values matching
            keys listed in the 'defaults' attribute. 'default' can also be set
            using the 'catalog['default'] = new_default' assignment. If 
            'defaults' is not passed when the instance is initialized, the 
            initial value of 'defaults' is 'all'
        3) It recognizes a 'none' key which will return an empty list.
        4) It supports a list of keys being accessed with the matching
            values returned. For example, 'catalog[['first_key', 'second_key']]' 
            will return the values for those keys in a list.
        5) If a single key is sought, a Corpus can either return the stored
            value or a stored value in a list (if 'always_return_list' is
            True). The latter option is available to make iteration easier
            when the iterator assumes a single datatype will be returned.
        6) It includes a 'create' method which will either instance a stored
            class or return a stored instance.

    Args:
        contents (Union[sourdough.Component, Sequence[sourdough.Component], 
            Mapping[str, sourdough.Component]]): Component(s) to validate or
            convert to a dict. If 'contents' is a Sequence or a Component, 
            the key for storing 'contents' is the 'name' attribute of each 
            Component.
        defaults (Sequence[str]]): a list of keys in 'contents' which will be 
            used to return items when 'default' is sought. If not passed, 
            'default' will be set to all keys.
        always_return_list (bool]): whether to return a list even when
            the key passed is not a list or special access key (True) or to 
            return a list only when a list or special acces key is used (False). 
            Defaults to False.

    """
    contents: Union[
        'sourdough.Component',
        Sequence['sourdough.Component'],
        Mapping[str, 'sourdough.Component']] = dataclasses.field(
            default_factory = dict)    
    defaults: Sequence[str] = dataclasses.field(default_factory = list)
    always_return_list: bool = False

    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Validates 'contents' or converts it to a dict.
        super().__post_init__()
        # Sets 'default' to all keys of 'contents', if not passed.
        self.defaults = self.defaults or 'all'
        
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
    
    def subsetify(self, subset: Union[str, Sequence[str]]) -> 'Corpus':
        """Returns a subset of 'contents'.

        Args:
            subset (Union[str, Sequence[str]]): key(s) to get key/value pairs 
                from 'contents'.

        Returns:
            Corpus: with only keys in 'subset'.

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

    """ Private Methods """
    
    def _validate(self, 
            contents: Union[
                'sourdough.Component',
                Sequence['sourdough.Component'],
                Mapping[str, 'sourdough.Component']]) -> Mapping[
                    str, 'sourdough.Component']:
        """Validates 'contents' or converts 'contents' to the proper type.
        
        Args:
            contents (Union[sourdough.Component, Sequence[sourdough.Component], 
                Mapping[str, sourdough.Component]]): Component(s) to validate or
                convert to a dict. If 'contents' is a Sequence or a Component, 
                the key for storing 'contents' is the 'name' attribute of each 
                Component.

        Raises:
            TypeError: if 'contents' is neither a Component subclass, Sequence
                of Component subclasses, or Mapping with Components subclasses
                as values.

        Returns:
            Mapping (str, sourdough.Component): a properly typed dict derived
                from passed 'contents'.
            
        """
        if isinstance(contents, sourdough.Component):
            return {contents.get_name(): contents}
        elif isinstance(contents, Mapping):
            return contents
        elif isinstance(contents, Sequence):
            new_contents = {}
            for component in contents:
                new_contents[component.get_name()] = component
            return new_contents
        else:
            raise TypeError(
                'contents must a Component or Mapping or Sequence storing \
                Components')
  