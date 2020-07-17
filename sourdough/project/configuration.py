"""
.. module:: settings
:synopsis: base class for configuring sourdough managers
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
class Settings(sourdough.base.Settings):
    """Stores sourdough manager settings.



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
    this limitation. Settings overcomes this limitation by using the steps,
    steps, technqiues, and parameters structure described above.

    Args:
        contents (Union[str, pathlib.Path, Mapping[str, Any]]): a dict, a
            str file path to a file with settings, or a pathlib Path to a file
            with settings. Defaults to en empty dict.
        infer_types (bool]): whether values in 'contents' are converted
            to other datatypes (True) or left alone (False). If 'contents' was
            imported from an .ini file, a False value will leave all values as
            strings. Defaults to True.

    """
    contents: Union[
        str,
        pathlib.Path,
        Mapping[str, 
            Mapping[str, Any]]] = dataclasses.field(default_factory = dict)
    infer_types: bool = True

    """ Initialization Methods """

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

    def add(self, section: str, settings: Mapping[str, Any]) -> None:
        """Adds 'settings' to 'contents'.

        Args:
            section (str): name of section to add 'dictionary' to.
            settings (MutableMapping[str, Any]): dict to add to 'section'.

        """
        if section in self:
            self[section].update(settings)
        else:
            self[section] = settings
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
            sections.extend(sourdough.utilities.listify(additional))
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

    # def get_overview(self, name: str) -> 'sourdough.base.Overview':
    #     """Returns an Overview with 'contents' from this instance.

    #     Args:
    #         name (str): key to section to search for information to create an
    #             Overview instance.

    #     Returns:
    #         sourdough.base.Overview: with contents derived from the settings
    #             settings in this instance.

    #     """
    #     steps = sourdough.utilities.listify(
    #         self.contents[name][f'{name}_steps'])
    #     overview = sourdough.base.Overview(name = f'{name}_overview')
    #     for step in steps:
    #         overview = self._parse_step_section(
    #             name = step, 
    #             overview = overview)
    #     return overview

    # def create_manager(self, 
    #         name: str, 
    #         manager: 'sourdough.manager.Manager' = None) -> 'sourdough.manager.Manager':
    #     """Returns a single worker instance created from a 'contents' section.

    #     Args:
    #         name (str): name of step to create. It must correspond to a key in
    #             'contents'.
    #         manager (sourdough.manager.Manager): Manager class or subclass to store the
    #             information from 'contents' in. Defaults to None. If not
    #             passed, a generic Manager class is used.

    #     Returns:
    #         sourdough.manager.Manager: an instance or subclass instance with attributes 
    #             from a section of 'contents'
                
    #     """
    #     manager = manager or sourdough.manager.Manager
    #     instance = self.create_step(name = name, step = manager)
    #     new_contents = []
    #     for labor in instance.contents:
    #         new_contents.append(self._create_step)
            
    # def create_step(self, 
    #         name: str, 
    #         step: 'sourdough.manager.Worker' = None) -> 'sourdough.manager.Worker':
    #     """Returns a single worker instance created from a 'contents' section.

    #     Args:
    #         name (str): name of step to create. It must correspond to a key in
    #             'contents'.
    #         step (sourdough.manager.Worker): Worker class or subclass to store the
    #             information from 'contents' in. Defaults to None. If not
    #             passed, a generic Worker or Worker class is used based upon
    #             whether steps or steps are stored within the name section of
    #             'contents'.

    #     Returns:
    #         sourdough.manager.Worker: an instance or subclass instance with attributes 
    #             from a section of 'contents'
                
    #     """
    #     parameters = {'name': name}
    #     contents = []
    #     techniques = {}
    #     attributes = {}
    #     for key, value in self.contents[name].items():
    #         if key.endswith('_design'):
    #             parameters['design'] = value
    #         elif key.endswith('_steps'):
    #             step = step or sourdough.manager.Worker
    #             contents = sourdough.utilities.listify(value)
    #         elif key.endswith('_steps'):
    #             step = step or sourdough.manager.Worker
    #             contents = sourdough.utilities.listify(value)
    #         elif key.endswith('_techniques'):
    #             new_key = key.replace('_techniques', '')
    #             techniques[new_key] = sourdough.utilities.listify(value)
    #         else:
    #             attributes[key] = value
    #     if techniques:
    #         contents = sourdough.utilities.subsetify(
    #             dictionary = techniques,
    #             subset = contents)
    #     parameters['contents'] = contents
    #     instance = step(**parameters)
    #     for key, value in attributes.items():
    #         setattr(instance, key, value)
    #     return instance        
        
    # def get_parameters(self, step: str, technique: str) -> Mapping[str, Any]:
    #     """Returns 'parameters' dictionary appropriate to 'step' or 'technique'.

    #     The method firsts look for a match with 'technique' as a prefix (the
    #     more specific label) and then 'step' as a prefix' if there is no match
    #     for 'technique'.

    #     Args:
    #         step (str): name of 'step' for which parameters are sought.
    #         technique (str): name of 'technique' for which parameters are
    #             sought.

    #     Returns:
    #         Mapping[str, Any]: parameters dictionary stored in 'contents'.

    #     """
    #     try:
    #         return self[f'{technique}_parameters']
    #     except KeyError:
    #         try:
    #             return self[f'{step}_parameters']
    #         except KeyError:
    #             raise KeyError(
    #                 f'parameters for {step} and {technique} not found')

    """ Required ABC Methods """

    def __getitem__(self, key: str) -> Union[Mapping[str, Any], Any]:
        """Returns a section of the active dictionary or key within a section.

        Args:
            key (str): the name of the dictionary key for which the value is
                sought.

        Returns:
            Union[Mapping[str, Any], Any]: dict if 'key' matches a section in
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

    def __setitem__(self, key: str, value: Mapping[str, Any]) -> None:
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
            Mapping[str, Any]]) -> Mapping[str, Any]:
        """

        Args:
            contents (Union[str,pathlib.Path, Mapping[str, Any]]): [description]

        Raises:
            TypeError: [description]

        Returns:
            Mapping[str, Any]: [description]

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
            raise TypeError('contents must be a dict, Path, or str type')

    def _get_special(self, section: str, prefix: str, suffix: str) -> Sequence[str]:
        """Returns list of items in 'section' with key of f'{prefix}_{suffix}'.

        Args:
            section (str): name of section in 'contents' to search.
            prefix (str): prefix of key in section to search for.
            suffix (str): suffix of key in section to search for.

        Returns:
            Sequence[str]: stored in 'contents'.

        """
        return sourdough.utilities.listify(
            self.contents[section][f'{prefix}_{suffix}'])

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
            contents (Mapping[str, Mapping[str, Any]]): a nested contents dictionary
                to review.

        Returns:
            Mapping[str, Mapping[str, Any]]: with the nested values converted to the
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
            contents: Mapping[str, Mapping[str, Any]]) -> Mapping[str, Mapping[str, Any]]:
        """Creates a backup set of mappings for sourdough settings lookup.


        Args:
            contents (MutableMapping[str, Mapping[str, Any]]): a nested contents dictionary
                to review.

        Returns:
            Mapping[str, Mapping[str, Any]]: with stored defaults chained as a backup
                dictionary to 'contents'.

        """
        return collections.ChainMap(contents, sourdough.base.defaults.settings)

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

    # def _parse_step_section(self, 
    #         name: str,
    #         overview: 'sourdough.base.Overview') -> 'sourdough.base.Overview':
    #     """[summary]

    #     Returns:
    #         [type]: [description]
            
    #     """
    #     print('test settings name', name, overview)
    #     print('test settings contents', self.contents)
    #     overview[name] = {}
    #     section = self.contents[name]
    #     try:
    #         overview.contents[name]['steps'] = sourdough.utilities.listify(
    #             section[f'{name}_steps'])
    #     except KeyError:
    #         overview.contents[name]['steps'] = []
    #     try:
    #         overview.contents[name]['design'] = section[f'{name}_design']
    #     except KeyError:
    #         overview.contents[name]['design'] = None
    #     step_keys = [k for k in section.keys() if k.endswith('_techniques')]
    #     if len(step_keys) > 0:
    #         overview.contents[name]['stores_steps'] = True
    #         for step_key in step_keys:
    #             step_name = step_key.replace('_techniques', '')
    #             if step_name in overview.contents[name]['steps']:
    #                 techniques = sourdough.utilities.listify(section[step_key])
    #                 self.contents[name][step_name] = techniques
    #     else:
    #         overview.contents[name]['stores_steps'] = False
    #         for step in overview.contents[name]['steps']:
    #             overview = self._parse_step_section(
    #                 name = step,
    #                 overview = overview)
    #     return overview