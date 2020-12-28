"""
base: core base classes for sourdough projects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Manager (Registrar, Hybrid):
    Creator (Registrar, ABC): base class for creating outputs for a sourdough
        project. All subclasses must have a 'create' method. All concrete
        subclasses are automatically registered in the 'registry' class
        attribute and in 'creators'.
    Product (Registrar, Element, Lexicon, ABC): base class for outputs of a 
        Creator's 'create' method.
    Component (Librarian, Registrar, Element, ABC):

    
"""
from __future__ import annotations
import abc
import dataclasses
import textwrap
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import sourdough
     
  
@dataclasses.dataclass
class Manager(sourdough.quirks.Registrar, sourdough.types.Hybrid):
    """Constructs, organizes, and implements a part of a sourdough project.
    
    Unlike an ordinary Hybrid, a Manager instance will iterate 'creators' 
    instead of 'contents'. However, all access methods still point to 
    'contents', which is where the results of iterating the class are stored.
        
    Args:
        contents (Mapping[str, object]]): stored objects created by the 
            'create' methods of 'creators'. Defaults to an empty dict.
        creators (Sequence[Union[Type, str]]): a Creator-compatible classes or
            strings corresponding to the keys in registry of the default
            'creator' in 'bases'. Defaults to a list of 'architect', 
            'builder', and 'worker'. 
        project (sourdough.Project)
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. If it is None, the 'name' will be attempted to be 
            inferred from the first section name in 'settings' after 'general' 
            and 'files'. If that fails, 'name' will be the snakecase name of the
            class. Defaults to None. 
        identification (str): a unique identification name for a Manager 
            instance. The name is used for creating file folders related to the 
            project. If it is None, a str will be created from 'name' and the 
            date and time. Defaults to None.   
        automatic (bool): whether to automatically advance 'director' (True) or 
            whether the director must be advanced manually (False). Defaults to 
            True.
        data (object): any data object for the project to be applied. If it is
            None, an instance will still execute its workflow, but it won't
            apply it to any external data. Defaults to None.  
        bases (ClassVar[object]): contains information about default base 
            classes used by a Manager instance. Defaults to an instance of 
            Bases.
        rules (ClassVar[object]):
        options (ClassVar[object]):
         
    """
    contents: Mapping[str, Any] = dataclasses.field(default_factory = list)
    creators: Sequence[Union[Type, str]] = dataclasses.field(
        default_factory = lambda: ['architect', 'builder', 'worker'])
    project: Union[object, Type] = None
    name: str = None
    automatic: bool = True
    data: object = None
    bases: ClassVar[object] = sourdough.resources.bases
    options: ClassVar[object] = sourdough.resources.options
    registry: ClassVar[Mapping[str, Manager]] = (
        sourdough.resources.options.managers)
    
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent and/or mixin initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass
        # Converts 'creators' to classes, if necessary.
        self._validate_creators() 
        # Sets index for iteration.
        self.index = 0
        # Advances through 'creators' if 'automatic' is True.
        if self.automatic:
            self.complete()

    """ Public Methods """
    
    def advance(self) -> Any:
        """Returns next product created in iterating a Manager instance."""
        return self.__next__()

    def complete(self) -> None:
        """Advances through the stored Creator instances.
        
        The results of the iteration is that each item produced is stored in 
        'content's with a key of the 'produces' attribute of each creator.
        
        """
        for creator in iter(self):
            self.add(self.__next__())
        return self
    
    """ Private Methods """

    def _validate_creators(self) -> None:
        """Validates 'creators' or converts it to a list of Creator instances.
        
        If strings are passed, those are converted to classes from the registry
        of the designated 'creator' in bases'.
        
        """
        new_creators = []
        for creator in self.creators:
            if isinstance(creator, str):
                new_creators.append(self.project.bases.creator.acquire(creator))
            else:
                new_creators.append(creator)
        self.creators = new_creators
        return self
    
    """ Dunder Methods """
    
    def __next__(self) -> Any:
        """Returns products of the next Creator in 'creators'.

        Returns:
            Any: item creator by the 'create' method of a Creator.
            
        """
        if self.index < len(self.creators):
            creator = self.creators[self.index]()
            if hasattr(self, 'verbose') and self.project.verbose:
                print(
                    f'{creator.action} {creator.produces} from {creator.needs}')
            self.index += 1
            product = creator.create(manager = self)
        else:
            raise IndexError()
        return product
    
    def __iter__(self) -> Iterable:
        """Returns iterable of 'creators'.
        
        Returns:
            Iterable: iterable sequence of 'creators'.
            
        """
        return iter(self.creators)


@dataclasses.dataclass
class Creator(sourdough.quirks.Registrar, abc.ABC):
    """Base class for creating objects outputted by a Project's iteration.
    
    All subclasses must have a 'create' method that takes 'project' as a 
    parameter and returns an object or class to be stored in a Project
    instance's contents. The Craetor subclasses included in sourdough all create
    Product subclasses.
    
    Args:
        action (str): name of action performed by the class. This is used in
            messages in the terminal and logging.
        needs (ClassVar[str]): name of item needed by the class's 'create' 
            method. This can correspond to the name of an attribute in a
            Project instance or a key to an item in the 'contents' attribute
            of a Project instance.
        produces (ClassVar[str]): name of item produced by the class's 'create'
            method.
        registry (ClassVar[Mapping[str, Type]]): a mapping storing all concrete
            subclasses. Defaults to the Catalog instance 'creators'.
            
    """
    action: ClassVar[str]
    needs: ClassVar[str]
    produces: ClassVar[str]
    registry: ClassVar[Mapping[str, Type]] = sourdough.resources.options.creators

    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def create(self, manager: sourdough.Manager, **kwargs) -> Any:
        """Performs some action based on 'project' with kwargs (optional).
        
        Subclasses must provide their own methods.

        Args:
            project (object): a Project-compatible instance.
            kwargs: any additional parameters to pass to a 'create' method.

        Return:
            Any: object or class created by a 'create' method.
        
        """
        pass


@dataclasses.dataclass
class Product(sourdough.quirks.Registrar, sourdough.quirks.Element, 
              sourdough.types.Lexicon, abc.ABC):
    """Stores output of a Creator's 'create' method.
    
    Args:
        contents (Mapping[str, Any]]): stored dictionary which contains created
            items. Defaults to an empty dict.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. 
        identification (str): a unique identification name for the related 
            Project instance.  
        stores (ClassVar[Type]): type of instances stored in 'contents'. The
            designated class allows autovivification by creating an instance of 
            the stored type.
                      
    """
    contents: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    name: str = None
    identification: str = None
    registry: ClassVar[Mapping[str, Type]] = sourdough.resources.options.products

                       
@dataclasses.dataclass
class Component(sourdough.quirks.Librarian, sourdough.quirks.Registrar,  
                sourdough.quirks.Element, abc.ABC):
    """Base container class for sourdough composite objects.
    
    A Component has a 'name' attribute for internal referencing and to allow 
    sourdough iterables to function propertly. Component instances can be used 
    to create a variety of composite workflows such as trees, cycles, contests, 
    studies, and graphs.
    
    Args:
        contents (Any): item(s) contained by a Component instance.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. 
        registry (ClassVar[Mapping[str, Type]]): a mapping storing all concrete
            subclasses. Defaults to the Catalog instance 'components'.
        library (ClassVar[Mapping[str, Type]]): a mapping storing all concrete
            subclasses. Defaults to the Catalog instance 'instances'.
            
    """
    contents: Any = None
    name: str = None
    registry: ClassVar[Mapping[str, Type]] = sourdough.resources.options.components
    library: ClassVar[Mapping[str, Component]] = sourdough.resources.options.instances

    """ Required Subclass Methods """

    @abc.abstractmethod
    def apply(self, manager: sourdough.Manager) -> sourdough.Manager:
        """Subclasses must provide their own methods."""
        return manager
