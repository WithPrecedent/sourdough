"""
framework: base classes for sourdough projects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Inventory (Catalog): dictionary for storing Component options.
    Component (Element, Registry): base class for all elements of a 
        sourdough composite object. If you want to create custom elements for
        composites, you must subclass Component or one of its subclasses for
        the auto-registration library to work.


"""

from __future__ import annotations
import abc
import collections.abc
import dataclasses
import typing
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union

import sourdough


@dataclasses.dataclass
class Inventory(sourdough.base.Catalog):
    """Catalog subclass with a more limiting 'validate' method.

    Args:
        contents (Union[Component, Sequence[Component], Mapping[Any, 
            Component]]): Component(s) to validate or convert to a dict. If 
            'contents' is a Sequence or a Component, the key for storing 
            'contents' is the 'name' attribute of each Component.
        defaults (Sequence[str]]): a list of keys in 'contents' which will be 
            used to return items when 'default' is sought. If not passed, 
            'default' will be set to all keys.
        always_return_list (bool]): whether to return a list even when
            the key passed is not a list or special access key (True) or to 
            return a list only when a list or special acces key is used (False). 
            Defaults to False.
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
                     
    """
    contents: Mapping[Any, Any] = dataclasses.field(default_factory = dict)  
    defaults: Sequence[str] = dataclasses.field(default_factory = list)
    always_return_list: bool = False
    name: str = None
    validator: sourdough.Validator = sourdough.Validator(products = 'mapify')

    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent initialization method(s).
        super().__post_init__()
        # Sets 'stored_types' if not passed.
        # self.stored_types = self.stored_types or ('Component')
        
    """ Public Methods """

    def validate(self, 
            contents: sourdough.base.Elemental) -> Mapping[str, Component]:
        """Validates 'contents' or converts 'contents' to a dict.
        
        Args:
            contents (Union[Component, Mapping[Any, self.stored_types], 
                Sequence[Component]]): Component(s) to validate or convert to a 
                dict. If 'contents' is a Sequence or a Component, the key for 
                storing 'contents' is the 'name' attribute of each Component.
                
        Raises:
            TypeError: if 'contents' is neither a Component subclass, Sequence
                of Component subclasses, or Mapping with Components subclasses
                as values.
                
        Returns:
            Mapping (str, self.stored_types): a properly typed dict derived
                from passed 'contents'.
            
        """
        # if (isinstance(contents, Mapping)
        #     and (all(isinstance(c, self.stored_types) 
        #             for c in contents.values())
        #         or all(issubclass(c, self.stored_types)
        #                  for c in contents.values()))):
        #     return contents
        # elif isinstance(contents, self.stored_types):
        #     return {contents.name: contents}
        # elif (inspect.isclass(contents) 
        #         and issubclass(contents, self.stored_types)):
        #     return {contents.get_name(): contents}
        # elif isinstance(contents, Sequence):
        #     new_contents = {}
        #     for element in contents:
        #         if (isinstance(contents, self.stored_types) or 
        #                 (inspect.isclass(contents) 
        #                     and issubclass(contents, self.stored_types))):
        #             try:
        #                 new_contents[element.name] = element
        #             except AttributeError:
        #                 new_contents[element.get_name()] = element
        #         else:
        #             raise TypeError(
        #                 'contents must contain all Component subclasses or '
        #                 'subclass instances')  
        #     return new_contents
        # else:
        #     raise TypeError(
        #         f'contents must a dict with {self.stored_types} values, '
        #         f'{self.stored_types}, or a list of {self.stored_types}')    
 
 
@dataclasses.dataclass
class Component(sourdough.base.Registry, sourdough.base.Element):
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
        library (ClassVar[Inventory]): the instance which automatically stores 
            any subclass of Component.
              
    """
    contents: Any = None
    name: str = None
    library: ClassVar[Inventory] = Inventory()

    """ Public Methods """
    
    def validate(self, contents: Sequence[Any]) -> Sequence[Any]:
        """Validates 'contents' or converts 'contents' to proper type.
        
        Args:
            contents (Sequence[Any]): item(s) to validate or convert to a list.
            
        Raises:
            TypeError: if 'contents' argument is not of a supported datatype.
            
        Returns:
            Sequence[Any]: validated or converted argument that is compatible 
                with an instance.
        
        """
        contents = self.validator.verify(contents = contents)
        return self.validator.convert(element = contents)  

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
class Structure(sourdough.base.Registry, sourdough.base.Hybrid, abc.ABC):
    """Base class for composite objects in sourdough projects.
      
        3) It uses a 'validate' method to validate or convert the passed 
            'contents' argument. It will convert all supported datatypes to 
            a list. The 'validate' method is automatically called when a
            Slate is instanced and when the 'add' method is called.  
            
    Args:
        contents (Sequence[Union[str, Component]]): a list of str or Components. 
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
        library (ClassVar[Inventory]): An Inventory instance which 
            will automatically store all subclasses.
                
    """
    contents: Sequence[Union[str, Component]] = dataclasses.field(
        default_factory = list)
    name: str = None
    validator: ClassVar[sourdough.base.Validator] = sourdough.base.Validator(
            products = 'sequence',                                                                               
            accepts = sourdough.base.Elemental)
    library: ClassVar[Inventory] = Inventory(stored_types = Component)

    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent initialization method(s).
        super().__post_init__()        
        # Initializes 'index' for iteration.
        self.index = -1
            
    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def iterate(self, **kwargs) -> Iterable:
        pass
    
    @abc.abstractmethod
    def activate(self, **kwargs) -> Iterable:
        pass    
    
    @abc.abstractmethod
    def finalize(self, **kwargs) -> Iterable:
        pass

    """ Public Methods """
    
    def validate(self, contents: Sequence[Any]) -> Sequence[Any]:
        """Validates 'contents' or converts 'contents' to proper type.
        
        Args:
            contents (Sequence[Any]): item(s) to validate or convert to a list.
            
        Raises:
            TypeError: if 'contents' argument is not of a supported datatype.
            
        Returns:
            Sequence[Any]: validated or converted argument that is compatible 
                with an instance.
        
        """
        contents = self.validator.verify(contents = contents)
        return self.validator.convert(element = contents)
  
    """ Dunder Methods """
    
    def __iter__(self) -> Iterable:
        if self.index + 1 < len(self.contents):
            self.index += 1
            yield self.iterate()
        else:
            raise StopIteration


@dataclasses.dataclass
class Stage(
        sourdough.base.Registry, 
        sourdough.base.Action, 
        abc.ABC):
    """Base class for a stage in a Workflow.
    
    Args:
    
    """
    name: str = None
    needs: ClassVar[Sequence[str]] = []
    library: ClassVar[Inventory] = Inventory()

    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def perform(self, **kwargs) -> object:
        """Performs some action related to kwargs.
        
        Subclasses must provide their own methods.
        
        """
        pass
        

@dataclasses.dataclass
class Workflow(
        sourdough.base.Registry, 
        sourdough.base.Hybrid, 
        abc.ABC):
    """Base class for sourdough workflows.
    
    Args:
        
    """
    contents: Sequence[Union[str, Stage]] = dataclasses.field(
        default_factory = list)
    name: str = None
    library: ClassVar[Inventory] = Inventory(stored_types = Stage)
     
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
