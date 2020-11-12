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
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Union)

""" 
sourdough imports are designed to allow key classes and functions to have first 
or second-level access.

For example:

    Instead of acccesing Hybrid via sourdough.core.types.Hybrid,
    you can just use: sourdough.types.Hybrid
    
"""

from .utilities import tools

from .core import types
from .core import quirks
from .core.configuration import Settings
from .core.files import Manager

from .project import resources
from .project.base import Creator
from .project.base import Component
from .project import creators
from .project.interface import Project

from .components import workflows
from .components import elements
from .components import graphs


__version__ = '0.1.1'

__author__ = 'Corey Rayburn Yung'

__all__ = []
