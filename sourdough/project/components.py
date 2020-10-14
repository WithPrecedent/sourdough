"""
components: classes for sourdough composite objects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    
"""
from __future__ import annotations
import collections.abc
import dataclasses
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Union)

import sourdough


@dataclasses.dataclass
class Technique(sourdough.quirks.Loader, sourdough.Component):
    """Base class for primitive objects in a sourdough composite object.
    
    The 'contents' and 'parameters' attributes are combined at the last moment
    to allow for runtime alterations.
    
    Args:
        contents (object): core object used by the 'perform' method. Defaults 
            to None.
        parameters (Mapping[Any, Any]]): parameters to be attached to
            'contents' when the 'perform' method is called. Defaults to an 
            empty dict.
        modules Union[str, Sequence[str]]: name(s) of module(s) where the 
            contents to load is/are located. Defaults to an empty list.
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
        _loaded (ClassVar[Mapping[Any, Any]]): dict of str keys and previously
            loaded objects. This is checked first by the 'load' method to avoid
            unnecessary re-importation. Defaults to an empty dict.
                                    
    """
    contents: object = None
    parameters: Mapping[Any, Any] = dataclasses.field(default_factory = dict)
    modules: Union[str, Sequence[str]] = dataclasses.field(
        default_factory = list)
    name: str = None
    _loaded: ClassVar[Mapping[Any, Any]] = {}

    """ Initialization Methods """
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Adds new subclass to 'library'.
        if not hasattr(cls, '_base'):
            cls._base = cls

    """ Properties """
    
    @property
    def algorithm(self) -> Union[object, str]:
        return self.contents
    
    @algorithm.setter
    def algorithm(self, value: Union[object, str]) -> None:
        self.contents = value
        return self
    
    @algorithm.deleter
    def algorithm(self) -> None:
        self.contents = None
        return self
        
    """ Public Methods """
    
    def perform(self, data: object = None, **kwargs) -> object:
        """Applies stored 'contents' with 'parameters'.
        
        Args:
            data (object): optional object to apply 'contents' to. Defaults to
                None.
                
        Returns:
            object: with any modifications made by 'contents'. If data is not
                passed, nothing is returned.        
        
        """
        self.contents = self.load(key = self.name)
        if data is None:
            self.contents.perform(**self.parameters, **kwargs)
            return self
        else:
            return self.contents.perform(data, **self.parameters, **kwargs)

             
@dataclasses.dataclass
class Step(sourdough.Component):
    """Wrapper for a Technique.

    Subclasses of Step can store additional methods and attributes to apply to 
    all possible technique instances that could be used. This is often useful 
    when creating 'comparative' Worker instances which test a variety of 
    strategies with similar or identical parameters and/or methods.

    A Step instance will try to return attributes from 'technique' if the
    attribute is not found in the Step instance. 

    Args:
        technique (Technique): technique object for this Worker in a sourdough
            sequence. Defaults to None.
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
        contains (ClassVar[Sequence[str]]): list of snake-named base class
            types that can be stored in this component. Defaults to a list
            containing 'technique'.
        containers (ClassVar[Sequence[str]]): list of snake-named base class
            types that can store this component. Defaults to a list containing
            'Worker' and 'manager'. 
                        
    """
    contents: Union['Technique', str] = None
    name: str = None

    """ Initialization Methods """
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Adds new subclass to 'library'.
        if not hasattr(cls, '_base'):
            cls._base = cls
                
    """ Properties """
    
    @property
    def technique(self) -> Union['Technique', str]:
        return self.contents
    
    @technique.setter
    def technique(self, value: Union['Technique', str]) -> None:
        self.contents = value
        return self
    
    @technique.deleter
    def technique(self) -> None:
        self.contents = None
        return self
    
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

    """ Dunder Methods """

    def __getattr__(self, attribute: str) -> Any:
        """Looks for 'attribute' in 'contents'.

        Args:
            attribute (str): name of attribute to return.

        Raises:
            AttributeError: if 'attribute' is not found in 'contents'.

        Returns:
            Any: matching attribute.

        """
        try:
            return getattr(self.contents, attribute)
        except AttributeError:
            raise AttributeError(
                f'{attribute} neither found in {self.name} nor '
                f'{self.contents}') 
   

@dataclasses.dataclass
class Worker(sourdough.Component, sourdough.Hybrid):
    """Base class for composite objects in sourdough projects.
    
    Worker differs from an ordinary Hybrid in 1 significant way:
        1) It is mixed in with Sequencify which allows for type validation and 
            conversion, using the 'verify' and 'convert' methods.
            
    Args:
        contents (collections.abc.Collection): a python Collection of items. 
            Defaults to an empty list.
        name (str): property which designates the internal reference of a class 
            instance that is used throughout sourdough. For example, if a 
            sourdough instance needs options from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            Defaults to None. If 'name' is None, it will be assigned to the 
            snake case version of the class name ('__name__' or 
            '__class__.__name__').
                            
    """
    contents: collections.abc.Collection = dataclasses.field(
        default_factory = list)
    name: str = None
    branches: ClassVar[bool] = False 
    
    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent and/or mixin initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass 
        # Initializes 'index' for iteration.
        self.index = -1

    """ Public Methods """
    
    def perform(self, data: object = None, **kwargs) -> NotImplementedError:
        """Subclasses must provide their own methods.       
        
        """
        raise NotImplementedError(
            'subclasses of Worker must provide their own perform methods')
                   
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


# @dataclasses.dataclass
# class Element(Component):
#     """                     
#     """
#     name: str = None
#     contents: Union[object, Callable] = None
    
#     """ Initialization Methods """
    
#     def __post_init__(self) -> None:
#         """Initializes class instance attributes."""
#         # Calls parent and/or mixin initialization method(s).
#         try:
#             super().__post_init__()
#         except AttributeError:
#             pass 

#     """ Public Methods """
    
#     def perform(self, data: object = None, **kwargs) -> NotImplementedError:
#         """Subclasses must provide their own methods.       
        
#         """
#         raise NotImplementedError(
#             'subclasses of Element must provide their own perform methods') 
