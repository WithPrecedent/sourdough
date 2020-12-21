"""
settings: loads and/or stores configuration options for sourdough and projects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Settings (Lexicon): stores configuration settings after either loading them
        from disk or by the passed arguments.

"""
from __future__ import annotations
import configparser
import dataclasses
import importlib.util
import json
import pathlib
import toml
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)
import sourdough


@dataclasses.dataclass
class Options(object):
    """[summary]

    Args:
        
    """
    projects: Mapping[str, Type] = sourdough.types.Catalog()
    creators: Mapping[str, Type] = sourdough.types.Catalog()
    products: Mapping[str, Type] = sourdough.types.Catalog()
    components: Mapping[str, Type] = sourdough.types.Catalog()
    instances: Mapping[str, object] = sourdough.types.Catalog()
    algorithms: Mapping[str, Type] = sourdough.types.Catalog()
    criteria: Mapping[str, Callable] = sourdough.types.Catalog(
        always_return_list= True)

options = Options()


@dataclasses.dataclass
class Rules(object):
    """
    """
    options: Options = Options()
    skip_sections: Sequence[str] = dataclasses.field(
        default_factory = lambda: ['general', 'files'])
    skip_suffixes: Sequence[str] = dataclasses.field(
        default_factory = lambda: ['parameters'])
    special_section_suffixes: Sequence[str] = dataclasses.field(
        default_factory = lambda: ['design'])
    default_design: str = 'pipeline'


    """ Properties """
    
    @property
    def component_suffixes(self) -> Tuple[str]: 
        return tuple(k + 's' for k in self.options.components.keys()) 

rules = Rules(options = options)


@dataclasses.dataclass
class Bases(sourdough.quirks.Loader):
    """Base classes for a sourdough project.
    
    Args:
        settings (Union[str, Type]): the configuration class to use in a 
            sourdough project. Defaults to 'sourdough.Settings'.
        clerk (Union[str, Type]): the file clerk class to use in a sourdough 
            project. Defaults to 'sourdough.Clerk'.   
        creator (Union[str, Type]): the product/builder class to use in a 
            sourdough project. Defaults to 'sourdough.Creator'.    
        product (Union[str, Type]): the product output class to use in a 
            sourdough project. Defaults to 'sourdough.Product'. 
        component (Union[str, Type]): the node class to use in a sourdough 
            project. Defaults to 'sourdough.Component'. 
        workflow (Union[str, Type]): the workflow to use in a sourdough 
            project. Defaults to 'sourdough.products.Workflow'.      
            
    """
    settings: Union[str, Type] = 'sourdough.Settings'
    clerk: Union[str, Type] = 'sourdough.Clerk'
    creator: Union[str, Type] = 'sourdough.Creator'
    product: Union[str, Type] = 'sourdough.Product'
    component: Union[str, Type] = 'sourdough.Component'
    workflow: Union[str, Type] = 'sourdough.products.Workflow'

bases = Bases()  


default_settings: Mapping[str, Any] = {
    'general': {
        'verbose': False,
        'parallelize': True,
        'conserve_memery': False},
    'files': {
        'source_format': 'csv',
        'interim_format': 'csv',
        'final_format': 'csv',
        'file_encoding': 'windows-1252'}}


@dataclasses.dataclass
class Settings(sourdough.types.Lexicon):
    """Loads and Stores configuration settings.

    To create Settings instance, a user can pass a:
        1) file path to a compatible file type;
        2) string containing a a file path to a compatible file type;
                                or,
        3) 2-level nested dict.

    If 'contents' is imported from a file, 'Settings' creates a dict and can 
    convert the dict values to appropriate datatypes. 
    
    Currently, supported file types are: ini, json, toml, and python.

    If 'infer_types' is set to True (the default option), str dict values are 
    automatically converted to appropriate datatypes (str, list, float, bool, 
    and int are currently supported).

    Because Settings uses ConfigParser for .ini files, by default it stores a 
    2-level dict. The desire for accessibility and simplicity dictated this 
    limitation. A greater number of levels can be stored by storing dicts in 
    values of Settings or importing configuration options from a different
    supported file format.

    Args:
        contents (Union[str, pathlib.Path, Mapping[Any, Mapping[Any, Any]]]): a 
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
        Mapping[Any, Mapping[Any, Any]]] = dataclasses.field(
            default_factory = dict)
    infer_types: bool = True
    defaults: ClassVar[Mapping[str, Any]] = default_settings

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent and/or mixin initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass
        self._initial_validation()
        # Infers types for values in 'contents', if the 'infer_types' option is 
        # selected.
        if self.infer_types:
            self.contents = self._infer_types(contents = self.contents)
        # Adds default settings as backup settings to 'contents'.
        self.contents = self._add_defaults(contents = self.contents)

    """ Public Methods """

    def validate(self, 
            contents: Union[
                str,
                pathlib.Path,
                Mapping[Any, Any]]) -> Mapping[Any, Any]:
        """Validates 'contents' or converts 'contents' to the proper type.

        Args:
            contents (Union[str, pathlib.Path, Mapping[Any, Any]]): a dict, a
                str file path to a file with settings, or a pathlib Path to a 
                file with settings.

        Raises:
            TypeError: if 'contents' is neither a str, dict, or Path.

        Returns:
            Mapping[Any, Any]: 'contents' in its proper form.

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

    def add(self, 
            section: str, 
            contents: Mapping[Any, Any]) -> None:
        """Adds 'settings' to 'contents'.

        Args:
            section (str): name of section to add 'contents' to.
            contents (Mapping[Any, Any]): a dict to store in 'section'.

        """
        try:
            self[section].update(self.validate(contents = contents))
        except KeyError:
            self[section] = self.validate(contents = contents)
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

    """ Dunder Methods """

    def __setitem__(self, key: str, value: Mapping[Any, Any]) -> None:
        """Creates new key/value pair(s) in a section of the active dictionary.

        Args:
            key (str): name of a section in the active dictionary.
            value (MutableMapping): the dictionary to be placed in that section.

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

    def __missing__(self, key: str) -> 'Settings':
        """Automatically creates a nested Settings if 'key' is missing.
        
        This method implements autovivification.
        
        Args:
            key (str): name of key sought in this instance.
            
        Returns:
            Settings: a new, nested settings at 'key'.
        
        """
        value = self[key] = type(self)(infer_types = False)
        return value
        
    """ Private Methods """

    def _initial_validation(self) -> None:
        """Validates passed 'contents' on class initialization."""
        self.contents = self.validate(contents = self.contents)
        return self

    def _load_from_ini(self, file_path: str) -> Mapping[Any, Any]:
        """Returns settings dictionary from an .ini file.

        Args:
            file_path (str): path to configparser-compatible .ini file.

        Returns:
            Mapping[Any, Any] of contents.

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

    def _load_from_json(self, file_path: str) -> Mapping[Any, Any]:
        """Returns settings dictionary from an .json file.

        Args:
            file_path (str): path to configparser-compatible .json file.

        Returns:
            Mapping[Any, Any] of contents.

        Raises:
            FileNotFoundError: if the file_path does not correspond to a file.

        """
        try:
            with open(pathlib.Path(file_path)) as settings_file:
                settings = json.load(settings_file)
            return settings
        except FileNotFoundError:
            raise FileNotFoundError(f'settings file {file_path} not found')

    def _load_from_py(self, file_path: str) -> Mapping[Any, Any]:
        """Returns a settings dictionary from a .py file.

        Args:
            file_path (str): path to python module with '__dict__' dict
                defined.

        Returns:
            Mapping[Any, Any] of contents.

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

    def _load_from_toml(self, file_path: str) -> Mapping[Any, Any]:
        """Returns settings dictionary from a .toml file.

        Args:
            file_path (str): path to configparser-compatible .toml file.

        Returns:
            Mapping[Any, Any] of contents.

        Raises:
            FileNotFoundError: if the file_path does not correspond to a file.

        """
        try:
            return toml.load(file_path)
        except FileNotFoundError:
            raise FileNotFoundError(f'settings file {file_path} not found')

    def _infer_types(self,
            contents: Mapping[Any, Mapping[Any, Any]]) -> Mapping[
                str, Mapping[Any, Any]]:
        """Converts stored values to appropriate datatypes.

        Args:
            contents (Mapping[Any, Mapping[Any, Any]]): a nested contents dict
                to review.

        Returns:
            Mapping[Any, Mapping[Any, Any]]: with the nested values converted to 
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
            contents: Mapping[Any, Mapping[Any, Any]]) -> Mapping[
                str, Mapping[Any, Any]]:
        """Creates a backup set of mappings for sourdough settings lookup.


        Args:
            contents (MutableMapping[Any, Mapping[Any, Any]]): a nested contents 
                dict to add defaults to.

        Returns:
            Mapping[Any, Mapping[Any, Any]]: with stored defaults added.

        """
        new_contents = self.defaults
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
