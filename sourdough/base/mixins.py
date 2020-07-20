"""
mixins: sourdough mixins
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    LibraryMixin: mixin for automatically storing subclass instances in a
        'library' class attribute.
    RegistryMixin: mixin for automatically storing subclasses in a 'registry'
        class attribute.
    OptionsMixin: mixin for storing strategies or options in an 'options'
        class attribute.
    ProxyMixin: mixin which creates a python property which refers to another
        attribute by using the 'proxify' method.
    LoaderMixin: lazy loader mixin which uses a 'load' method to look for str
        names of objects stored in attributes in the 'module' and 
        'default_module' attributes.

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
class LibraryMixin(abc.ABC):
    """Mixin which stores subclass instances in a 'library' class attribute.

    In order to ensure that a subclass instance is added to the base Catalog 
    instance, super().__post_init__() should be called by that subclass.

    Args:
        library (ClassVar[sourdough.Catalog]): dictionary which stores 
            subclass instances.
            
    Namespaces: 'library', 'borrow'.

    """
    library: ClassVar['sourdough.Catalog'] = sourdough.Catalog()

    """ Initialization Methods """
    
    def __post_init__(self):
        """Registers an instance with 'library'."""
        # Calls initialization method of other inherited classes.
        try:
            super().__post_init__()
        except AttributeError:
            pass
        # Adds this instance to the 'library' class variable.
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
        registry (ClassVar[sourdough.Catalog]): the instance which stores 
            subclass in a Catalog instance.

    Namespaces: 'registry', 'register_from_disk', 'build', 
        'find_subclasses', '_import_from_path', '_get_subclasse'
        
    To Do:
        Fix 'find_subclasses' and related classes. Currently, 
            importlib.util.module_from_spec returns None.
    
    """
    # register_from_disk: bool = False
    registry: ClassVar['sourdough.Catalog'] = sourdough.Catalog()
    
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
    #                     sourdough.utilities.snakify(subclass.__name__): subclass})    
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
        options (ClassVar[sourdough.Catalog]): the instance which stores 
            subclass in a Catalog instance.
            
    Namespaces: 'options', 'select'

    """
    options: ClassVar['sourdough.Catalog'] = sourdough.Catalog(
        always_return_list = True)
    
    """ Public Methods """
        
    def select(self, key: Union[str, Sequence[str]], **kwargs) -> Union[
            object, Sequence[object]]:
        """Creates instance(s) of a class(es) stored in 'options'.

        Args:
            key (str): name matching a key in 'options' for which the value
                is sought.

        Raises:
            TypeError: if 'option' is neither a str nor Sequence type.
            
        Returns:
            Union[object, Sequence[object]]: instance(s) of a stored value(s).
            
        """
        def _select_item(single_key: str) -> object:
            """Nested function to return a single value in 'options'.
        
            A nested function is used to avoid cluttering the namespace of a
            an object using the OptionsMixin.
            
            Args:
                single_key (str): name of key for value to be returned.
                
            Returns:
                object: instance of a stored value.
            
            """
            try:
                return self.options[key](**kwargs)
            except TypeError:
                return self.options[key]
            
        if isinstance(key, str):
            return _select_item(single_key = key)
        elif isinstance(key, Sequence):
            instances = []
            for k in key:
                instances.append(_select_item(single_key = k))
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

    Namespaces: 'proxify', '_proxy_getter', '_proxy_setter', 
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


@dataclasses.dataclass
class LoaderMixin(abc.ABC):
    """Mixin for lazy loading of python modules and objects.

    Args:
        module (str): name of module where object to use is located (can either 
            be a sourdough or non-sourdough module). Defaults to 'sourdough'.
        default_module (str): a backup name of module where object to use is 
            located (can either be a sourdough or non-sourdough module).
            Defaults to 'sourdough'.

    Namespaces: 'module', 'default_module', 'load'

    """
    module: str = dataclasses.field(default_factory = lambda: 'sourdough')
    default_module: str = dataclasses.field(
        default_factory = lambda: 'sourdough')

    """ Public Methods """

    def load(self, attribute: str) -> object:
        """Returns object named in 'attribute'.

        If 'attribute' is not a str, it is assumed to have already been loaded
        and is returned as is.

        The method searches both 'module' and 'default_module' for the named
        'attribute'. It also checks to see if the 'attribute' is directly
        loadable from the module or if it is the name of a local attribute that
        has a value of a loadable object in the module.

        Args:
            attribute (str): name of attribute to load from 'module' or
                'default_module'.

        Returns:
            object: from 'module' or 'default_module'.

        """
        # If 'attribute' is a string, attempts to load from 'module' or, if not
        # found there, 'default_module'.
        if isinstance(getattr(self, attribute), str):
            try:
                return getattr(importlib.import_module(self.module), attribute)
            except (ImportError, AttributeError):
                try:
                    return getattr(
                        importlib.import_module(self.module),
                        getattr(self, attribute))
                except (ImportError, AttributeError):
                    try:
                        return getattr(
                            importlib.import_module(self.module), attribute)
                    except (ImportError, AttributeError):
                        try:
                            return getattr(
                                importlib.import_module(self.default_module),
                                getattr(self, attribute))
                        except (ImportError, AttributeError):
                            raise ImportError(
                                f'{attribute} is neither in \
                                {self.module} nor {self.default_module}')
        # If 'attribute' is not a string, it is returned as is.
        else:
            return getattr(self, attribute)
