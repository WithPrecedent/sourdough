"""
base: sourdough base classes for accessing and loading sourdough objects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:

 
"""
from __future__ import annotations
import abc
import collections.abc
import dataclasses
import functools
import inspect
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Union)

import sourdough

@sourdough.namify
@dataclasses.dataclass
class Component(collections.abc.Container, abc.ABC):
    """Base class for all pieces of sourdough composite objects.
    
    A Component differs from a Container in 3 significant ways:
        1) It includes a 'contents' attribute which can store any type of
            object as part of a larger composite structure. In this way, 
            Component acts as a wrapper for pieces in a composite whole.
        2) It includes a 'library' registry that stores all subclasses. This
            makes it easy to access any imported Component subclass using a
            string key.
        3) It has several private class methods which allow access to 'library' 
            using other techniques other than the associated string key.
    
    Args:
        contents (Any): a stored object.
        name (str): property which designates the internal reference of a class 
            instance that is used throughout sourdough. For example, if a 
            sourdough instance needs options from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            Defaults to None. If 'name' is None, it will be assigned to the 
            snake case version of the class name ('__name__' or 
            '__class__.__name__').
        library (ClassVar[Mapping[str, Callable]): stores subclasses. The keys 
            are derived from the 'name' property of subclasses and values are
            the subclasses themselves. Defaults to an empty Catalog instance.
              
    """
    name: str = None
    contents: Any = None
    library: ClassVar[Mapping[str, Callable]] = sourdough.Catalog()

    """ Initialization Methods """
    
    def __init_subclass__(cls, **kwargs):
        """Adds 'cls' to 'library' if it is a concrete class."""
        super().__init_subclass__(**kwargs)
        if not abc.ABC in cls.__bases__:
            cls.library[cls.name] = cls
            
    # """ Properties """
    
    # @property
    # def name(self) -> str:
    #     """Sets 'name' property.

    #     Returns:
    #         str: 'name' passed to a subclass instance or the snake case name of
    #             either '__name__' or '__class__.__name__'.
        
    #     """
    #     if self._name is None:
    #         try:
    #             return sourdough.tools.snakify(self.__name__)
    #         except AttributeError:
    #             return sourdough.tools.snakify(self.__class__.__name__)
    #     else:
    #         return self._name

    # @name.setter
    # def name(self, value: str) -> None:
    #     """Sets '_name' to 'value'.
        
    #     Args:
    #         value (str): str to set 'name' property to.
            
    #     """
    #     self._name = value
    #     return self
    
    """ Class Methods """

    @classmethod
    def instance(cls, key: Union[str, Sequence[str]], **kwargs) -> Union[
                 object, Sequence[object]]:
        """Returns instance(s) of a stored class(es).
        
        This method acts as a factory for instancing stored classes.
        
        Args:
            key (Union[str, Sequence[str]]): name(s) of key(s) in 'contents'.
            kwargs: arguments to pass to the selected item(s) when instanced.
                    
        Returns:
            Union[object, Sequence[object]]: instance(s) of stored classes.
            
        """
        return cls.library.instance(key = key, **kwargs)
 
    @classmethod
    def select(cls, key: Union[str, Sequence[str]]) -> Union[
               Any, Sequence[Any]]:
        """Returns value(s) stored in 'contents'.

        Args:
            key (Union[str, Sequence[str]]): name(s) of key(s) in 'contents'.

        Returns:
            Union[Any, Sequence[Any]]: stored value(s).
            
        """
        return cls.library.select(key = key)
 
    """ Dunder Methods """
    
    def __contains__(self, item: object) -> bool:
        """
        """
        return item in self.contents
        
    """ Private Class Methods """

    @classmethod
    def _get_keys_by_type(cls, component: Component) -> Sequence[Component]:
        """[summary]

        Returns:
        
            [type]: [description]
            
        """
        return [k for k, v in cls.library.items() if issubclass(v, component)]

    @classmethod
    def _get_values_by_type(cls, component: Component) -> Sequence[Component]:
        """[summary]

        Returns:
        
            [type]: [description]
            
        """
        return [v for k, v in cls.library.items() if issubclass(v, component)]
   
    @classmethod
    def _suffixify(cls) -> Mapping[str, Component]:
        """[summary]

        Returns:
            [type]: [description]
        """
        return {f'_{k}s': v for k, v in cls.library.items()}   

   
@dataclasses.dataclass
class Structure(sourdough.Factory, sourdough.Hybrid, Component, abc.ABC):
    """Base class for composite objects in sourdough projects.
    
    Structure differs from an ordinary Hybrid in 1 significant way:
        1) It is mixed in with Sequencify which allows for type validation and 
            conversion, using the 'verify' and 'convert' methods.
            
    Args:
        contents (Sequence[Union[str, Component]]): a list of str or Components. 
            Defaults to an empty list.
        name (str): property which designates the internal reference of a class 
            instance that is used throughout sourdough. For example, if a 
            sourdough instance needs options from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            Defaults to None. If 'name' is None, it will be assigned to the 
            snake case version of the class name ('__name__' or 
            '__class__.__name__').
                
    """
    name: str
    contents: Sequence[Union[str, Stage]] = dataclasses.field(
        default_factory = list)
    _name: str = dataclasses.field(init = False, repr = False)
    library: ClassVar[Mapping[str, Callable]] = sourdough.Catalog()
    
    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent initialization method(s).
        super().__post_init__()        
        # Initializes 'index' for iteration.
        self.index = -1
            
    """ Required Subclass Methods """
    
    # @abc.abstractmethod
    # def iterate(self, **kwargs) -> Iterable:
    #     pass
    
    # @abc.abstractmethod
    # def activate(self, **kwargs) -> Iterable:
    #     pass    
    
    # @abc.abstractmethod
    # def finalize(self, **kwargs) -> Iterable:
    #     pass
  
    """ Dunder Methods """
    
    def __iter__(self) -> Iterable:
        if self.index + 1 < len(self.contents):
            self.index += 1
            yield self.iterate()
        else:
            raise StopIteration


@dataclasses.dataclass
class Stage(sourdough.Factory, abc.ABC):
    """Base class for a stage in a Workflow.
    
    Args:
        name (str): property which designates the internal reference of a class 
            instance that is used throughout sourdough. For example, if a 
            sourdough instance needs options from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            Defaults to None. If 'name' is None, it will be assigned to the 
            snake case version of the class name ('__name__' or 
            '__class__.__name__').
        library (ClassVar[Mapping[str, Callable]): stores subclasses. The keys 
            are derived from the 'name' property of subclasses and values are
            the subclasses themselves. Defaults to an empty Catalog instance.
            
    """
    name: str
    _name: str = dataclasses.field(init = False, repr = False)
    library: ClassVar[Mapping[str, Callable]] = sourdough.Catalog()

    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def perform(self, project: sourdough.interface.Project, **kwargs) -> object:
        """Performs some action related to kwargs.
        
        Subclasses must provide their own methods.
        
        """
        pass
        

@dataclasses.dataclass
class Workflow(sourdough.Factory, sourdough.Hybrid, abc.ABC):
    """Base class for sourdough workflows.
    
    Args:
        contents (Sequence[Union[str, Stage]]): a list of str or Stages. 
            Defaults to an empty list.
        name (str): property which designates the internal reference of a class 
            instance that is used throughout sourdough. For example, if a 
            sourdough instance needs options from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            Defaults to None. If 'name' is None, it will be assigned to the 
            snake case version of the class name ('__name__' or 
            '__class__.__name__').   
        library (ClassVar[Mapping[str, Callable]): stores subclasses. The keys 
            are derived from the 'name' property of subclasses and values are
            the subclasses themselves. Defaults to an empty Catalog instance.
               
    """
    name: str
    contents: Sequence[Union[str, Stage]] = dataclasses.field(
        default_factory = list)
    _name: str = dataclasses.field(init = False, repr = False)
    library: ClassVar[Mapping[str, Callable]] = sourdough.Catalog()

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass
        # Validates or converts 'contents'.
        self.contents = self.convert(contents = self.contents)
        
    """ Public Methods """

    def perform(self, project: sourdough.Project) -> sourdough.Project:
        """[summary]

        Args:
            project (sourdough.Project): [description]

        Returns:
            sourdough.Project: [description]
        """
        for step in self.contents:
            instance = step()
            parameters = self._get_stage_parameters(
                flow = step, 
                project = project)
            result = instance.perform(**parameters)
            setattr(project, result.name, result)
        return project
    
    """ Private Methods """
       
    def _get_stage_parameters(self, 
            flow: Stage,
            project: sourdough.Project) -> Mapping[str, Any]:
        """[summary]

        Args:
            flow (Stage): [description]

        Returns:
            Mapping[str, Any]: [description]
            
        """
        parameters = {}
        for need in flow.needs:
            if need in ['project']:
                parameters['project'] = project
            else:
                parameters[need] = getattr(project, need)
        return parameters


@dataclasses.dataclass
class Quirk(sourdough.Factory, abc.ABC):
    """Base class for sourdough mixins.
    
    Quirk automatically stores all non-abstract subclasses in the 'options' 
    class attribute.

    Args:
        library (ClassVar[Mapping[str, Callable]): stores subclasses. The keys 
            are derived from the 'name' property of subclasses and values are
            the subclasses themselves. Defaults to an empty Catalog instance.
                
    """
    name: str
    _name: str = dataclasses.field(init = False, repr = False)
    library: ClassVar[Mapping[str, Callable]] = sourdough.Catalog()
    
    """ Initialization Methods """
    
    """ Required Subclass Methods """
    
    @classmethod
    @abc.abstractmethod
    def inject(self, item: Any) -> Any:
        """Subclasses must provide their own methods.
        
        This method should add methods, attributes, and/or properties to the
        passed argument.
        
        """
        pass
