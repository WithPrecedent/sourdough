"""
base: base sourdough classes
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    core: structural classes for sourdough.
    mixins: mixins for sourdough Elements.

"""


from .core import Element
from .core import Action
from .core import Lexicon
from .core import Catalog
from .core import Slate
from .core import Hybrid
from .mixins import LibraryMixin
from .mixins import RegistryMixin
from .mixins import OptionsMixin
from .mixins import LoaderMixin
from .mixins import ProxyMixin


__version__ = '0.1.1'

__author__ = 'Corey Rayburn Yung'
