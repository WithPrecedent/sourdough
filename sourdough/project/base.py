"""
base: essential classes executeing sourdough's core to a project
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Bases
    Settings
    Filer
    Creator
    Component

"""
from __future__ import annotations
import abc
import dataclasses
import inspect
import pathlib
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import sourdough


@dataclasses.dataclass
class Settings(sourdough.resources.Configuration):
    """Loads and Stores configuration settings for a Project.

    Args:
        contents (Union[str, pathlib.Path, Mapping[str, Mapping[str, Any]]]): a 
            dict, a str file path to a file with settings, or a pathlib Path to
            a file with settings. Defaults to en empty dict.
        infer_types (bool): whether values in 'contents' are converted to other 
            datatypes (True) or left alone (False). If 'contents' was imported 
            from an .ini file, a False value will leave all values as strings. 
            Defaults to True.
        defaults (Mapping[str, Mapping[str]]): any default options that should
            be used when a user does not provide the corresponding options in 
            their configuration settings. Defaults to a dict with 'general'
            and 'files' section listed in the class annotations.
        skip (Sequence[str]): names of suffixes to skip when constructing nodes
            for a sourdough project.

    """
    contents: Union[str, pathlib.Path, Mapping[str, Mapping[str, Any]]] = (
        dataclasses.field(default_factory = dict))
    infer_types: bool = True
    defaults: Mapping[str, Mapping[str, Any]] = dataclasses.field(
        default_factory = lambda: {
            'general': {
                'verbose': False,
                'parallelize': True,
                'conserve_memery': False},
            'files': {
                'source_format': 'csv',
                'interim_format': 'csv',
                'final_format': 'csv',
                'file_encoding': 'windows-1252'}})
    skip: Sequence[str] = dataclasses.field(
        default_factory = lambda: ['general', 'files', 'filer', 'parameters'])


@dataclasses.dataclass
class Filer(sourdough.resources.Clerk):
    pass


@dataclasses.dataclass
class Manager(sourdough.quirks.Element, sourdough.quirks.Validator, 
              sourdough.foundry.Builder, sourdough.project.Component, 
              sourdough.types.Base):
    """Creates and executes portions of a workflow in a sourdough project.

    Args:
        library (ClassVar[Library]): related Library instance that will store
            subclasses and allow runtime construction and instancing of those
            stored subclasses.
        
    """
    
    contents: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    name: str = None
    project: Union[object, Type] = None
    bases: sourdough.interface.Bases = None
    iterations: Union[int, str] = 1
    criteria: str = None
    parallel: ClassVar[bool] = False 
    library: ClassVar[sourdough.types.Library] = sourdough.types.Library()
    validations: ClassVar[Sequence[str]] = dataclasses.field(
        default_factory = lambda: ['bases', 'contents']) 
    
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent and/or mixin initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass
      
    """ Public Methods """
    
    def create(self, name: str = None, **kwargs) -> None:
        """Builds and stores an instance based on 'name' and 'kwargs'.

        Args:
            name (str): name of a class stored in 'creator.base.registry.' If 
                there is no registry, 'name' is None, or 'name' doesn't match a 
                key in 'creator.base.registry', then an instance of 
                'creator.base' is instanced and stored.
            kwargs (Dict[Any, Any]): any specific parameters that a user wants
                passed to a class when an instance is created.
            
        """
        if name is not None:
            self.contents[name] = self.creators[name].create(name = name, 
                                                             **kwargs)
        else:
            for key, creator in self.creators.items():
                self.contents[key] = creator.create(name = key, **kwargs)
        return self
    
    """ Private Methods """

    def _validate_bases(self, bases: Union[
            Type[sourdough.interface.Bases],
            sourdough.interface.Bases]):
        """[summary]

        Args:
            bases (Union[ Type[sourdough.interface.Bases], 
                sourdough.interface.Bases]): [description]

        Raises:
            TypeError: [description]

        Returns:
            [type]: [description]
        """
        if isinstance(bases, sourdough.interface.Bases):
            pass
        elif inspect.issubclass(bases, sourdough.interface.Bases):
            bases = bases()
        elif bases is None:
            bases = self.project.bases
        else:
            raise TypeError('bases must be a Bases or None.')
        return bases 
            
    def _validate_contents(self, contents: Sequence[Union[
            sourdough.project.Component, 
            Type[sourdough.project.Component],
            str]]) -> Sequence[sourdough.project.Component]:
        """[summary]

        Args:
            contents (Sequence[Union[ sourdough.project.Component, 
                Type[sourdough.project.Component], str]]): [description]

        Returns:
            Sequence[sourdough.project.Component]: [description]
            
        """
        return self._validate_component_contents(name = self.name, 
                                                 contents = contents)

    def _validate_component_contents(self, name: str, 
            contents: Sequence[Union[
                sourdough.project.Component, 
                Type[sourdough.project.Component],
                str]]) -> Sequence[sourdough.project.Component]:
        """[summary]

        Args:
            name (str): [description]
            contents (Sequence[Union[ sourdough.project.Component, 
                Type[sourdough.project.Component], str]]): [description]

        Returns:
            Sequence[sourdough.project.Component]: [description]
            
        """
        if not contents:
            contents, base = self._get_components_from_settings(name = name)
        else:
            base = self.bases.component
        new_contents = []
        for component in contents:
            subcomponent = self._validate_component(
                component = component,
                base = base)
            if (isinstance(subcomponent, Iterable) 
                    and hasattr(subcomponent, 'contents')):
                subcomponent.contents = self._validate_component_contents(
                    name = subcomponent.name,
                    contents = subcomponent.contents)
            new_contents.append(subcomponent)
        return new_contents
    
    def _get_components_from_settings(self, name: str) -> Tuple[List[str], str]:
        """[summary]

        Raises:
            ValueError: [description]
            ValueError: [description]

        Returns:
            List[str]: [description]
            
        """
        suffixes = self.bases.component_suffixes
        try:
            matches = [
                k for k in self.settings[name].keys() 
                if k.startswith(name) and k.endswith(suffixes)]
        except KeyError:
            matches = [
                k for k in self.settings[self.name].keys() 
                if k.startswith(name) and k.endswith(suffixes)]    
        if len(matches) > 1:
            raise ValueError(f'{name} must have only 1 set of components')
        elif len(matches) == 0:
            raise ValueError(f'No components found for {name}')
        else:
            key = matches[0]
            base = key.split('_')[-1][:-1]
            try:
                components = sourdough.tools.listify(self.settings[name][key])
            except KeyError:
                try:
                    components = sourdough.tools.listify(
                        self.settings[self.name][key])
            return components, base
        
    def _validate_component(self, component: Union[str, object], 
                            base: str) -> object:
        """
        """
        if isinstance(component, str):
            kwargs = {'name': component}
            name = kwargs['name'] 
            design = self._get_design(name = component)
            if design is None:
                keys = [component, base]
            else:
                keys = [component, design, base]
            component = self.bases.component.borrow(name = keys)
            component = component(name = component)
        elif inspect.issubclass(component, self.bases.settings.component):
            kwargs = {}
            name = sourdough.tools.snakify(component.__name__)
        elif isinstance(component, self.bases.settings.component):
            kwargs = {}
            name = component.name
        else:
            raise TypeError('contents must be a list of str or Component')
        if inspect.isclass(component):
            parameters = self._get_components_from_settings(
                component = component)
            for parameter in parameters:
                try:
                    kwargs[parameter] = getattr(self, f'_get_{parameter}')()
                except AttributeError:
                    argument = self._get_generic_argument(
                        name = name,
                        parameter = parameter)
                    if argument is not None:
                        kwargs[parameter] = argument
            component = component(**kwargs)
        return component

    def _get_design(self, name: str) -> str:
        """
        """
        try:
            design = self.settings[name][f'{name}_design']
        except KeyError:
            try:
                design = self.settings[name][f'design']
            except KeyError:
                try:
                    design = self.settings[self.name][f'{name}_design']
                except KeyError:
                    design = None
        return design

    def _get_component_parameters(self, 
            component: Type[sourdough.types.Base], 
            skip: List[str] = lambda: ['name', 'contents']) -> Tuple[str]:
        """
        """
        parameters = list(component.__annotations__.keys())
        return tuple(i for i in parameters if i not in [skip])
    
    def _get_generic_argument(self, name: str, parameter: str) -> Any:
        """
        """
        try:
            argument = self.settings[name][f'{name}_{parameter}']
        except KeyError:
            try:
                argument = self.settings[name][parameter]
            except KeyError:
                try:
                    argument = self.settings[self.name][f'{name}_{parameter}']
                except KeyError:
                    argument = None
        return argument
             
    """ Dunder Methods """
    
    def __iter__(self) -> Iterable[Any]:
        """Returns iterable of 'creators'.

        Returns:
            Iterable: of 'creators'.

        """
        return iter(self.creators)
