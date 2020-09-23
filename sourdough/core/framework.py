"""
framework: core classes for sourdough projects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Inventory (Mapify, Catalog): type validated dictionary for storing Component 
        options and strategies.
    Component (Registry, Element, ABC): base class for all elements of a 
        sourdough composite object. If you want to create custom elements for
        composites, you must subclass Component or one of its subclasses for
        the auto-registration library to work.
    Componental: annotation type for all classes that contain Components. This
        includes any Component subclass, Sequences of Components, and Mappings 
        with Components values.
    Stage (Registry, Element, ABC): step in a Workflow. All Stage subclasses
        must have 'perform' methods.
    Workflow (Registry, Sequencify, Hybrid, ABC): type validated iterable only 
        containing Stage instances. 
    
"""
from __future__ import annotations
import abc
import dataclasses
import typing
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union

import sourdough


@dataclasses.dataclass
class Inventory(sourdough.quirks.Mapify, sourdough.base.Catalog):
    """Catalog subclass with a more limiting 'validate' method.

    Inventory differs from a 'Catalog' in one way:
        1) It inherits from Mapify which has the following methods for type
            validation and conversion: 'verify', 'convert'.
            
    Args:
        contents (Mapping[str, Component]]): stored dictionary. Defaults to an 
            empty dict.
        defaults (Sequence[str]]): a list of keys in 'contents' which will be 
            used to return items when 'default' is sought. If not passed, 
            'default' will be set to all keys.
        always_return_list (bool]): whether to return a list even when
            the key passed is not a list or special access key (True) or to 
            return a list only when a list or special acces key is used (False). 
            Defaults to False.
        accepts (Union[Sequence[Any], Any]): type(s) accepted by the parent 
            class either as an individual item, in a Mapping, or in a Sequence.
            Defaults to Component.
        stores (Any): a single type stored by the parent class. Defaults 
            to dict.
                     
    """
    contents: Mapping[str, Component] = dataclasses.field(
        default_factory = dict)  
    defaults: Sequence[str] = dataclasses.field(default_factory = list)
    always_return_list: bool = False
    accepts: Union[Sequence[Any], Any] = dataclasses.field(
        default_factory = lambda: Component)
    stores: Any = dataclasses.field(default_factory = lambda: dict)
    

@dataclasses.dataclass
class Component(sourdough.quirks.Registry, sourdough.base.Element, abc.ABC):
    """Base class for all pieces of sourdough composite objects.
    
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
        library (ClassVar[Inventory[str, Component]]): an instance which 
            automatically stores any subclasses. 
              
    """
    contents: Any = None
    name: str = None
    library: ClassVar[Inventory[str, Component]] = Inventory()

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


Componental = Union[Component, Mapping[str, Component], Sequence[Component]]


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
        library (ClassVar[Inventory[str, Stage]]): an instance which 
            automatically stores any subclasses. 
            
    """
    name: str = None
    library: ClassVar[Inventory[str, Stage]] = Inventory()

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
        sourdough.quirks.Sequencify,
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
        library (ClassVar[Inventory[str, Workflow]]): an instance which 
            automatically stores any subclasses.        
               
    """
    contents: Sequence[Union[str, Stage]] = dataclasses.field(
        default_factory = list)
    name: str = None
    library: ClassVar[Inventory[str, Workflow]] = Inventory()
     
    """ Public Methods """
    
    def validate(self, 
            contents: Sequence[Union[str, Stage]]) -> Sequence[Stage]:
        """Validates 'contents' or converts 'contents' to proper type.
        
        Args:
            contents (Sequence[Union[str, Stage]]): items to validate 
                or convert to a list of Stage instances.
            
        Raises:
            TypeError: if 'contents' argument is not of a supported datatype.
            
        Returns:
            Sequence[Stage]: validated or converted argument that is 
                compatible with an instance.
        
        """
        new_contents = []
        for item in contents:
            if isinstance(item, str):
                new_contents.append(Stage.build(key = item))
            elif isinstance(item, Stage):
                new_contents.append(item)
            else:
                raise TypeError('contents must be a list of Stage or str types')
        return new_contents

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
