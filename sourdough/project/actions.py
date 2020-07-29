"""
components: composite objects in a sourdough project that perform some action
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Technique (Action): primitive object which performs some action.
    Task (Action): wrapper for Technique which performs some action (optional).

"""

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
                f'{self.technique}')


@dataclasses.dataclass
class Worker(sourdough.Action, sourdough.Hybrid):
    """Base class for a tree object.

    Worker inherits all of the differences between a Hybrid and a python 
    list.
    
    A Worker differs from a Hybrid in 4 significant ways:
        1) It has a 'design' attribute which indicates how the contained 
            iterable should be ordered. 
        2) It mixes in Action which allows it to be stored as part of a 
            sourdough tree object (a tree within a tree). This also adds a 
            'perform' method which is used to execute stored Action subclass 
            instance methods.
        3) It adds workers, tasks, and techniques properties which return all 
            contained instances of Worker, Task, and Technique, respectively.
            This is done recursively so that all contained tree objects
            are searched.
        4) An 'overview' property is added which returns a dict of the names
            of the various parts of the tree objects. It doesn't include the
            hierarchy itself. Rather, it includes lists of all the types of
            component objects (Worker, Task, and Technique).
        
    Args:
        contents (Sequence[sourdough.Action]]): stored iterable of components to 
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
    
    ToDo:
        draw: a method for printing an ASCII diagram of a Worker in its 
            'contents' to the console or a text file.
            
    """
    contents: Union[
        Sequence['sourdough.Action'], 
        str] = dataclasses.field(default_factory = list)
    name: str = None
    design: str = dataclasses.field(default_factory = lambda: 'chained')
    
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent initialization method(s).
        super().__post_init__()
        # Converts str in 'contents' to objects.
        self.contents = self.validate(contents = self.contents)

    """ Public Methods """
        
    def perform(self, data: object = None) -> object:
        """Applies stored Action instances to 'data'.

        Args:
            data (object): an object to be modified and/or analyzed by stored 
                Action instances. Defaults to None.

        Returns:
            object: data, possibly with modifications made by Operataor 
                instances. If data is not passed, no object is returned.
            
        """
        if data is None:
            for action in iter(self):
                action.perform()
            return self
        else:
            for action in iter(self):
                data = action.perform(data = data)
            return data
    
    def apply(self, tool: Callable, recursive: bool = True, **kwargs) -> None:
        """
        
        """
        new_contents = []
        for item in iter(self.contents):
            if isinstance(item, sourdough.Hybrid):
                if recursive:
                    new_item = item.apply(
                        tool = tool, 
                        recursive = True, 
                        **kwargs)
                else:
                    new_item = item
            else:
                new_item = tool(item, **kwargs)
            new_contents.append(new_item)
        self.contents = new_contents
        return self

    def find(self, 
            tool: Callable, 
            recursive: bool = True, 
            matches: Sequence = None,
            **kwargs) -> Sequence['sourdough.Component']:
        """
        
        """
        if matches is None:
            matches = []
        for item in iter(self.contents):
            matches.extend(sourdough.utilities.listify(tool(item, **kwargs)))
            if isinstance(item, sourdough.Hybrid):
                if recursive:
                    matches.extend(item.find(
                        tool = tool, 
                        recursive = True,
                        matches = matches, 
                        **kwargs))
        return matches
               
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
        return self.find(self._get_type, component = Worker)
 
    @property
    def tasks(self) -> Sequence['sourdough.Task']:
        """Returns all instances of Task in 'contents' (recursive).
        
        Returns:
            Sequence[Task]: all Task instances in the contained tree
                object.
                
        """
        return self.find(self._get_type, component = sourdough.Task)
    
    @property    
    def techniques(self) -> Sequence['sourdough.Technique']:
        """Returns all instances of Technique in 'contents' (recursive).
        
        Returns:
            Sequence[Technique]: all Technique instances in the contained 
                tree object.
                
        """
        return self.find(self._get_type, component = sourdough.Technique)
    
    """ Dunder Methods """
    
    def __iter__(self) -> Iterable:
        """Returns iterable selected by structural settings."""
        if isinstance(self.design.iterator, str):
            return getattr(self, self.design.iterator)(
                contents = self.contents)
        else:
            return self.design.iterator(self.contents)

    # def __str__(self) -> str:
    #     """Returns default string representation of an instance.

    #     Returns:
    #         str: default string representation of an instance.

    #     """
    #     if hasattr(self.design, 'name'):
    #         return '\n'.join([textwrap.dedent(f'''
    #             sourdough {self.__class__.__name__}
    #             name: {self.name}
    #             design: {self.design.name}
    #             contents:'''),
    #             f'''{textwrap.indent(str(self.contents), '    ')}'''])
    #     else:
    #         return '\n'.join([textwrap.dedent(f'''
    #             sourdough {self.__class__.__name__}
    #             name: {self.name}
    #             design: {self.design}
    #             contents:'''),
    #             f'''{textwrap.indent(str(self.contents), '    ')}'''])
            
    """ Private Methods """
    
    def _get_flattened(self) -> Sequence['sourdough.Action']:
        """Returns a flattened list of all items in 'contents'.
        
        Returns:
            Sequence[Action]: all Action subclass instances in the contained 
                tree object.
                
        """
        return list(more_itertools.collapse(self.contents))

    def _get_type(self, 
            item: 'sourdough.Component', 
            component: 'sourdough.Component') -> bool: 
        """[summary]

        Args:
            item (sourdough.Component): [description]
            component (sourdough.Component): [description]

        Returns:
            bool: [description]
        """
        if isinstance(item, component):
            return [item]
        else:
            return []
          
    def _get_overview(self) -> Mapping[str, Sequence[str]]:
        """Returns outline of the overal project tree.
        
        Returns:  
            Mapping[str, Sequence[str]]: the names of the contained Worker, 
                Task, and/or Technique instances.
                
        """
        overview = {}
        overview['workers'] = [w.name for w in self.workers]
        overview['tasks'] = [s.name for s in self.tasks]
        overview['techniques'] = [t.name for t in self.techniques]
        return overview
