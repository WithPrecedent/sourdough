"""
.. module:: strategies
:synopsis: class for storing project options
:publisher: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import dataclasses
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union

import sourdough


@dataclasses.dataclass
class Strategies(sourdough.base.Catalog):
    """[summary]

    Args:
        sourdough ([type]): [description]

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

    def validate(self, 
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
                'contents must a Component or Mapping or Sequence storing'
                'Components')


