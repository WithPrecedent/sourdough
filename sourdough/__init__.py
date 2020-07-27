"""
sourdough: getting a head start on python projects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    base: core structural classes and mixins.
    configuration: classes related to configuration options and file management.
    project: classes applying 'base' to composite object projects.
    utilities: classes and functions that make complex and commmon tasks easier.

In general, python files in sourdough are over-documented to allow beginning
programmers to understand basic design choices that were made. If there is any
area of the documentation that could be made clearer, please don't hesitate
to email me - I want to ensure the package is as accessible as possible.

"""

""" 
Imports are designed to allow key classes and functions to have first or 
second-level access.

For example:

    Instead of acccesing Component via sourdough.base.components.Component,
    you can just use: sourdough.Component
    
"""

# Imports of functions and decorators for use throughout sourdough.
from sourdough import utilities

# Imports of core base classes and compatible mixins.
from sourdough.base.components import Component
from sourdough.base.components import Action
from sourdough.base.components import Inventory
from sourdough.base.components import Creator
from sourdough.base.components import Loader
from sourdough.base.components import Lexicon
from sourdough.base.components import Catalog
from sourdough.base.mixins import LibraryMixin
from sourdough.base.mixins import RegistryMixin
from sourdough.base.mixins import ProxyMixin
from sourdough.base.mixins import OptionsMixin

# Imports of configuration and file management classes.
from sourdough.configuration import defaults
from sourdough.configuration.settings import Settings
from sourdough.configuration.filer import Filer

# Imports for sourdough projects.
from sourdough.project import structures
from sourdough.project.creators import Author
from sourdough.project.creators import Publisher
from sourdough.project.creators import Reader
from sourdough.project.project import Project


__version__ = '0.1.1'

__author__ = 'Corey Rayburn Yung'

__all__ = [
    'utilities',
    'Component',
    'Action',
    'Inventory',
    'Creator',
    'Lexicon',
    'Catalog',
    'LibraryMixin',
    'RegistryMixin',
    'ProxyMixin',
    'OptionsMixin',
    'Loader',
    'defaults',
    'Settings',
    'Filer',
    'structures',
    'Author',
    'Publisher',
    'Reader',  
    'Project']
