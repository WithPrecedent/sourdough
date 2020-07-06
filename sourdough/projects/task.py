"""
.. module:: task
:synopsis: sourdough Task and Technique classes
:publisher: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import dataclasses
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union

import sourdough
    
 
@dataclasses.dataclass
class Technique(sourdough.Component):
    """Base class for creating or modifying data objects.

    Args:
        name (str): designates the name of the class instance used
            for internal referencing throughout sourdough. If the class instance
            needs settings from the shared Settings instance, 'name' should
            match the appropriate section name in that Settings instance. When
            subclassing, it is a good settings to use the same 'name' attribute
            as the base class for effective coordination between sourdough
            classes. Defaults to None or __class__.__name__.lower().
        algorithm (Union[str, object]]): name of object in 'module' to
            load or the process object which executes the primary method of
            a class instance. Defaults to None.
        parameters (Mapping[str, Any]]): parameters to be attached to
            'algorithm' when 'algorithm' is called. Defaults to an empty
            dictionary.
            
    """
    name: str = None
    algorithm: Union[str, object] = None
    parameters: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    
    """ Required Subclass Methods """
    
    def apply(self,
            data: sourdough.Component, **kwargs) -> NotImplementedError:
        """Subclasses must provide their own methods."""
        raise NotImplementedError(
            'Technique subclasses must include apply methods')
    
    """ Dunder Methods """

    def __repr__(self) -> str:
        """Returns string representation of a class instance."""
        return self.__str__()

    def __str__(self) -> str:
        """Returns string representation of a class instance."""
        return (
            f'sourdough {self.__class__.__name__} {self.name}\n'
            f'worker: {self.worker.name}\n'
            f'algorithm: {str(self.algorithm)}\n'
            f'parameters: {str(self.parameters)}\n')
        
            
@dataclasses.dataclass
class Task(sourdough.Component):
    """Base class for wrapping a Technique.

    A Task is a basic wrapper for a Technique that adds a 'name' for the
    'worker' that a stored technique instance is associated with. Subclasses of
    Task can store additional methods and attributes to apply to all possible
    technique instances that could be used. This is often useful when creating
    'comparative' Worker instances which test a variety of strategies with
    similar or identical parameters and/or methods.

    A Worker instance will try to return attributes from 'technique' if the
    attribute is not found in the Worker instance. 

    Args:
        name (str): designates the name of the class instance used
            for internal referencing throughout sourdough. If the class instance
            needs settings from the shared Settings instance, 'name' should
            match the appropriate section name in that Settings instance. When
            subclassing, it is a good settings to use the same 'name' attribute
            as the base class for effective coordination between sourdough
            classes. Defaults to None or __class__.__name__.lower().
        worker (str): the name of the worker in a Worker instance that 
            the algorithm is being performed. This attribute is generally 
            optional but can be useful for tracking and/or displaying the status 
            of iteration. It is automatically created when using a chained or 
            comparative Worker. Defaults to None.
        technique (technique): technique object for this worker in a sourdough
            sequence. Defaults to None.

    """
    name: str = None
    worker: str = dataclasses.field(default_factory = lambda: '')
    technique: Union[Technique, str] = None

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
                    {self.technique}')

    def __repr__(self) -> str:
        """Returns string representation of a class instance."""
        return self.__str__()

    def __str__(self) -> str:
        """Returns string representation of a class instance."""
        return (
            f'sourdough {self.__class__.__name__} {self.name}\n'
            f'worker: {self.worker.name}\n'
            f'technique: {str(self.technique)}\n')
