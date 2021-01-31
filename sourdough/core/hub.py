"""
quirks: classes to implement sourdough's subclass registration system.
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Base (ABC): abstract class for connecting another class to a Library, which
        stores subclass instances.
    Library (Catalog): a dictionary that stores subclasses and includes methods
        to access, build, or instance those classes. This includes runtime
        construction of new classes using sourdough quirks.

"""
from __future__ import annotations
import abc
import dataclasses
import types
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import sourdough
