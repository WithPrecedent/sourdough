"""
.. module:: technique
:synopsis: sourdough project algorithm and parameter wrapper
:author: Corey Rayburn Yung
:copyright: 2019-2020
:license: Apache-2.0
"""

import dataclasses
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Union

import sourdough


@dataclasses.dataclass
class Technique(sourdough.Loader):
    """Base class for storing and combining algorithms and parameters.

    Args:
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. If the class instance
            needs settings from the shared Settings instance, 'name' should
            match the appropriate section name in that Settings instance. When
            subclassing, it is a good settings to use the same 'name' attribute
            as the base class for effective coordination between sourdough
            classes. Defaults to None or __class__.__name__.lower().
        module (Optional[str]): name of module where object to use is located
            (can either be a sourdough or non-sourdough module). Defaults to
            'sourdough'.
        algorithm (Optional[Union[str, object]]): name of object in 'module' to
            load or the process object which executes the primary method of
            a class instance. Defaults to None.
        parameters (Optional[Dict[str, Any]]): parameters to be attached to
            'algorithm' when 'algorithm' is instanced. Defaults to an empty
            dictionary.

    """
    name: Optional[str] = None
    module: Optional[str] = dataclasses.field(
        default_factory = lambda: 'sourdough')
    algorithm: Optional[Union[str, object]] = None
    parameters: Optional[Dict[str, Any]] = dataclasses.field(
        default_factory = dict)

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        if (self.name not in ['none', None, 'None']
                and self.algorithm not in ['none', None, 'None']):
            self.load('algorithm')
        return self

    """ Public Methods """

    def finalize(self) -> None:
        """Adds 'parameters' to 'algorithm'."""
        if technique is not None:
            try:
                self.algorithm = self.algorithm(**self.parameters)
            except AttributeError:
                try:
                    self.algorithm = self.algorithm(self.parameters)
                except AttributeError:
                    self.algorithm = self.algorithm()
            except TypeError:
                try:
                    self.algorithm = self.algorithm()
                except TypeError:
                    pass
        return self

    """ Other Dunder Methods """

    def __repr__(self) -> str:
        """Returns string representation of a class instance."""
        return self.__str__()

    def __str__(self) -> str:
        """Returns string representation of a class instance."""
        return (
            f'sourdough {self.name} '
            f'algorithm: {str(self.algorithm)} '
            f'parameters: {str(self.parameters)} ')