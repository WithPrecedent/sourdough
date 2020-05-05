"""
.. module:: step
:synopsis: sourdough project technique wrapper
:author: Corey Rayburn Yung
:copyright: 2019-2020
:license: Apache-2.0
"""

import dataclasses
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Union

import sourdough


@dataclasses.dataclass
class Step(sourdough.Component):
    """Base class for storing Techniques stored in Plans.

    A Step is a basic wrapper for a technique that adds a 'name' for the
    'step' that a stored Technique instance is associated with. Subclasses of
    Step can store additional methods and attributes to apply to all possible
    Technique instances that could be used.

    A Step instance will try to return attributes from 'technique' if the
    attribute is not found in the Step instance. Similarly, when setting
    or deleting attributes, a Step instance will set or delete the
    attribute in the stored Technique instance.

    Args:
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. If the class instance
            needs settings from the shared Settings instance, 'name' should
            match the appropriate section name in that Settings instance. When
            subclassing, it is a good settings to use the same 'name' attribute
            as the base class for effective coordination between sourdough
            classes. Defaults to None or __class__.__name__.lower().
        technique (Technique): Technique object for this step in a sourdough
            sequence. Defaults to None.

    """
    name: Optional[str] = None
    technique: [sourdough.Technique] = None

    """ Public Methods """

    def finalize(self, data: sourdough.Component) -> None:
        """Adds final parameters and combines algorithm with parameters.

        Args:
            data (sourdough.Component): instance with information used to
                finalize 'parameters' and/or 'algorithm'.

        """
        self.technique = self._add_conditionals(data = data)
        self.technique = self._add_data_dependent(data = data)
        self.technique.finalize()
        return self

    """ Dunder Methods """

    def __getattr__(self, attribute: str) -> Any:
        """Looks for 'attribute' in 'technique'.

        Args:
            attribute (str): name of attribute to return.

        Returns:
            Any: matching attribute.

        Raises:
            AttributeError: if 'attribute' is not found in 'technique'.

        """
        try:
            return getattr(self.technique, attribute)
        except AttributeError:
            raise AttributeError(
                f'{attribute} neither found in {self.name} nor \
                    {self.technique.name}')

    def __setattr__(self, attribute: str, value: Any) -> None:
        """Adds 'value' to 'technique' with the name 'attribute'.

        Args:
            attribute (str): name of the attribute to add to 'technique'.
            value (Any): value to store at that attribute in 'technique'.

        """
        setattr(self.technique, attribute, value)
        return self

    def __delattr__(self, attribute: str) -> None:
        """Deletes 'attribute' from 'technique'.

        Args:
            attribute (str): name of attribute to delete.

        """
        try:
            delattr(self.technique, attribute)
        except AttributeError:
            pass
        return self

    def __repr__(self) -> str:
        """Returns string representation of a class instance."""
        return self.__str__()

    def __str__(self) -> str:
        """Returns string representation of a class instance."""
        return (
            f'step: {self.name} '
            f'technique: {self.technique.name}')

    """ Private Methods """

    def _add_conditionals(self, data: sourdough.Component) -> None:
        """Adds conditional parameters, if applicable.

        Args:
            data (sourdough.Component): instance with information used to
                finalize 'parameters' and/or 'algorithm'.

        """
        if (self.technique.name not in ['none', None, 'None']
                and self.technique.conditionals):
            try:
                return getattr(manuscript, '_'.join(
                    ['_add', self.technique.name, 'conditionals']))(
                        technique = technique,
                        data = data)
            except AttributeError:
                try:
                    return getattr(manuscript, '_'.join(
                        ['_add', self.name, 'conditionals']))(
                            technique = technique,
                            data = data)
                except AttributeError:
                    pass
        return self

    def _add_data_dependent(self, data: sourdough.Component) -> None:
        """Adds data dependent parameters, if applicable.

        Args:
            data (sourdough.Component): instance with information used to
                finalize 'parameters' and/or 'algorithm'.

        """
        if (self.technique.name not in ['none', None, 'None']
                and self.technique.data_dependent):
            for key, value in self.technique.data_dependent.items():
                try:
                    technique.parameters[key] = getattr(data, value)
                except KeyError:
                    print('no matching parameter found for', key, 'in data')
        return self