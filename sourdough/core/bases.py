"""
bases: abstract base classes for core sourdough class interfaces
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)



Contents:

"""
from __future__ import annotations
import abc
import collections.abc
import dataclasses
import functools
import inspect
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import sourdough


