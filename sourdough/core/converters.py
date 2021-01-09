"""
converters: classes and instances for converting types
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
import pathlib
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import sourdough


@dataclasses.dataclass
class SettingsConverter(sourdough.bases.Converter):
    """
    """
    accepts: Tuple[Type] = tuple(sourdough.Settings, str, pathlib.Path)
    returns: Type = sourdough.Settings
    parameters: Tuple[str] = tuple()
    additions: Tuple[str] = tuple()
    
    """ Public Methods """
        
    @convert.register
    def convert(self, item: str) -> sourdough.Settings:
        return self.returns(contents = item)

    @convert.register
    def convert(self, item: pathlib.Path) -> sourdough.Settings:
        return self.returns(contents = item)
    
    @convert.register
    def convert(self, item: None) -> sourdough.Settings:
        return self.returns(contents = item)