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
import copy
import dataclasses
import inspect
import pathlib
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import sourdough

    
@dataclasses.dataclass
class Manager(sourdough.quirks.Element, sourdough.quirks.Validator, 
              sourdough.composites.Pipeline, sourdough.types.Base):
    """Creates and executes portions of a workflow in a sourdough project.

    Args:
        library (ClassVar[Library]): related Library instance that will store
            subclasses and allow runtime construction and instancing of those
            stored subclasses.
        
    """
    
    contents: Sequence[str] = dataclasses.field(default_factory = list)
    name: str = None
    project: sourdough.Project = dataclasses.field(repr = False, default = None)
    bases: sourdough.project.Bases = None
    validations: ClassVar[Sequence[str]] = ['bases', 'contents']
    library: ClassVar[sourdough.types.Library] = sourdough.types.Library()
    
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent and/or mixin initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass
        self.validate()
      
    """ Public Methods """
    
    def create(self, **kwargs) -> None:
        """Builds and stores an instance based on 'name' and 'kwargs'.

        Args:
            
        """
        return self
    
    """ Private Methods """

    def _validate_bases(self, bases: Union[
            Type[sourdough.project.Bases],
            sourdough.project.Bases]):
        """[summary]

        Args:
            bases (Union[ Type[sourdough.project.Bases], 
                sourdough.project.Bases]): [description]

        Raises:
            TypeError: [description]

        Returns:
            [type]: [description]
        """
        if isinstance(bases, sourdough.project.Bases):
            pass
        elif (inspect.isclass(bases) 
                and issubclass(bases, sourdough.project.Bases)):
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
        return self._validate_component_contents(
            name = self.name,
            contents = contents,
            instances = [])

    def _validate_component_contents(self, 
            name: str, 
            contents: Sequence[Union[
                sourdough.project.Component, 
                Type[sourdough.project.Component],
                str]],
            instances: List[sourdough.project.Component]) -> (
                Sequence[sourdough.project.Component]):
        """[summary]

        Args:
            name (str): [description]
            contents (Sequence[Union[ sourdough.project.Component, 
                Type[sourdough.project.Component], str]]): [description]

        Returns:
            Sequence[sourdough.project.Component]: [description]
            
        """
        print('test incoming contents', name, contents)
        if not contents:
            contents, base = self._get_components_from_settings(name = name)
        else:
            base = self.bases.component
        print('test after settings contents', contents, base)
        for component in contents:
            instance = self._validate_component(
                component = component,
                base = base)
            print('test instance', instance)
            if hasattr(instance, 'contents'):
                subinstances = self._validate_component_contents(
                    name = instance.name,
                    contents = instance.contents,
                    instances = instances)
                if subinstances:
                    instances.extend(subinstances)
            instances.append(instance)
        return instances
    
    def _get_components_from_settings(self, name: str) -> Tuple[List[str], str]:
        """[summary]

        Raises:
            ValueError: [description]
            ValueError: [description]

        Returns:
            List[str]: [description]
            
        """
        suffixes = self.bases.component.library.suffixes
        try:
            matches = [
                k for k in self.project.settings[name].keys() 
                if k.startswith(name) and k.endswith(suffixes)]
        except KeyError:
            matches = [
                k for k in self.project.settings[self.name].keys() 
                if k.startswith(name) and k.endswith(suffixes)] 
        if len(matches) > 1:
            raise ValueError(f'{name} must have only 1 set of components')
        elif len(matches) == 0:
            base = None
            components = []
        else:
            key = matches[0]
            base = key.split('_')[-1][:-1]
            try:
                components = sourdough.tools.listify(
                    self.project.settings[name][key])
                del self.project.settings[name][key]
            except KeyError:
                try:
                    components = sourdough.tools.listify(
                        self.project.settings[self.name][key])
                    del self.project.settings[name][key]
                except KeyError:
                    components = []
        return components, base
        
    def _validate_component(self, 
            component: Union[
                str, 
                sourdough.project.Component, 
                Type[sourdough.project.Component]], 
            base: str) -> object:
        """
        """
        if isinstance(component, str):
            name = copy.deepcopy(component)
            kwargs = {'name': name}
            design = self._get_design(name = component)
            if design is None:
                keys = [name, base]
            else:
                keys = [name, design, base]
            component = self.bases.component.library.borrow(name = keys)
            component = component(name = name)
        elif issubclass(component, self.bases.component):
            kwargs = {}
            name = sourdough.tools.snakify(component.__name__)
        elif isinstance(component, self.bases.component):
            kwargs = {}
            name = component.name
        else:
            raise TypeError('contents must be a list of str or Component')
        if inspect.isclass(component):
            parameters = self._get_components_from_settings(name = component)
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
            design = self.project.settings[name][f'{name}_design']
        except KeyError:
            try:
                design = self.project.settings[name][f'design']
            except KeyError:
                try:
                    design = self.project.settings[self.name][f'{name}_design']
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
            argument = self.project.settings[name][f'{name}_{parameter}']
        except KeyError:
            try:
                argument = self.project.settings[name][parameter]
            except KeyError:
                try:
                    argument = self.project.settings[self.name][
                        f'{name}_{parameter}']
                except KeyError:
                    argument = None
        return argument
