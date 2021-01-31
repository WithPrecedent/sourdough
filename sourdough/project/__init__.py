"""
project: applying the sourdough core to create and implement projects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:

"""
import dataclasses
import importlib
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Set, Tuple, Type, Union)

import sourdough


importables = {
    'Settings': 'base.Settings',
    'Filer': 'base.Filer',
    'Workflow': 'base.Workflow',
    'Component': 'base.Component',
    'Manager': 'workbench.Manager',
    'Creator': 'workbench.Creator',
    'interface': 'interface',
    'structure': 'structure',
    'base': 'base',
    'workbench': 'workbench'}


def __getattr__(name: str) -> Any:
    """Lazily imports modules and items within them.

    This code is adapted from PEP 562: https://www.python.org/dev/peps/pep-0562/

    Args:
        name (str): name of sourdough item.

    Raises:
        AttributeError: if there is no module matching 'name'.

    Returns:
        Any: a module or item stored within a module.
        
    """
    if name in importables:
        key = '.' + importables[name]
        try:
            return importlib.import_module(key, package = __name__)
        except ModuleNotFoundError:
            item = key.split('.')[-1]
            module_name = key[:-len(item) - 1]
            module = importlib.import_module(module_name, package = __name__)
            return getattr(module, item)
    raise AttributeError(f'module {__name__} has no attribute {name}')


@dataclasses.dataclass
class Bases(sourdough.quirks.Loader):
    """Base classes for a sourdough projects.
    
    Changing the attributes on a Bases instance allows users to specify 
    different base classes for a sourdough project in the necessary categories.
    Project will automatically use the base classes in the Bases instance 
    passed to it.
    
    Since this is a subclass of Loader, attribute values can either be classes
    or strings of the import path of classes. In the latter case, the base
    classes will be lazily loaded when called.
    
    Args:
        settings (Union[str, Type]): configuration class or a str of the import
            path for the configuration class. 
        filer (Union[str, Type]): file management class or a str of the import
            path for the file management class. 
        component (Union[str, Type]): base node class or a str of the import
            path for the base node class. 
        manager (Union[str, Type]): base director class or a str of the import
            path for the base director class.

            
    """
    settings: Union[str, Type] = 'sourdough.project.Settings'
    filer: Union[str, Type] = 'sourdough.project.Filer' 
    workflow: Union[str, Type] = 'sourdough.project.Workflow'
    component: Union[str, Type] = 'sourdough.project.Component'
    creator: Union[str, Type] = 'sourdough.project.Builder'
    manager: Union[str, Type] = 'sourdough.project.Director'



__version__ = '0.1.2'

__author__ = 'Corey Rayburn Yung'

__all__ = []
