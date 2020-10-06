"""
library: dictionaries for storing classes and instances.
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:

"""
from __future__ import annotations
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Union)

import sourdough 


workflows = sourdough.Catalog()

designs = sourdough.Catalog()

components = sourdough.Catalog()

options = sourdough.Catalog()