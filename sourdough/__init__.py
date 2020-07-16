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

from sourdough.utilities import tools
from sourdough.utilities import decorators

from sourdough.structure.base import Component
from sourdough.structure.base import Task
from sourdough.structure.base import Stage
from sourdough.structure.base import Anthology
from sourdough.structure.base import Lexicon
from sourdough.structure.base import Corpus
from sourdough.structure.base import Progression
from sourdough.structure.mixins import LibraryMixin
from sourdough.structure.mixins import RegistryMixin
from sourdough.structure.mixins import ProxyMixin
from sourdough.structure.mixins import OptionsMixin

from sourdough.structure.iterables import Corpus
from sourdough.structure.iterables import Reflector

from sourdough.project.tasks import Technique
from sourdough.project.tasks import Step
from sourdough.project.tasks import Plan
from sourdough.project.tasks import Project

# from sourdough.structure.creators import Factory
# from sourdough.structure.creators import LazyLoader

# from sourdough.configuration import defaults
# from sourdough.configuration.settings import Settings
# from sourdough.configuration.filer import Filer

# from sourdough.structure.iterables import Director

# from sourdough.structure.graphs import DAGraph

# from sourdough.projects.stages import Stage
# from sourdough.projects.stages import Author
# from sourdough.projects.stages import Editor
# from sourdough.projects.stages import Publisher
# from sourdough.projects.stages import Reader
# from sourdough.projects.manager import Manager


__version__ = '0.1.0'

__author__ = 'Corey Rayburn Yung'

__all__ = []
