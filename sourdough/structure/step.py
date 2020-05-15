"""
.. module:: step
:synopsis: sourdough project task wrapper
:author: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import dataclasses
from typing import (
    Any, Callable, ClassVar, Dict, Iterable, List, Optional, Tuple, Union)

import sourdough


@dataclasses.dataclass
class Step(sourdough.Component):
    """Base class for storing tasks stored in Plans.

    A Step is a basic wrapper for a task that adds a 'name' for the
    'step' that a stored task instance is associated with. Subclasses of
    Step can store additional methods and attributes to apply to all possible
    task instances that could be used.

    A Step instance will try to return attributes from 'task' if the
    attribute is not found in the Step instance. Similarly, when setting
    or deleting attributes, a Step instance will set or delete the
    attribute in the stored task instance.

    Arguments:
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. If the class instance
            needs settings from the shared Settings instance, 'name' should
            match the appropriate section name in that Settings instance. When
            subclassing, it is a good settings to use the same 'name' attribute
            as the base class for effective coordination between sourdough
            classes. Defaults to None or __class__.__name__.lower().
        task (task): task object for this step in a sourdough
            sequence. Defaults to None.

    """
    name: Optional[str] = None
    task: [sourdough.task] = None

    """ Dunder Methods """

    def __getattr__(self, attribute: str) -> Any:
        """Looks for 'attribute' in 'task'.

        Arguments:
            attribute (str): name of attribute to return.

        Returns:
            Any: matching attribute.

        Raises:
            AttributeError: if 'attribute' is not found in 'task'.

        """
        try:
            return getattr(self.task, attribute)
        except AttributeError:
            raise AttributeError(
                f'{attribute} neither found in {self.name} nor \
                    {self.task.name}')

    def __setattr__(self, attribute: str, value: Any) -> None:
        """Adds 'value' to 'task' with the name 'attribute'.

        Arguments:
            attribute (str): name of the attribute to add to 'task'.
            value (Any): value to store at that attribute in 'task'.

        """
        setattr(self.task, attribute, value)
        return self

    def __delattr__(self, attribute: str) -> None:
        """Deletes 'attribute' from 'task'.

        Arguments:
            attribute (str): name of attribute to delete.

        """
        try:
            delattr(self.task, attribute)
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
            f'task: {self.task.name}')
    

@dataclasses.dataclass
class Task(sourdough.Component):
    """Base class for creating or modifying other sourdough classes.

    Arguments:
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. If the class instance
            needs settings from the shared Settings instance, 'name' should
            match the appropriate section name in that Settings instance. When
            subclassing, it is a good settings to use the same 'name' attribute
            as the base class for effective coordination between sourdough
            classes. Defaults to None or __class__.__name__.lower().
        algorithm (Optional[Union[str, object]]): name of object in 'module' to
            load or the process object which executes the primary method of
            a class instance. Defaults to None.
        parameters (Optional[Dict[str, Any]]): parameters to be attached to
            'algorithm' when 'algorithm' is instanced. Defaults to an empty
            dictionary.
            
    """
    name: Optional[str] = None
    step: Optional[Step] = None
    algorithm: Optional[Union[str, object]] = None
    parameters: Optional[Dict[str, Any]] = dataclasses.field(
        default_factory = dict)
    
    """ Required Subclass Methods """
    
    def apply(self,
            data: sourdough.Component, **kwargs) -> NotImplementedError:
        """Subclasses must provide their own methods."""
        raise NotImplementedError('Task subclasses must include apply methods')
    
    """ Dunder Methods """

    def __repr__(self) -> str:
        """Returns string representation of a class instance."""
        return self.__str__()

    def __str__(self) -> str:
        """Returns string representation of a class instance."""
        return (
            f'sourdough {self.__class__.__name__} {self.name} '
            f'step {self.step.name} '
            f'algorithm: {str(self.algorithm)} '
            f'parameters: {str(self.parameters)} ')
        