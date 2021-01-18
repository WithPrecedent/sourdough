"""
base: essential classes applying sourdough's core to a project
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Bases
    Settings
    Filer
    Creator
    Component

"""
from __future__ import annotations
import abc
import dataclasses
import pathlib
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import sourdough
    

@dataclasses.dataclass
class ComponentWorkshop(sourdough.factory.Workshop):
    """[summary]

    Args:
        sourdough ([type]): [description]
    """
    registry: ClassVar[Mapping[str, Type]] = sourdough.types.Catalog()
 

@dataclasses.dataclass
class Component(sourdough.factory.Product, sourdough.workflows.Node):
    """[summary]

    Args:
        sourdough ([type]): [description]
    """
    name: str = None
    contents: Any = None

    """ Class Methods """

    @classmethod
    def register(cls) -> None:
        """Registers a subclass in a Catalog in ComponentWorkshop.
        
        The default 'register' method uses the snake-case name of the class as
        the key for the stored subclass.
        
        """
        key = sourdough.tools.snakify(cls.__name__)
        ComponentWorkshop.registry[key] = cls
        return cls
    
    
@dataclasses.dataclass    
class Parameters(sourdough.types.Lexicon):
    """
    """
    contents: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    name: str = None
    base: Union[Type, str] = None
    required: Sequence[str] = dataclasses.field(default_factory = list)
    runtime: Mapping[str, str] = dataclasses.field(default_factory = dict)
    selected: Sequence[str] = dataclasses.field(default_factory = list)
    default: ClassVar[Mapping[str, Any]] = {}
    
    """ Public Methods """
    
    def create(self, creator: sourdough.project.Creator, **kwargs) -> None:
        """[summary]

        Args:
            creator (sourdough.project.Creator): [description]

        """
        if not kwargs:
            kwargs = self.default
        for kind in ['settings', 'required', 'runtime', 'selected']:
            kwargs = getattr(self, f'_get_{kind}')(creator = creator, **kwargs)
        self.contents = kwargs
        return self
    
    """ Private Methods """
    
    def _get_settings(self, creator: sourdough.project.Creator, 
                      **kwargs) -> Dict[str, Any]:
        """[summary]

        Args:
            creator (sourdough.project.Creator): [description]

        Returns:
            Dict[str, Any]: [description]
            
        """
        try:
            kwargs.update(creator.settings[f'{self.name}_parameters'])
        except KeyError:
            pass
        return kwargs
    
    def _get_required(self, creator: sourdough.project.Creator, 
                      **kwargs) -> Dict[str, Any]:
        """[summary]

        Args:
            creator (sourdough.project.Creator): [description]

        Returns:
            Dict[str, Any]: [description]
            
        """
        for item in self.required:
            if item not in kwargs:
                kwargs[item] = self.default[item]
        return kwargs
    
    def _get_runtime(self, creator: sourdough.project.Creator, 
                      **kwargs) -> Dict[str, Any]:
        """[summary]

        Args:
            creator (sourdough.project.Creator): [description]

        Returns:
            Dict[str, Any]: [description]
            
        """
        for parameter, attribute in self.runtime.items():
            try:
                kwargs[parameter] = getattr(creator, attribute)
            except AttributeError:
                pass
        return kwargs

    def _get_selected(self, creator: sourdough.project.Creator, 
                      **kwargs) -> Dict[str, Any]:
        """[summary]

        Args:
            creator (sourdough.project.Creator): [description]

        Returns:
            Dict[str, Any]: [description]
            
        """
        if self.selected:
            kwargs = {k: kwargs[k] for k in self.selected}
        return kwargs
     