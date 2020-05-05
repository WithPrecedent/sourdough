"""
.. module:: component
:synopsis: project structure made simple
:author: Corey Rayburn Yung
:copyright: 2019-2020
:license: Apache-2.0
"""

import abc
import dataclasses
import pathlib
import re
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Optional,
                    Tuple, Union)

import sourdough

@dataclasses.dataclass
class Component(abc.ABC):
    """Base class for components in sourdough.

    Component and its subclasses store subclasses in 'library'. 'library' is a
    dictionary with string keys and Component values. Users can call the
    'create' classmethod to create subclass instances directly from Component.

    Whenever a Component subclass is instanced, it is automatically created to
    the 'library' if super().__post_init() is called.

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

    Args:
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. If the class instance
            needs settings from the shared Settings instance, 'name' should
            match the appropriate section name in that Settings instance. When
            subclassing, it is sometimes a good idea to use the same 'name'
            attribute as the base class for effective coordination between
            sourdough classes. Defaults to None. If None and '__post_init__' of
            Component is called, it is set to a snake case version of the class
            name.

    """
    name: Optional[str] = None
    library: ClassVar[Dict[str, 'Component']] = {}

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Sets 'name' to default value if it is not passed.
        self.name = self.name or sourdough.utilities.snakify(
            self.__class__.__name__)
        # Adds class to 'library', if it is not already there.
        if self.name not in Component.library:
            Component.register(component = self.__class__, name = self.name)
        return self

    """ Class Methods """

    @classmethod
    def create(cls,
            component: Union[str, 'Component'],
            **kwargs) -> 'Component':
        """Returns a Component subclass for 'component'.

        Args:
            component (Union[str, Component]): either a key in 'library' or a
                Component subclass. If a Component subclass is passed, it is
                automatically added to 'library' and instanced.
            kwargs: arguments to be passed to instanced Component subclass.

        Raises:
            ValueError: if 'component' is a string but does not exist in
                'library'.
            TypeError: if 'component' is neither a string nor Component.

        Returns:
            Component: instanced subclass with kwargs as initialization
                parameters.

        """
        if isinstance(component, cls):
            cls.register(component = component)
            return component(**kwargs)
        elif isinstance(component, str):
            if component in cls.library:
                return cls.library[component](**kwargs)
            else:
                raise ValueError(
                    f'{component} is not a recognized {cls.__name__} type')
        else:
            raise TypeError(f'component must be a str or {cls.__name__} type')

    @classmethod
    def register(cls,
            component: 'Component',
            name: Optional[str] = None) -> None:
        """Adds 'component' to 'library'.

        If 'name' is passed, that is the key used in 'library'.

        If not and 'component' is an instance, the 'name' attribute of that
        instance is used. If 'component' has not been instanced, two keys
        are created: 1) the string name of the subclass; and 2) the snake case
        of the class name (lower case and underscored appropriately).

        'register' can be overwritten by subclasses to store the 'library' in
        Component subclasses by simply replacing 'Component' in the method code
        with the class where the 'library' should be stored.

        Args:
            component (Component): subclass of Component to add to 'library'.
            name (Optional[str]): optional key name to use in 'library'.

        """
        if name is None:
            if component.name is not None:
                name = component.name
            else:
                name = component.__name__
                snake_name = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
                Component.library[snake_name] = component
        if isinstance(component, Component):
            component = component.__class__
        Component.library[name] = component
        return cls


@dataclasses.dataclass
class Proxy(abc.ABC):
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