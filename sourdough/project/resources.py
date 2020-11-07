"""
resources: dictionaries for storing classes and instances.
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:

"""
from __future__ import annotations
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Union)

import sourdough 


workflows = sourdough.types.Catalog()

stages = sourdough.types.Catalog()

bases = sourdough.types.Catalog()

components = sourdough.types.Catalog()

options = sourdough.types.Catalog()

algorithms = sourdough.types.Catalog()
