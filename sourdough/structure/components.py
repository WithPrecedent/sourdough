"""
.. module:: components
:synopsis: sourdough core objects
:author: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import abc
import dataclasses
from typing import Any, ClassVar, Iterable, Mapping, Sequence, Tuple, Union

import sourdough


@dataclasses.dataclass
class Component(abc.ABC):
    """Base class for components in sourdough.

    A Component maintains a 'name' attribute for internal referencing and to
    allow the classes in 'iterables' to function. It can be used to create
    a variety of composite data structures such as trees and graphs. 

    The mixins included with sourdough are all compatible, individually and
    collectively, with Component.

    Args:
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. For example if a 
            class instance needs settings from the shared Settings instance, 
            'name' should match the appropriate section name in that Settings 
            instance. When subclassing, it is sometimes a good idea to use the 
            same 'name' attribute as the base class for effective coordination 
            between sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Component is called, 'name' is set to a snake 
            case version of the class name ('__class__.__name__').
    
    """
    name: str = None

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Sets 'name' to the default value if it is not passed.
        self.name = self.name or self._get_name(component = self)

    """ Private Methods """

    def _get_name(self) -> str:
        """Returns 'name' of class for use throughout sourdough.
        
        This method converts the class name from CapitalCase to snake_case.
        
        If a user wishes to use an alternate naming system, a subclass should
        simply override this method. 
        
        Returns:
            str: name of class for internal referencing.
        
        """
        return sourdough.tools.snakify(self.__class__.__name__)


@dataclasses.dataclass
class Operator(Component):
    """Base class for classes which apply methods to objects.
    
    All subclasses must have 'apply' methods. 
    
    Args:
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. For example if a 
            class instance needs settings from the shared Settings instance, 
            'name' should match the appropriate section name in that Settings 
            instance. When subclassing, it is sometimes a good idea to use the 
            same 'name' attribute as the base class for effective coordination 
            between sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Component is called, 'name' is set to a snake 
            case version of the class name ('__class__.__name__').
    
    """
    name: str = None
    
    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def apply(self, *args, **kwargs) -> None:
        """Subclasses must provide their own methods."""
        pass
