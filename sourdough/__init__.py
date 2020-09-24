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
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union

""" 
sourdough imports are designed to allow key classes and functions to have first 
or second-level access.

For example:

    Instead of acccesing Element via sourdough.core.base.Element,
    you can just use: sourdough.base.Element
    
"""

# Imports of select functions and decorators for use throughout sourdough.
from .utilities import tools
from .utilities import decorators
from .utilities import memory

# Imports of core base classes and mixins.
from .core import base
from .core import types
from .core import framework
from .core.framework import Inventory
from .core.framework import Component
from .core.framework import Stage
from .core.framework import Workflow

# Imports of configuration and file management classes.
from .configuration.settings import Settings
from .configuration.filer import Filer

# Imports for sourdough projects.
from .project.components import Structure
from .project.components import Aggregation
from .project.components import Pipeline
from .project.components import Contest
from .project.components import Study
from .project.components import Survey
from .project.components import Technique 
from .project.components import Step
from .project.workflow import Editor
from .project.interface import Project


"""
sourdough type annotations.

The following aliases are used for simpler annotation in sourdough and are
accessible at sourdough.[Annotation]
    
    Elemental: annotation type for all classes that contain Elements. This
        includes any Element subclass, Sequences of Elements, and Mappings with
        Element values.
    
    Componental: annotation type for all classes that contain Components. This
        includes any Component subclass, Sequences of Components, and Mappings 
        with Components values.
        
"""
Elemental = Union[
    base.Element, 
    Mapping[str, base.Element], 
    Sequence[base.Element]]


Componental = Union[
    Component, 
    Mapping[str, Component], 
    Sequence[Component]]


__version__ = '0.1.1'

__author__ = 'Corey Rayburn Yung'

__all__ = [
    'tools',
    'decorators',
    'memory',
    'base',
    'types',
    'framework',
    'Element',
    'Elemental',
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
    'Step', 
    'Details', 
    'Outline', 
    'Editor', 
    'Project']
