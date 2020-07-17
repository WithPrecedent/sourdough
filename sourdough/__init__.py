"""
.. module:: sourdough
:synopsis: get a head start on python managers
:author: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

""" 
Imports are designed to allow key classes and functions to have first or 
second-level access.

For example:

    Instead of acccesing Component via sourdough.base.core.Component,
    you can just use: sourdough.base.Component
    
"""

from sourdough import utilities
from sourdough import base
from sourdough import manager


__version__ = '0.1.0'

__author__ = 'Corey Rayburn Yung'

__all__ = [
    'utilities',
    'base',
    'manager']
