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
from typing import Any, ClassVar, Iterable, Mapping, Sequence, Tuple, Union

import more_itertools
import numpy as np
import pandas as pd


""" Conversion/Validation Functions """

def classify(
        variable: Any, 
        options: Optional[Mapping[str, Any]] = None) -> object:
    """Converts 'variable' to a class, if possible.

    Args:
        variable (Any): variable to create a class out of.
        options (Optional[Mapping[str, Any]]): mapping containing str keys and
            classes as values. If 'variable' is a string, the method will seek
            to use it as a key in options. Defaults to None.

    Returns:
        object: a class object, if possible.
        
    """
    if inspect.isclass(variable):
        return variable
    else:
        if options:
            try:
                return options[variable]
            except (KeyError, TypeError):
                pass
        try:
            return variable.__class__
        except AttributeError:
            return variable
            
def instancify(
        variable: Any, 
        options: Optional[Mapping[str, Any]] = None,
        **kwargs) -> object:
    """Converts 'variable' to a class instance with 'kwargs' as parameters.

    Args:
        variable (Any): variable to create an instance out of.
        options (Optional[Mapping[str, Any]]): mapping containing str keys and
            classes as values. If 'variable' is a string, the method will seek
            to use it as a key in options. Defaults to None.

    Returns:
        object: a class instance, if possible.
        
    """
    if options:
        try:
            variable = options[variable]
        except (KeyError, TypeError):
            pass           
    if inspect.isclass(variable):
        return variable(**kwargs)
    else:
        return variable
            
def listify(
        variable: Any,
        default_value: Any = None) -> Sequence[Any]:
    """Returns passed variable as a list (if not already a list).

    Args:
        variable (any): variable to be transformed into a list to allow proper
            iteration.
        default_value (Any): the default value to return if 'variable' is None.
            Unfortunately, to indicate you want None to be the default value,
            you need to put 'None' in quotes. If not passed, 'default_value'
            is set to [].

    Returns:
        Sequence[Any]: a passed list, 'variable' converted to a list, or 
            'default_value'.

    """
    if variable is None:
        if default_value is None:
            return []
        elif default_value in ['None', 'none']:
            return None
        else:
            return default_value
    elif isinstance(variable, list):
        return variable
    else:
        return list(variable)

def numify(variable: str) -> Union[int, float, str]:
    """Attempts to convert 'variable' to a numeric type.
    
    If 'variable' cannot be converted to a numeric type, it is returned as is.

    Args:
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

    Args:
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

def snakify(variable: str) -> str:
    """Converts a capitalized word name to snake case.

    Args:
        variable (str): string to convert.

    Returns:
        str: 'variable' converted to snake case.

    """
    return re.sub(r'(?<!^)(?=[A-Z])', '_', variable).lower()

def stringify(
        variable: Union[str, Sequence],
        default_null: Optional[bool] = False,
        default_empty: Optional[bool] = False) -> str:
    """Converts one item list to a string (if not already a string).

    Args:
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
    dictionary: Mapping[Any, Any],
    subset: Union[Any, Sequence[Any]]) -> Mapping[Any, Any]:
    """Returns a subset of a dictionary.

    The returned subset is a dictionary with keys in 'subset'.

    Args:
        dictionary (MutableMapping[Any, Any]): dict to be subsetted.
        subset (Union[Any, Sequence[Any]]): key(s) to get key/value pairs from
            'dictionary'.

    Returns:
        Mapping[Any, Any]: with only keys in 'subset'

    """
    return {key: dictionary[key] for key in listify(subset)}

def typify(variable: str) -> Union[Sequence, int, float, bool, str]:
    """Converts stingsr to appropriate, supported datatypes.

    The method converts strings to list (if ', ' is present), int, float,
    or bool datatypes based upon the content of the string. If no
    alternative datatype is found, the variable is returned in its original
    form.

    Args:
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

""" Other Functions """

def add_prefix(
        iterable: Union[Mapping[str, Any], Sequence],
        prefix: str) -> Union[Mapping[str, Any], Sequence]:
    """Adds prefix to each item in a list or keys in a dict.

    An underscore is automatically added after the string prefix.

    Args:
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
        iterable: Union[Mapping[str, Any], Sequence],
        suffix: str) -> Union[Mapping[str, Any], Sequence]:
    """Adds suffix to each item in a list or keys in a dict.

    An underscore is automatically added after the string suffix.

    Args:
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
    iterable: Union[Sequence, pd.DataFrame, pd.Series]) -> (
        Union[Sequence, pd.DataFrame, pd.Series]):
    """Deduplicates list, pandas DataFrame, or pandas Series.

    Args:
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

def is_nested(dictionary: Mapping[Any, Any]) -> bool:
    """Returns if passed 'contents' is nested at least one-level.

    Args:
        dictionary (dict): dict to be tested.

    Returns:
        bool: indicating whether any value in the 'contents' is also a
            dict (meaning that 'contents' is nested).

    """
    return any(isinstance(v, dict) for v in dictionary.values())

def propertify(
        instance: object,
        name: str,
        getter: Callable,
        setter: Optional[Callable],
        deleter: Optional[Callable]) -> object:
    """Adds 'name' property to 'instance' at runtime.

    Args:
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

        Args:
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


""" Decorators """

def simple_timer(process: Optional[str] = None) -> Callable:
    """Decorator for computing the length of time a process takes.

    Args:
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
