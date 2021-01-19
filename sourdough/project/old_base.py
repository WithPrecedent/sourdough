"""
base: core base classes for sourdough projects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Director (Registrar, Hybrid):
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
class Creator(sourdough.quirks.Registrar, sourdough.quirks.Element, 
              sourdough.types.Lexicon, abc.ABC):
    """
            
    Args:
        
    """
    contents: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    product: Type = None
    registry: ClassVar[Mapping[str, Creator]] = sourdough.types.Catalog()
    
    """ Public Methods """
    
    @abc.abstractmethod
    def create(self, name: str, director: sourdough.Director, 
               **kwargs) -> object:
        """[summary]

        Args:
            name (str): [description]
            director (sourdough.Director): [description]

        Returns:
            object: [description]
            
        """
        pass      

          
@dataclasses.dataclass
class Director(sourdough.quirks.Registrar, sourdough.quirks.Element, 
               sourdough.types.Lexicon, abc.ABC):
    """Constructs, organizes, and implements part of a sourdough project.
        
    Args:
        contents (Mapping[str, object]]): stored objects created by the 
            'create' methods of 'stages'. Defaults to an empty dict.

        project (sourdough.Project)
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example if a 
            sourdough instance needs settings from a Configuration instance, 'name' 
            should match the appropriate section name in the Configuration instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. If it is None, the 'name' will be attempted to be 
            inferred from the first section name in 'settings' after 'general' 
            and 'files'. If that fails, 'name' will be the snakecase name of the
            class. Defaults to None. 
         
    """
    contents: Mapping[str, Type] = dataclasses.field(default_factory = dict)
    creators: Mapping[str, Creator] = dataclasses.field(default_factory = dict)
    project: Union[object, Type] = None
    name: str = None
    validations: Sequence[str] = dataclasses.field(default_factory = lambda: [
        'creators'])
    registry: ClassVar[Mapping[str, Director]] = sourdough.types.Catalog()
    
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent and/or mixin initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass
        # Calls validation methods based on items listed in 'validations'.
        for validation in self.validations:
            getattr(self, f'_validate_{validation}')()
        # Advances through 'creator' stages if 'automatic' is True.
        if self.automatic:
            self.complete()

    """ Public Methods """

    def advance(self) -> Any:
        """Returns next product created in iterating a Director instance."""
        return self.__next__()

    def complete(self) -> None:
        """Advances through the stored Creator instances.
        
        The results of the iteration is that each item produced is stored in 
        'content's with a key of the 'produces' attribute of each stage.
        
        """
        self.creator.complete()
        return self
    
    """ Private Methods """
    
    def _validate_name(self) -> None:
        """Creates 'name' if one doesn't exist."""
        if not self.name:
            self.name = sourdough.tools.snakify(self.__class__)
        return self
    
    def _validate_creators(self) -> None:
        """Creates 'name' if one doesn't exist.
        
        If 'name' was not passed, this method first tries to infer 'name' as the 
        first appropriate section name in 'settings'. If that doesn't work, it 
        uses the snakecase name of the class.
        
        """

        return self

    
@dataclasses.dataclass
class Component(sourdough.quirks.Registrar, sourdough.quirks.Element, abc.ABC):
    """Base container class for sourdough composite objects.
    
    A Component has a 'name' attribute for internal referencing and to allow 
    sourdough iterables to function propertly. Component instances can be used 
    to create a variety of composite workflows such as trees, cycles, contests, 
    studies, and graphs.
    
    Args:
        contents (Any): item(s) contained by a Component instance.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Configuration instance, 
            'name' should match the appropriate section name in a Configuration 
            instance. Defaults to None. 
        registry (ClassVar[Mapping[str, Type]]): a mapping storing all concrete
            subclasses. Defaults to the Catalog instance 'components'.
            
    """
    contents: Any = None
    subcontents: Any = None
    name: str = None
    needs: Union[str, Sequence[str]] = dataclasses.field(default_factory = list)
    produces: str = None
    design: str = None
    iterations: Union[int, str] = 1
    criteria: Union[str, Callable, Sequence[Union[Callable, str]]] = None
    parallel: ClassVar[bool] = False
    parameters: Mapping[Any, Any] = dataclasses.field(default_factory = dict)
    registry: ClassVar[Mapping[str, Type]] = sourdough.types.Catalog()

    """ Required Subclass Methods """

    @abc.abstractmethod
    def apply(self, director: sourdough.Director) -> sourdough.Director:
        """Subclasses must provide their own methods."""
        return director
          
    """ Public Methods """ 
    
    def finalize(self, recursive: bool = True) -> None:
        """[summary]

        Args:
            recursive (bool, optional): [description]. Defaults to True.

        Returns:
            [type]: [description]
            
        """
        new_contents = []
        for child in self.contents:
            new_child = self._instancify(component = child)
            if hasattr(new_child, 'finalize') and recursive:
                new_child = new_child.finalize(recursive = recursive)
            new_contents.append(new_child)
        self.contents = new_contents
        return self 
         
    # def implement(self, data: Any = None, **kwargs) -> Any:
    #     """[summary]

    #     Args:
    #         data (Any): [description]

    #     Returns:
    #         Any: [description]
    #     """
    #     if data is not None:
    #         kwargs['data'] = data
    #     try:
    #         self.contents.implement(**kwargs)
    #     except AttributeError:
    #         raise AttributeError(
    #             'stored object in Workflow lacks implement method')              

    """ Private Methods """

    def _instancify(self, component: Union[str, Component], 
                    **kwargs) -> Component:
        """
            
        """
        if isinstance(component, Component):
            for key, value in kwargs.items():
                setattr(component, key, value)
        else:
            if isinstance(component, str):
                try:
                    component = self.registry.select(key = component)
                except KeyError:
                    raise KeyError(
                        'component not found in the Component registry')
            elif issubclass(component, Component):
                pass
            else:
                raise TypeError('component must be a Component or str')
            component = component(**kwargs)
        return component 

    """ Dunder Methods """

    def __str__(self) -> str:
        """Returns default string representation of an instance.

        Returns:
            str: default string representation of an instance.

        """
        return '\n'.join([textwrap.dedent(f'''
            sourdough {self.__class__.__name__}
            name: {self.name}
            components:'''),
            f'''{textwrap.indent(str(self.contents), '    ')}'''])   
        