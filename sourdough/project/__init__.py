"""
project: applying the sourdough core to create and implement projects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    importables
    __getattr__
    
"""
__version__ = '0.1.2'

__author__ = 'Corey Rayburn Yung'


import importlib
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Set, Tuple, Type, Union)


importables: Dict[str, str] = {
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
