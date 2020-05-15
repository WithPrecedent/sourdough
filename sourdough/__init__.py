"""
.. module:: sourdough
:synopsis: get a head start on python projects
:author: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

""" 
Imports are designed to allow certain objects to have first or second-level 
access.

For example:

    Instead of acccesing Component via sourdough.core.base.Component,
    you can just use: sourdough.Component

    Rather than accessing MirrorType via sourdough.core.types.MirrorType,
    you can just use: sourdough.types.MirrorType
    
"""

from sourdough.core import utilities
from sourdough.core.component import Component
from sourdough.core import mixins as mixins
from sourdough.core import base as base
from sourdough.core import types as types
from sourdough.core.options import Options

from sourdough.configuration import defaults
from sourdough.configuration.settings import Settings
from sourdough.configuration.filer import Filer

from sourdough.structure.plan import Plan
from sourdough.structure.project import Project

from sourdough.workflow.manager import Stage
from sourdough.workflow.manager import Manager


__version__ = '0.1.0'

__author__ = 'Corey Rayburn Yung'

__all__ = [
    'Catalog',
    'Library',
    'utilities',
    'Component',
    'Options',
    'types',
    'defaults',
    'Settings',
    'Filer',
    'Plan',
    'Project',
    'Stage',
    'Manager',
    ]
