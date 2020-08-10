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

    Instead of acccesing Element via sourdough.base.core.Element,
    you can just use: sourdough.Element
    
"""

# Imports of select functions and decorators for use throughout sourdough.
from sourdough import utilities

# Imports of core base classes and mixins.
from sourdough.base.core import Element
from sourdough.base.core import Action
from sourdough.base.core import Hybrid
from sourdough.base.core import Lexicon
from sourdough.base.core import Catalog
from sourdough.base.mixins import LibraryMixin
from sourdough.base.mixins import RegistryMixin
from sourdough.base.mixins import OptionsMixin
from sourdough.base.mixins import LoaderMixin
from sourdough.base.mixins import ProxyMixin

# Imports of configuration and file management classes.
from sourdough.configuration.settings import Settings
from sourdough.configuration.filer import Filer

# Imports for sourdough projects.
from sourdough.project.containers import Outline
from sourdough.project.containers import Inventory
from sourdough.project.containers import Overview
from sourdough.project.components import Component
from sourdough.project.components import Technique
from sourdough.project.components import Task
from sourdough.project.components import Worker
from sourdough.project.components import Manager
from sourdough.project.roles import Role
from sourdough.project.roles import Obey
from sourdough.project.roles import Compare
from sourdough.project.roles import Survey
from sourdough.project.workflow import Workflow
from sourdough.project.workflow import Editor
from sourdough.project.project import Project


__version__ = '0.1.1'

__author__ = 'Corey Rayburn Yung'

# __all__ = [
#     'utilities',
#     'Element',
#     'Action',
#     'Hybrid',
#     'Action',
#     'Lexicon',
#     'Catalog',
#     'LibraryMixin',
#     'RegistryMixin',
#     'OptionsMixin',
#     'LoaderMixin',
#     'ProxyMixin',
#     'Settings',
#     'Filer',
#     'roles',
#     'Role',
#     'Technique',
#     'Task',
#     'Edge',
#     'Node',
#     'workflow',
#     'Worker',
#     'Manager']
