"""
creator: base class for workflow construction and application
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Creator (Registrar):
    Component ():
    
"""
from __future__ import annotations
import abc
import collections.abc
import dataclasses
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Union)

import sourdough
   

@dataclasses.dataclass
class Creator(sourdough.quirks.Registrar):
    """Base class for creating objects for a Project.
    
    Args:
        action (str): name of action performed by the class. This is used in
            messages in the terminal and logging. It is usually the verb form
            of the class name (i.e., for Draft, the action is 'drafting').
            
    """
    action: ClassVar[str]
    needs: ClassVar[Union[str, Tuple[str]]]
    produces: ClassVar[str]
    
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
    def create(self, previous: Any, 
               project: sourdough.Project, **kwargs) -> Any:
        """Performs some action based on 'project' with kwargs (optional).
        
        Subclasses must provide their own methods.
        
        """
        pass

    """ Class Methods """
    
    @classmethod
    def register(cls) -> None:
        """Registers a subclass in a Catalog."""
        key = sourdough.tools.snakify(cls.__name__)
        sourdough.project.resources.creators[key] = cls
        return cls

    @classmethod
    def parameterize(cls, project: sourdough.Project) -> Mapping[str, Any]:
        """[summary]

        Args:
            project (sourdough.Project): [description]

        Returns:
            Mapping[str, Any]: [description]
            
        """
        parameters = {}
        for item in sourdough.tools.tuplify(cls.needs):
            try:
                parameters.update({item: project[item]})
            except KeyError:
                parameters.update({item: getattr(project, item)})
        parameters.update({'project': project})
        return parameters
    
    # @classmethod
    # def store(cls, project: sourdough.Project, product: Any) -> None:
    #     """[summary]

    #     Args:
    #         project (sourdough.Project): [description]
    #         product (Any): [description]

    #     Returns:
    #         [type]: [description]
    #     """
    #     project.update({cls.produces: product})
    #     return cls


    """ Private Methods """
    
    @classmethod
    def _get_name(cls) -> str:
        """Returns 'name' of class instance for use throughout sourdough.
        
        This method converts the class name from CapitalCase to snake_case.
        
        If a user wishes to use an alternate naming system, a subclass should
        simply override this method. 
        
        Returns:
            str: name of class for internal referencing and some access methods.
        
        """
        return sourdough.tools.snakify(cls.__name__)
                
    
@dataclasses.dataclass
class Component(sourdough.quirks.Registrar, sourdough.quirks.Librarian, 
                collections.abc.Container):
    """Base container class for sourdough composite objects.
    
    A Component has a 'name' attribute for internal referencing and to allow 
    sourdough iterables to function propertly. Component instances can be used 
    to create a variety of composite data workflows such as trees, cycles, 
    contests, studies, and graphs.
    
    Args:
        contents (Any): item(s) contained by a Component instance.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. 

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

    """ Required Subclass Methods """

    @abc.abstractmethod
    def apply(self, project: sourdough.Project) -> sourdough.Project:
        """Subclasses must provide their own methods."""
        return project

    """ Class Methods """
    
    @classmethod
    def register(cls) -> None:
        """Registers a subclass in a Catalog."""
        key = sourdough.tools.snakify(cls.__name__)
        sourdough.project.resources.components[key] = cls
        return cls
    
    """ Public Methods """
    
    def deposit(self) -> None:
        """Stores a subclass instance in a Catalog."""
        sourdough.project.resources.instances[self.name] = self
        return self

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
class Workflow(sourdough.Component, sourdough.types.Hybrid):
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
                            
    """
    contents: Sequence[Component] = dataclasses.field(default_factory = list)
    name: str = None
    parallel: ClassVar[bool] = False 
    

    """ Public Methods """
    
    def apply(self, data: object = None, **kwargs) -> NotImplementedError:
        """Subclasses must provide their own methods.       
        
        """
        raise NotImplementedError(
            'subclasses of Flow must provide their own apply methods')
