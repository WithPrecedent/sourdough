"""
components: core pieces of a sourdough composite object
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Technique (Action): primitive object which performs some action.
    Task (Action): wrapper for Technique which performs some action (optional).

"""

import dataclasses
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
        parameters (Mapping[Any, Any]]): parameters to be attached to
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
    parameters: Mapping[Any, Any] = dataclasses.field(default_factory = dict)
    name: str = None
    selected: Sequence[str] = None
    required: Mapping[Any, str] = None
    runtime: Mapping[Any, str] = None
    data_dependent: Mapping[Any, str] = None
    
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
    technique: Union[Technique, str] = None
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
            self.technique.perform(item = data, **kwargs)
            return self
        else:
            return self.technique.perform(item = data, **kwargs)

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
                f'{self.technique}')
            
            
@dataclasses.dataclass
class Edge(sourdough.Component):
    """An edge in a sourdough Graph.

    'start' and 'stop' are the ends of the Edge. However, which value is 
    assigned to each attribute only matters in a directional graph.

    By default Edge is slotted so that no other attributes can be added. This
    lowers memory consumption and increases speed. If you wish to add more 
    functionality to your Graph edges, you should subclass Edge.

    Args:
        start (str): name of the Component where the edge starts.
        stop (str): name of the Component where the edge ends.
        directed (bool): whether this edge is directed (True). Defaults to 
            False. 
        weight (float): a weight value assigned to this edge. Defaults to None.

    """
    start: 'sourdough.Node' = None
    stop: 'sourdough.Node' = None
    directed: bool = False
    weight: float = 1.0
    name: str = None
    
    """ Public Methods """

    def get_name(self) -> str:
        """Returns 'name' based upon attached nodes.
        
        Returns:
            str: name of class for internal referencing.
        
        """
        return f'{self.start.name}_to_{self.stop.name}'


@dataclasses.dataclass
class Node(sourdough.Component):
    """An edge in a sourdough Graph.

    'start' and 'stop' are the ends of the Edge. However, which value is 
    assigned to each attribute only matters in a directional graph.

    By default Edge is slotted so that no other attributes can be added. This
    lowers memory consumption and increases speed. If you wish to add more 
    functionality to your Graph edges, you should subclass Edge.

    Args:
        start (str): name of the Component where the edge starts.
        stop (str): name of the Component where the edge ends.
        directed (bool): whether this edge is directed (True). Defaults to 
            False. 
        weight (float): a weight value assigned to this edge. Defaults to None.

    """

    name: str = None
    edges: Sequence['Edge'] = dataclasses.field(default_factory = list)
    