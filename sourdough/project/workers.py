"""
workers: containers for composite sourdough objects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:


"""

import dataclasses
import inspect
import textwrap
from typing import (
    Any, Callable, ClassVar, Iterable, Mapping, Sequence, Tuple, Union)

import sourdough


@dataclasses.dataclass
class Worker(sourdough.Hybrid):
    """A lightweight container for describing a portion of a sourdough project.

    Worker inherits all of the differences between a Hybrid and a python list.
    
    A Worker differs from a Hybrid in 3 significant ways:
        1) It has a 'role' attribute which indicates how the contained 
            iterator should be ordered. 
        2) An 'overview' property is added which returns a dict of the names
            of the various parts of the tree objects. It doesn't include the
            hierarchy itself. Rather, it includes lists of all the types of
            sourdough.Component objects.
        
    Args:
        contents (Sequence[sourdough.Component]]): stored iterable of Action
            subclasses. Defaults to an empty list.
        name (str): creates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Component is called, 'name' is set based upon
            the 'get_name' method in sourdough.Component. If that method is not 
            overridden by a subclass instance, 'name' will be assigned to the 
            snake case version of the class name ('__class__.__name__').
        role (Union[sourdough.Role, str]): role for the 
            organization, iteration, and composition of 'contents' or a str
            corresponding to an option in 'Role.registry'.


    Attributes:
        contents (Sequence[sourdough.Component]): all objects in 'contents' must 
            be sourdough Component subclass instances and are stored in a list.
        _default (Any): default value to use when there is a KeyError using the
            'get' method.    

    ToDo:
        draw: a method for producting a diagram of a Worker instance's 
            'contents' to the console or a file.
            
    """
    contents: Sequence[Union['sourdough.Task', 'Worker']] = dataclasses.field(
        default_factory = list)
    role: Union['sourdough.Role', str] = 'obey'
    name: str = None
      
    """ Properties """
    
    @property
    def overview(self) -> 'sourdough.Overview':
        """Returns a dict snapshot of a Worker subclass instance.
        
        Returns:
            sourdough.Overview: based on the stored 'contents' of an instance.
        
        """
        return sourdough.Overview(worker = self)

    """ Dunder Methods """
    
    def __iter__(self) -> Iterable:
        """Returns iterable of 'contents' based upon 'role'.
        
        If 'role' has not been initialized, this method returns the default
        python 'iter' method of 'contents'. This should not happen as long as
        the '__post_init__' method from Hybrid is not overwritten without 
        calling 'super().__post_init__'.
        
        Returns:
            Iterable: of 'contents'.
            
        """
        try:
            return iter(self.role)
        except (AttributeError, TypeError):
            return iter(self.contents)
        
    """ Private Methods """
    
    def _initial_validation(self) -> None:
        """Validates passed 'contents' on class initialization."""
        super()._initial_validation()
        # Validates or converts 'role'.
        self = sourdough.Role.validate(worker = self)
        return self


@dataclasses.dataclass
class Manager(Worker):
    """A lightweight container for describing a sourdough project.

    An Manager inherits the differences between a Hybrid and an ordinary python
    list.
    
    An Manager differs from a Hybrid in 2 significant ways:
        1) It only stores Task instances and other Manager instances.
        2)
    
    Args:
        contents (Tuple[str, str]): stored dictionary. Defaults to an empty 
            dict.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Component is called, 'name' is set based upon
            the 'get_name' method in Component. If that method is not 
            overridden by a subclass instance, 'name' will be assigned to the 
            snake case version of the class name ('__class__.__name__').
              
    """
    contents: Sequence[Union['sourdough.Task', 'Worker']] = dataclasses.field(
        default_factory = list)
    role: Union['sourdough.Role', str] = 'obey'
    identification: str = None
    name: str = None
    
    """ Public Methods """
    
    def validate(self, 
            contents: Union[
                Tuple[str, str],
                'sourdough.Task',
                'Worker',
                Sequence[Union[
                    Tuple[str, str],
                    'sourdough.Task',
                    'Worker']]]) -> Sequence[Union[
                        'sourdough.Task', 
                        'Worker']]:
        """Validates 'contents' or converts 'contents' to proper type.
        
        Args:

            
        Raises:
            TypeError: if 'contents' argument is not of a supported datatype.
            
        Returns:

                
        """
        new_contents = []
        if isinstance(contents, (Tuple[str, str], sourdough.Task, Worker)):
            new_contents = [contents]
        elif isinstance(contents, Sequence):
            for item in contents:
                if (isinstance(item, Tuple)
                        and len(item) == 2
                        and all(isinstance(item, str) for i in item)):
                    new_contents.append(
                        sourdough.Task(name = item[0], technique = item[1]))
                elif isinstance(item, (sourdough.Task, Worker)):
                    new_contents.append(item)
                else:
                    raise TypeError(
                        'contents must be a list containing Task instances, '
                        'Worker instances, or Tuples of two str types')
        else:
            raise TypeError('contents must be a list')
        return new_contents

    def add(self, 
            contents: Union[
                Tuple[str, str],
                'sourdough.Task',
                'Worker',
                Sequence[Union[
                    Tuple[str, str],
                    'sourdough.Task',
                    'Worker']]]) -> None:
        """Extends 'contents' argument to 'contents' attribute.
        
        Args:

        """
        super().add(contents = contents)
        return self    
              