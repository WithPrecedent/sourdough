"""
sourdough: get a head start on python projects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    core: core structural classes and mixins.
    project: base classes for sourdough projects.
    components: composite object classes.
    utilities: functions that make complex and tedious tasks easier.

In general, python files in sourdough are over-documented to allow beginning
programmers to understand basic design choices that were made. If there is any
area of the documentation that could be made clearer, please don't hesitate
to email me - I want to ensure the package is as accessible as possible.

"""

""" 
sourdough imports are designed to allow key classes and functions to have first 
or second-level access.

For example:

    Instead of acccesing Hybrid via sourdough.core.types.Hybrid,
    you can just use: sourdough.types.Hybrid
    
They also operate on a lazy importing system. This means that modules are only
imported when first needed. This allows users to only use part of sourdough
without the memory footprint of the entire package. This also avoids some of
the circular import problems (and the need for solutions to those problems)
when the package is first initialized. However, this can come at the cost of 
less than clear error messages if your fork of sourdough imports classes and
objects out of order. However, given that python 3.8+ calls almost every import
error a "circular import," I don't think the error tracebacks are any less
confusing in sourdough.

"""
__version__ = '0.1.2'

__author__ = 'Corey Rayburn Yung'


import importlib
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)


importables: Dict[str, str] = {
    'core': 'core',
    'project': 'project',
    'utilities': 'utilities',
    'decorators': 'utilities.decorators',
    'memory': 'utilities.memory',
    'tools': 'utilities.tools',
    'quirks': 'core.quirks',
    'structures': 'core.structures',
    'filing': 'core.filing',
    'framework': 'core.framework',
    'quirks': 'core.quirks',
    'types': 'core.types',
    'Proxy': 'core.types.Proxy',
    'Bunch': 'core.types.Bunch',
    'Progression': 'core.types.Progression',
    'Hybrid': 'core.types.Hybrid',
    'Lexicon': 'core.types.Lexicon',
    'Catalog': 'core.types.Catalog',
    'Configuration': 'core.framework.Configuration',
    'Clerk': 'core.files.Clerk',
    'Base': 'core.quirks.Base',
    'Bases': 'core.quirks.Bases',
    'Library': 'core.quirks.Library',
    'Structure': 'core.structures.Structure',
    'Graph': 'core.structures.Graph',
    'Project': 'project.interface.Project'}


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
