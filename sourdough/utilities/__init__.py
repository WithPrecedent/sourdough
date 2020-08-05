"""
utilities: sourdough utility functions and decorators
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    decorators: class, method, and function decorators.
    memory: classes and functions for conserving system memory.
    tools: assorted functions for making basic tasks easier.

"""

from .tools import importify
from .tools import listify
from .tools import numify
from .tools import snakify
from .tools import subsetify
from .tools import typify
from .tools import datetime_string
from .tools import add_prefix
from .tools import add_suffix
from .tools import drop_prefix
from .tools import drop_suffix
from .tools import deduplicate


__version__ = '0.1.1'

__author__ = 'Corey Rayburn Yung'

__all__ = [
    'importify',
    'listify',
    'numify',
    'snakify',
    'subsetify',
    'typify',
    'datetime_string']