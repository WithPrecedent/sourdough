"""
actions: composite objects in a sourdough project that perform some action
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Technique (Action): primitive object which performs some action.
    Task (Action): wrapper for Technique which performs some action (optional).

"""

import abc
import dataclasses
import textwrap
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union

import sourdough


@dataclasses.dataclass
class Technique(sourdough.Action):
    """Base class for primitive objects in a sourdough composite object.
    
    The 'algorithm' and 'parameters' attributes are combined at the last moment
    to allow for runtime alterations.
    
    Args:
        algorithm (object): core object used by the 'perform' method. Defaults 
            to None.
        parameters (Mapping[str, Any]]): parameters to be attached to
            'algorithm' when the 'perform' method is called. Defaults to an 
            empty dict.
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
    algorithm: object = None
    parameters: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    name: str = None
    selected: Sequence[str] = None
    required: Mapping[str, str] = None
    runtime: Mapping[str, str] = None
    data_dependent: Mapping[str, str] = None
    
    """ Public Methods """
    
    def perform(self, data: object = None, **kwargs) -> object:
        """Applies stored 'algorithm' with 'parameters'.
        
        Args:
            data (object): optional object to apply 'algorithm' to. Defaults to
                None.
                
        Returns:
            object: with any modifications made by 'algorithm'. If data is not
                passed, nothing is returned.        
        
        """
        if data is None:
            self.algorithm(**self.parameters, **kwargs)
            return self
        else:
            return self.algorithm(data, **self.parameters, **kwargs)
        
    """ Dunder Methods """

    def __repr__(self) -> str:
        """Returns string representation of a class instance."""
        return self.__str__()

    def __str__(self) -> str:
        """Returns string representation of a class instance."""
        return textwrap.dedent(f'''
            sourdough {self.__class__.__name__} {self.name}
            algorithm: {str(self.algorithm)}
            parameters: {str(self.parameters)}''')
        
            
@dataclasses.dataclass
class Task(sourdough.Action):
    """Wrapper for a Technique.

    Subclasses of Task can store additional methods and attributes to apply to 
    all possible technique instances that could be used. This is often useful 
    when creating 'comparative' Worker instances which test a variety of 
    strategies with similar or identical parameters and/or methods.

    A Task instance will try to return attributes from 'technique' if the
    attribute is not found in the Task instance. 

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
            
    """
    technique: Technique = None
    name: str = None

    """ Public Methods """
    
    def perform(self, data: object = None, **kwargs) -> object:
        """Subclasses must provide their own methods.
        
        The code below outlines a basic method that a subclass should build on
        for a properly functioning Task.
        
        Applies stored 'algorithm' with 'parameters'.
        
        Args:
            data (object): optional object to apply 'algorithm' to. Defaults to
                None.
                
        Returns:
            object: with any modifications made by 'algorithm'. If data is not
                passed, nothing is returned.        
        
        """
        if data is None:
            self.technique.perform(data = data, **kwargs)
            return self
        else:
            return self.technique.perform(data = data, **kwargs)

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
                f'{attribute} neither found in {self.name} nor '
                 '{self.technique}')

    def __repr__(self) -> str:
        """Returns string representation of a class instance."""
        return self.__str__()

    def __str__(self) -> str:
        """Returns string representation of a class instance."""
        return textwrap.dedent(f'''
            sourdough {self.__class__.__name__} {self.name}
            technique: {str(self.technique)}''')
