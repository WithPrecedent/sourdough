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

The sourdough tree design emphasizes:
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
        design.

"""

import dataclasses
import more_itertools
import textwrap
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union

import sourdough




    
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
                             
    """  
    contents: Sequence[Union[
        'sourdough.Action', 
        str]] = dataclasses.field(default_factory = list) 
    name: str = None
    design: str = 'chained'
    identification: str = None
    data: Any = None
  