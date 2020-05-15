"""
.. module:: component
:synopsis: sourdough core component and related registry classes
:author: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import abc
import collections.abc
import dataclasses
import importlib
import inspect
import pathlib
import pyclbr
import re
from typing import (
    Any, Callable, ClassVar, Dict, Iterable, List, Optional, Tuple, Union)

import sourdough


   
@dataclasses.dataclass
class Library(collections.abc.MutableMapping): 
    """Stores subclass instances.
    
    Arguments:
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. If the class instance
            needs settings from the shared Settings instance, 'name' should
            match the appropriate section name in that Settings instance. When
            subclassing, it is a good settings to use the same 'name' attribute
            as the base class for effective coordination between sourdough
            classes. Defaults to None or __class__.__name__.lower().
        contents (Optional[Dict[str, Component]]): stored dictionary. Defaults 
            to an empty dictionary.
        base (object): related class for which matching subclasses and/or
            subclass instances should be stored.

    """
    name: Optional[str] = None
    contents: Optional[Dict[str, 'Component']] = dataclasses.field(
        default_factory = dict)
    base: Optional[object] = None

    """ Public Methods """
    
    def add(self, component: 'Component') -> None:
        """
        
        """
        self.contents[component.name] = component
        return self
        

    """ Required ABC Methods """

    def __getitem__(self, key: str) -> Any:
        """Returns value for 'key' in 'contents'.

        Arguments:
            key (str): name of key in 'contents' for which value is sought.

        Returns:
            Any: value stored in 'contents'.

        """
        return self.contents[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Sets 'key' in 'contents' to 'value'.

        Arguments:
            key (str): name of key to set in 'contents'.
            value (Any): value to be paired with 'key' in 'contents'.

        """
        self.contents[key] = value
        return self

    def __delitem__(self, key: str) -> None:
        """Deletes 'key' in 'contents'.

        Arguments:
            key (str): name of key in 'contents' to delete the key/value pair.

        """
        del self.contents[key]
        return self

    def __iter__(self) -> Iterable:
        """Returns iterable of 'contents'.

        Returns:
            Iterable: of 'contents'.

        """
        return iter(self.contents)

    def __len__(self) -> int:
        """Returns length of 'contents'.

        Returns:
            int: length of 'contents'.

        """
        return len(self.contents)

    """ Other Dunder Methods """

    def __add__(self, other: 'MappingBase') -> None:
        """Combines argument with 'contents'.

        Arguments:
            other (MappingBase): another MappingBase or compatiable dictionary

        """
        self.add(contents = other)
        return self
    
    def __iadd__(self, other: 'MappingBase') -> None:
        """Combines argument with 'contents'.

        Arguments:
            other (MappingBase): another MappingBase or compatiable dictionary

        """
        self.add(contents = other)
        return self

    def __repr__(self) -> str:
        """Returns '__str__' representation.

        Returns:
            str: default dictionary representation of 'contents'.

        """
        return self.__str__()

    def __str__(self) -> str:
        """Returns default dictionary representation of 'contents'.

        Returns:
            str: default dictionary representation of 'contents'.

        """
        return (
            f'sourdough {self.__class__.__name__} '
            f'name: {self.name} '
            f'contents: {self.contents.__str__()} ')   
    

@dataclasses.dataclass
class Catalog(Library): 
    """Base class for storing Component subclasses.

    Arguments:
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. If the class instance
            needs settings from the shared Settings instance, 'name' should
            match the appropriate section name in that Settings instance. When
            subclassing, it is a good settings to use the same 'name' attribute
            as the base class for effective coordination between sourdough
            classes. Defaults to None or __class__.__name__.lower().
        contents (Optional[Dict[str, Component]]): stored dictionary. Defaults 
            to an empty dictionary.
        base (object): related class for which matching subclasses and/or
            subclass instances should be stored.

        auto_register (Optional[bool]): whether to walk through the current
            working directory and subfolders to search for classes to add to
            the Library (True). Defaults to True.
    
    """ 
    name: Optional[str] = None  
    contents: Optional[Dict[str, 'Component']] = dataclasses.field(
        default_factory = dict)
    base: Optional[object] = None
    auto_register: Optional[bool] = False
        
    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        self.base
        if self.auto_register:
            self.walk(folder = pathlib.Path.cwd())
        return self
        
    """ Public Methods """

    def add(self, component: 'Component') -> None:
        """Combines argument with 'contents'.
        

        """
        try:
            key = sourdough.utilities.snakify(component.__name__)
            self.contents[key] = component
        except AttributeError:
            key = sourdough.utilities.snakify(component.__class__.__name__)
            self.contents[key] = component.__class__
        return self
    
    def create(self, name: str, **kwargs) -> 'Component':
        """Returns an instance of a stored subclass.
        
        Arguments:
            name (str): key to desired Component in 'contents'.
            
        Returns:
            Component: that has been instanced with kwargs as arguments.
            
        """
        return self[name](**kwargs)
     
    def walk(self, 
            folder: Union[str, pathlib.Path], 
            recursive: Optional[bool] = True) -> None:
        """Adds Component subclasses for python files in 'folder'.
        
        If 'recursive' is True, subfolders are searched as well.
        
        Arguments:
            folder (Union[str, pathlib.Path]): folder to initiate search for 
                Component subclasses.
            recursive (Optional[bool]): whether to also search subfolders (True)
                or not (False). Defaults to True.
                
        """
        if recursive:
            glob_method = 'rglob'
        else:
            glob_method = 'glob'
        for file_path in getattr(pathlib.Path(folder), glob_method)('*.py'):
            module = self._import_from_path(file_path = file_path)
            subclasses = self._get_subclasses(module = module)
            for subclass in subclasses:
                self.add({
                    sourdough.utilities.snakify(subclass.__name__): subclass})    
        return self
       
    """ Private Methods """
    
    def _import_from_path(self, file_path: Union[pathlib.Path, str]) -> object:
        """Returns an imported module from a file path.
        
        Arguments:
            file_path (Union[pathlib.Path, str]): path of a python module.
        
        Returns:
            object: an imported python module. 
        
        """
        file_path = pathlib.Path(file_path)
        module_spec = importlib.util.spec_from_file_location(file_path)
        module = importlib.util.module_from_spec(module_spec)
        return module_spec.loader.exec_module(module)
    
    def _get_subclasses(self, module: object) -> List['Component']:
        """Returns a list of Component subclasses.
        
        Arguments:
            module (object): an import python module.
        
        Returns:
            List[Component]: list of subclasses of Component. If none are found,
                an empty list is returned.
                
        """
        matches = []
        for item in pyclbr.readmodule(module):
            # Adds direct subclasses.
            if inspect.issubclass(item, Component):
                matches.append[item]
            else:
                # Adds subclasses of other subclasses.
                for subclass in self.contents.values():
                    if subclass(item, subclass):
                        matches.append[item]
        return matches


@dataclasses.dataclass
class Component(abc.ABC):
    """Base class for components in sourdough.

    Component and its subclasses store subclasses in 'library'. 'library' is a
    dictionary with string keys and Component values. Users can call the
    'create' classmethod to create subclass instances directly from Component.

    Whenever a Component subclass is instanced, it is automatically created to
    the 'library' if 'super().__post_init()' is called.

    To manually add new Component subclasses to the 'library', users can either
    call the 'register' classmethod or call the 'create' method. In the latter
    case, an instanced version of the Component subclass is returned.

    If a user wishes to use the 'library' feature of the sourdough Component
    class, no two Component subclasses should have the same name. This is
    because python dictionaries do not allow duplicate keys. It is possible to
    avoid this problem by having different 'name' attributes for classes with
    the same python class name and only using the automatic registration feature
    or only passing instances to the 'register' method. Although alternate keys
    could be automatically created, this process was determined to either be
    too cumbersome or likely to confuse users (without overly verbose feedback
    about the alternate key used).

    Arguments:
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. For example if a 
            class instance needs settings from the shared Settings instance, 
            'name' should match the appropriate section name in that Settings 
            instance. When subclassing, it is sometimes a good idea to use the 
            same 'name' attribute as the base class for effective coordination 
            between sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Component is called, 'name' is set to a snake 
            case version of the class name ('__class__.__name__').

    ToDo:
        Clean up catalog and library
    
    """
    name: Optional[str] = None
    catalog: ClassVar['Catalog'] = Catalog()
    library: ClassVar['Catalog'] = Library()

    """ Initialization Methods """
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Creates a Catalog instance if one doesn't exist.
        # print('test class', cls.__class__)
        # if not hasattr(cls.__class__, 'catalog') or not cls.__class__.catalog:
        #     cls.__class__.catalog = sourdough.core.registry.Catalog(base = cls)
        # # Creates a Library instance if one doesn't exist.
        # if not hasattr(cls.__class__, 'library') or not cls.__class__.library:
        #     cls.__class__.library = sourdough.core.registry.Library(base = cls)
        # Adds new subclass to 'catalog'.
        catalog_key = cls._get_name(component = cls)
        cls.catalog.add(cls)

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Sets 'name' to the default value if it is not passed.
        self.name = self.name or self._get_name(component = self)
        # Adds this subclass to instance to the parent class 'library'.
        self.__class__.library.add(self)  

    """ Class Methods """

    # @classmethod
    # def create(cls,
    #         component: Union[str, 'Component'],
    #         **kwargs) -> 'Component':
    #     """Returns a Component subclass for 'component'.

    #     Arguments:
    #         component (Union[str, Component]): either a key in 'catalog' or a
    #             Component subclass. If a Component subclass is passed, it is
    #             automatically added to 'catalog' and instanced.
    #         kwArguments: arguments to be passed to instanced Component subclass.

    #     Raises:
    #         ValueError: if 'component' is a string but does not exist in
    #             'catalog'.
    #         TypeError: if 'component' is neither a string nor Component.

    #     Returns:
    #         Component: instanced subclass with kwargs as initialization
    #             parameters.

    #     """
    #     if isinstance(component, cls):
    #         if cls.name not in cls.catalog:
    #             cls.register(component = component)
    #         return component(**kwargs)
    #     elif isinstance(component, str):
    #         if component in cls.catalog:
    #             return cls.catalog[component](**kwargs)
    #         else:
    #             raise ValueError(
    #                 f'{component} is not a recognized {cls.__name__} type')
    #     elif inspect.isclass(component):
    #         instance = component(**kwargs)
    #         if instance.name not in cls.catalog:
    #             cls.register(component = instance)
    #         return instance          
    #     else:
    #         raise TypeError(
    #             f'component must be a str or {cls.__name__} type or instance')

    # @classmethod
    # def register(cls,
    #         component: 'Component',
    #         name: Optional[str] = None) -> None:
    #     """Adds 'component' to 'library'.

    #     If 'name' is passed, that is the key used in 'library'.

    #     If not and 'component' is an instance, the 'name' attribute of that
    #     instance is used. If 'component' has not been instanced, the snake case
    #     of the class name (lower case and underscored appropriately) is used.

    #     Arguments:
    #         component (Component): subclass of Component to add to 'library'.
    #         name (Optional[str]): optional key name to use in 'library'.

    #     """
    #     if name is None:
    #         if inspect.isclass(component) or component.name is None:
    #             name = self._get_name()
    #         else:
    #             name = component.name
    #     if base is None:
    #         base = Component 
    #     cls._register_class(component = component, name = name)
    #     cls._register_instance(component = component, name = name)
    #     return cls

    @classmethod
    def _get_name(cls, component: 'Component') -> str:
        """Returns 'name' of class for use throughout sourdough.
        
        This method converts the class name from CapitalCase to snake_case.
        
        If a user wishes to use an alternate naming system, a subclass should
        simply override this method. When overriding '_get_name', a subclass
        should follow the same if/then/else structure in the code below so that
        the method handles both classes and instances.
        
        Returns:
            str: name of class for internal referencing.
        
        """
        if inspect.isclass(component):
            return sourdough.utilities.snakify(component.__name__)
        else:
            if component.name is not None:
                return component.name
            else:
                return sourdough.utilities.snakify(component.__class__.__name__)

    @classmethod
    def _initialize_catalog(cls) -> None:
        if inspect.isclass(cls):
            base = cls
        elif cls.__class__ == abc.ABC:
            print('yeah it found abc')
            base = Component
        else:
            base = cls.__class__
        if base == Component or cls.catalog is True:
            'yeah it found base'
            base.catalog = sourdough.core.registry.Catalog(base = base) 
        return cls    
        
    @classmethod
    def _register_in_catalog(cls, component: 'Component', name: str) -> None:
        """Adds 'component' class to 'catalog'.

        Arguments:
            component (Component): subclass of Component to add to 'catalog'.
            name (str): key name to use in 'catalog'.

        """          
        base = cls._get_catalog_base()
        if isinstance(component, base):
            component = component.__class__
        base.catalog[name] = component
        return cls

    @classmethod
    def _get_catalog_base(cls) -> 'Component':
        """Returns subclass or Component to be base for 'catalog'.
        
        Returns:
            Component: this class will serve as the base for 'catalog'.
        
        """
        try:
            return cls._catalog_base
        except AttributeError:
            return Component

    @classmethod
    def _initialize_library(cls) -> None:
        if inspect.isclass(cls):
            base = cls
        elif cls.__class__ is abc.ABC:
            base = Component
        else:
            base = cls.__class__
        if base is Component or cls.library is True:
            base.library = sourdough.core.registry.Library(base = base) 
        return cls    
            
    @classmethod
    def _register_in_library(cls, component: 'Component', name: str) -> None:
        """Adds 'component' to 'library' if it is an instance.

        Arguments:
            component (Component): subclass of Component to add to 'library'.
            name (str): key name to use in 'library'.

        """           
        base = cls._get_catalog_base()
        if isinstance(component, base):
            base.library[name] = component
        return cls

    @classmethod
    def _get_library_base(cls) -> 'Component':
        """Returns subclass or Component to be base for 'library'.
        
        Returns:
            Component: this class will serve as the base for 'library'.
        
        """
        try:
            return cls._library_base
        except AttributeError:
            return Component
     
    # @property
    # def catalog(self) -> Dict[str, 'Component']:
    #     return {
    #         sourdough.utilities.snakify(i.__name__): i
    #         for i in self.__subclasses__}
