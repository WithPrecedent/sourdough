"""
project: classes for constructing and executing composite objects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    elements: subclasses of Action which can be used in composite objects.
    creators: subclasses of Action which are used to construct composite
        objects (including elements of the complete objects).
    graphs: classes related to graph designs.
    project: interface classes for constructing and executing composite objects.
    designs: classes containing instructions for building and executing
        different types of composite objects.
    workers: classes related to tree designs. 

"""

from .containers import Outline
from .containers import Overview
from .components import Technique
from .components import Task
from .structures import Aggregation
from .structures import Pipeline
from .structures import Contest
from .structures import Study
from .structures import Survey
# from .structures import Graph
from .editor import Editor


__version__ = '0.1.1'

__author__ = 'Corey Rayburn Yung'
