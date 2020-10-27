"""
project: a foundation for a python project
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:


"""
from . import resources
from .settings import Settings
from .filer import Filer
from .workflow import Stage
from .workflow import Workflow
from .structure import Component
from .interface import Results
from .interface import Project


__version__ = '0.1.1'

__author__ = 'Corey Rayburn Yung'

__all__ = []
