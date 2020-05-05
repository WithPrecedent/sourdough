"""
.. module:: sourdough
:synopsis: python projects made simple
:author: Corey Rayburn Yung
:copyright: 2019-2020
:license: Apache-2.0
"""

from pkg_resources import get_distribution, DistributionNotFound

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = __name__
    __version__ = get_distribution(dist_name).version
except DistributionNotFound:
    __version__ = 'unknown'
finally:
    del get_distribution, DistributionNotFound


from .structure.component import Component
from sourdough.structure.loader import LazyLoader
from sourdough.configuration.settings import Settings
from sourdough.configuration import defaults
from sourdough.configuration.filer import Filer
from sourdough.utilities import utilities
from sourdough.creation.system import System
from sourdough.structure.definition import MirrorType
# from sourdough.project import Project
#


# from sourdough.creation.worker import Worker

# from sourdough.structure.component import Proxy
# from sourdough.structure.definition import Type
# from sourdough.structure.handler import Task
# from sourdough.structure.loader import LazyLoader
# from sourdough.structure.plan import Plan
# from sourdough.structure.repository import Repository
# from sourdough.structure.technique import Technique


__version__ = '0.1.0'

__author__ = 'Corey Rayburn Yung'

__all__ = [
    'Component',
    'LazyLoader',
    'utilities',
    'Settings',
    'defaults',
    'Filer',
    'System',
    'MirrorType',

    # 'Project',
    # 'System',
    # 'Worker',

    # 'Proxy',
    # 'Type',
    # 'Task',

    # 'Plan',
    # 'Repository',
    # 'System',
    # 'Technique',
    # 'Worker'
    ]
