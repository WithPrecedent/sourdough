"""
.. module:: configuration
:synopsis: project configuration made simple
:author: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import collections
import collections.abc
import configparser
import dataclasses
import importlib
import json
import pathlib
from typing import (
    Any, Callable, ClassVar, Dict, Iterable, List, Optional, Tuple, Union)

import sourdough


@dataclasses.dataclass
class Settings(collections.abc.MutableMapping):
    """Stores a sourdough project settings.

    To create Settings instance, a user can pass a:
        1) file path to a compatible file type;
        2) string containing a a file path to a compatible file type;
                                or,
        3) dictionary.

    If 'contents' is imported from a file, 'Settings' creates a dictionary
    and can convert the dictionary values to appropriate datatypes. Currently
    supported file types are: .ini and .py. With .py files, users are free to
    set any datatypes in the original python file.

    For .ini files, Settings uses python's ConfigParser. It seeks to cure
    some of the shortcomings of the base ConfigParser including:
        1) All values in ConfigParser are strings.
        2) It does not automatically create a regular dictionary or compatiable
            MutableMapping.
        3) Access methods are unforgiving across the nested structure.
        4) It uses OrderedDict (python 3.6+ dictionaries are fast and ordered).

    If 'infer_types' is set to True (the default option), the dictionary values
    are automatically converted to appropriate datatypes (str, list, float,
    bool, and int are currently supported)

    Because Settings uses ConfigParser for .ini files, it only allows
    1- or 2-level settings dictionaries. The desire for accessibility and
    simplicity dictated this limitation. Further levels of nesting are not
    prohibited, but the forgiving '__getitem__' method will only catch for
    matches in the first nested level.

    Args:
        contents (Optional[Union[str, pathlib.Path, Dict[str, Any]]): a dict, a
            str file path to a file with settings, or a pathlib Path to a file
            with settings. Defaults to an empty dictionary.
        infer_types (Optional[bool]): whether values in 'contents' are converted
            to other datatypes (True) or left alone (False). If 'contents' was
            imported from an .ini file, a False value will leave all values as
            strings. Defaults to True.

    """
    contents: Optional[Union[
        str,
        pathlib.Path,
        Dict[str, Any]]] = dataclasses.field(default_factory = dict)
    infer_types: Optional[bool] = True

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Configures 'contents' to proper type.
        self.contents = self._validate_contents(contents = self.contents)
        # Infers types for values in 'contents', if option selected.
        if self.infer_types:
            self.contents = self._infer_types(contents = self.contents)
        # Adds default settings as backup settings to 'contents'.
        self.contents = self._chain_defaults(contents = self.contents)
        return self

    """ Public Methods """

    def add(self, section: str, settings: Dict[str, Any]) -> None:
        """Adds 'settings' to 'contents'.

        Args:
            section (str): name of section to add 'dictionary' to.
            settings (Dict[str, Any]): dict to add to 'section'.

        """
        if section in self:
            self[section].update(settings)
        else:
            self[section] = settings
        return self

    def inject(self,
            instance: object,
            other_sections: Optional[Union[List[str], str]] = None,
            overwrite: Optional[bool] = False) -> object:
        """Injects appropriate items into 'instance' from 'contents'.

        Args:
            instance (object): sourdough class instance to be modified.
            other_sections (Optional[Union[List[str], str]]): other section(s)
                in 'contents' to inject into 'instance'. Defaults to None.
            overwrite (Optional[bool]): whether to overwrite a local attribute
                in 'instance' if there are values stored in that attribute.
                Defaults to False.

        Returns:
            instance (object): sourdough class instance with modifications made.

        """
        sections = ['general']
        try:
            sections.append(instance.name)
        except AttributeError:
            pass
        if other_sections:
            sections.extend(sourdough.utilities.listify(other_sections))
        for section in sections:
            try:
                for key, value in self.contents[section].items():
                    instance = self._inject(
                        instance = instance,
                        attribute = key,
                        value = value,
                        overwrite = overwrite)
            except KeyError:
                pass
        return instance

    def get_overview(self, name: str) -> 'sourdough.Overview':
        """Returns an Overview with 'contents' from this instance.

        Args:
            name (str): key to section to search for information to create an
                Overview instance.

        Returns:
            sourdough.Overview: with contents derived from the configuration
                settings in this instance.

        """
        workers = sourdough.utilities.listify(
            self.contents[name][f'{name}_workers'])
        overview = sourdough.Overview(name = f'{name}_overview')
        for worker in workers:
            overview = self._parse_worker_section(
                name = worker, 
                overview = overview)
        return overview

    def get_workers(self, section: str, name: str) -> List[str]:
        """Returns a list of names of workers.

        Args:
            section (str): name of section of 'contents' to search.
            name (str): prefix of key ending in '_workers'.

        Returns:
            List[str]: values stored in 'contents' converted to a list.

        """
        return self._get_special(
            section = section,
            prefix = name, 
            suffix = 'workers')

    def get_techniques(self, section: str, name: str) -> List[str]:
        """Returns a list of names of techniques.

        Args:
            section (str): name of section of 'contents' to search.
            name (str): prefix of key ending in '_techniques'.

        Returns:
            List[str]: values stored in 'contents' converted to a list.

        """
        return self._get_special(
            section = section,
            prefix = name, 
            suffix = 'techniques')
        
    def get_design(self, section: str, name: str) -> str:
        """Returns name of a structural design.

        Args:
            section (str): name of section of 'contents' to search.
            name (str): prefix of key ending in '_design'.

        Returns:
            str: name of 'design'.

        """
        return self.contents[section][f'{name}_design']
        
    def get_parameters(self, worker: str, technique: str) -> Dict[str, Any]:
        """Returns 'parameters' dictionary appropriate to 'worker' or 'technique'.

        The method firsts look for a match with 'technique' as a prefix (the
        more specific label) and then 'worker' as a prefix' if there is no match
        for 'technique'.

        Args:
            worker (str): name of 'worker' for which parameters are sought.
            technique (str): name of 'technique' for which parameters are
                sought.

        Returns:
            Dict[str, Any]: parameters dictionary stored in 'contents'.

        """
        try:
            return self[f'{technique}_parameters']
        except KeyError:
            try:
                return self[f'{worker}_parameters']
            except KeyError:
                raise KeyError(
                    f'parameters for {worker} and {technique} not found')

    """ Required ABC Methods """

    def __getitem__(self, key: str) -> Union[Dict[str, Any], Any]:
        """Returns a section of the active dictionary or key within a section.

        Args:
            key (str): the name of the dictionary key for which the value is
                sought.

        Returns:
            Union[Dict[str, Any], Any]: dict if 'key' matches a section in
                the active dictionary. If 'key' matches a key within a section,
                the value, which can be any of the supported datatypes is
                returned.

        """
        try:
            return self.contents[key]
        except KeyError:
            for section in list(self.contents.keys()):
                try:
                    return self.contents[section][key]
                except KeyError:
                    pass
            raise KeyError(f'{key} is not found in {self.__class__.__name__}')

    def __setitem__(self, key: str, value: Dict[str, Any]) -> None:
        """Creates new key/value pair(s) in a section of the active dictionary.

        Args:
            key (str): name of a section in the active dictionary.
            value (Dict): the dictionary to be placed in that section.

        Raises:
            TypeError if 'key' isn't a str or 'value' isn't a dict.

        """
        try:
            self.contents[key].update(value)
        except KeyError:
            try:
                self.contents[key] = value
            except TypeError:
                raise TypeError(
                    'key must be a str and value must be a dict type')
        return self

    def __delitem__(self, key: str) -> None:
        """Deletes 'key' entry in 'contents'.

        Args:
            key (str): name of key in 'contents'.

        """
        try:
            del self.contents[key]
        except KeyError:
            pass
        return self

    def __iter__(self) -> Iterable:
        """Returns iterable of 'contents'.

        Returns:
            Iterable stored in 'contents'.

        """
        return iter(self.contents)

    def __len__(self) -> int:
        """Returns length of 'contents'.

        Returns:
            Integer: length of 'contents'.

        """
        return len(self.contents)

    """ Private Methods """

    def _validate_contents(self, contents: Union[
            str,
            pathlib.Path,
            Dict[str, Any]]) -> Dict[str, Any]:
        """

        Args:
            contents (Union[str,pathlib.Path,Dict[str, Any]]): [description]

        Raises:
            TypeError: [description]

        Returns:
            Dict[str, Any]: [description]

        """
        if isinstance(contents, (dict, collections.abc.MutableMapping)):
            return contents
        elif isinstance(contents, (str, pathlib.Path)):
            extension = str(pathlib.Path(contents).suffix)[1:]
            load_method = getattr(self, f'_load_from_{extension}')
            return load_method(file_path = contents)
        elif contents is None:
            return {}
        else:
            raise TypeError('contents must be a dict, Path, or str type')

    def _get_special(self, section: str, prefix: str, suffix: str) -> List[str]:
        """Returns list of items in 'section' with key of f'{prefix}_{suffix}'.

        Args:
            section (str): name of section in 'contents' to search.
            prefix (str): prefix of key in section to search for.
            suffix (str): suffix of key in section to search for.

        Returns:
            List[str]: stored in 'contents'.

        """
        return sourdough.utilities.listify(
            self.contents[section][f'{prefix}_{suffix}'])

    def _load_from_ini(self, file_path: str) -> Dict[str, Any]:
        """Returns settings dictionary from an .ini file.

        Args:
            file_path (str): path to configparser-compatible .ini file.

        Returns:
            Dict[str, Any] of contents.

        Raises:
            FileNotFoundError: if the file_path does not correspond to a file.

        """
        try:
            contents = configparser.ConfigParser(dict_type = dict)
            contents.optionxform = lambda option: option
            contents.read(str(file_path))
            return dict(contents._sections)
        except FileNotFoundError:
            raise FileNotFoundError(f'settings file {file_path} not found')

    def _load_from_json(self, file_path: str) -> Dict[str, Any]:
        """Returns settings dictionary from an .json file.

        Args:
            file_path (str): path to configparser-compatible .json file.

        Returns:
            Dict[str, Any] of contents.

        Raises:
            FileNotFoundError: if the file_path does not correspond to a file.

        """
        try:
            with open(pathlib.Path(file_path)) as settings_file:
                settings = json.load(settings_file)
            return settings
        except FileNotFoundError:
            raise FileNotFoundError(f'settings file {file_path} not found')

    def _load_from_py(self, file_path: str) -> Dict[str, Any]:
        """Returns a settings dictionary from a .py file.

        Args:
            file_path (str): path to python module with '__dict__' dict
                defined.

        Returns:
            Dict[str, Any] of contents.

        Raises:
            FileNotFoundError: if the file_path does not correspond to a
                file.

        """
        # Disables type conversion if the source is a python file.
        self.infer_types = False
        try:
            file_path = pathlib.Path(file_path)
            import_path = importlib.util.spec_from_file_location(
                file_path.name,
                file_path)
            import_module = importlib.util.module_from_spec(import_path)
            import_path.loader.exec_module(import_module)
            return import_module.settings
        except FileNotFoundError:
            raise FileNotFoundError(f'settings file {file_path} not found')

    def _infer_types(self,
            contents: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Converts stored values to appropriate datatypes.

        Args:
            contents (Dict[str, Dict[str, Any]]): a nested contents dictionary
                to review.

        Returns:
            Dict[str, Dict[str, Any]]: with the nested values converted to the
                appropriate datatypes.

        """
        new_contents = {}
        for key, value in contents.items():
            if isinstance(value, dict):
                inner_bundle = {
                    inner_key: sourdough.utilities.typify(inner_value)
                    for inner_key, inner_value in value.items()}
                new_contents[key] = inner_bundle
            else:
                new_contents[key] = sourdough.utilities.typify(value)
        return new_contents

    def _chain_defaults(self,
            contents: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Creates a backup set of mappings for sourdough settings lookup.


        Args:
            contents (Dict[str, Dict[str, Any]]): a nested contents dictionary
                to review.

        Returns:
            Dict[str, Dict[str, Any]]: with stored defaults chained as a backup
                dictionary to 'contents'.

        """
        return collections.ChainMap(contents, sourdough.defaults.settings)

    def _inject(self,
            instance: object,
            attribute: str,
            value: Any,
            overwrite: bool) -> object:
        """Adds attribute to 'instance' based on conditions.

        Args:
            instance (object): sourdough class instance to be modified.
            attribute (str): name of attribute to inject.
            value (Any): value to assign to attribute.
            overwrite (Optional[bool]): whether to overwrite a local attribute
                in 'instance' if there are values stored in that attribute.
                Defaults to False.

        Returns:
            object: with attribute possibly injected.

        """
        if (not hasattr(instance, attribute)
                or not getattr(instance, attribute)
                or overwrite):
            setattr(instance, attribute, value)
        return instance

    def _parse_worker_section(self, 
            name: str,
            overview: 'sourdough.Overview') -> 'sourdough.Overview':
        """[summary]

        Returns:
            [type]: [description]
            
        """
        overview[name] = {}
        section = self.contents[name]
        try:
            overview.contents[name]['workers'] = sourdough.utilities.listify(
                section[f'{name}_workers'])
        except KeyError:
            overview.contents[name]['workers'] = []
        try:
            overview.contents[name]['design'] = section[f'{name}_design']
        except KeyError:
            overview.contents[name]['design'] = None
        task_keys = [k for k in section.keys() if k.endswith('_techniques')]
        if len(task_keys) > 0:
            overview.contents[name]['stores_tasks'] = True
            for task_key in task_keys:
                task_name = task_key.replace('_techniques', '')
                if task_name in overview.contents[name]['workers']:
                    techniques = sourdough.utilities.listify(section[task_key])
                    self.contents[name][task_name] = techniques
        else:
            overview.contents[name]['stores_tasks'] = False
            for worker in overview.contents[name]['workers']:
                overview = self._parse_worker_section(
                    name = worker,
                    overview = overview)
        return overview