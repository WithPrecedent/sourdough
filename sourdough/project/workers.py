"""
workers: tree objects in a sourdough project
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Worker (Action, Hybrid): iterable of Task, Technique, or other Worker
        instances.
    Manager (Worker): top-level Worker, which also contains information for
        project serialization and replicability.

The sourdough tree structure emphasizes:
    1) Independence: components of the tree do not require knowledge of parent
        objects to function. The primitive Technique objects can be completely
        detached from the tree and still function. Any segment of the tree can
        be removed from the rest and operate and be serialized.
    2) Flexibility: tree objects can contain Worker, Task, and/or Technique 
        instances. There are no limits on the number of children that the tree 
        objects can have. The trees can be constructed for different iteration 
        patterns (using the 'design') attribute or manually built by users.
    3) Accessibility: because sourdough tree objects inherit from Hybrid,
        users can access the trees with list and dictionary methods. Further,
        'workers', 'tasks', and 'techniques' properties all for instance access
        to the various types of contained objects.
    4) Familiarity: for people without a computer science background, the varied
        language of trees can be confusing: nodes, leafs, root, edges, etc. 
        Instead, sourdough follows an employment hierarchy with a Manager, 
        Workers, Tasks (optional), and Techniques. The hope is that these labels
        better indicate the functionality of the objects within the tree 
        structure.

"""

import dataclasses
import more_itertools
import textwrap
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union

import sourdough


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
        contents (Sequence[sourdough.Action]]): stored iterable of actions to 
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
    structure: str = dataclasses.field(default_factory = lambda: 'chained')
    
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent initialization method(s).
        super().__post_init__()
        # Converts str in 'contents' to objects.
        self.contents = self.validate(contents = self.contents)

    """ Public Methods """
    
    # def validate(self, 
    #         contents: Union[
    #             'sourdough.Action',
    #             Sequence['sourdough.Action']]) -> Sequence['sourdough.Action']:
    #     """Converts all str in 'contents' to 'Action' instances.
        
    #     Args:
    #         contents (Union[sourdough.Action, Sequence[sourdough.Action]]): 
    #             Action subclass instance(s).
                
    #     Returns:
    #         Sequence[sourdough.Action]: a list of all Action subclass instances.
            
    #     """
    #     new_contents = []
    #     if isinstance(contents, Sequence):
    #         for task in contents:
    #             if isinstance(task, str):
    #                 try:
    #                     new_contents.append(self.options[task])
    #                 except KeyError:
    #                     new_contents.append(task)
    #             else:
    #                 new_contents.append(task)
    #     elif isinstance(contents, sourdough.Action):
            
    #     return new_contents
        
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
            for action in self.__iter__():
                action.perform()
            return self
        else:
            for action in self.__iter__():
                data = action.perform(data = data)
            return data
    
    def apply(self, tool: Callable, recursive: bool = True) -> None:
        """
        
        """
        new_contents = []
        for item in self.__iter__():
            if isinstance(item, sourdough.Hybrid):
                if recursive:
                    new_item = item.apply(tool = tool, recursive = True)
                else:
                    new_item = item
            else:
                new_item = tool(item)
            new_contents.append(new_item)
        self.contents = new_contents
        return self
               
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
    def tasks(self) -> Sequence['sourdough.Task']:
        """Returns all instances of Task in 'contents' (recursive).
        
        Returns:
            Sequence[Task]: all Task instances in the contained tree
                object.
                
        """
        return [isinstance(i, sourdough.Task) for i in self._get_flattened()]
    
    @property    
    def techniques(self) -> Sequence['sourdough.Technique']:
        """Returns all instances of Technique in 'contents' (recursive).
        
        Returns:
            Sequence[Technique]: all Technique instances in the contained 
                tree object.
                
        """
        return [
            isinstance(i, sourdough.Technique) for i in self._get_flattened()]
    
    """ Dunder Methods """
    
    def __iter__(self) -> Iterable:
        """Returns iterable selected by structural settings."""
        if isinstance(self.structure.iterator, str):
            return getattr(self, self.structure.iterator)(
                contents = self.contents)
        else:
            return self.structure.iterator(self.contents)

    def __str__(self) -> str:
        """Returns default string representation of an instance.

        Returns:
            str: default string representation of an instance.

        """
        if hasattr(self.structure, 'name'):
            return '\n'.join([textwrap.dedent(f'''
                sourdough {self.__class__.__name__}
                name: {self.name}
                structure: {self.structure.name}
                contents:'''),
                f'''{textwrap.indent(str(self.contents), '    ')}'''])
        else:
            return '\n'.join([textwrap.dedent(f'''
                sourdough {self.__class__.__name__}
                name: {self.name}
                structure: {self.structure}
                contents:'''),
                f'''{textwrap.indent(str(self.contents), '    ')}'''])
            
    """ Private Methods """
    
    def _get_flattened(self) -> Sequence['sourdough.Action']:
        """Returns a flattened list of all items in 'contents'.
        
        Returns:
            Sequence[Action]: all Action subclass instances in the contained 
                tree object.
                
        """
        return more_itertools.collapse(self.contents)
        
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

    
@dataclasses.dataclass
class Manager(Worker):
    """Base class for the root of a tree object.
    
    A Manager differs from an ordinary Worker instance in 2 significant ways:
        1) It includes a metadata label for this unique project in the 
            'identification' attribute. By default, this will combine the 'name'
            attribute with the date and time when this class is instanced. This
            inclusion also necessitates a small tweak to the value returned by
            the 'overview' property.
        2) A 'data' attribute is added for storing any data object(s) that are
            needed when automatic processing is chosen.

    Args:
        contents (Sequence[Union[sourdough.Worker, sourdough.Task, str]]]): 
            stored Worker or Task instances or strings corresponding to keys in
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
        structure (str): the name of the structural design that should
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
                             
    """  
    contents: Sequence[Union[
        'sourdough.Action', 
        str]] = dataclasses.field(default_factory = list) 
    name: str = None
    structure: str = dataclasses.field(default_factory = lambda: 'chained')
    identification: str = None
    data: Any = None

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent initialization method(s).
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
                the names of the contained Worker, Task, and/or Technique
                instances.
                
        """
        overview = {'project': self.identification}
        overview['workers'] = [w.name for w in self.workers]
        overview['tasks'] = [s.name for s in self.tasks]
        overview['techniques'] = [t.name for t in self.techniques]
        return overview

    def __str__(self) -> str:
        """Returns default string representation of an instance.

        Returns:
            str: default string representation of an instance.

        """
        if hasattr(self.structure, 'name'):
            return '\n'.join([textwrap.dedent(f'''
                sourdough {self.__class__.__name__}
                name: {self.name}
                identification: {self.identification}
                data: {self.data is not None}
                structure: {self.structure.name}
                contents:'''),
                f'''{textwrap.indent(str(self.contents), '    ')}'''])
        else:
            return '\n'.join([textwrap.dedent(f'''
                sourdough {self.__class__.__name__}
                name: {self.name}
                identification: {self.identification}
                data: {self.data is not None}
                structure: {self.structure}
                contents:'''),
                f'''{textwrap.indent(str(self.contents), '    ')}'''])    