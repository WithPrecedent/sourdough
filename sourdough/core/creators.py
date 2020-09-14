"""
creators: sourdough abstract base classes for object creation
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Factory: abstract base class for sourdough factories.

"""
from __future__ import annotations
import abc
import dataclasses
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union


@dataclasses.dataclass
class Factory(abc.ABC):
    """Instances a class from available Callables stored in 'options'.

    Args:
        products (Union[str, Sequence[str]]: name(s) of objects to return. 
            'products' must correspond to key(s) in 'options'.
        options (Mapping[str, Callable]): a dict of available options for object 
            creation. Defaults to an empty dict.

    Raises:
        TypeError: if 'products' is neither a str nor Sequence of str.

    Returns:
        Any: the factory uses the '__new__' method to return a different object 
            product instance with kwargs as the parameters.

    """
    products: Union[str, Sequence[str]]
    options: ClassVar[Mapping[str, Any]] = {}

    """ Initialization Methods """
    
    def __new__(cls, products: str, **kwargs) -> Any:
        """Returns an instance from 'options'.

        Args:
            products (str): name of sourdough products(s) to return. 'products' 
                must correspond to key(s) in 'options'.
            kwargs: parameters to pass to the object being created.

        Returns:
            Any: an instance of a Callable stored in 'options'.
        
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
    def add(cls, key: str, value: Any) -> None:
        """Adds 'option' to 'options' at 'key'.
        
        Args:
            key (str): name of key to link to 'value'.
            value (Any): object to store in 'options'.
            
        """
        cls.options[key] = value
        return cls
    