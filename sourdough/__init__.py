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
from sourdough.structure.dictionaries import Lexicon
from sourdough.structure.dictionaries import Corpus
from sourdough.structure.dictionaries import Reflector

from sourdough.structure.components import Component
from sourdough.structure.components import Task
from sourdough.structure.components import Stage
from sourdough.structure.components import LibraryMixin
from sourdough.structure.components import RegistryMixin
from sourdough.structure.components import ProxyMixin
from sourdough.structure.components import OptionsMixin
from sourdough.structure.iterables import Progression
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
