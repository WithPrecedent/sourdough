"""
.. module:: handler
:synopsis: project application made simple
:author: Corey Rayburn Yung
:copyright: 2019-2020
:license: Apache-2.0
"""

import abc
import dataclasses
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Union

try:
    import pathos.multiprocessing as mp
except ImportError:
    import multiprocessing as mp

import sourdough


@dataclasses.dataclass
class Task(sourdough.Component):
    """Base class for creating or modifying other sourdough classes.

    Args:
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. If the class instance
            needs settings from the shared Settings instance, 'name' should
            match the appropriate section name in that Settings instance. When
            subclassing, it is a good settings to use the same 'name' attribute
            as the base class for effective coordination between sourdough
            classes. Defaults to None or __class__.__name__.lower().

    """
    name: Optional[str] = None

    """ Required Subclass Methods """

    @abc.abstractmethod
    def apply(self,
            data: sourdough.Component, **kwargs) -> sourdough.Component:
        """Subclasses must provide their own methods."""
        return self


# @dataclasses.dataclass
# class ParallelTask(Task):
#     """Applies workflow using one or more CPU or GPU cores.

#     Args:
#         name (Optional[str]): designates the name of the class instance used
#             for internal referencing throughout sourdough. If the class instance
#             needs settings from the shared Settings instance, 'name' should
#             match the appropriate section name in that Settings instance. When
#             subclassing, it is a good settings to use the same 'name' attribute
#             as the base class for effective coordination between sourdough
#             classes. Defaults to None or __class__.__name__.lower().
#         gpu (Optional[bool]): whether to use GPU cores, when possible, to
#             parallelize operations (True) or to solely use CPU cores (False).
#             Defaults to False.

#     """
#     name: Optional[str] = None
#     gpu: Optional[bool] = False

#     """ Private Methods """

#     def _apply_gpu(self, process: Callable, data: object, **kwargs) -> object:
#         """

#         """
#         try:
#             return process(data, **kwargs)
#         except TypeError:
#             return self._apply_cpu(process = process, data = data, **kwargs)

#     def _apply_cpu(self, process: Callable, data: object, **kwargs) -> object:
#         """

#         """
#         results = []
#         arguments = data
#         arguments.update(kwargs)
#         with mp.Pool() as pool:
#             results.append(pool.starmap(method, arguments))
#         pool.close()
#         return results

#     """ Core sourdough Methods """

#     def apply(self, process: Callable, data: object, **kwargs) -> object:
#         """

#         """
#         if self.gpu:
#             return self._apply_gpu(process = process, data = data, **kwargs)
#         else:
#             return self._apply_cpu(process = process, data = data, **kwargs)