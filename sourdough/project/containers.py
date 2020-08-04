"""
containers: storage classes for sourdough projects
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
class Inventory(sourdough.Catalog):
    """

    Args:
        contents (Union[Component, Sequence[Component], Mapping[Any, 
            Component]]): Component(s) to validate or convert to a dict. If 
            'contents' is a Sequence or a Component, the key for storing 
            'contents' is the 'name' attribute of each Component.
        defaults (Sequence[str]]): a list of keys in 'contents' which will be 
            used to return items when 'default' is sought. If not passed, 
            'default' will be set to all keys.
        always_return_list (bool]): whether to return a list even when
            the key passed is not a list or special access key (True) or to 
            return a list only when a list or special acces key is used (False). 
            Defaults to False.
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
    contents: Mapping[Any, Any] = dataclasses.field(default_factory = dict)  
    defaults: Sequence[str] = dataclasses.field(default_factory = list)
    always_return_list: bool = False
    name: str = None
        
    """ Public Methods """

    def validate(self, 
            contents: Union[
                'sourdough.Component',
                Mapping[Any, 'sourdough.Component'],
                Sequence['sourdough.Component']]) -> Mapping[
                    str, 'sourdough.Component']:
        """Validates 'contents' or converts 'contents' to a dict.
        
        Args:
            contents (Union[Component, Mapping[Any, sourdough.Component], 
                Sequence[Component]]): Component(s) to validate or convert to a 
                dict. If 'contents' is a Sequence or a Component, the key for 
                storing 'contents' is the 'name' attribute of each Component.
                
        Raises:
            TypeError: if 'contents' is neither a Component subclass, Sequence
                of Component subclasses, or Mapping with Components subclasses
                as values.
                
        Returns:
            Mapping (str, sourdough.Component): a properly typed dict derived
                from passed 'contents'.
            
        """
        if (isinstance(contents, Mapping)
            and (all(isinstance(c, sourdough.Component) 
                    for c in contents.values())
                or all(issubclass(c, sourdough.Component)
                         for c in contents.values()))):
            return contents
        elif isinstance(contents, sourdough.Component):
            return {contents.name: contents}
        elif (inspect.isclass(contents) 
                and issubclass(contents, sourdough.Component)):
            return {contents.get_name(): contents}
        elif isinstance(contents, Sequence):
            new_contents = {}
            for component in contents:
                if (isinstance(contents, sourdough.Component) or 
                        (inspect.isclass(contents) 
                            and issubclass(contents, sourdough.Component))):
                    try:
                        new_contents[component.name] = component
                    except AttributeError:
                        new_contents[component.get_name()] = component
                else:
                    raise TypeError(
                        'contents must contain all Component subclasses or '
                        'subclass instances')  
                
            return new_contents
        else:
            raise TypeError(
                'contents must a dict with Component values, Component, or '
                'list of Components')    


@dataclasses.dataclass
class Overview(sourdough.Lexicon):
    """Dictionary of different Component types in a Worker instance.
    
    Args:
        contents (Mapping[Any, Any]]): stored dictionary. Defaults to an empty 
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
    contents: Mapping[Any, Any] = dataclasses.field(default_factory = dict)
    name: str = None
    worker: 'sourdough.Worker' = None
    
    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent initialization method(s).
        super().__post_init__()
        if self.worker.role is not None:
            self.add({
                'name': self.worker.name, 
                'role': self.worker.role.name})
            for key, value in self.worker.role.options.items():
                matches = self.worker.find(
                    self._get_type, 
                    component = value)
                if len(matches) > 0:
                    self.contents[f'{key}s'] = matches
        else:
            raise ValueError(
                'role must be a Role for an overview to be created.')
        return self          
    
    """ Dunder Methods """
    
    def __str__(self) -> str:
        """Returns pretty string representation of an instance.
        
        Returns:
            str: pretty string representation of an instance.
            
        """
        new_line = '\n'
        representation = [f'sourdough {self.get_name}']
        for key, value in self.contents.items():
            if isinstance(value, Sequence):
                names = [v.name for v in value]
                representation.append(f'{key}: {", ".join(names)}')
            else:
                representation.append(f'{key}: {value}')
        return new_line.join(representation)    

    """ Private Methods """

    def _get_type(self, 
            item: 'sourdough.Component', 
            component: 'sourdough.Component') -> Sequence[
                'sourdough.Component']: 
        """[summary]

        Args:
            item (sourdough.Component): [description]
            sourdough.Component (sourdough.Component): [description]

        Returns:
            Sequence[sourdough.Component]:
            
        """
        if isinstance(item, component):
            return [item]
        else:
            return []
        

@dataclasses.dataclass
class Worker(sourdough.Hybrid):
    """Iterator in sourdough composite projects.

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
    contents: Union[
        'sourdough.Component',
        Mapping[Any, 'sourdough.Component'],
        Mapping[str, str], 
        Sequence['sourdough.Component'],
        Sequence[str]] = dataclasses.field(default_factory = list)
    name: str = None
    role: Union['sourdough.Role', str] = 'progression'
      
    """ Properties """
    
    @property
    def overview(self) -> 'Overview':
        """Returns a dict snapshot of a Worker subclass instance.
        
        Returns:
            Overview: based on the stored 'contents' of an instance.
        
        """
        return Overview(worker = self)

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
            return self.role.__iter__()
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
    contents: Sequence[Union['sourdough.Task', 'Manager']] = dataclasses.field(
        default_factory = list)
    name: str = None
    role: Union['sourdough.Role', str] = 'progression'
    options: ClassVar['Inventory'] = Inventory(
        contents = {
            'create': sourdough.Create,
            'job': sourdough.Job,
            'study': sourdough.Study,
            'survey': sourdough.Survey,
            
        })
    
    """ Public Methods """
    
    def validate(self, 
            contents: Union[
                Tuple[str, str],
                'sourdough.Task',
                'Manager',
                Sequence[Union[
                    Tuple[str, str],
                    'sourdough.Task',
                    'Manager']]]) -> Sequence[Union[
                        'sourdough.Task', 
                        'Manager']]:
        """Validates 'contents' or converts 'contents' to proper type.
        
        Args:

            
        Raises:
            TypeError: if 'contents' argument is not of a supported datatype.
            
        Returns:

                
        """
        new_contents = []
        if isinstance(contents, (Tuple[str, str], sourdough.Task, Manager)):
            new_contents = [contents]
        elif isinstance(contents, Sequence):
            for item in contents:
                if (isinstance(item, Tuple)
                        and len(item) == 2
                        and all(isinstance(item, str) for i in item)):
                    new_contents.append(
                        sourdough.Task(name = item[0], technique = item[1]))
                elif isinstance(item, (sourdough.Task, Manager)):
                    new_contents.append(item)
                else:
                    raise TypeError(
                        'contents must be a list containing Task instances, '
                        'Manager instances, or Tuples of two str types')
        else:
            raise TypeError('contents must be a list')
        return new_contents

    def add(self, 
            contents: Union[
                Tuple[str, str],
                'sourdough.Task',
                'Manager',
                Sequence[Union[
                    Tuple[str, str],
                    'sourdough.Task',
                    'Manager']]]) -> None:
        """Extends 'contents' argument to 'contents' attribute.
        
        Args:

        """
        super().add(contents = contents)
        return self    
    
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
            return self.role.__iter__()
        except (AttributeError, TypeError):
            return iter(self.contents)
        
    """ Private Methods """
    
    def _initial_validation(self) -> None:
        """Validates passed 'contents' on class initialization."""
        super()._initial_validation()
        # Validates or converts 'role'.
        self = sourdough.Role.validate(worker = self)
        return self
              