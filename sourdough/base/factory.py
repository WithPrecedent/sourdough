"""
factory: sourdough abstract base factory class
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:


"""
from __future__ import annotations
import abc
import dataclasses
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union

import sourdough


@dataclasses.dataclass
class Factory(abc.ABC):
    """The Factory interface instances a class from available options.

    Args:
        products (Union[str, Sequence[str]]: name of sourdough products to 
            return. 'products' must correspond to key(s) in 'options'. Defaults 
            to None.
        options (ClassVar[sourdough.base.Catalog]): a dict of available options 
            for object creation. Defaults to an empty Catalog instance.

    Raises:
        TypeError: if 'products' is neither a str nor Sequence of str.

    Returns:
        Any: the factory uses the '__new__' method to return a different object 
            product instance with kwargs as the parameters.

    """
    products: Union[str, Sequence[str]] = None
    options: ClassVar[sourdough.base.Catalog] = sourdough.base.Catalog()

    """ Initialization Methods """
    
    def __new__(cls, products: str = None, **kwargs) -> Any:
        """Returns an instance from 'options'.

        Args:
            products (str): name of sourdough products(s) to return. 
                'products' must correspond to key(s) in 'options'. Defaults to 
                None.
            kwargs (MutableMapping[Any, Any]): parameters to pass to the object 
                being created.

        Returns:
            Any: an instance of an object stored in 'options'.
        
        """
        if isinstance(products, str):
            return cls.options[products](**kwargs)
        elif isinstance(products, Sequence):
            instances = []
            for match in cls.options[products]:
                instances.append(match(**kwargs))
            return instances
        else:
            raise TypeError('products must be a str or list type')
    
    """ Class Methods """
    
    @classmethod
    def add(cls, key: str, option: Any) -> None:
        """Adds 'option' to 'options' at 'key'.
        
        Args:
            key (str): name of key to link to 'option'.
            option (Any): object to store in 'options'.
            
        """
        cls.options[key] = option
        return cls
    