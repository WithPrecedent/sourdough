"""
base: core base classes for sourdough projects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    creators (Catalog): stored Creator subclasses. By default, snakecase names
        of the subclasses are used as the keys.
    components (Catalog): stored Component subclasses. By default, snakecase
        names of the subclasses are used as the keys.
    instances (Catalog): stored instances of Component subclasses. By default,
        the 'name' attribute of the instances are used as the keys.
    algorithms (Catalog): stored classes of algorithms, usually from other
        packages. The keys are assigned by the user or a package utilizing the
        sourdough framework.
    Creator (Registrar): base class for creating outputs for a sourdough
        project. All subclasses must have a 'create' method. All concrete
        subclasses are automatically registered in the 'registry' class
        attribute and in 'creators'.
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
    
"""
from __future__ import annotations
import abc
import collections.abc
import dataclasses
import pprint
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import sourdough


""" Catalogs of objects and classes for sourdough projects """

creators = sourdough.types.Catalog()

components = sourdough.types.Catalog()

instances = sourdough.types.Catalog()

algorithms = sourdough.types.Catalog()
    

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
    produces: ClassVar[str]
    registry: ClassVar[Mapping[str, Type]] = creators

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
class Component(sourdough.quirks.Librarian, sourdough.quirks.Registrar,  
                collections.abc.Container):
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
    registry: ClassVar[Mapping[str, Type]] = components
    library: ClassVar[Mapping[str, object]] = instances
    
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

    """ Required Subclass Methods """

    @abc.abstractmethod
    def apply(self, project: sourdough.Project) -> sourdough.Project:
        """Subclasses must provide their own methods."""
        return project

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
               
    # def __str__(self) -> str:
    #     """Returns pretty string representation of an instance.
        
    #     Returns:
    #         str: pretty string representation of an instance.
            
    #     """
    #     new_line = '\n'
    #     representation = [f'sourdough {self.__class__.__name__}']
    #     attributes = [a for a in self.__dict__ if not a.startswith('_')]
    #     for attribute in attributes:
    #         value = getattr(self, attribute)
    #         if (isinstance(value, Component) 
    #                 and isinstance(value, (Sequence, Mapping))):
    #             representation.append(
    #                 f'''{attribute}:{new_line}{textwrap.indent(
    #                     str(value.contents), '    ')}''')            
    #         elif (isinstance(value, (Sequence, Mapping)) 
    #                 and not isinstance(value, str)):
    #             representation.append(
    #                 f'''{attribute}:{new_line}{textwrap.indent(
    #                     str(value), '    ')}''')
    #         else:
    #             representation.append(f'{attribute}: {str(value)}')
    #     return new_line.join(representation)  


@dataclasses.dataclass
class Workflow(Component, sourdough.types.Hybrid):
    """Iterable base class in a sourdough composite object.
            
    Args:
        contents (Sequence[Component]): Component subclass instances. Defaults 
            to an empty list.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes.
        iterations (Union[int, str]): number of times the 'apply' method should 
            be called. If 'iterations' is 'infinite', the 'apply' method will
            continue indefinitely unless the method stops further iteration.
            Defaults to 1.
        criteria (str): after iteration is complete, a 'criteria' determines
            what should be outputted. This should correspond to a key in the
            'algorithms' Catalog for the sourdough project. Defaults to None.
        parallel (ClassVar[bool]): whether the 'contents' contain other 
            iterables (True) or static objects (False). If True, a subclass
            should include a custom iterable for navigating the stored 
            iterables. Defaults to False.
                            
    """
    contents: Sequence[Component] = dataclasses.field(default_factory = list)
    name: str = None
    iterations: Union[int, str] = 1
    criteria: str = None
    parallel: ClassVar[bool] = False 
    
    """ Public Methods """
    
    def apply(self, project: sourdough.Project, **kwargs) -> sourdough.Project:
        """[summary]

        Args:
            project (sourdough.Project): [description]

        Returns:
            sourdough.Project: [description]
            
        """
        if 'data' not in kwargs and project.data:
            kwargs['data'] = project.data
        for i in self.iterations:
            project = super().apply(project = project, **kwargs)
        return project   


@dataclasses.dataclass
class Resources(collections.abc.Container):
    """[summary]

    Args:
        collections ([type]): [description]

    Returns:
        [type]: [description]
        
    """ 
    
    settings: Type = sourdough.Settings
    manager: Type = sourdough.Manager
    creator: Type = Creator
    creators: Mapping[str, Type] = creators
    component: Type = Component
    components: Mapping[str, Type] = components
    instances: Mapping[str, object] = instances
    algorithms: Mapping[str, Type] = algorithms
    
    """ Dunder Methods """
    
    def __contains__(self, item: str) -> bool:
        """Returns whether an attribute exists mataching 'item'.
        
        Args:
            item (Any): item to look for a matching attribute name.
            
        Returns:
            bool: whether 'item' is the name of an attribute.
                
        """
        return item in self.__dir__()

    def __str__(self) -> str:
        """Returns pretty string representation of a class instance.
        
        Returns:
            str: normal representation of a class instance.
        
        """
        return pprint.pformat(self, sort_dicts = False, compact = True)


@dataclasses.dataclass
class Rules(object):
    """[summary]

    Args:
        object ([type]): [description]

    Returns:
        [type]: [description]
        
    """
    resources: Resources
    skip_sections: Sequence[str] = dataclasses.field(
        default_factory = lambda: ['general', 'files'])
    skip_suffixes: Sequence[str] = dataclasses.field(
        default_factory = lambda: ['parameters'])
    special_section_suffixes: Sequence[str] = dataclasses.field(
        default_factory = lambda: ['design'])
    default_design: str = 'pipeline'
    
    """ Properties """

    @property
    def component_suffixes(self) -> Tuple[str]:
        return tuple(k + 's' for k in self.resources.components.keys()) 
    