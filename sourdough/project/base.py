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
class Factory(sourdough.types.Lexicon, abc.ABC):
    """
            
    Args:
        
    """
    contents: Mapping[str, str] = dataclasses.field(default_factory = dict)
    manager: object = None
   
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent and/or mixin initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass
        # Sets index for iteration.
        self.index = 0
            
    """ Public Methods """
    
    def advance(self) -> Any:
        """Returns next product created in iterating a Factory instance."""
        product = self.contents[self.contents.keys()[self.index]]
        self.mananger.contents[product] = self.__next__()
        return self

    def complete(self) -> None:
        """Executes each step in an instance's iterable."""
        for action, product in iter(self):
            self.advance()
        return self

    """ Dunder Methods """
 
    def __next__(self) -> object:
        """Returns product from next stage in an instance iterable.

        Returns:
            Any: item project by the 'create' method of a Creator.
            
        """
        if self.index < len(self.contents):
            action = self.contents.keys()[self.index]
            product = self.contents[action]
            method = f'create_{product}'
            if self.index < 1:
                previous_product = 'settings'
            else:
                previous_product = self.contents(
                    self.contents.keys()[self.index - 1])
            if (hasattr(self.manager.project, 'verbose') 
                    and self.manager.project.verbose):
                print(f'{action} {product} from {previous_product}')
            self.index += 1
            return getattr(self, method)()
        else:
            StopIteration
        
          
@dataclasses.dataclass
class Manager(sourdough.quirks.Registrar, sourdough.quirks.Loader, 
              sourdough.types.Lexicon):
    """Constructs, organizes, and implements part of a sourdough project.
        
    Args:
        contents (Mapping[str, object]]): stored objects created by the 
            'create' methods of 'stages'. Defaults to an empty dict.
        stages (Sequence[Union[Type, str]]): a Creator-compatible classes or
            strings corresponding to the keys in registry of the default
            'stage' in 'bases'. Defaults to a list of 'architect', 
            'builder', and 'worker'. 
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
    contents: Mapping[str, object] = dataclasses.field()
    project: Union[object, Type] = None
    creator: Union[object, Type] = None
    name: str = None
    automatic: bool = True
    data: object = None
    validations: Sequence[str] = dataclasses.field(default_factory = lambda: [
        'name', 'creator'])
    default_design: str = 'pipeline'
    registry: ClassVar[Mapping[str, Manager]] = sourdough.types.Catalog()
    
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
        """Returns next product created in iterating a Manager instance."""
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
    
    def _validate_creator(self) -> None:
        """Creates 'name' if one doesn't exist.
        
        If 'name' was not passed, this method first tries to infer 'name' as the 
        first appropriate section name in 'settings'. If that doesn't work, it 
        uses the snakecase name of the class.
        
        """
        if not self.name:
            node_sections = self.settings.excludify(subset = self.rules.skip)
            try:
                self.name = node_sections.keys()[0]
            except IndexError:
                self.name = sourdough.tools.snakify(self.__class__)
        return self
    
    """ Dunder Methods """

    def __iter__(self) -> None:
        """
        """
        self.creator.__next__()
        return self
 
    def __next__(self) -> None:
        """
        """
        self.creator.__next__()
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
            sourdough instance needs settings from a Configuration instance, 'name' 
            should match the appropriate section name in the Configuration instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. 
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
    def apply(self, manager: sourdough.Manager) -> sourdough.Manager:
        """Subclasses must provide their own methods."""
        return manager
          
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
        