"""
workflows: Workflow and Stage base classes and registries.
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:

"""
from __future__ import annotations
import abc
import copy
import dataclasses
import pprint
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Union)

import sourdough


stages = sourdough.Catalog(
    defaults = ['draft', 'publish', 'apply'],
    always_return_list = True)


@dataclasses.dataclass
class Stage(sourdough.quirks.Registrar, abc.ABC):
    """Base class for a stage in a Workflow.
    
    Args:
        action (str): name of action performed by the class. This is used in
            messages in the terminal and logging. It is usually the verb form
            of the class name (i.e., for Draft, the action is 'drafting').
            
    """
    action: str = None

    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def perform(self, project: sourdough.Project, **kwargs) -> sourdough.Project:
        """Performs some action based on 'project' with kwargs (optional).
        
        Subclasses must provide their own methods.
        
        """
        pass
                
    """ Private Methods """
    
    def _get_need(self, name: str, project: sourdough.Project) -> Any:
        try:
            return getattr(project, name)
        except AttributeError:
            return project.results[name]
        
    def _set_product(self, name: str, product: Any, 
                     project: sourdough.Project) -> None:
        project.results[name] = product
        return project
    
    
@dataclasses.dataclass
class Workflow(sourdough.quirks.Registrar, sourdough.Hybrid, abc.ABC):
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
        sourdough.library.workflows[key] = cls
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
