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

""" 
Imports are designed to allow key classes and functions to have first or 
second-level access.

For example:

    Instead of acccesing Element via sourdough.core.base.Element,
    you can just use: sourdough.Element
    
"""

# Imports of select functions and decorators for use throughout sourdough.
from .utilities import tools
from .utilities import decorators
from .utilities import memory

# Imports of core base classes and mixins.
from .core.base import Element
from .core.base import Elemental
# from .core import creators
# from .core import validators
from .core import containers
from .core import mixins
from .core import iterables

# Imports of configuration and file management classes.
from .configuration.settings import Settings
from .configuration.filer import Filer

# Imports for sourdough projects.
from .project.framework import Inventory
from .project.framework import Component
from .project.framework import Structure
from .project.framework import Stage
from .project.framework import Workflow
from .project.components import Aggregation
from .project.components import Pipeline
from .project.components import Contest
from .project.components import Study
from .project.components import Survey
from .project.components import Technique 
from .project.components import Task
from .project.workflow import Editor
from .project.interface import Project


__version__ = '0.1.1'

__author__ = 'Corey Rayburn Yung'

__all__ = [
    'tools',
    'decorators',
    'memory',
    'Element',
    'Elemental',
    'creators',
    'validators',
    'containers',
    'composites',
    'mixins',
    'Settings',
    'Filer',
    'Inventory',
    'Component',
    'Structure',
    'Stage',
    'Workflow',
    'Aggregation', 
    'Pipeline', 
    'Contest', 
    'Study', 
    'Survey', 
    'Technique', 
    'Task', 
    'Details', 
    'Outline', 
    'Editor', 
    'Project']
