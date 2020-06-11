"""
.. module:: components
:synopsis: sourdough core objects
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
from typing import Any, ClassVar, Iterable, Mapping, Sequence, Tuple, Union

import sourdough


@dataclasses.dataclass
class Component(abc.ABC):
    """Base class for components in sourdough.

    Args:
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

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Sets 'name' to the default value if it is not passed.
        self.name = self.name or self._get_name(component = self)


@dataclasses.dataclass
class Operator(Component):
    """Base class for workflow steps controlled by a Manager instance.
    
    All subclasses must have 'apply' methods. 
    
    Args:
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. For example if a 
            class instance needs settings from the shared Settings instance, 
            'name' should match the appropriate section name in that Settings 
            instance. When subclassing, it is sometimes a good idea to use the 
            same 'name' attribute as the base class for effective coordination 
            between sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Component is called, 'name' is set to a snake 
            case version of the class name ('__class__.__name__').
    
    """
    name: Optional[str] = None
    
    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def apply(self, *args, **kwargs) -> None:
        """Subclasses must provide their own methods."""
        pass


@dataclasses.dataclass
class Factory(abc.ABC):
    """The Factory interface instances a class from available options.

    Args:
        product (Optional[str]): name of sourdough object to return. 'product' 
            must correspond to a key in 'options'. Defaults to None.
        default (ClassVar[str]): the name of the default object to instance. If 
            'product' is not passed, 'default' is used. 'default' must 
            correspond  to a key in 'options'. Defaults to None. If 'default'
            is to be used, it should be specified by a subclass, declared in an
            instance, or set via the class attribute.
        options (ClassVar[Mapping]): a dictionary or other mapping of 
            available options for object creation. Keys are the names of the 
            'product'. Values are the objects to create. Defaults to an 
            empty dictionary.

    Returns:
        Any: the factory uses the '__new__' method to return a different object 
            instance with kwargs as the parameters.

    """
    product: Optional[str] = None
    default: ClassVar[str] = None
    options: ClassVar['sourdogh.Catalog'] = sourdough.Catalog(
        always_return_list = True)

    """ Initialization Methods """
    
    def __new__(cls, 
            product: Optional[str] = None, 
            **kwargs) -> Any:
        """Returns an instance from 'options'.

        Args:
            product (Optional[str]): name of sourdough object to return. 
                'product' must correspond to a key in 'options'. Defaults to 
                None. If not passed, the product listed in 'default' will be 
                used.
            kwargs (MutableMapping[str, Any]): parameters to pass to the object being 
                created.

        Returns:
            Any: an instance of an object stored in 'options'.
        
        """
        if product:
            return cls.options[product](**kwargs) 
        else:
            return cls.options[cls.default](**kwargs)
    
    """ Class Methods """
    
    @classmethod
    def add(cls, key: str, option: 'sourdough.Component') -> None:
        """Adds 'option' to 'options' at 'key'.
        
        Args:
            key (str): name of key to link to 'option'.
            option (sourdough.Component): object to store in 'options'.
            
        """
        cls.options[key] = option
        return cls
        
    """ Dunder Methods """
    
    def __repr__(self) -> str:
        """Returns '__str__' representation.

        Returns:
            str: default representation of a class instance.

        """
        return self.__str__()

    def __str__(self) -> str:
        """Returns default representation of a class instance.

        Returns:
            str: default representation of a class instance.

        """
        return (
            f'sourdough {self.__class__.__name__} '
            f'product: {self.product} '
            f'default: {self.default} '
            f'options: {str(self.options)}') 
        

@dataclasses.dataclass
class LazyLoader(abc.ABC):
    """Base class for lazy loading of python modules and objects.

    Args:
        module (Optional[str]): name of module where object to use is located
            (can either be a sourdough or non-sourdough module). Defaults to
            'sourdough'.
        default_module (Optional[str]): a backup name of module where object to
            use is located (can either be a sourdough or non-sourdough module).
            Defaults to 'sourdough'.

    """
    module: Optional[str] = dataclasses.field(
        default_factory = lambda: 'sourdough')
    default_module: Optional[str] = dataclasses.field(
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