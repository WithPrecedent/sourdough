"""
.. module:: base
:synopsis: sourdough abstract base classes and mixins
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
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union

import sourdough


@dataclasses.dataclass
class Component(abc.ABC):
    """Base class for core sourdough objects.

    A Component has a 'name' attribute for internal referencing and to allow 
    sourdough iterables to function propertly. Component instances can be used 
    to create a variety of composite data structures such as trees and graphs. 

    The mixins included with sourdough are all compatible, individually and
    collectively, with Component.

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Component is called, 'name' is set based upon
            the 'get_name' method in Component. If that method is not 
            overridden by a subclass instance, 'name' will be assigned to the 
            snake case version of the class name ('__class__.__name__').
    
    """
    name: str = None

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Sets 'name' to the default value if it is not passed.
        self.name: str = self.name or self.get_name()

    """ Class Methods """

    @classmethod
    def get_name(cls) -> str:
        """Returns 'name' of class for use throughout sourdough.
        
        The method is a classmethod so that a 'name' can properly derived even
        before a class is instanced. It can also be called after a subclass is
        instanced (as is the case in '__post_init__').
        
        This method converts the class name from CapitalCase to snake_case.
        
        If a user wishes to use an alternate naming system, a subclass should
        simply override this method. 
        
        Returns:
            str: name of class for internal referencing and some access methods.
        
        """
        try:
            return cls.name
        except AttributeError:
            if inspect.isclass(cls):
                return sourdough.tools.snakify(cls.__name__)
            else:
                return sourdough.tools.snakify(cls.__class__.__name__)


@dataclasses.dataclass
class Task(Component, abc.ABC):
    """Base class for applying stored methods to passed data.
    
    Task subclass instances are often arranged in an ordered sequence such as a
    Progression instance. All Task subclasses must have 'apply' methods for 
    handling data. 
    
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Component is called, 'name' is set based upon
            the 'get_name' method in Component. If that method is not 
            overridden by a subclass instance, 'name' will be assigned to the 
            snake case version of the class name ('__class__.__name__').
    
    """
    name: str = None
    
    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def apply(self, data: object = None, **kwargs) -> object:
        """Subclasses must provide their own methods."""
        pass

 
@dataclasses.dataclass
class Creator(Component, abc.ABC):
    """Base class for stages of creation of sourdough objects.
    
    All subclasses must have 'create' methods. 
    
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Component is called, 'name' is set based upon
            the 'get_name' method in Component. If that method is not 
            overridden by a subclass instance, 'name' will be assigned to the 
            snake case version of the class name ('__class__.__name__').
    
    """
    name: str = None
    
    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def create(self, component: 'Component' = None, **kwargs) -> 'Component':
        """Constructs or modifies a Component instance.
        
        Subclasses must provide their own methods.
        
        """
        pass
    

@dataclasses.dataclass
class Anthology(abc.ABC):
    """Base class for sourdough iterables,
    
    All Anthology subclasses must include 'validate' and 'add' methods. 
    Requirements for those methods are described in the respective 
    abstractmethods.
    
    Args:
        contents (Iterable): stored iterable. Defaults to None.
              
    """
    contents: Iterable = None 

    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Validates 'contents' or converts it to appropriate iterable.
        self.contents = self.validate(contents = self.contents)
        
    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def validate(self, contents: Any, **kwargs) -> Iterable:
        """Validates 'contents' or converts 'contents' to proper type.
        
        Subclasses must provide their own methods.
        
        The 'contents' argument should accept any supported datatype and either
        validate its type or convert it to an iterable. This method is used to 
        validate or convert both the passed 'contents' and by the 'add' method
        to add new keys and values to the 'contents' attribute.
        
        """
        pass
    
    @abc.abstractmethod
    def add(self, contents: Any, **kwargs) -> None:
        """Adds 'contents' to the 'contents' attribute.
        
        Subclasses must provide their own methods.
        
        This method should first call 'validate' to convert or 'validate' the
        passed argument. It should then use the appropraite default mechanism
        for adding 'contents' argument to the 'contents' attribute.
        
        """
        contents = self.validate(contents = contents)
        # Subclasses should add code for incorporating 'contents' argument here.
        return self  
    
    """ Dunder Methods """
    
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

    def __add__(self, other: Any) -> None:
        """Combines argument with 'contents'.

        Args:
            other (Any): item to add to 'contents' using the 'add' method.

        """
        self.add(other)
        return self

    def __repr__(self) -> str:
        """Returns '__str__' representation.

        Returns:
            str: default string representation of an instance.

        """
        return self.__str__()
    
    def __str__(self) -> str:
        """Returns default string representation of an instance.

        Returns:
            str: default string representation of an instance.

        """
        return (
            f'sourdough {self.__class__.__name__}\n'
            f'contents: {self.contents.__str__()}')     
    
    
@dataclasses.dataclass
class LibraryMixin(abc.ABC):
    """Mixin which stores subclass instances in a 'library' class attribute.

    In order to ensure that a subclass instance is added to the base Corpus 
    instance, super().__post_init__() should be called by that subclass.

    Args:
        library (ClassVar[sourdough.Corpus]): the instance which stores 
            subclass in a Corpus instance.
            
    Mixin Namespaces: 'library', 'borrow'

    """
    library: ClassVar['sourdough.Corpus'] = sourdough.Corpus()

    """ Initialization Methods """
    
    def __post_init__(self):
        """Registers an instance with 'library'."""
        super().__post_init__()
        # Adds instance to the 'library' class variable.
        self.library[self.name] = self
        
    """ Public Methods """
    
    def borrow(self, key: Union[str, Sequence[str]]) -> object:
        """Returns a value stored in 'library'.

        Args:
            key (Union[str, Sequence[str]]): key(s) to values in 'library' to
                return.

        Returns:
            Any: value(s) stored in library.
            
        """
        return self.library[key]
  
      
@dataclasses.dataclass
class RegistryMixin(abc.ABC):
    """Mixin which stores subclasses in a 'registry' class attribute.

    Args:
        register_from_disk (bool): whether to look in the current working
            folder and subfolders for subclasses of the Component class for 
            which this class is a mixin. Defaults to False.
        registry (ClassVar[sourdough.Corpus]): the instance which stores 
            subclass in a Corpus instance.

    Mixin Namespaces: 'registry', 'register_from_disk', 'build', 
        'find_subclasses', '_import_from_path', '_get_subclasse'
        
    To Do:
        Fix 'find_subclasses' and related classes. Currently, 
            importlib.util.module_from_spec returns None.
    
    """
    register_from_disk: bool = False
    registry: ClassVar['sourdough.Corpus'] = sourdough.Corpus()
    
    """ Initialization Methods """
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Adds new subclass to 'registry'.
        if not hasattr(super(), 'registry'):
            cls.registry[cls.get_name()] = cls

    # def __post_init__(self) -> None:
    #     """Initializes class instance attributes."""
    #     super().__post_init__()
    #     # Adds subclasses from disk to 'registry' if 'register_from_disk'.
    #     if self.register_from_disk:
    #         self.find_subclasses(folder = pathlib.Path.cwd())
                
    """ Public Methods """
    
    def build(self, key: Union[str, Sequence[str]], **kwargs) -> Any:
        """Creates instance(s) of a class(es) stored in 'registry'.

        Args:
            key (str): name matching a key in 'registry' for which the value
                is sought.

        Raises:
            TypeError: if 'key' is neither a str nor Sequence type.
            
        Returns:
            Any: instance(s) of a stored class(es) with kwargs passed as 
                arguments.
            
        """
        if isinstance(key, str):
            return self.registry.create(key = key, **kwargs)
        elif isinstance(key, Sequence):
            instances = []
            for item in key:
                instances.append(self.registry.create(name = item, **kwargs))
            return instances
        else:
            raise TypeError('key must be a str or list type')

    # def find_subclasses(self, 
    #         folder: Union[str, pathlib.Path], 
    #         recursive: bool = True) -> None:
    #     """Adds Component subclasses for python files in 'folder'.
        
    #     If 'recursive' is True, subfolders are searched as well.
        
    #     Args:
    #         folder (Union[str, pathlib.Path]): folder to initiate search for 
    #             Component subclasses.
    #         recursive (bool]): whether to also search subfolders (True)
    #             or not (False). Defaults to True.
                
    #     """
    #     if recursive:
    #         glob_method = 'rglob'
    #     else:
    #         glob_method = 'glob'
    #     for file_path in getattr(pathlib.Path(folder), glob_method)('*.py'):
    #         if not file_path.name.startswith('__'):
    #             module = self._import_from_path(file_path = file_path)
    #             subclasses = self._get_subclasses(module = module)
    #             for subclass in subclasses:
    #                 self.add({
    #                     sourdough.tools.snakify(subclass.__name__): subclass})    
    #     return self
       
    # """ Private Methods """
    
    # def _import_from_path(self, file_path: Union[pathlib.Path, str]) -> object:
    #     """Returns an imported module from a file path.
        
    #     Args:
    #         file_path (Union[pathlib.Path, str]): path of a python module.
        
    #     Returns:
    #         object: an imported python module. 
        
    #     """
    #     # file_path = str(file_path)
    #     # file_path = pathlib.Path(file_path)
    #     print('test file path', file_path)
    #     module_spec = importlib.util.spec_from_file_location(file_path)
    #     print('test module_spec', module_spec)
    #     module = importlib.util.module_from_spec(module_spec)
    #     return module_spec.loader.exec_module(module)
    
    # def _get_subclasses(self, 
    #         module: object) -> Sequence['sourdough.Component']:
    #     """Returns a list of subclasses in 'module'.
        
    #     Args:
    #         module (object): an import python module.
        
    #     Returns:
    #         Sequence[Component]: list of subclasses of Component. If none are 
    #             found, an empty list is returned.
                
    #     """
    #     matches = []
    #     for item in pyclbr.readmodule(module):
    #         # Adds direct subclasses.
    #         if inspect.issubclass(item, sourdough.Component):
    #             matches.append[item]
    #         else:
    #             # Adds subclasses of other subclasses.
    #             for subclass in self.contents.values():
    #                 if subclass(item, subclass):
    #                     matches.append[item]
    #     return matches


@dataclasses.dataclass
class OptionsMixin(abc.ABC):
    """Mixin which stores classes or instances in 'options'.

    Args:
        options (ClassVar[sourdough.Corpus]): the instance which stores 
            subclass in a Corpus instance.
            
    Mixin Namespaces: 'options', 'select'

    """
    options: ClassVar['sourdough.Corpus'] = sourdough.Corpus(
        always_return_list = True)
    
    """ Public Methods """
        
    def select(self, key: Union[str, Sequence[str]], **kwargs) -> Any:
        """Creates instance(s) of a class(es) stored in 'options'.

        Args:
            option (str): name matching a key in 'options' for which the value
                is sought.

        Raises:
            TypeError: if 'option' is neither a str nor Sequence type.
            
        Returns:
            Any: instance of a stored class with kwargs passed as arguments.
            
        """
        if isinstance(key, str):
            try:
                return self.options[key](**kwargs)
            except TypeError:
                return self.options[key]
        elif isinstance(key, Sequence):
            instances = []
            for k in key:
                try:
                    instance = self.options[key](**kwargs)
                except TypeError:
                    instance = self.options[key]
                instances.append(instance)
            return instances
        else:
            raise TypeError('option must be a str or list type')
     
    
@dataclasses.dataclass
class ProxyMixin(abc.ABC):
    """Mixin which creates a proxy name for a Component subclass attribute.

    The 'proxify' method dynamically creates a property to access the stored
    attribute. This allows class instances to customize names of stored
    attributes while still maintaining the interface of the base sourdough
    classes.

    Only one proxy should be created per class. Otherwise, the created proxy
    properties will all point to the same attribute.

    Mixin Namespaces: 'proxify', '_proxy_getter', '_proxy_setter', 
        '_proxy_deleter', '_proxify_attribute', '_proxify_method', the name of
        the proxy property set by the user with the 'proxify' method.
       
    To Do:
        Add property to class instead of instance to prevent return of property
            object.
        Implement '__set_name__' in a secondary class to simplify the code and
            namespace usage.
        
    """

    """ Public Methods """

    def proxify(self,
            proxy: str,
            attribute: str,
            default_value: Any = None,
            proxify_methods: bool = True) -> None:
        """Adds a proxy property to refer to class attribute.

        Args:
            proxy (str): name of proxy property to create.
            attribute (str): name of attribute to link the proxy property to.
            default_value (Any): default value to use when deleting 'attribute' 
                with '__delitem__'. Defaults to None.
            proxify_methods (bool): whether to create proxy methods replacing 
                'attribute' in the original method name with the string passed 
                in 'proxy'. So, for example, 'add_chapter' would become 
                'add_recipe' if 'proxy' was 'recipe' and 'attribute' was
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
   