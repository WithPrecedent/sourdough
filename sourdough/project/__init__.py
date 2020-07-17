"""
.. module: project
:synopsis: sourdough project classes
:author: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

from .filer import Filer
from .creators import Author
from .creators import Publisher
from .creators import Reader
from .manager import Manager
from .project import Technique
from .project import Step
from .project import Worker
from .project import Project


__version__ = '0.1.0'

__author__ = 'Corey Rayburn Yung'

__all__ = [
    'Settings',
    'Filer',
    'Author',
    'Publisher',
    'Reader',
    'Manager',
    'Technique',
    'Step',
    'Worker',
    'Project']