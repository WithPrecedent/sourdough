"""
sourdough: getting a head start on python projects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    base: core structural classes and mixins.
    configuration: classes related to configuration options and file management.
    project: classes applying 'base' to composite object projects.
    utilities: functions and decorators that make complex and tedious tasks 
        easier.

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
    you can just use: sourdough.Hybrid
    
"""
from .utilities import tools
from .utilities.decorators import namify
from .core import types
from .core.types import Lexicon
from .core.types import Catalog
from .core.types import Slate
from .core.types import Hybrid
from .core.types import Quirk
from .core import quirks
from .configuration.settings import Settings
from .configuration.filer import Filer
from .core.base import Component
from .core.base import Structure
from .core.base import Stage
from .core.base import Workflow
from .project.components import Technique 
from .project.components  import Step
from .project import structures
from .project import workflows
from .project.interface import Project


__version__ = '0.1.1'

__author__ = 'Corey Rayburn Yung'

__all__ = []
