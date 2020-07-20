"""
.. module:: sourdough
:synopsis: get a head start on python managers
:author: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

""" 
Imports are designed to allow key classes and functions to have first or 
second-level access.

For example:

    Instead of acccesing Component via sourdough.base.core.Component,
    you can just use: sourdough.base.Component
    
"""

# Functions and decorators for use in sourdough.
from sourdough import utilities

# Core base class imports
from sourdough.base.core import Component
from sourdough.base.core import Task
from sourdough.base.core import Creator
from sourdough.base.core import Lexicon
from sourdough.base.core import Catalog
from sourdough.base.core import Progression
from sourdough.base.settings import Settings
from sourdough.base.mixins import LibraryMixin
from sourdough.base.mixins import RegistryMixin
from sourdough.base.mixins import ProxyMixin
from sourdough.base.mixins import OptionsMixin

# Imports for sourdough projects
from sourdough.project.filer import Filer
from sourdough.project.creators import Author
from sourdough.project.creators import Publisher
from sourdough.project.creators import Reader
from sourdough.project.tree import Technique
from sourdough.project.tree import Step
from sourdough.project.tree import Worker
from sourdough.project.tree import Manager
from sourdough.project.project import Project


__version__ = '0.1.0'

__author__ = 'Corey Rayburn Yung'

__all__ = [
    'utilities',
    'Component',
    'Task',
    'Creator',
    'Lexicon',
    'Catalog',
    'Progression',
    'LibraryMixin',
    'RegistryMixin',
    'ProxyMixin',
    'OptionsMixin',
    'Filer',
    'Author',
    'Publisher',
    'Reader',
    'Project',
    'Technique',
    'Step',
    'Worker',
    'Manager']
