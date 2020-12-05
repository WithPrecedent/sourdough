"""
elements: primitive Component subclasses
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Technique (Loader, Component): base-level class to apply algorithms as
        part of a Workflow.
    Step (Component): wrapper for a Technique used in construction of parallel
        Workflows.
    
"""
from __future__ import annotations
import collections.abc
import dataclasses
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import sourdough


@dataclasses.dataclass
class Technique(sourdough.Component):
    """Base class for primitive objects in a sourdough composite object.
    
    The 'contents' and 'parameters' attributes are combined at the last moment
    to allow for runtime alterations.
    
    Args:
        contents (Callable, str): core object used by the 'apply' method or a
            str matching a callable object in the algorithms resource. Defaults 
            to None.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. 
        parameters (Mapping[Any, Any]]): parameters to be attached to 'contents' 
            when the 'apply' method is called. Defaults to an empty dict.
                                    
    """
    contents: Union[Callable, str] = None
    name: str = None
    parameters: Mapping[Any, Any] = dataclasses.field(default_factory = dict)

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
    
    def apply(self, data: object = None, **kwargs) -> object:
        """Applies stored 'contents' with 'parameters'.
        
        Args:
            data (object): optional object to apply 'contents' to. Defaults to
                None.
                
        Returns:
            object: with any modifications made by 'contents'. If data is not
                passed, nothing is returned.        
        
        """
        if data is None:
            if self.contents:
                data = self.contents.apply(**self.parameters, **kwargs)
            return data
        else:
            if self.contents:
                return self.contents.apply(data, **self.parameters, **kwargs)
            else:
                return None

             
@dataclasses.dataclass
class Step(sourdough.Component):
    """Wrapper for a Technique.

    Subclasses of Step can store additional methods and attributes to apply to 
    all possible technique instances that could be used. This is often useful 
    when using parallel Worklow instances which test a variety of strategies 
    with similar or identical parameters and/or methods.

    A Step instance will try to return attributes from Technique if the
    attribute is not found in the Step instance. 

    Args:
        contents (Technique): technique instance to be used in a Workflow.
            Defaults ot None.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. 
                        
    """
    contents: Union[Technique, str] = None
    name: str = None
                
    """ Properties """
    
    @property
    def technique(self) -> Technique:
        return self.contents
    
    @technique.setter
    def technique(self, value: Technique) -> None:
        self.contents = value
        return self
    
    @technique.deleter
    def technique(self) -> None:
        self.contents = None
        return self
    
    """ Public Methods """
    
    def apply(self, data: object = None, **kwargs) -> object:
        """Applies Technique instance in 'contents'.
        
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
            self.contents.apply(**kwargs)
            return self
        else:
            return self.contents.apply(data = data, **kwargs)

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
            raise AttributeError(f'{attribute} neither found in {self.name} '
                                 f'nor {self.contents}') 
