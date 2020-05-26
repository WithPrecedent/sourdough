"""
.. module:: techniques
:synopsis: sourdough Technique and Technique
:publisher: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import dataclasses
from typing import (
    Any, Callable, ClassVar, Dict, Iterable, List, Optional, Tuple, Union)

import sourdough
from sourdough import utilities
    
 
@dataclasses.dataclass
class Technique(sourdough.Component):
    """Base class for creating or modifying other sourdough classes.

    Args:
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. If the class instance
            needs settings from the shared Settings instance, 'name' should
            match the appropriate section name in that Settings instance. When
            subclassing, it is a good settings to use the same 'name' attribute
            as the base class for effective coordination between sourdough
            classes. Defaults to None or __class__.__name__.lower().
        worker (Optional[str]): the name of the worker in a Worker instance that the
            algorithm is being performed. This attribute is generally optional
            but can be useful for tracking and/or displaying the status of
            iteration. It is automatically created when using a chained or 
            comparative Worker. Defaults to None.
        algorithm (Optional[Union[str, object]]): name of object in 'module' to
            load or the process object which executes the primary method of
            a class instance. Defaults to None.
        parameters (Optional[Dict[str, Any]]): parameters to be attached to
            'algorithm' when 'algorithm' is instanced. Defaults to an empty
            dictionary.
            
    """
    name: Optional[str] = None
    worker: Optional[str] = None
    algorithm: Optional[Union[str, object]] = None
    parameters: Optional[Dict[str, Any]] = dataclasses.field(
        default_factory = dict)
    
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
            f'sourdough {self.__class__.__name__} {self.name} '
            f'worker: {self.worker.name} '
            f'algorithm: {str(self.algorithm)} '
            f'parameters: {str(self.parameters)} ')
        
            
@dataclasses.dataclass
class Task(sourdough.Component):
    """Base class for storing techniques stored in SequenceBases.

    A Worker is a basic wrapper for a technique that adds a 'name' for the
    'worker' that a stored technique instance is associated with. Subclasses of
    Worker can store additional methods and attributes to apply to all possible
    technique instances that could be used.

    A Worker instance will try to return attributes from 'technique' if the
    attribute is not found in the Worker instance. Similarly, when setting
    or deleting attributes, a Worker instance will set or delete the
    attribute in the stored technique instance.

    Args:
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. If the class instance
            needs settings from the shared Settings instance, 'name' should
            match the appropriate section name in that Settings instance. When
            subclassing, it is a good settings to use the same 'name' attribute
            as the base class for effective coordination between sourdough
            classes. Defaults to None or __class__.__name__.lower().
        technique (technique): technique object for this worker in a sourdough
            sequence. Defaults to None.

    """
    name: Optional[str] = None
    worker: Optional[str] = dataclasses.field(default_factory = lambda: '')
    technique: Optional[Union[Technique, str]] = None

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

    # def __setattr__(self, attribute: str, value: Any) -> None:
    #     """Adds 'value' to 'technique' with the name 'attribute'.

    #     Args:
    #         attribute (str): name of the attribute to add to 'technique'.
    #         value (Any): value to store at that attribute in 'technique'.

    #     """
    #     setattr(self.technique, attribute, value)
    #     return self

    # def __delattr__(self, attribute: str) -> None:
    #     """Deletes 'attribute' from 'technique'.

    #     Args:
    #         attribute (str): name of attribute to delete.

    #     """
    #     try:
    #         delattr(self.technique, attribute)
    #     except AttributeError:
    #         pass
    #     return self

    def __repr__(self) -> str:
        """Returns string representation of a class instance."""
        return self.__str__()

    def __str__(self) -> str:
        """Returns string representation of a class instance."""
        if isinstance(self.technique, Technique):
            technique = self.technique.name
        else:
            technique = self.technique
        return(
            f'worker: {self.name} '
            f'technique: {technique}') 

 