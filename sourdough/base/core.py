"""
core: sourdough base classes for composite objects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Element: abstract base class for sourdough objects that are part of 
        composite structures.
    Elemental: annotation type for all classes that contain Elements.

"""
from __future__ import annotations
import abc
import collections.abc
import copy
import dataclasses
import inspect
import textwrap
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union

import sourdough


@dataclasses.dataclass
class Element(abc.ABC):
    """Base class for core sourdough objects.

    A Element has a 'name' attribute for internal referencing and to allow 
    sourdough iterables to function propertly. Element instances can be used 
    to create a variety of composite data structures such as trees and graphs. 

    The mixins included with sourdough are all compatible, individually and
    collectively, with Element and its subclasses.

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Element is called, 'name' is set based upon
            the 'get_name' method in Element. If that method is not overridden 
            by a subclass instance, 'name' will be assigned to the snake case 
            version of the class name ('__class__.__name__').
    
    """
    name: str = None

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Sets 'name' to the default value if it is not passed.
        self.name = self.name or self.get_name()

    """ Class Methods """

    @classmethod
    def get_name(cls) -> str:
        """Returns 'name' of class for use throughout sourdough.
        
        The method is a classmethod so that a 'name' can properly derived even
        before a class is instanced. It can also be called after a subclass is
        instanced (as is the case in '__post_init__').
        
        This method converts the class name from CapitalCase to snake_case.
        
        If a user wishes to use an alternate naming system, a subclass should
        simply override this method. 
        
        Returns:
            str: name of class for internal referencing and some access methods.
        
        """
        if isinstance(cls, Element):
            return cls.name
        elif inspect.isclass(cls):
            return sourdough.tools.snakify(cls.__name__)
        else:
            return sourdough.tools.snakify(cls.__class__.__name__)

    """ Dunder Methods """

    def __repr__(self) -> str:
        """Returns '__str__' representation.

        Returns:
            str: default string representation of an instance.

        """
        return self.__str__()
        
    def __str__(self) -> str:
        """Returns pretty string representation of an instance.
        
        Returns:
            str: pretty string representation of an instance.
            
        """
        new_line = '\n'
        representation = [f'sourdough {self.__class__.__name__}']
        attributes = [a for a in self.__dict__ if not a.startswith('_')]
        for attribute in attributes:
            value = getattr(self, attribute)
            if (isinstance(value, Element) 
                    and isinstance(value, (Sequence, Mapping))):
                representation.append(
                    f'''{attribute}:{new_line}{textwrap.indent(
                        str(value.contents), '    ')}''')            
            elif (isinstance(value, (Sequence, Mapping)) 
                    and not isinstance(value, str)):
                representation.append(
                    f'''{attribute}:{new_line}{textwrap.indent(
                        str(value), '    ')}''')
            else:
                representation.append(f'{attribute}: {str(value)}')
        return new_line.join(representation)    


Elemental = Union['Element', Mapping[str, 'Element'], Sequence['Element']]