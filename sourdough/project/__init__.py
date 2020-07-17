"""
.. module: manager
:synopsis: sourdough manager classes
:author: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

from .filer import Filer
from .creators import Author
from .creators import Publisher
from .creators import Reader
from .project import Project
from .workers import Technique
from .workers import Step
from .workers import Worker
from .workers import Manager


__version__ = '0.1.0'

__author__ = 'Corey Rayburn Yung'

__all__ = [
    'Settings',
    'Filer',
    'Author',
    'Publisher',
    'Reader',
    'Project',
    'Technique',
    'Step',
    'Worker',
    'Manager']