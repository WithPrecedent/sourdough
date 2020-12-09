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
    Product (Lexicon): base class for outputs of a Creator's 'create' method.
        Products have auto-vivification making dynamic storage of products
        easier.

    
"""
from __future__ import annotations
import abc
import collections.abc
import dataclasses
import textwrap
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import sourdough
     

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
    registry: ClassVar[Mapping[str, Type]] = sourdough.options.creators

    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def create(self, project: sourdough.Project, **kwargs) -> Any:
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
    registry: ClassVar[Mapping[str, Type]] = sourdough.options.products

                       
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
    registry: ClassVar[Mapping[str, Type]] = sourdough.options.components
    library: ClassVar[Mapping[str, Component]] = sourdough.options.instances

    """ Required Subclass Methods """

    @abc.abstractmethod
    def apply(self, project: sourdough.Project) -> sourdough.Project:
        """Subclasses must provide their own methods."""
        return project
