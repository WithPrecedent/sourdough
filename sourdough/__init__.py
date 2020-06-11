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

    Instead of acccesing Component via sourdough.structure.components.Component,
    you can just use: sourdough.Component
    
"""

from sourdough.structure import utilities
from sourdough.structure.components import Component
from sourdough.structure.components import Operator
from sourdough.structure.components import Factory
from sourdough.structure.components import LazyLoader
from sourdough.structure.dictionaries import Lexicon
from sourdough.structure.dictionaries import Catalog
from sourdough.structure.graphs import DAGraph
from sourdough.structure.iterables import Progression
from sourdough.structure.iterables import Plan
from sourdough.structure.iterables import Director
from sourdough.structure.mixins import LibraryMixin
from sourdough.structure.mixins import RegistryMixin
from sourdough.structure.mixins import ProxyMixin
from sourdough.structure.types import MirrorType

from sourdough.configuration import defaults
from sourdough.configuration.settings import Settings
from sourdough.configuration.filer import Filer

from sourdough.projects.task import Technique
from sourdough.projects.task import Task
from sourdough.projects.worker import Worker
from sourdough.projects.worker import Project
from sourdough.projects.stages import Stage
from sourdough.projects.stages import Author
from sourdough.projects.stages import Editor
from sourdough.projects.stages import Publisher
from sourdough.projects.stages import Reader
from sourdough.projects.manager import Manager


__version__ = '0.1.0'

__author__ = 'Corey Rayburn Yung'

__all__ = []
