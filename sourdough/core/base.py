"""
base: sourdough base classes for accessing and loading sourdough objects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:

 
"""
from __future__ import annotations
import abc
import dataclasses
import functools
import inspect
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Union)

import sourdough


@dataclasses.dataclass
class Components(sourdough.quirks.Library):
    """Base class for all pieces of sourdough composite objects.
    
    A Components differs from a Library in 3 significant ways:
        1) It includes a 'contents' attribute which can store any type of
            object as part of a larger composite structure. In this way, 
            Component acts as a wrapper for pieces in a composite whole.
        2) It includes a registry that stores all subclasses in 'registry'. This
            makes it easy to access any imported Component subclass using a
            string key.
        3) It has several private class methods which allow access to 'registry' 
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
        registry (ClassVar[Mapping[str, Callable]): stores subclasses. The keys 
            are derived from the 'name' property of subclasses and values are
            the subclasses themselves. Defaults to an empty Catalog instance.
              
    """
    name: str = None
    contents: Any = None
    library: ClassVar[Mapping[str, Callable]] = sourdough.Catalog()
        
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
class Structure(sourdough.quirks.Registry, sourdough.Hybrid):
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
        registry (ClassVar[Mapping[str, Callable]): stores subclasses. The keys 
            are derived from the 'name' property of subclasses and values are
            the subclasses themselves. Defaults to an empty Catalog instance.
                            
    """
    name: str = None
    contents: Union[Sequence[str], Sequence[Any]] = dataclasses.field(
        default_factory = list)
    registry: ClassVar[Mapping[str, Callable]] = sourdough.Catalog()
    
    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent initialization method(s).
        print('test structure contents', self.contents)
        super().__post_init__()    
        print('test structure contents post super', self.contents)    
        # Initializes 'index' for iteration.
        self.index = -1

    """ Public Methods """
    
    def perform(self, data: object = None, **kwargs) -> object:
        """Subclasses must provide their own methods.
        
        The code below outlines a basic method that a subclass should build on
        for a properly functioning Step.
        
        Applies stored 'contents' with 'parameters'.
        
        Args:
            data (object): optional object to apply 'contents' to. Defaults to
                None.
                
        Returns:
            object: with any modifications made by 'contents'. If data is not
                passed, nothing is returned.        
        
        """
        if data is None:
            self.contents.perform(**kwargs)
            return self
        else:
            return self.contents.perform(item = data, **kwargs)
                   
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
    
    # def __iter__(self) -> Iterable:
    #     if self.index + 1 < len(self.contents):
    #         self.index += 1
    #         yield self.iterate()
    #     else:
    #         raise StopIteration


@dataclasses.dataclass
class Stage(sourdough.quirks.Registry):
    """Base class for a stage in a Workflow.
    
    Args:
        name (str): property which designates the internal reference of a class 
            instance that is used throughout sourdough. For example, if a 
            sourdough instance needs options from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            Defaults to None. If 'name' is None, it will be assigned to the 
            snake case version of the class name ('__name__' or 
            '__class__.__name__').
        registry (ClassVar[Mapping[str, Callable]): stores subclasses. The keys 
            are derived from the 'name' property of subclasses and values are
            the subclasses themselves. Defaults to an empty Catalog instance.
            
    """
    action: str = None
    registry: ClassVar[Mapping[str, Callable]] = sourdough.Catalog()

    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def perform(self, project: sourdough.Project, **kwargs) -> sourdough.Project:
        """Performs some action based on 'project' and kwargs.
        
        Subclasses must provide their own methods.
        
        """
        pass

    """ Private Methods """
    
    def _get_need(self, name: str, project: sourdough.Project) -> Any:
        try:
            return getattr(project, name)
        except AttributeError:
            return project.results[name]
        
    def _set_product(self, name: str, product: Any, 
                     project: sourdough.Project) -> None:
        project.results[name] = product
        return project
                

@dataclasses.dataclass
class Workflow(sourdough.quirks.Registry, sourdough.Hybrid):
    """Base class for sourdough workflows.
    
    Args:
        contents (Sequence[Union[str, Stage]]): a list of str or Stages. 
            Defaults to an empty list.
        project (sourdough.Project): related project instance.
        registry (ClassVar[Mapping[str, Callable]): stores subclasses. The keys 
            are derived from the 'name' property of subclasses and values are
            the subclasses themselves. Defaults to an empty Catalog instance.
               
    """
    contents: Union[Sequence[str], Sequence[Workflow]] = dataclasses.field(
        default_factory = list)
    project: sourdough.Project = None
    name: str = None
    registry: ClassVar[Mapping[str, Callable]] = sourdough.Catalog()

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass
        # Validates or converts 'contents'.
        self._initialize_stages()
         
    """ Private Methods """
    
    def _initialize_stages(self) -> None:
        """[summary]

        Raises:
            TypeError: [description]

        Returns:
            [type]: [description]
            
        """
        new_stages = []
        for stage in self.contents:
            if isinstance(stage, str):
                new_stages.append(Stage.instance(stage))
            elif issubclass(stage, Stage):
                new_stages.append(stage())
            else:
                raise TypeError('All stages must be str or Stage type')
        self.contents = new_stages
        return self
