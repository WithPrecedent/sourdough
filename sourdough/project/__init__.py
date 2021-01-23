"""
project: applying the sourdough core to create projects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:

"""

from .configuration import Settings
from .clerk import Filer
from .structures import *
from .nodes import *
from .interface import Bases
from .builder import Manager


__version__ = '0.1.2'

__author__ = 'Corey Rayburn Yung'

__all__ = []
