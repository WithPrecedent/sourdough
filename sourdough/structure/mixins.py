
"""
.. module:: mixins
:synopsis: sourdough mixins
:author: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import abc
import dataclasses
import importlib
import inspect
import pathlib
import pyclbr
from typing import Any, ClassVar, Iterable, Mapping, Sequence, Tuple, Union

import sourdough


@dataclasses.dataclass
class Library(sourdough.Catalog): 
    """Dictionary for storing subclass instances.

    Library adds 'base' to an ordinary Catalog implementation. 'base' is the
    object where the Library instance is stored as a class variable. This allows
    each subclass, with a registration method to automatically store instances
    in the base class Library instance.
    
    Args:
        contents (Optional[Mapping[str, Component]]): stored dictionary. 
            Defaults to en empty dict.
        defaults (Optional[Sequence[str]]): a list of keys in 'contents' which
            will be used to return items when 'default' is sought. If not
            passed, 'default' will be set to all keys.
        always_return_list (Optional[bool]): whether to return a list even when
            the key passed is not a list (True) or to return a list in all cases
            (False). Defaults to True.
        base (object): related class where Component subclass instances should 
            be stored.

    """
    contents: Optional[Mapping[str, 'sourdough.Component']] = dataclasses.field(
        default_factory = dict)
    defaults: Optional[Sequence[str]] = dataclasses.field(
        default_factory = list)
    always_return_list: Optional[bool] = True
    base: Optional[object] = None
    
    """ Public Methods """

    def add(self, component: 'sourdough.Component') -> None:
        """Adds 'component' to 'contents'.
        
        Args:
            component (sourdough.Component) -> a Component instance to add to
                'contents'.

        Raises:
            TypeError: if 'component' is not a Component instance.
            
        """
        if isinstance(component, sourdough.Component):
            self.contents[component.name] = component
        else:
            raise TypeError('component must be a Component instance')
        return self
    
    """ Dunder Methods """

    def __str__(self) -> str:
        """Returns default string representation of an instance.

        Returns:
            str: default string representation of an instance.

        """
        return (
            f'sourdough {self.__class__.__name__}\n'
            f'base: {self.base.__name__}\n'
            f'contents: {self.contents.__str__()}')   


@dataclasses.dataclass
class LibraryMixin(abc.ABC):
    """Mixin which creates a proxy name for a Component subclass attribute.


    """
    library: ClassVar['sourdough.Library'] = sourdough.Library()
    
    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Adds this class instance to the base library of instances if the 
        # current instance is not the base class.
        if self.library.base != self.__class__:
            self.library.base.add(component = self)
    
        
@dataclasses.dataclass
class Registry(sourdough.Catalog): 
    """Dictionary for  storing subclasses.

    Args:
        contents (Optional[Mapping[str, Component]]): stored dictionary. 
            Defaults to en empty dict.
        defaults (Optional[Sequence[str]]): a list of keys in 'contents' which
            will be used to return items when 'default' is sought. If not
            passed, 'default' will be set to all keys.
        always_return_list (Optional[bool]): whether to return a list even when
            the key passed is not a list (True) or to return a list in all cases
            (False). Defaults to False.
        base (object): related class where subclasses should be stored.
        auto_register (Optional[bool]): whether to walk through the current
            working directory and subfolders to search for classes to add to
            the Library (True). Defaults to True.
    
    """ 
    contents: Optional[Mapping[str, 'sourdough.Component']] = dataclasses.field(
        default_factory = dict)
    defaults: Optional[Sequence[str]] = dataclasses.field(
        default_factory = list)
    always_return_list: Optional[bool] = False
    base: Optional[object] = None
    auto_register: Optional[bool] = False
        
    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Sets base class to this instance's class if 'base' is not passed.
        self.base = self.base or self.__class__
        # Finds Component subclasses in the present working folder or 
        # subfolders if 'auto_register' is True.
        if self.auto_register:
            self.walk(folder = pathlib.Path.cwd())
        return self
     
    """ Class Methods """
    
    @classmethod
    def create(cls, name: str, **kwargs) -> 'sourdough.Component':
        """Returns an instance of a stored subclass.
        
        This method acts as a factory for instancing stored Component 
        subclasses.
        
        Args:
            name (str): key to desired Component in 'contents'.
            kwargs: arguments to pass to the selected Component when it is
                instanced.
                    
        Returns:
            sourdough.Component: that has been instanced with kwargs as 
                arguments.
            
        """
        return cls.contents[name](**kwargs) 
        
    """ Public Methods """

    def add(self, component: 'sourdough.Component') -> None:
        """Adds 'component' to 'contents'.
        
        Args:
            component (sourdough.Component) -> a Component subclass to add to
                'contents'.

        Raises:
            TypeError: if 'component' is not a Component subclass
            
        """
        try:
            key = sourdough.utilities.snakify(component.__name__)
            self.contents[key] = component
        except AttributeError:
            try:
                key = sourdough.utilities.snakify(component.__class__.__name__)
                self.contents[key] = component.__class__
            except AttributeError:
                raise TypeError('component must be a Component subclass')
        return self

    def walk(self, 
            folder: Union[str, pathlib.Path], 
            recursive: Optional[bool] = True) -> None:
        """Adds Component subclasses for python files in 'folder'.
        
        If 'recursive' is True, subfolders are searched as well.
        
        Args:
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
        
        Args:
            file_path (Union[pathlib.Path, str]): path of a python module.
        
        Returns:
            object: an imported python module. 
        
        """
        file_path = pathlib.Path(file_path)
        module_spec = importlib.util.spec_from_file_location(file_path)
        module = importlib.util.module_from_spec(module_spec)
        return module_spec.loader.exec_module(module)
    
    def _get_subclasses(self, 
            module: object) -> Sequence['sourdough.Component']:
        """Returns a list of Component subclasses.
        
        Args:
            module (object): an import python module.
        
        Returns:
            Sequence[Component]: list of subclasses of Component. If none are 
                found, an empty list is returned.
                
        """
        matches = []
        for item in pyclbr.readmodule(module):
            # Adds direct subclasses.
            if inspect.issubclass(item, sourdough.Component):
                matches.append[item]
            else:
                # Adds subclasses of other subclasses.
                for subclass in self.contents.values():
                    if subclass(item, subclass):
                        matches.append[item]
        return matches

    # @classmethod
    # def create(cls,
    #         component: Union[str, 'Component'],
    #         **kwargs) -> 'Component':
    #     """Returns a Component subclass for 'component'.

    #     Args:
    #         component (Union[str, Component]): either a key in 'catalog' or a
    #             Component subclass. If a Component subclass is passed, it is
    #             automatically added to 'catalog' and instanced.
    #         kwArgs: arguments to be passed to instanced Component subclass.

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

    #     Args:
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
      
@dataclasses.dataclass
class RegistryMixin(abc.ABC):
    """Mixin which creates a proxy name for a Component subclass attribute.

    """
    registry: ClassVar['sourdough.Registry'] = sourdough.Registry()
    
    """ Initialization Methods """
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Adds new subclass to 'registry'.
        cls.registry.add(cls)   
        
    """ Class Methods """
              
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
            base.catalog = sourdough.core.registry.Codex(base = base) 
        return cls    
        
    @classmethod
    def _register_in_catalog(cls, component: 'Component', name: str) -> None:
        """Adds 'component' class to 'catalog'.

        Args:
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
        
    """ Public Methods """


@dataclasses.dataclass
class ProxyMixin(abc.ABC):
    """Mixin which creates a proxy name for a Component subclass attribute.
    The 'proxify' method dynamically creates a property to access the stored
    attribute. This allows class instances to customize names of stored
    attributes while still maintaining the interface of the base sourdough
    classes.
    Only one proxy should be created per class. Otherwise, the created proxy
    properties will all point to the same attribute.
    """

    """ Public Methods """

    def proxify(self,
            proxy: str,
            attribute: str,
            default_value: Optional[Any] = None,
            proxify_methods: Optional[bool] = True) -> None:
        """Adds a proxy property to refer to class attribute.

        Args:
            proxy (str): name of proxy property to create.
            attribute (str): name of attribute to link the proxy property to.
            default_value (Optional[Any]): default value to use when deleting
                'attribute' with '__delitem__'. Defaults to None.
            proxify_methods (Optiona[bool]): whether to create proxy methods
                replacing 'attribute' in the original method name with the
                string passed in 'proxy'. So, for example, 'add_chapter' would
                become 'add_recipe' if 'proxy' was 'recipe' and 'attribute' was
                'chapter'. The original method remains as well as the proxy.
                This does not change the rest of the signature of the method so
                parameter names remain the same. Defaults to True.

        """
        self._proxied_attribute = attribute
        self._default_proxy_value = default_value
        self._proxify_attribute(proxy = proxy)
        if proxify_methods:
            self._proxify_methods(proxy = proxy)
        return self

    """ Proxy Property Methods """

    def _proxy_getter(self) -> Any:
        """Proxy getter for '_proxied_attribute'.

        Returns:
            Any: value stored at '_proxied_attribute'.

        """
        return getattr(self, self._proxied_attribute)

    def _proxy_setter(self, value: Any) -> None:
        """Proxy setter for '_proxied_attribute'.

        Args:
            value (Any): value to set attribute to.

        """
        setattr(self, self._proxied_attribute, value)
        return self

    def _proxy_deleter(self) -> None:
        """Proxy deleter for '_proxied_attribute'."""
        setattr(self, self._proxied_attribute, self._default_proxy_value)
        return self

    """ Other Private Methods """

    def _proxify_attribute(self, proxy: str) -> None:
        """Creates proxy property for '_proxied_attribute'.

        Args:
            proxy (str): name of proxy property to create.

        """
        setattr(self, proxy, property(
            fget = self._proxy_getter,
            fset = self._proxy_setter,
            fdel = self._proxy_deleter))
        return self

    def _proxify_methods(self, proxy: str) -> None:
        """Creates proxy method with an alternate name.

        Args:
            proxy (str): name of proxy to repalce in method names.

        """
        for item in dir(self):
            if (self._proxied_attribute in item
                    and not item.startswith('__')
                    and callable(item)):
                self.__dict__[item.replace(self._proxied_attribute, proxy)] = (
                    getattr(self, item))
        return self

