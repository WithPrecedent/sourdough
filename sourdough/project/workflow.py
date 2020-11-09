"""
workflows: Workflow and Stage base classes and registries.
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Stage (Registrar, Container):
    Workflow (Registrar, Hybrid, ABC):
    
"""
from __future__ import annotations
import abc
import collections.abc
import dataclasses
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Union)

import sourdough
   

@dataclasses.dataclass
class Stage(sourdough.quirks.Registrar, collections.abc.Container):
    """Base class for a stage in a Workflow.
    
    Args:
        contents (Any): item(s) contained by an instance. Defaults to None.
        action (str): name of action performed by the class. This is used in
            messages in the terminal and logging. It is usually the verb form
            of the class name (i.e., for Draft, the action is 'drafting').
            
    """
    contents: Any = None
    action: str = None

    """ Required Subclass Methods """
    
    @classmethod
    @abc.abstractmethod
    def create(cls, project: sourdough.Project, **kwargs) -> Stage:
        """Performs some action based on 'project' with kwargs (optional).
        
        Subclasses must provide their own methods.
        
        """
        pass

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
    
    def __iter__(self) -> Iterable:
        """Returns iterable of 'contents'.

        Raises:
            TypeError: if 'contents' is not iterable or if it is a str type.

        Returns:
            Iterable: of 'contents'.
            
        """
        if not isinstance(self.contents, str):
            return iter(self.contents)
        else:
            return TypeError('This Stage''s contents are not iterable.')

   
@dataclasses.dataclass
class Workflow(sourdough.quirks.Registrar, sourdough.types.Hybrid, abc.ABC):
    """Base class for sourdough workflows.
    
    Args:
        contents (Union[Sequence[str], Sequence[Stage]]): a list of str or 
            Stages. Defaults to an empty list.
        project (sourdough.Project): related project instance.
               
    """
    contents: Union[Sequence[str], Sequence[Stage]] = dataclasses.field(
        default_factory = list)
    project: sourdough.Project = None

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent and/or mixin initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass
        # Validates or converts 'contents'.
        self._initialize_stages()

    """ Class Methods """
    
    @classmethod
    def register(cls) -> None:
        key = sourdough.tools.snakify(cls.__name__)
        sourdough.project.resources.workflows[key] = cls
        return cls
   
    """ Private Methods """
     
    def _initialize_stages(self) -> None:
        """[summary]

        Raises:
            TypeError: [description]

        Returns:
            [type]: [description]
            
        """
        new_stages = []
        for stage in self.contents:
            if isinstance(stage, str):
                new_stages.append(Stage.instance(stage))
            elif issubclass(stage, Stage):
                new_stages.append(stage())
            else:
                raise TypeError('All stages must be str or Stage type')
        self.contents = new_stages
        return self

    
    def _get_last_stage(self) -> sourdough.Stage:
        last_key = self.project.contents.keys()[:-1]
        return self.project.contents[last_key]
        
    """ Dunder Methods """
    
    def __next__(self) -> Stage:
        previous_stage = self._get_last_stage()
        key = sourdough.tools.snakify(stage.__class__.__name__)
        self.add({key : stage.create(project = self)})
    
    def __iter__(self) -> Iterable:
        
        