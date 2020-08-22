"""
sourdough: getting a head start on python projects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    base: core structural classes and mixins.
    configuration: classes related to configuration options and file management.
    project: classes applying 'base' to composite object projects.
    utilities: classes and functions that make complex and tedious tasks easier.

In general, python files in sourdough are over-documented to allow beginning
programmers to understand basic design choices that were made. If there is any
area of the documentation that could be made clearer, please don't hesitate
to email me - I want to ensure the package is as accessible as possible.

"""

""" 
Imports are designed to allow key classes and functions to have first or 
second-level access.

For example:

    Instead of acccesing Element via sourdough.core.Element,
    you can just use: sourdough.core.Element
    
"""

# Imports of select functions and decorators for use throughout sourdough.
from sourdough import utilities

# Imports of core base classes and mixins.
from sourdough.base import core as core
from sourdough.base import mixins as mixins

# Imports of configuration and file management classes.
from sourdough.configuration.settings import Settings
from sourdough.configuration.filer import Filer

# Imports for sourdough projects.
from sourdough.project.framework import Component
from sourdough.project.framework import Structure
from sourdough.project.framework import Stage
from sourdough.project.framework import Workflow
from sourdough.project.interface import Project
from sourdough import project


__version__ = '0.1.1'

__author__ = 'Corey Rayburn Yung'

# __all__ = []
