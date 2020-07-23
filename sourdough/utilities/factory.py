"""
.. module:: creators
:synopsis: sourdough factory and lazy loader
:author: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import abc
import dataclasses
import textwrap
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union

import sourdough


@dataclasses.dataclass
class Factory(abc.ABC):
    """The Factory interface instances a class from available options.

    Args:
        product (Union[str, Sequence[str]]): name(s) of sourdough object(s) to 
            return. 'product' must correspond to a key(s) in 'options'. 
            Defaults to None.
        default (ClassVar[Union[str, Sequence[str]]]): the name(s) of the 
            default object(s) to instance. If 'product' is not passed, 'default' 
            is used. 'default' must correspond to key(s) in 'options'. Defaults 
            to None.
        options (ClassVar[sourdough.Catalog]): a dictionary of available options 
            for object creation. Keys are the names of the 'product'. Values are 
            the objects to create. Defaults to an empty dictionary.

    Returns:
        Any: the factory uses the '__new__' method to return a different object 
            instance with kwargs as the parameters.

    """
    product: Union[str, Sequence[str]] = None
    default: ClassVar[Union[str, Sequence[str]]] = None
    options: ClassVar['sourdough.Catalog'] = sourdough.Catalog(
        always_return_list = True)

    """ Initialization Methods """
    
    def __new__(cls, product: str = None, **kwargs) -> Any:
        """Returns an instance from 'options'.

        Args:
            product (str): name of sourdough object(s) to return. 
                'product' must correspond to key(s) in 'options'. Defaults to 
                None. If not passed, the product listed in 'default' will be 
                used.
            kwargs (MutableMapping[str, Any]): parameters to pass to the object 
                being created.

        Returns:
            Any: an instance of an object stored in 'options'.
        
        """
        if not product:
            product = cls.default
        if isinstance(product, str):
            return cls.options[product](**kwargs)
        else:
            instances = []
            for match in cls.options[product]:
                instances.append(match(**kwargs))
            return instances
    
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
        return textwrap.dedent(f'''
            sourdough {self.__class__.__name__}
            product: {self.product}
            default: {self.default}
            options: {str(self.options)}''') 
        