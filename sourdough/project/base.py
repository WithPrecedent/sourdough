"""
base: core base classes for sourdough projects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Creator (Registrar): base class for creating outputs for a sourdough
        project. All subclasses must have a 'create' method. All concrete
        subclasses are automatically registered in the 'registry' class
        attribute and in 'creators'.
    Deliverable (Lexicon): base class for outputs of a Creator's 'create' method.
        Deliverables have auto-vivification making dynamic storage of creations
        easier.
    Component (Librarian, Registrar, Container): base class for nodes in a
        sourdough project workflow. All subclasses must have an 'apply' 
        method. All concrete subclasses are automatically registered in the 
        'registry' class attribute and in 'components'. All subclass instances
        are automatically stored in the 'library' class attribute and in
        'instances'.
    Resources (Container): a collection of base classes and Catalogs used for a
        sourdough project. Changing the base classes or Catalogs in an instance
        or subclassing Resources with different options will change the base
        classes and Catalogs used by Project.
    Rules
    
"""
from __future__ import annotations
import abc
import collections.abc
import dataclasses
import pprint
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import sourdough
   

@dataclasses.dataclass
class Creator(sourdough.quirks.Registrar, abc.ABC):
    """Base class for creating objects outputted by a Project's iteration.
    
    All subclasses must have a 'create' method that takes 'project' as a 
    parameter.
    
    Args:
        action (str): name of action performed by the class. This is used in
            messages in the terminal and logging.
        needs (ClassVar[Union[str, Tuple[str]]]): name(s) of item(s) needed
            by the class's 'create' method.
        produces (ClassVar[str]): name of item produced by the class's 'create'
            method.
        registry (ClassVar[Mapping[str, Type]]): a mapping storing all concrete
            subclasses. Defaults to the Catalog instance 'creators'.
            
    """
    action: ClassVar[str]
    needs: ClassVar[Union[str, Tuple[str]]]
    produces: ClassVar[Type]
    registry: ClassVar[Mapping[str, Type]] = sourdough.defaults.creators

    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def create(self, project: sourdough.Project, **kwargs) -> Any:
        """Performs some action based on 'project' with kwargs (optional).
        
        Subclasses must provide their own methods.

        Args:
            project (object): a Project-compatible instance.
            kwargs: any additional parameters to pass to a 'create' method.

        Return:
            Any: object created by a 'create' method.
        
        """
        pass

    """ Dunder Methods """

    def __str__(self) -> str:
        """Returns pretty string representation of a class instance.
        
        Returns:
            str: normal representation of a class instance.
        
        """
        return pprint.pformat(self, sort_dicts = False, compact = True)

    
@dataclasses.dataclass
class Element(collections.abc.Container):
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
    
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Sets 'name' attribute.
        if not hasattr(self, 'name') or self.name is None:  
            self.name = self._get_name()
        # Calls parent and/or mixin initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass

    """ Private Methods """
    
    def _get_name(self) -> str:
        """Returns snakecase of the class name.

        If a user wishes to use an alternate naming system, a subclass should
        simply override this method. 
        
        Returns:
            str: name of class for internal referencing and some access methods.
        
        """
        return sourdough.tools.snakify(self.__class__.__name__)

    """ Dunder Methods """
    
    def __contains__(self, item: Any) -> bool:
        """Returns whether 'item' is in the 'contents' attribute.
        
        Args:
            item (Any): item to look for in 'contents'.
            
        Returns:
            bool: whether 'item' is in 'contents' if it is a Collection.
                Otherwise, it evaluates if 'item' is equivalent to 'contents'.
                
        """
        try:
            return item in self.contents
        except TypeError:
            return item == self.contents

    def __str__(self) -> str:
        """Returns pretty string representation of a class instance.
        
        Returns:
            str: normal representation of a class instance.
        
        """
        return pprint.pformat(self, sort_dicts = False, compact = True)


@dataclasses.dataclass
class Deliverable(sourdough.quirks.Registrar, Element, sourdough.types.Lexicon, 
                  abc.ABC):
    """Stores output of a Creator's 'create' method.
    
    Deliverable autovivifies by automatically creating a correspond key if a
    user attempts to access a key that does not exist. In doing so, it creates
    an instance of the class listed in the 'stores' class attribue.
    
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
    stores: ClassVar[Type] = None
    registry: ClassVar[Mapping[str, Type]] = sourdough.defaults.deliverables
    
    """ Dunder Methods """
    
    def __missing__(self, key: str) -> Any:
        """Autovivifies if there is no matching key.
        
        Args:
        
        """
        super().__setitem__(key = key, value = self.stores(name = key))
        return self[key]

    def __str__(self) -> str:
        return pprint.pformat(self, sort_dicts = False, compact = True)  
