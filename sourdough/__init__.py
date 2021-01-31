"""
sourdough: get a head start on python projects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    importables (Dict): dict of imports available directly from 'sourdough.'.
        This dict is needed for the 'lazily_import' function which is called by
        this modules '__getattr__' function.
    lazily_import (function): function which imports sourdough modules and
        contained only when such modules and items are first accessed.

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
    you can just use: sourdough.Hybrid
    
They also operate on a lazy importing system. This means that modules are only
imported when first needed. This allows users to only use part of sourdough
without the memory footprint of the entire package. This also avoids some of
the circular import problems (and the need for solutions to those problems)
when the package is first initialized. However, this can come at the cost of 
less than clear error messages if your fork of sourdough imports classes and
objects out of order. However, given that python 3.8+ calls almost every import
error a "circular import," I don't think the error tracebacks are any less
confusing in sourdough. It's possible that this lazy import system will cause
trouble for some IDEs (such as pycharm) if you choose to fork sourdough. 
However, I have not encountered any such issuse using VSCode and its default 
python linter.

"""
__version__ = '0.1.2'

__author__ = 'Corey Rayburn Yung'


import importlib
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)


""" 
The keys of 'importables' are the attribute names of how users should access
the modules and other items listed in values. 'importables' is necessary for
the lazy importation system used throughout sourdough.
"""
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
    
    Args:
        name (str): name of sourdough module or item.

    Raises:
        AttributeError: if there is no module or item matching 'name'.

    Returns:
        Any: a module or item stored within a module.
        
    """
    return lazily_import(name = name)

def lazily_import(name: str) -> Any:
    """Lazily imports modules and items within them.

    Lazy importing means that modules are only imported when they are first
    accessed. This can save memory and keep namespaces decluttered.
    
    This code is adapted from PEP 562: https://www.python.org/dev/peps/pep-0562/
    which outlines how the decision to incorporate '__getattr__' functions to 
    modules allows lazy loading. Rather than place this function solely within
    '__getattr__', it is included here seprately so that it can easily be called 
    by '__init__.py' files throughout sourdough and by users (as 
    'sourdough.lazily_import').
    
    To effictively use 'lazily_import' in an '__init__.py' file, the user needs
    to also include an 'importables' dict which indicates how users should
    accesss imported modules and included items. This modules includes such an
    example 'importables' dict and how to easily add this function to a 
    '__getattr__' function.
    
    Instead of limiting its lazy imports to full import paths as the example in 
    PEP 562, this function has 2 major advantages:
        1) It allows importing items within modules and not just modules. The
            function first tries to import 'name' assuming it is a module. But if
            that fails, it parses the last portion of 'name' and attempts to 
            import the preceding module and then returns the item within it.
        2) It allows import paths that are less than the full import path by
            using the 'importables' dict. 'importables' has keys which are the
            name of the attribute being sought and values which are the full
            import path (dropping the leading '.'). 'importables' thus acts
            as the normal import block in an __init__.py file but insures that
            all importing is done lazily.

    Args:
        name (str): name of module or item within a module.

    Raises:
        AttributeError: if there is no module or item matching 'name'.

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
