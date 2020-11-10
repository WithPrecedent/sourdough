"""
sourdough: get a head start on python projects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    core: core structural classes and mixins.
    project: base classes for sourdough projects.
    workflows: composite object classes.
    directors: classes containing director sequences for sourdough projects.
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

""" Shared Utility Imports """

from .utilities import tools

""" Second-level Imports """

from .core import types
from .core import quirks

from .project import resources
from .project import workflow

from .core.configuration import Settings
from .core.files import Manager
from .project.labor import Specialist
from .project.labor import Director
from .project.interface import Project

from .workflows import components
from .workflows import graphs
from .workflows import flows

from .workers import specialists
from .workers import directors

__version__ = '0.1.1'

__author__ = 'Corey Rayburn Yung'

__all__ = []

