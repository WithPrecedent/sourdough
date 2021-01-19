"""
creators: 
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:

    
"""
from __future__ import annotations
import abc
import dataclasses
import itertools
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import sourdough


@dataclasses.dataclass
class Creator(sourdough.types.Base):
    """[summary]

    Args:
        sourdough ([type]): [description]
        
    """
    contents: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    library: ClassVar[sourdough.types.Library] = sourdough.types.Library()
 