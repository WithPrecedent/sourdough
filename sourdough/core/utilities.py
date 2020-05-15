"""
.. module:: utilities
:synopsis: general functions and decorators for sourdough
:author: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import datetime
import functools
import inspect
import pathlib
import re
import time
import types
from typing import (
    Any, Callable, ClassVar, Dict, Iterable, List, Optional, Tuple, Union)

import more_itertools
import numpy as np
import pandas as pd


""" Functions """

def add_prefix(
        iterable: Union[Dict[str, Any], List],
        prefix: str) -> Union[Dict[str, Any], List]:
    """Adds prefix to each item in a list or keys in a dict.

    An underscore is automatically added after the string prefix.

    Arguments:
        iterable (list(str) or dict(str: any)): iterable to be modified.
        prefix (str): prefix to be added.

    Returns:
        list or dict with prefixes added.

    """
    try:
        return {prefix + '_' + k: v for k, v in iterable.items()}
    except TypeError:
        return [prefix + '_' + item for item in iterable]

def add_suffix(
        iterable: Union[Dict[str, Any], List],
        suffix: str) -> Union[Dict[str, Any], List]:
    """Adds suffix to each item in a list or keys in a dict.

    An underscore is automatically added after the string suffix.

    Arguments:
        iterable (list(str) or dict(str: any)): iterable to be modified.
        suffix (str): suffix to be added.

    Returns:
        list or dict with suffixes added.

    """
    try:
        return {k + '_' + suffix: v for k, v in iterable.items()}
    except TypeError:
        return [item + '_' + suffix for item in iterable]

def datetime_string(prefix: Optional[str] = None) -> str:
    """Creates a string from current date and time.

    Returns:
        str with current date and time in Y/M/D/H/M format.

    """
    if prefix is None:
        prefix = ''
    time_string = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
    return f'{prefix}_{time_string}'

def deduplicate(
    iterable: Union[List, pd.DataFrame, pd.Series]) -> (
        Union[List, pd.DataFrame, pd.Series]):
    """Deduplicates list, pandas DataFrame, or pandas Series.

    Arguments:
        iterable (list, DataFrame, or Series): iterable to have duplicate
            entries removed.

    Returns:
        iterable (list, DataFrame, or Series, same as passed type):
            iterable with duplicate entries removed.

    """
    try:
        return list(more_itertools.unique_everseen(iterable))
    except TypeError:
        return iterable.drop_duplicates(inplace = True)

def is_nested(dictionary: Dict[Any, Any]) -> bool:
    """Returns if passed 'contents' is nested at least one-level.

    Arguments:
        dictionary (dict): dict to be tested.

    Returns:
        bool: indicating whether any value in the 'contents' is also a
            dict (meaning that 'contents' is nested).

    """
    return any(isinstance(v, dict) for v in dictionary.values())

def listify(
        variable: Any,
        default_null: Optional[bool]  = False,
        default_empty: Optional[bool] = False) -> Union[list, None]:
    """Stores passed variable as a list (if not already a list).

    Arguments:
        variable (any): variable to be transformed into a list to allow proper
            iteration.
        default_null (boolean): whether to return None (True) or ['none']
            (False).

    Returns:
        variable (list): either the original list, a string converted to a
            list, None, or a list containing 'none' as its only item.

    """
    if not variable or variable in ['none', ['none']]:
        if default_null:
            return None
        elif default_empty:
            return []
        else:
            return ['none']
    elif isinstance(variable, list):
        return variable
    else:
        return [variable]

def numify(variable: str) -> Union[int, float, str]:
    """Attempts to convert 'variable' to a numeric type.

    Arguments:
        variable (str): variable to be converted.

    Returns
        variable (int, float, str) converted to numeric type, if possible.

    """
    try:
        return int(variable)
    except ValueError:
        try:
            return float(variable)
        except ValueError:
            return variable

def pathlibify(path: Union[str, pathlib.Path]) -> pathlib.Path:
    """Converts string 'path' to pathlib.pathlib.Path object.

    Arguments:
        path (Union[str, pathlib.Path]): either a string representation of a
            path or a pathlib.Path object.

    Returns:
        pathlib.Path object.

    Raises:
        TypeError if 'path' is neither a str or pathlib.Path type.

    """
    if isinstance(path, str):
        return pathlib.Path(path)
    elif isinstance(path, pathlib.Path):
        return path
    else:
        raise TypeError('path must be str or pathlib.Path type')

def propertify(
        instance: object,
        name: str,
        getter: Callable,
        setter: Optional[Callable],
        deleter: Optional[Callable]) -> object:
    """Adds 'name' property to 'instance' at runtime.

    Arguments:
        instance (object): instance to add a property to.
        name (str): name that the new property should be given.
        getter (Callable): getter method for the new property.
        setter (Optional[Callable]): setter method for the new property.
        deleter (Optional[Callable]): deleter method for the new property.

    Returns:
        object: with new 'name' property added.

    """
    def _bind_process(process: Callable, instance: object) -> Callable:
        """Binds 'process' to 'instance'.

        Arguments:
            process (Callable): function, method in 'instance' or method in
                another class instance.
            instance (object): class instance to bind 'process to'.

        Returns:
            Callable: appropriate process object.

        """
        if process.im_self is not None:
            if process.__name__ in instance.__dict__:
                return process
            else:
                setattr(instance, process.__name__, process)
                return getattr(instance, process.__name__)
        else:
            types.MethodType(process, instance, instance.__class__)
            return getattr(instance, process.__name__)

    def _property_not_implemented() -> NotImplemented:
        raise NotImplemented(f'property method is not implemented')

    if setter and deleter:
        setattr(instance, name, property(
            fget = _bind_process(process = getter, instance = instance),
            fset = _bind_process(process = setter, instance = instance),
            fdel = _bind_process(process = deleter, instance = instance)))
    elif setter:
        setattr(instance, name, property(
            fget = _bind_process(process = getter, instance = instance),
            fset = _bind_process(process = setter, instance = instance),
            fdel = _property_not_implemented))
    elif deleter:
        setattr(instance, name, property(
            fget = _bind_process(process = getter, instance = instance),
            fset = _property_not_implemented,
            fdel = _bind_process(process = deleter, instance = instance)))
    else:
        setattr(instance, name, property(
            fget = _bind_process(process = getter, instance = instance)),
            fset = _property_not_implemented,
            fdel = _property_not_implemented)
    return instance

def snakify(variable: str) -> str:
    """Converts a capitalized word name to snake case.

    Arguments:
        variable (str): string to convert.

    Returns:
        str: 'variable' converted to snake case.

    """
    return re.sub(r'(?<!^)(?=[A-Z])', '_', variable).lower()

def stringify(
        variable: Union[str, List],
        default_null: Optional[bool] = False,
        default_empty: Optional[bool] = False) -> str:
    """Converts one item list to a string (if not already a string).

    Arguments:
        variable (str, list): variable to be transformed into a string.
        default_null (boolean): whether to return None (True) or ['none']
            (False).

    Returns:
        variable (str): either the original str, a string pulled from a
            one-item list, or the original list.

    """
    if variable is None:
        if default_null:
            return None
        elif default_empty:
            return []
        else:
            return ['none']
    elif isinstance(variable, str):
        return variable
    else:
        try:
            return variable[0]
        except TypeError:
            return variable

def subsetify(
    dictionary: Dict[Any, Any],
    subset: Union[Any, List[Any]]) -> Dict[Any, Any]:
    """Returns a subset of a dictionary.

    The returned subset is a dictionary with keys in 'subset'.

    Arguments:
        dictionary (Dict[Any, Any]): dict to be subsetted.
        subset (Union[Any, List[Any]]): key(s) to get key/value pairs from
            'dictionary'.

    Returns:
        Dict[Any, Any]: with only keys in 'subset'

    """
    return {key: dictionary[key] for key in listify(subset)}

def typify(variable: str) -> Union[List, int, float, bool, str]:
    """Converts stingsr to appropriate, supported datatypes.

    The method converts strings to list (if ', ' is present), int, float,
    or bool datatypes based upon the content of the string. If no
    alternative datatype is found, the variable is returned in its original
    form.

    Arguments:
        variable (str): string to be converted to appropriate datatype.

    Returns:
        variable (str, list, int, float, or bool): converted variable.

    """
    if not isinstance(variable, str):
        return variable
    try:
        return int(variable)
    except ValueError:
        try:
            return float(variable)
        except ValueError:
            if variable.lower() in ['true', 'yes']:
                return True
            elif variable.lower() in ['false', 'no']:
                return False
            elif ', ' in variable:
                variable = variable.split(', ')
                return [numify(item) for item in variable]
            else:
                return variable

""" Decorators """

def simple_timer(process: Optional[str] = None) -> Callable:
    """Decorator for computing the length of time a process takes.

    Arguments:
        process (Optional[str]): name of class or method to be used in the
            output describing time elapsed.

    """
    if not process:
        if isinstance(process, types.FunctionType):
            process = process.__class__.__name__
        else:
            process = process.__class__.__name__
    def shell_timer(_function):
        def decorated(*args, **kwargs):
            def convert_time(seconds: int) -> tuple(int, int, int):
                minutes, seconds = divmod(seconds, 60)
                hours, minutes = divmod(minutes, 60)
                return hours, minutes, seconds
            implement_time = time.time()
            result = _function(*args, **kwargs)
            total_time = time.time() - implement_time
            h, m, s = convert_time(total_time)
            print(f'{process} completed in %d:%02d:%02d' % (h, m, s))
            return result
        return decorated
    return shell_timer
