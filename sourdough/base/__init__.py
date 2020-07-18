"""
.. module:: base
:synopsis: base structural classes for sourdough
:author: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""


from .core import Component
from .core import Task
from .core import Creator
from .core import Lexicon
from .core import Catalog
# from .core import Reflector
from .core import Progression
from .settings import Settings
from .mixins import LibraryMixin
from .mixins import RegistryMixin
from .mixins import ProxyMixin
from .mixins import OptionsMixin


__version__ = '0.1.0'

__author__ = 'Corey Rayburn Yung'

__all__ = [
    'Component',
    'Task',
    'Creator',
    'Lexicon',
    'Catalog',
    # 'Reflector',
    'Progression',
    'LibraryMixin',
    'RegistryMixin',
    'ProxyMixin',
    'OptionsMixin']