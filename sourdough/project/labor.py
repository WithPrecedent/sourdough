"""
directors: Director and Specialist base classes and registries.
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Specialist (Registrar, Container):
    Director (Registrar, Hybrid, ABC):
    
"""
from __future__ import annotations
import abc
import collections.abc
import dataclasses
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Union)

import sourdough
   

@dataclasses.dataclass
class Specialist(sourdough.quirks.Registrar, collections.abc.Container):
    """Base class for a specialist in a Director.
    
    Args:
        contents (Any): item(s) contained by an instance. Defaults to None.
        action (str): name of action performed by the class. This is used in
            messages in the terminal and logging. It is usually the verb form
            of the class name (i.e., for Draft, the action is 'drafting').
            
    """
    contents: Any = None
    action: str = None

    """ Required Subclass Methods """
    
    # @classmethod
    # @abc.abstractmethod
    def create(self, previous: Specialist, 
               project: sourdough.Project, **kwargs) -> Specialist:
        """Performs some action based on 'project' with kwargs (optional).
        
        Subclasses must provide their own methods.
        
        """
        pass

    """ Dunder Methods """
    
    def __contains__(self, item: Any) -> bool:
        """Returns whether 'item' is in the 'contents' attribute.
        
        Args:
            item (Any): item to look for in 'contents'.
            
        Returns:
            bool: whether 'item' is in 'contents' if it is a Collection.
                Otherwise, it evaluates if 'item' is equivalent to 'contents'.
                
        """
        try:
            return item in self.contents
        except TypeError:
            return item == self.contents
    
    def __iter__(self) -> Iterable:
        """Returns iterable of 'contents'.

        Raises:
            TypeError: if 'contents' is not iterable or if it is a str type.

        Returns:
            Iterable: of 'contents'.
            
        """
        if not isinstance(self.contents, str):
            return iter(self.contents)
        else:
            return TypeError('This Specialist''s contents are not iterable.')

   
@dataclasses.dataclass
class Director(sourdough.quirks.Registrar, sourdough.types.Hybrid, abc.ABC):
    """Base class for sourdough directors.
    
    Args:
        contents (Union[Sequence[str], Sequence[Specialist]]): a list of str or 
            Specialists. Defaults to an empty list.
        project (sourdough.Project): related project instance.
               
    """
    contents: Union[Sequence[str], Sequence[Specialist]] = dataclasses.field(
        default_factory = list)
    project: sourdough.Project = dataclasses.field(default = None, repr = False)

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent and/or mixin initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass
        self.index = -1
        # Validates or converts 'contents'.
        self._initialize_specialists()

    """ Class Methods """
    
    @classmethod
    def register(cls) -> None:
        key = sourdough.tools.snakify(cls.__name__)
        sourdough.project.resources.directors[key] = cls
        return cls
   
    """ Private Methods """
     
    def _initialize_specialists(self) -> None:
        """[summary]

        Raises:
            TypeError: [description]

        Returns:
            [type]: [description]
            
        """
        new_specialists = []
        for specialist in self.contents:
            if isinstance(specialist, str):
                new_specialists.append(self.project.resources.specialists.instance(specialist))
            elif issubclass(specialist, self.project.defaults['specialist']):
                new_specialists.append(specialist())
            else:
                raise TypeError('All specialists must be str or Specialist type')
        self.contents = new_specialists
        return self

    
    def _get_last_specialist(self) -> sourdough.Specialist:
        last_key = self.project.contents.keys()[:-1]
        return self.project.contents[last_key]
        
    """ Dunder Methods """
    
    def __next__(self) -> Specialist:
        if self.index < 0:
            previous = self.project.settings
        else:
            previous = self.project.contents[self.index]
        self.index += 1
        current = self.contents[self.index]
        print('test current in next', current)
        if hasattr(self.project, 'verbose') and self.project.verbose:
            print(f'Beginning {current.action} process')
        creation = current.create(previous = previous, project = self.project)
        print('test creation', creation)
        return creation
    
    def __iter__(self) -> Iterable:
        return self
          