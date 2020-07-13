"""
.. module:: settings
:synopsis: base class for configuring sourdough projects
:author: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import collections
import configparser
import dataclasses
import importlib
import json
import pathlib
import toml
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union

import sourdough


@dataclasses.dataclass
class Settings(sourdough.Corpus):
    """Stores sourdough project settings.

    To create Settings instance, a user can pass a:
        1) file path to a compatible file type;
        2) string containing a a file path to a compatible file type;
                                or,
        3) 2-level nested dict.

    If 'contents' is imported from a file, 'Settings' creates a dict and can 
    convert the dict values to appropriate datatypes. 
    
    Currently, supported file types are: ini, json, toml, and python.

    If 'infer_types' is set to True (the default option), str dict values
    are automatically converted to appropriate datatypes (str, list, float,
    bool, and int are currently supported)

    Because Settings uses ConfigParser for .ini files, it only allows 2-level 
    settings dictionaries. The desire for accessibility and simplicity dictated 
    this limitation. 

    Args:
        contents (Union[str, pathlib.Path, Mapping[str, Mapping[str, Any]]]): a 
            dict, a str file path to a file with settings, or a pathlib Path to
            a file with settings. Defaults to en empty dict.
        infer_types (bool]): whether values in 'contents' are converted
            to other datatypes (True) or left alone (False). If 'contents' was
            imported from an .ini file, a False value will leave all values as
            strings. Defaults to True.

    """
    contents: Union[
        str,
        pathlib.Path,
        Mapping[str, Mapping[str, Any]]] = dataclasses.field(
            default_factory = dict)
    infer_types: bool = True

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Validates 'contents' or converts it to a dict.
        super().__post_init__()
        # Infers types for values in 'contents', if the 'infer_types' option is 
        # selected.
        if self.infer_types:
            self.contents = self._infer_types(contents = self.contents)
        # Adds default settings as backup settings to 'contents'.
        self.contents = self._add_defaults(contents = self.contents)

    """ Public Methods """

    def add(self, 
            section: str, 
            contents: Union[
                str,
                pathlib.Path,
                Mapping[str, Mapping[str, Any]]]) -> None:
        """Adds 'settings' to 'contents'.

        Args:
            section (str): name of section to add 'contents' to.
            contents (Union[str, pathlib.Path, Mapping[str, Mapping[str, 
                Any]]]): a dict, a str file path to a file with settings, or a 
                pathlib Path to a file with settings.

        """
        super().add(section = section, contents = contents)
        return self

    def inject(self,
            instance: object,
            additional: Union[Sequence[str], str] = None,
            overwrite: bool = False) -> object:
        """Injects appropriate items into 'instance' from 'contents'.

        Args:
            instance (object): sourdough class instance to be modified.
            additional (Union[Sequence[str], str]]): other section(s) in 
                'contents' to inject into 'instance'. Defaults to None.
            overwrite (bool]): whether to overwrite a local attribute
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
        if additional:
            sections.extend(sourdough.tools.listify(additional))
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

    def validate(self, 
            contents: Union[
                str,
                pathlib.Path,
                Mapping[str, Any]]) -> Mapping[str, Any]:
        """Validates 'contents' or converts 'contents' to the proper type.

        Args:
            contents (Union[str, pathlib.Path, Mapping[str, Any]]): a dict, a
                str file path to a file with settings, or a pathlib Path to a 
                file with settings.

        Raises:
            TypeError: if 'contents' is neither a str, dict, or Path.

        Returns:
            Mapping[str, Any]: 'contents' in its proper form.

        """
        if isinstance(contents, Mapping):
            return contents
        elif isinstance(contents, (str, pathlib.Path)):
            extension = str(pathlib.Path(contents).suffix)[1:]
            load_method = getattr(self, f'_load_from_{extension}')
            return load_method(file_path = contents)
        elif contents is None:
            return {}
        else:
            raise TypeError(
                'contents must be None or a dict, Path, or str type')

    """ Private Methods """

    def _load_from_ini(self, file_path: str) -> Mapping[str, Any]:
        """Returns settings dictionary from an .ini file.

        Args:
            file_path (str): path to configparser-compatible .ini file.

        Returns:
            Mapping[str, Any] of contents.

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

    def _load_from_json(self, file_path: str) -> Mapping[str, Any]:
        """Returns settings dictionary from an .json file.

        Args:
            file_path (str): path to configparser-compatible .json file.

        Returns:
            Mapping[str, Any] of contents.

        Raises:
            FileNotFoundError: if the file_path does not correspond to a file.

        """
        try:
            with open(pathlib.Path(file_path)) as settings_file:
                settings = json.load(settings_file)
            return settings
        except FileNotFoundError:
            raise FileNotFoundError(f'settings file {file_path} not found')

    def _load_from_py(self, file_path: str) -> Mapping[str, Any]:
        """Returns a settings dictionary from a .py file.

        Args:
            file_path (str): path to python module with '__dict__' dict
                defined.

        Returns:
            Mapping[str, Any] of contents.

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

    def _load_from_toml(self, file_path: str) -> Mapping[str, Any]:
        """Returns settings dictionary from a .toml file.

        Args:
            file_path (str): path to configparser-compatible .toml file.

        Returns:
            Mapping[str, Any] of contents.

        Raises:
            FileNotFoundError: if the file_path does not correspond to a file.

        """
        try:
            return toml.load(file_path)
        except FileNotFoundError:
            raise FileNotFoundError(f'settings file {file_path} not found')

    def _infer_types(self,
            contents: Mapping[str, Mapping[str, Any]]) -> Mapping[
                str, Mapping[str, Any]]:
        """Converts stored values to appropriate datatypes.

        Args:
            contents (Mapping[str, Mapping[str, Any]]): a nested contents dict
                to review.

        Returns:
            Mapping[str, Mapping[str, Any]]: with the nested values converted to 
                the appropriate datatypes.

        """
        new_contents = {}
        for key, value in contents.items():
            if isinstance(value, dict):
                inner_bundle = {
                    inner_key: sourdough.tools.typify(inner_value)
                    for inner_key, inner_value in value.items()}
                new_contents[key] = inner_bundle
            else:
                new_contents[key] = sourdough.tools.typify(value)
        return new_contents

    def _add_defaults(self,
            contents: Mapping[str, Mapping[str, Any]]) -> Mapping[
                str, Mapping[str, Any]]:
        """Creates a backup set of mappings for sourdough settings lookup.


        Args:
            contents (MutableMapping[str, Mapping[str, Any]]): a nested contents 
                dict to add defaults to.

        Returns:
            Mapping[str, Mapping[str, Any]]: with stored defaults added.

        """
        new_contents = sourdough.defaults.settings
        new_contents.update(contents)
        return new_contents

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
            overwrite (bool]): whether to overwrite a local attribute
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
