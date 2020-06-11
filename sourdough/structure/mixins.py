
"""
.. module:: mixins
:synopsis: sourdough mixins
:author: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

"""
sourdough mixins are designed to be compatiable, individually and collectively,
with Component subclasses. Using them with other classes is not guaranteed to
work.

"""

import abc
import dataclasses
from typing import Any, ClassVar, Iterable, Mapping, Sequence, Tuple, Union

import sourdough
 

@dataclasses.dataclass
class LibraryMixin(abc.ABC):
    """Mixin which stores subclass instances in a 'library' class attribute.

    In order to ensure that a subclass instance is added to the base Library 
    instance, super().__post_init__() should be called by that subclass.

    Args:
        library (ClassVar[sourdough.Library]): the instance which stores 
            subclass in a Library instance.

    """
    library: ClassVar['sourdough.Library'] = sourdough.Library()
    
    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Adds this class instance to the base library of instances if the 
        # current instance is not the base class.
        if self.library.base != self.__class__:
            self.library.base.add(component = self)

      
@dataclasses.dataclass
class RegistryMixin(abc.ABC):
    """Mixin which stores subclasses in a 'registry' class attribute.

    Args:
        registry (ClassVar[sourdough.Registry]): the instance which stores 
            subclass in a Registry instance.

    """
    registry: ClassVar['sourdough.Registry'] = sourdough.Registry()
    
    """ Initialization Methods """
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Adds new subclass to 'registry'.
        cls.registry.add(cls)   
        
    # """ Class Methods """
              
    # @classmethod
    # def _initialize_catalog(cls) -> None:
    #     if inspect.isclass(cls):
    #         base = cls
    #     elif cls.__class__ == abc.ABC:
    #         print('yeah it found abc')
    #         base = Component
    #     else:
    #         base = cls.__class__
    #     if base == Component or cls.catalog is True:
    #         'yeah it found base'
    #         base.catalog = sourdough.core.registry.Codex(base = base) 
    #     return cls    
        
    # @classmethod
    # def _register_in_catalog(cls, component: 'sourdough.Component', name: str) -> None:
    #     """Adds 'sourdough.Component' class to 'catalog'.

    #     Args:
    #         component (Component): subclass of Component to add to 'catalog'.
    #         name (str): key name to use in 'catalog'.

    #     """          
    #     base = cls._get_catalog_base()
    #     if isinstance(component, base):
    #         component = component.__class__
    #     base.catalog[name] = component
    #     return cls

    # @classmethod
    # def _get_catalog_base(cls) -> 'sourdough.Component':
    #     """Returns subclass or Component to be base for 'catalog'.
        
    #     Returns:
    #         Component: this class will serve as the base for 'catalog'.
        
    #     """
    #     try:
    #         return cls._catalog_base
    #     except AttributeError:
    #         return Component


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
