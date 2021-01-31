"""
project: subpackage applying the sourdough core to create and implement projects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    importables (Dict): dict of imports available directly from 'sourdough.'.
        This dict is needed for the 'lazily_import' function which is called by
        this modules '__getattr__' function.
    lazily_import (function): function which imports sourdough modules and
        contained only when such modules and items are first accessed.
    
"""
__version__ = '0.1.2'

__author__ = 'Corey Rayburn Yung'


import importlib
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Set, Tuple, Type, Union)

import sourdough


""" 
The keys of 'importables' are the attribute names of how users should access
the modules and other items listed in values. 'importables' is necessary for
the lazy importation system used throughout sourdough.
"""
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
    
    For further information about how this lazy import system works, read the
    documentation accompanying the 'lazily_import' function.
    
    Args:
        name (str): name of sourdough project module or item.

    Raises:
        AttributeError: if there is no module or item matching 'name'.

    Returns:
        Any: a module or item stored within a module.
        
    """
    return sourdough.lazily_import(name = name)
