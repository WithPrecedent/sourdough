"""
components: core pieces of sourdough composite objects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Component (Element, RegistryMixin): base class for all elements of a 
        sourdough composite object. If you want to create custom elements for
        composites, you must subclass Component or one of its subclasses for
        the auto-registration library to work.
    Technique (Component, Action): primitive object which performs some action.
    Task (Component, Action): wrapper for Technique which performs some action 
        (optional). Task can be useful when using Role subclasses with parallel
        structures such as Compare and Survey.
    Worker (Component, Hybrid): iterable container in composite objects.
    Manager (Worker): a subclass of Worker which stores metadata and the rest 
        of the sourdough Composition object. There should be only one Manager or
        Manager subclass per composite object.

"""
from __future__ import annotations
import abc
import dataclasses
import typing
from typing import (Any, Callable, ClassVar, Container, Generic, Iterable, 
                    Iterator, Mapping, Sequence, Tuple, TypeVar, Union)

import sourdough


@dataclasses.dataclass
class Component(sourdough.RegistryMixin, sourdough.Element, abc.ABC):
    """Base class for pieces of sourdough composite objects.
    
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Element is called, 'name' is set based upon
            the 'get_name' method in Element. If that method is not 
            overridden by a subclass instance, 'name' will be assigned to the 
            snake case version of the class name ('__class__.__name__'). 
        registry (ClassVar[sourdough.Inventory]): the instance which 
            automatically stores any subclass of Component.
              
    """
    contents: Any = None
    name: str = None
    registry: ClassVar[sourdough.Inventory] = sourdough.Inventory()

    """ Properties """
    
    @property
    def contains(self) -> Sequence[Any]:
        try:
            return typing.get_args(self.__annotations__['contents'])
        except AttributeError:
            return (sourdough.Component, str)

    """ Public Methods """
    
    def validate(self, contents: Any) -> Any:
        if isinstance(contents, self.contains):
            return contents
        else:
            raise TypeError(f'contents must be {str(self.contains)} types')     

    """ Private Class Methods """

    @classmethod
    def _get_keys_by_type(cls, 
            component: Component) -> Sequence[Component]:
        """[summary]

        Returns:
        
            [type]: [description]
            
        """
        return [k for k, v in cls.registry.items() if issubclass(v, component)]

    @classmethod
    def _get_values_by_type(cls, 
            component: Component) -> Sequence[Component]:
        """[summary]

        Returns:
        
            [type]: [description]
            
        """
        return [v for k, v in cls.registry.items() if issubclass(v, component)]
   
    @classmethod
    def _suffixify(cls) -> Mapping[str, Component]:
        """[summary]

        Returns:
            [type]: [description]
        """
        return {f'_{k}s': v for k, v in cls.registry.items()}   

    
@dataclasses.dataclass
class Technique(sourdough.LoaderMixin, sourdough.Action, Component):
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
        # Adds new subclass to 'registry'.
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
class Task(sourdough.Action, Component):
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
        contains (ClassVar[Sequence[str]]): list of snake-named base class
            types that can be stored in this component. Defaults to a list
            containing 'technique'.
        containers (ClassVar[Sequence[str]]): list of snake-named base class
            types that can store this component. Defaults to a list containing
            'worker' and 'manager'. 
                        
    """
    contents: Union['Technique', str] = None
    name: str = None

    """ Initialization Methods """
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Adds new subclass to 'registry'.
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
        for a properly functioning Task.
        
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
class Worker(sourdough.Hybrid, Component):
    """A lightweight container for a sourdough project.

    Worker inherits all of the differences between a Hybrid and a python list.
    
    A Worker differs from a Hybrid in 3 significant ways:
        1) It has a 'structure' attribute which indicates how the contained 
            iterator should be ordered. 
        2) An 'overview' property is added which returns a dict of the names
            of the various parts of the tree objects. It doesn't include the
            hierarchy itself. Rather, it includes lists of all the types of
            sourdough.Component objects.
        3) It has 'contains' and 'containers' class attributes inherited from
            Component which describe permissible relationships with other
            Component subclasses.
        
    Args:
        contents (Sequence[sourdough.Component]]): stored iterable of Component
            subclasses. Defaults to an empty list.
        structure (Union[sourdough.Role, str]): structure for the organization, iteration, 
            and composition of 'contents' or a str corresponding to an option in 
            'Role.registry'.
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

    Attributes:
        contents (Sequence[sourdough.Component]): all objects in 'contents' must 
            be sourdough Component subclass instances and are stored in a list.
        _default (Any): default value to use when there is a KeyError using the
            'get' method.    

    ToDo:
        draw: a method for producting a diagram of a Worker instance's 
            'contents' to the console or a file.
            
    """
    contents: Sequence[Union[
        'Worker', 
        'Task', 
        'Technique', 
        str]] = dataclasses.field(default_factory = list)
    outline: sourdough.Outline = sourdough.Outline()
    structure: Union[sourdough.Role, str] = 'obey'
    name: str = None

    """ Initialization Methods """
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Adds new subclass to 'registry'.
        if not hasattr(cls, '_base'):
            cls._base = cls
                      
    """ Properties """
    
    @property
    def overview(self) -> sourdough.Overview:
        """Returns a dict snapshot of a Worker subclass instance.
        
        Returns:
            sourdough.Overview: based on the stored 'contents' of an instance.
        
        """
        return sourdough.Overview(worker = self)   
  
    """ Dunder Methods """
    
    # def __iter__(self) -> Iterable:
    #     """Returns iterable of 'contents' based upon 'structure'.
        
    #     If 'structure' has not been initialized, this method returns the default
    #     python 'iter' method of 'contents'. This should not happen as long as
    #     the '__post_init__' method from Hybrid is not overwritten without 
    #     calling 'super().__post_init__'.
        
    #     Returns:
    #         Iterable: of 'contents'.
            
    #     """
    #     try:
    #         return iter(self.structure)
    #     except (AttributeError, TypeError):
    #         return iter(self.contents)
        
    """ Private Methods """
    
    # def _initial_validation(self) -> None:
    #     """Validates passed 'contents' on class initialization."""
    #     super()._initial_validation()
    #     # Validates or converts 'structure'.
    #     self = sourdough.Role.validate(worker = self)
    #     return self


@dataclasses.dataclass
class Manager(Worker):
    """A lightweight container for a sourdough project with metadata.
    
    Args:
        contents (Sequence[sourdough.Component]]): stored iterable of Component
            subclasses. Defaults to an empty list.
        structure (Union[sourdough.Role, str]): structure for the organization, iteration, 
            and composition of 'contents' or a str corresponding to an option in 
            'Role.registry'.
        identification (str): a unique identification name for a 
            Project instance. The name is used for creating file folders
            related to the 'Project'. If not provided, a string is created from
            'name' and the date and time. This is a notable difference
            between an ordinary Worker instancce and a Project instance. Other
            Workers are not given unique identification. Defaults to None.  
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
    contents: Sequence[Union[
        'Worker', 
        'Task', 
        'Technique', 
        str]] = dataclasses.field(default_factory = list)
    outline: sourdough.Outline = sourdough.Outline()
    structure: Union[sourdough.Role, str] = 'obey'
    identification: str = None
    name: str = None                    

    """ Initialization Methods """
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Adds new subclass to 'registry'.
        if not hasattr(cls, '_base'):
            cls._base = cls    

            
# @dataclasses.dataclass
# class Edge(Component):
#     """An edge in a sourdough Graph.

#     'start' and 'stop' are the ends of the Edge. However, which value is 
#     assigned to each attribute only matters in a directional graph.

#     By default Edge is slotted so that no other attributes can be added. This
#     lowers memory consumption and increases speed. If you wish to add more 
#     functionality to your Graph edges, you should subclass Edge.

#     Args:
#         start (str): name of the Component where the edge starts.
#         stop (str): name of the Component where the edge ends.
#         directed (bool): whether this edge is directed (True). Defaults to 
#             False. 
#         weight (float): a weight value assigned to this edge. Defaults to None.

#     """
#     start: sourdough.Node = None
#     stop: sourdough.Node = None
#     directed: bool = False
#     weight: float = 1.0
#     name: str = None
    
#     """ Public Methods """

#     # def get_name(self) -> str:
#     #     """Returns 'name' based upon attached nodes.
        
#     #     Returns:
#     #         str: name of class for internal referencing.
        
#     #     """
#     #     return f'{self.start.name}_to_{self.stop.name}'


# @dataclasses.dataclass
# class Node(Component):
#     """An edge in a sourdough Graph.

#     'start' and 'stop' are the ends of the Edge. However, which value is 
#     assigned to each attribute only matters in a directional graph.

#     By default Edge is slotted so that no other attributes can be added. This
#     lowers memory consumption and increases speed. If you wish to add more 
#     functionality to your Graph edges, you should subclass Edge.

#     Args:
#         start (str): name of the Component where the edge starts.
#         stop (str): name of the Component where the edge ends.
#         directed (bool): whether this edge is directed (True). Defaults to 
#             False. 
#         weight (float): a weight value assigned to this edge. Defaults to None.

#     """

#     name: str = None
#     edges: Sequence['Edge'] = dataclasses.field(default_factory = list)


    