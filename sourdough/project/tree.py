"""
tree: components of tree objects in a sourdough project
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Technique (Task): base-level tree object which performs some action.
    Step (Task): wrapper for Technique which performs some action (optional).
    Worker (Task, Progression): iterable of Step, Technique, or other Worker
        instances.
    Manager (Worker): top-level Worker, which also contains information for
        project serialization and replicability.

"""

import abc
import dataclasses
import inspect
import itertools
import more_itertools
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union

import sourdough


@dataclasses.dataclass
class Technique(sourdough.Task):
    """Base class for creating or modifying data objects.

    In the sourdough tree structure, a Technique is a bottom-level leaf that 
    does not have any children of its own.
    
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
            self.algorithm(**parameters, **kwargs)
            return self
        else:
            return self.algorithm(data, **parameters, **kwargs)
        
    """ Dunder Methods """

    def __repr__(self) -> str:
        """Returns string representation of a class instance."""
        return self.__str__()

    def __str__(self) -> str:
        """Returns string representation of a class instance."""
        return (
            f'sourdough {self.__class__.__name__} {self.name}\n'
            f'algorithm: {str(self.algorithm)}\n'
            f'parameters: {str(self.parameters)}\n')
        
            
@dataclasses.dataclass
class Step(sourdough.Task, abc.ABC):
    """Base class for wrapping a Technique.

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
            
    """
    technique: Union[Technique, str] = None
    name: str = None

    """ Public Methods """
    
    @abc.abstractmethod
    def perform(self, data: object = None, **kwargs) -> object:
        """Subclasses must provide their own methods.
        
        The code below outlines a basic method that a subclass should build on
        for a properly functioning Step.
        
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
        return (
            f'sourdough {self.__class__.__name__} {self.name}\n'
            f'technique: {str(self.technique)}\n')


@dataclasses.dataclass
class Worker(sourdough.OptionsMixin, sourdough.Task, sourdough.Progression):
    """Base class for iterables storing Task and Worker subclass instances.

    Worker inherits all of the differences between a Progression and a python 
    list.
    
    A Worker differs from a Progression in 5 significant ways:
        1) It has a 'design' attribute which indicates how the contained 
            iterable should be ordered. 
        2) It mixes in Task which allows it to be stored as part of a sourdough
            tree object. This also adds a 'perform' method which is used
            to execute stored Task subclass instances.
        3) It mixes in OptionsMixin, which adds an 'options' class attribute.
            This allows str to be added to 'contents' and converted to Task
            subclass instances. This is done through the 'validate' method.
        4) It adds workers, steps, and techniques properties which return all 
            contained instances of Worker, Step, and Technique, respectively.
            This is done recursively so that all contained tree objects
            are searched.
        5) An 'overview' property is added which returns a dict of the names
            of the various parts of the tree objects. It doesn't include the
            hierarchy itself. Rather, it includes lists of all the types of
            component objects (Worker, Step, and Technique).
        
    Args:
        contents (Sequence[sourdough.Task]]): stored iterable of actions to 
            apply in order. Defaults to an empty list.
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
        design (str): the name of the structural design that should be used to 
            create objects in an instance. This should correspond to a key in a 
            Project instance's 'designs' class attribute. Defaults to 'chained'.
        options (ClassVar['sourdough.Catalog']): a sourdough dictionary of 
            available Task instances available to use.
            
    """
    contents: Union[
        Sequence['sourdough.Task'], 
        str] = dataclasses.field(default_factory = list)
    name: str = None
    design: str = dataclasses.field(default_factory = lambda: 'chained')
    options: ClassVar['sourdough.Catalog'] = sourdough.Catalog(
        always_return_list = True)
    
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        super().__post_init__()
        # Converts str in 'contents' to objects.
        self.contents = self.validate(contents = self.contents)

    """ Public Methods """
    
    def validate(self, 
            contents: Union[
                Sequence['sourdough.Task'], 
                str]) -> Sequence['sourdough.Task']:
        """Converts all str in 'contents' to 'Task' instances.
        
        Args:
            contents (Union[Sequence[sourdough.Task], str]): Task subclass
                instances or str corresponding to keys in 'options'.
                
        Returns:
            Sequence[sourdough.Task]: a list of all Task subclass instances.
            
        """
        new_contents = []
        for step in contents:
            if isinstance(step, str):
                try:
                    new_contents.append[self.options[step]]
                except KeyError:
                    new_contents.append[step]
            else:
                new_contents.append[step]
        return new_contents
        
    def perform(self, data: object = None) -> object:
        """Applies stored Task instances to 'data'.

        Args:
            data (object): an object to be modified and/or analyzed by stored 
                Task instances. Defaults to None.

        Returns:
            object: data, possibly with modifications made by Operataor 
                instances. If data is not passed, no object is returned.
            
        """
        if data is None:
            for task in self.__iter__():
                task.perform()
            return self
        else:
            for task in self.__iter__():
                data = task.perform(data = data)
            return data
             
    """ Properties """
    
    @property
    def overview(self) -> Mapping[str, Sequence[str]]:
        """Returns a dict snapshot of a Worker subclass instance.
        
        Returns:
            Mapping[str, Sequence[str]]: configured according to the 
                '_get_overview' method.
        
        """
        return self._get_overview() 

    @property    
    def workers(self) -> Sequence['Worker']:
        """Returns all instances of Worker in 'contents' (recursive).
        
        Returns:
            Sequence[Worker]: all Worker instances in the contained tree
                object.
                
        """
        return [isinstance(i, Worker) for i in self._get_flattened()]
 
    @property
    def steps(self) -> Sequence['Step']:
        """Returns all instances of Step in 'contents' (recursive).
        
        Returns:
            Sequence[Step]: all Step instances in the contained tree
                object.
                
        """
        return [isinstance(i, Step) for i in self._get_flattened()]
    
    @property    
    def techniques(self) -> Sequence['Technique']:
        """Returns all instances of Technique in 'contents' (recursive).
        
        Returns:
            Sequence[Technique]: all Technique instances in the contained 
                tree object.
                
        """
        return [isinstance(i, Technique) for i in self._get_flattened()]
    
    """ Private Methods """
    
    def _get_flattened(self) -> Sequence['sourdough.Task']:
        """Returns a flattened list of all items in 'contents'.
        
        Returns:
            Sequence[Task]: all Task subclass instances in the contained 
                tree object.
                
        """
        return more_itertools.collapse(self.contents)
        
    def _get_overview(self) -> Mapping[str, Sequence[str]]:
        """Returns outline of the overal project tree.
        
        Returns:  
            Mapping[str, Sequence[str]]: the names of the contained Worker, 
                Step, and/or Technique instances.
                
        """
        overview = {}
        overview['workers'] = [p.name for p in self.workers]
        overivew['steps'] = [t.name for t in self.steps]
        overview['techniques'] = [t.name for t in self.techniques]
        return overview

    
@dataclasses.dataclass
class Manager(Worker):
    """Top-level sourdough manager iterable.
    
    A Manager differs from an ordinary Worker instance in 2 significant ways:
        1) It includes a metadata label for this unique project in the 
            'identification' attribute. By default, this will combine the 'name'
            attribute with the date and time when this class is instanced. This
            inclusion also necessitates a small tweak to the value returned by
            the 'overview' property.
        2) A 'data' attribute is added for storing any data object(s) that are
            needed when automatic processing is chosen.
            
    Subclasses can easily expand upon the basic design and functionality of this
    class. Or, if the underlying structure is acceptable, you can simply add to
    the 'options' class attribute. 

    Args:
        contents (Sequence[Union[sourdough.Worker, sourdough.Step, str]]]): 
            stored Worker or Step instances or strings corresponding to keys in
            'options'. Defaults to an empty list.  
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
        design (str): the name of the structural design that should
            be used to create objects in an instance. This should correspond
            to a key in a Project instance's 'designs' class attribute. 
            Defaults to 'chained'.
        identification (str): a unique identification name for a 
            Manager instance. The name is used for creating file folders
            related to the 'Manager'. If not provided, a string is created from
            'name' and the date and time. This is a notable difference
            between an ordinary Worker instancce and a Manager instance. Other
            Workers are not given unique identification. Defaults to None.    
        data (Any]): a data object to apply any constructed objects to.
            This need only be provided when the class is instanced for
            automatic execution. Defaults to None. If you are working on a data-
            focused Manager, consider using siMpLify instead 
            (https://github.com/WithPrecedent/simplify). It applies sourdough
            in the data science context. sourdough itself treats 'data' as an
            unknown object of any type which offers more flexibility of design.
        options (ClassVar['sourdough.Catalog']): an instance to store possible
            Worker and Step classes for use in the Manager. Defaults to an
            empty Catalog instance.
                             
    """  
    contents: Sequence[Union[
        'sourdough.Task', 
        str]] = dataclasses.field(default_factory = list) 
    name: str = None
    design: str = dataclasses.field(default_factory = lambda: 'chained')
    identification: str = None
    data: Any = None
    options: ClassVar['sourdough.Catalog'] = sourdough.Catalog()

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls inherited initialization method.
        super().__post_init__()
        # Creates unique 'identification' based upon date and time if none 
        # exists.
        self.identification = (
            self.identification or sourdough.utilities.datetime_string(
                prefix = self.name))

    """ Private Methods """
        
    def _get_overview(self) -> Mapping[str, Union[str, Sequence[str]]]:
        """Returns outline of the overal project tree.
        
        Returns:  
            Mapping[str, Union[str, Sequence[str]]]: project identification and
                the names of the contained Worker, Step, and/or Technique
                instances.
                
        """
        overview = {'project': self.identification}
        overview['workers'] = [p.name for p in self.workers]
        overivew['steps'] = [t.name for t in self.steps]
        overview['techniques'] = [t.name for t in self.techniques]
        return overview