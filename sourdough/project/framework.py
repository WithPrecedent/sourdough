"""
framework: core classes for sourdough projects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Component (Registry, Element, ABC): base class for all elements of a 
        sourdough composite object. If you want to create custom elements for
        composites, you must subclass Component or one of its subclasses for
        the auto-registration library to work.
    Stage (Registry, Element, ABC): step in a Workflow. All Stage subclasses
        must have 'perform' methods.
    Workflow (Registry, Sequencify, Hybrid, ABC): type validated iterable only 
        containing Stage instances. 
    
"""
from __future__ import annotations
import abc
import dataclasses
import inspect
from types import new_class
from typing import (
    Any, Callable, ClassVar, Dict, Iterable, List, Mapping, Sequence, Union)

import sourdough
    
    
@dataclasses.dataclass
class Component(sourdough.quirks.Registry, sourdough.base.Element, abc.ABC):
    """Base class for all pieces of sourdough composite objects.
    
    A Component differs from an Element in 3 significant ways:
        1) It includes a 'contents' attribute which can store any type of
            object as part of a larger composite structure. In this way, 
            Component acts as a wrapper for pieces in a composite whole.
        2) It includes a 'library' registry that stores all subclasses. This
            makes it easy to access any imported Component subclass using a
            string key.
        3) It has several private class methods which allow access to 'library' 
            using other techniques other than the associated string key.
    
    Args:
        contents (Any): a stored object.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Element is called, 'name' is set based upon
            the 'get_name' method in Element. If that method is not overridden 
            by a subclass instance, 'name' will be assigned to the snake case 
            version of the class name ('__class__.__name__'). 
        library (ClassVar[sourdough.base.Catalog[str, Component]]): an instance 
            which automatically stores any subclasses. 
              
    """
    contents: Any = None
    name: str = None
    library: ClassVar[
        sourdough.base.Catalog[str, Component]] = sourdough.base.Catalog()

    """ Private Class Methods """

    @classmethod
    def _get_keys_by_type(cls, component: Component) -> Sequence[Component]:
        """[summary]

        Returns:
        
            [type]: [description]
            
        """
        return [k for k, v in cls.library.items() if issubclass(v, component)]

    @classmethod
    def _get_values_by_type(cls, component: Component) -> Sequence[Component]:
        """[summary]

        Returns:
        
            [type]: [description]
            
        """
        return [v for k, v in cls.library.items() if issubclass(v, component)]
   
    @classmethod
    def _suffixify(cls) -> Mapping[str, Component]:
        """[summary]

        Returns:
            [type]: [description]
        """
        return {f'_{k}s': v for k, v in cls.library.items()}   


@dataclasses.dataclass
class Stage(
        sourdough.quirks.Registry, 
        sourdough.base.Element, 
        abc.ABC):
    """Base class for a stage in a Workflow.
    
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Element is called, 'name' is set based upon
            the 'get_name' method in Element. If that method is not overridden 
            by a subclass instance, 'name' will be assigned to the snake case 
            version of the class name ('__class__.__name__').
        library (ClassVar[sourdough.base.Catalog[str, Component]]): an instance 
            which automatically stores any subclasses. 
            
    """
    name: str = None
    library: ClassVar[
        sourdough.base.Catalog[str, Component]] = sourdough.base.Catalog()

    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def perform(self, project: sourdough.interface.Project, **kwargs) -> object:
        """Performs some action related to kwargs.
        
        Subclasses must provide their own methods.
        
        """
        pass
        

@dataclasses.dataclass
class Workflow(
        sourdough.quirks.Registry, 
        sourdough.validators.Sequencify,
        sourdough.base.Hybrid, 
        abc.ABC):
    """Base class for sourdough workflows.
    
    Args:
        contents (Sequence[Union[str, Component]]): a list of str or Stages. 
            Defaults to an empty list.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Element is called, 'name' is set based upon
            the 'get_name' method in Element. If that method is not overridden 
            by a subclass instance, 'name' will be assigned to the snake case 
            version of the class name ('__class__.__name__').     
        library (ClassVar[sourdough.base.Catalog[str, Component]]): an instance 
            which automatically stores any subclasses.     
               
    """
    contents: Sequence[Union[str, Stage]] = dataclasses.field(
        default_factory = list)
    name: str = None
    accepts: Union[Sequence[Any], Any] = dataclasses.field(
        default_factory = lambda: Stage)
    stores: Any = dataclasses.field(default_factory = lambda: list)
    library: ClassVar[
        sourdough.base.Catalog[str, Component]] = sourdough.base.Catalog()

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass
        # Validates or converts 'contents'.
        self.contents = self.convert(contents = self.contents)
        
    """ Public Methods """

    def perform(self, project: sourdough.Project) -> sourdough.Project:
        """[summary]

        Args:
            project (sourdough.Project): [description]

        Returns:
            sourdough.Project: [description]
        """
        for step in self.contents:
            instance = step()
            parameters = self._get_stage_parameters(
                flow = step, 
                project = project)
            result = instance.perform(**parameters)
            setattr(project, result.name, result)
        return project
    
    """ Private Methods """
       
    def _get_stage_parameters(self, 
            flow: Stage,
            project: sourdough.Project) -> Mapping[str, Any]:
        """[summary]

        Args:
            flow (Stage): [description]

        Returns:
            Mapping[str, Any]: [description]
            
        """
        parameters = {}
        for need in flow.needs:
            if need in ['project']:
                parameters['project'] = project
            else:
                parameters[need] = getattr(project, need)
        return parameters
