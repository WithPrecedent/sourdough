"""
sourdough: get a head start on python projects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
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
    
# They also operate on a lazy importing system. This means that modules are only
# imported when first needed. This allows users to only use part of sourdough
# without the memory footprint of the entire package. This also avoids some of
# the circular import problems (and the need for solutions to those problems)
# when the package is first initialized. However, this can come at the cost of 
# less than clear error messages if your fork of sourdough imports classes and
# objects out of order. However, given that python 3.8+ calls almost every import
# error a "circular import," I don't think the error tracebacks are any less
# confusing in sourdough.

"""
import importlib
from types import ModuleType
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)


from . import utilities
from . import core
from . import project
from . import components

from .utilities import tools

from .core import types
from .core import quirks
from .core import workshop

from .project.configuration import options
from .project.configuration import rules
from .project.configuration import bases
from .project.configuration import Settings
from .project.files import Clerk
from .project import configuration

from .project.base import Manager
from .project.base import Creator
from .project.base import Product
from .project.base import Component
from .project import products
from .project import creators

from .components import workflows
from .components import elements
from .components import graphs

from .project.interface import Project



# importables = {
#     'tools': 'utilities.tools',
#     'types': 'core.types',
#     'quirks': 'core.quirks',
#     'options': 'project.interface.options',
#     'rules': 'project.interface.rules',
#     'Settings': 'core.configuration.Settings',
#     'Clerk': 'core.files.Clerk',
#     'Creator': 'project.base.Creator',
#     'Product': 'project.base.Product',
#     'Component': 'project.base.Component',
#     'Bases': 'project.interface.Bases',
#     'Rules': 'project.interface.Rules',
#     'Project': 'project.interface.Project',
#     'workflows': 'components.workflows'}


# def __getattr__(name: str) -> Any:
#     """[summary]

#     Args:
#         name (str): [description]

#     Returns:
#         Any: [description]
#     """
#     value = importables[name]
#     if isinstance(value, str):
#         item = value.split('.')[-1]
#         module = value[:-len(item) - 1]
#         value = getattr(importlib.import_module(module, package = 'sourdough'), 
#                         value)
#         importables[item] = value       
#     return value
        

# from .core import types
# from .core import quirks
# from .project.resources import options
# from .project.resources import rules
# from .project import resources

# # from .core.configuration import Settings
# from .core.files import Clerk
# from .project.base import Creator
# from .project.base import Product
# from .project.base import Component
# from .project import products
# from .project import creators

# from .components import workflows
# from .components import elements
# from .components import graphs

# from .project.interface import Bases
# from .project.interface import Project


__version__ = '0.1.2'

__author__ = 'Corey Rayburn Yung'

__all__ = []
