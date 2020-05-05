"""
.. module:: loader
:synopsis: lazy loading made simple
:author: Corey Rayburn Yung
:copyright: 2019-2020
:license: Apache-2.0
"""

import dataclasses
import importlib
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Union

import sourdough


@dataclasses.dataclass
class LazyLoader(sourdough.Component):
    """Base class for lazy loading.

    Args:
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. If the class
            instance needs settings from the shared Settings instance, 'name'
            should match the appropriate section name in that Settings instance.
            When subclassing, it is a good settings to use the same 'name' attribute
            as the base class for effective coordination between sourdough
            classes. Defaults to None or __class__.__name__.lower().
        module (Optional[str]): name of module where object to use is located
            (can either be a sourdough or non-sourdough module). Defaults to
            'sourdough'.
        default_module (Optional[str]): a backup name of module where object to
            use is located (can either be a sourdough or non-sourdough module).
            Defaults to 'sourdough'.

    """
    name: Optional[str] = None
    module: Optional[str] = dataclasses.field(
        default_factory = lambda: 'sourdough')
    default_module: Optional[str] = dataclasses.field(
        default_factory = lambda: 'sourdough')

    """ Public Methods """

    def load(self, attribute: str) -> object:
        """Returns object named in 'attribute'.

        If 'attribute' is not a str, it is assumed to have already been loaded
        and is returned as is.

        The method searches both 'module' and 'default_module' for the named
        'attribute'. It also checks to see if the 'attribute' is directly
        loadable from the module or if it is the name of a local attribute that
        has a value of a loadable object in the module.

        Args:
            attribute (str): name of attribute to load from 'module' or
                'default_module'.

        Returns:
            object: from 'module' or 'default_module'.

        """
        # If 'attribute' is a string, attempts to load from 'module' or, if not
        # found there, 'default_module'.
        if isinstance(getattr(self, attribute), str):
            try:
                return getattr(importlib.import_module(self.module), attribute)
            except (ImportError, AttributeError):
                try:
                    return getattr(
                        importlib.import_module(self.module),
                        getattr(self, attribute))
                except (ImportError, AttributeError):
                    try:
                        return getattr(
                            importlib.import_module(self.module), attribute)
                    except (ImportError, AttributeError):
                        try:
                            return getattr(
                                importlib.import_module(self.default_module),
                                getattr(self, attribute))
                        except (ImportError, AttributeError):
                            raise ImportError(
                                f'{attribute} is neither in \
                                {self.module} nor {self.default_module}')
        # If 'attribute' is not a string, it is returned as is.
        else:
            return getattr(self, attribute)