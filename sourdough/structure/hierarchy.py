"""
.. module:: managers
:synopsis: sourdough project managers
:publisher: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import abc
import dataclasses
import copy
import inspect
from typing import (
    Any, Callable, ClassVar, Dict, Iterable, List, Optional, Tuple, Union)

import sourdough
from sourdough import utilities


@dataclasses.dataclass
class Overview(sourdough.base.MappingBase):
    """Base class for outlining a sourdough project.

    Args:
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. If the class instance
            needs settings from the shared Settings instance, 'name' should
            match the appropriate section name in that Settings instance. When
            subclassing, it is a good settings to use the same 'name' attribute
            as the base class for effective coordination between sourdough
            classes. Defaults to None or __class__.__name__.lower().
        contents (Dict[str, List[str]]): a dictionary with keys corresponding
            to worker names and a list of tasks in the values. Defaults to an
            empty dictionary.

    """
    name: Optional[str] = None
    contents: Optional[Dict[str, 'Overview']] = dataclasses.field(
            default_factory = dict)

    def add(self, 
            component: 'sourdough.Component', 
            key: Optional[str] = None) -> None:
        """Adds 'component' to 'contents'.

        Args:
            component ('sourdough.Component'): component object to add to add
            key {Optional[str]} -- [description] (default: {None})

        Returns:
            [type] -- [description]
        """
        if key is None:
            key = component.name
        self.contents[key] = component
        return self
   
        
@dataclasses.dataclass
class Employee(sourdough.Component, abc.ABC):
    """
    
    """
    name: Optional[str] = None
    settings: Optional[Union['sourddough.Settings', str]] = None
       
    """ Overview Property """
    
    @property
    def overview(self) -> 'Overview':
        """Returns string snapshot of a SequenceBase subclass instance.
        
        With a basic employee, the overview just appears as a simple dictionary of
        'name' attributes of 'contents' as keys and the 'contents' objects as 
        values. When using more complicated subclass instance, the overview 
        includes the entire composite structure, appearing as a tree-like 
        object.
        
        Returns:
            Overview: configured according to the '_get_overview' method.
        
        """
        return self._get_overview() 

    """ Private Methods """
    
    def _get_overview(self) -> 'sourdough.Overview':
        """Returns Overview instance with information about 'contents'.
                
        Returns:
            Overview: with 'contents' determined by stored Manager instances.
        
        """
        overview = sourdough.Overview(name = f'{self.name}_overview')
        for component in self.contents:
            try:
                overview.add(component.get_overview())
            except AttributeError: 
                overview.add({component.worker: component.name})
        return overview   
    

@dataclasses.dataclass
class Manager(sourdough.base.SequenceBase, Employee):
    """Contains information and objects to create parts of a Project.
    
    Args:
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. For example if a 
            class instance needs settings from the shared Settings instance, 
            'name' should match the appropriate section name in that Settings 
            instance. When subclassing, it is sometimes a good idea to use the 
            same 'name' attribute as the base class for effective coordination 
            between sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Component is called, 'name' is set to a snake 
            case version of the class name ('__class__.__name__').
        employees (Optional[List[Union[Manager, sourdough.Task, 
            str]]]): stored Manager instances, Task instances, or strings 
            corresponding to keys in 'options'. Defaults to an empty list.  
        design (Optional[str]): the name of the structural design that should
            be used to create objects in an instance. This should correspond
            to a key in a Director instance's 'designs' class attribute.
        settings (Optional[sourdough.Settings]): an instance of Settings which
            may be used by the Manager instance. Defaults to None. 
        data (Optional[Any]): a data object to apply any constructed objects to.
            This need only be provided when the class is instanced for
            automatic execution. Defaults to None. If you are working on a data-
            focused project, consider using siMpLify instead 
            (https://github.com/WithPrecedent/simplify). It applies sourdough
            in the data science context. sourdough itself treats 'data' as an
            unknown object of any type which offers more flexibility of design.
        options (ClassVar[sourdough.Options]): an Options instance containing
            either Manager or Task instances. Defaults to an empty Options 
            instance.
            
    """
    name: Optional[str] = None
    contents: Optional[List[Union['Employee', str]]] = dataclasses.field(
        default_factory = list)    
    design: Optional[str] = dataclasses.field(
        default_factory = lambda: 'chained')
    settings: Optional[Union['sourddough.Settings', str]] = None
    data: Optional[Any] = None
    manager: Optional[str] = dataclasses.field(default_factory = lambda: '')
    options: ClassVar['sourdough.Options'] = sourdough.Options()

    """ Private Methods """
        
    def _get_overview(self) -> List[Union[str, List[Any]]]:
        """Returns list of strings or lists of lists throughout a hierarchy.
                
        Returns:
            List[str, List[Any]]: with name information about related Task and
                Manager instances.
        
        """
        overview = []
        for responsibility in self.contents:
            try:
                overview.append(responsibility.get_overview())
            except AttributeError: 
                overview.append({responsibility.worker: responsibility.name})
        return overview
    
    
@dataclasses.dataclass
class Worker(Employee):
    """Base class for storing tasks stored in SequenceBases.

    A Worker is a basic wrapper for a task that adds a 'name' for the
    'worker' that a stored task instance is associated with. Subclasses of
    Worker can store additional methods and attributes to apply to all possible
    task instances that could be used.

    A Worker instance will try to return attributes from 'task' if the
    attribute is not found in the Worker instance. Similarly, when setting
    or deleting attributes, a Worker instance will set or delete the
    attribute in the stored task instance.

    Args:
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. If the class instance
            needs settings from the shared Settings instance, 'name' should
            match the appropriate section name in that Settings instance. When
            subclassing, it is a good settings to use the same 'name' attribute
            as the base class for effective coordination between sourdough
            classes. Defaults to None or __class__.__name__.lower().
        task (task): task object for this worker in a sourdough
            sequence. Defaults to None.

    """
    name: Optional[str] = None
    manager: Optional[str] = dataclasses.field(default_factory = lambda: '')
    task: ['sourdough.Task'] = None

    # """ Dunder Methods """

    # def __getattr__(self, attribute: str) -> Any:
    #     """Looks for 'attribute' in 'task'.

    #     Args:
    #         attribute (str): name of attribute to return.

    #     Returns:
    #         Any: matching attribute.

    #     Raises:
    #         AttributeError: if 'attribute' is not found in 'task'.

    #     """
    #     try:
    #         return getattr(self.task, attribute)
    #     except AttributeError:
    #         raise AttributeError(
    #             f'{attribute} neither found in {self.name} nor \
    #                 {self.task.name}')

    # def __setattr__(self, attribute: str, value: Any) -> None:
    #     """Adds 'value' to 'task' with the name 'attribute'.

    #     Args:
    #         attribute (str): name of the attribute to add to 'task'.
    #         value (Any): value to store at that attribute in 'task'.

    #     """
    #     setattr(self.task, attribute, value)
    #     return self

    # def __delattr__(self, attribute: str) -> None:
    #     """Deletes 'attribute' from 'task'.

    #     Args:
    #         attribute (str): name of attribute to delete.

    #     """
    #     try:
    #         delattr(self.task, attribute)
    #     except AttributeError:
    #         pass
    #     return self

    # def __repr__(self) -> str:
    #     """Returns string representation of a class instance."""
    #     return self.__str__()

    # def __str__(self) -> str:
    #     """Returns string representation of a class instance."""
    #     return (
    #         f'worker: {self.name} '
    #         f'task: {self.task.name}') 

  
@dataclasses.dataclass
class Task(sourdough.Component):
    """Base class for creating or modifying other sourdough classes.

    Args:
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. If the class instance
            needs settings from the shared Settings instance, 'name' should
            match the appropriate section name in that Settings instance. When
            subclassing, it is a good settings to use the same 'name' attribute
            as the base class for effective coordination between sourdough
            classes. Defaults to None or __class__.__name__.lower().
        worker (Optional[str]): the name of the worker in a Employee instance that the
            algorithm is being performed. This attribute is generally optional
            but can be useful for tracking and/or displaying the status of
            iteration. It is automatically created when using a chained or 
            comparative Employee. Defaults to None.
        algorithm (Optional[Union[str, object]]): name of object in 'module' to
            load or the process object which executes the primary method of
            a class instance. Defaults to None.
        parameters (Optional[Dict[str, Any]]): parameters to be attached to
            'algorithm' when 'algorithm' is instanced. Defaults to an empty
            dictionary.
            
    """
    name: Optional[str] = None
    worker: Optional[str] = None
    algorithm: Optional[Union[str, object]] = None
    parameters: Optional[Dict[str, Any]] = dataclasses.field(
        default_factory = dict)
    
    """ Required Subclass Methods """
    
    def apply(self,
            data: sourdough.Component, **kwargs) -> NotImplementedError:
        """Subclasses must provide their own methods."""
        raise NotImplementedError('Task subclasses must include apply methods')
    
    """ Dunder Methods """

    def __repr__(self) -> str:
        """Returns string representation of a class instance."""
        return self.__str__()

    def __str__(self) -> str:
        """Returns string representation of a class instance."""
        return (
            f'sourdough {self.__class__.__name__} {self.name} '
            f'worker: {self.worker.name} '
            f'algorithm: {str(self.algorithm)} '
            f'parameters: {str(self.parameters)} ')

 
@dataclasses.dataclass
class Job(sourdough.base.FactoryBase):
    """A factory for creating and returning Employee subclass instances.

    Args:
        product (Optional[str]): name of sourdough object to return. 'product' 
            must correspond to a key in 'products'. Defaults to None.
        default (ClassVar[str]): the name of the default object to instance. If 
            'product' is not passed, 'default' is used. 'default' must 
            correspond  to a key in 'products'. Defaults to None. If 'default'
            is to be used, it should be specified by a subclass, declared in an
            instance, or set via the class attribute.
        options (Dict[str, 'Employee']): a dictionary of available options for 
            object creation. Keys are the names of the 'product'. Values are the 
            objects to create. Defaults to an a dictionary with the managers 
            included in sourdough.

    Returns:
        Any: the factory uses the '__new__' method to return a different object 
            instance with kwargs as the parameters.

    """
    product: Optional[str] = None
    default: ClassVar[str] = 'worker'
    options: ClassVar[Dict[str, 'Employee']] = {
        'worker': Worker,
        'task': Task}

      
