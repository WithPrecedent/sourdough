"""
directors: classes controlling Creator subclasses
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:


"""
from __future__ import annotations
import abc
import copy
import dataclasses
import inspect
import itertools
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import sourdough


@dataclasses.dataclass
class Director(sourdough.types.Proxy, sourdough.types.Base, abc.ABC):
    """Directs actions of a stored Builder instance.

    Args:

    
    """
    contents: Any = None
    name: str = None
    builder: sourdough.project.Builder = None
    project: sourdough.Project = None
    library: ClassVar[sourdough.types.Library] = sourdough.types.Library()

    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def create(self, **kwargs) -> sourdough.types.Base:
        """Subclasses must provide their own methods."""
        pass
    


@dataclasses.dataclass
class Manager(sourdough.quirks.Element, sourdough.quirks.Validator, 
              Director):
    """Creates and executes portions of a workflow in a sourdough project.

    Args:
        library (ClassVar[Library]): related Library instance that will store
            subclasses and allow runtime construction and instancing of those
            stored subclasses.
    

    """
    contents: sourdough.project.Workflow = dataclasses.field(
        default_factory = sourdough.project.Workflow)
    name: str = None
    builder: sourdough.project.Creator = None
    project: sourdough.Project = None
    
    
    
    components: sourdough.types.Catalog = dataclasses.field(
        default_factory = sourdough.types.Catalog)
    workflows: sourdough.types.Catalog = dataclasses.field(
        default_factory = sourdough.types.Catalog)
    project: sourdough.Project = dataclasses.field(repr = False, default = None)
    bases: sourdough.project.Bases = dataclasses.field(
        repr = False, 
        default = None)
    validations: ClassVar[Sequence[str]] = ['bases', 'design', 'builder']
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
        self._validate_contents()
      
    """ Public Methods """
    
    def create(self, **kwargs) -> sourdough.project.Workflow:
        """Builds and stores an instance based on 'name' and 'kwargs'.

        Args:
            
        """
        first_workflow = True
        component_settings = self.settings.excludity(self.settings.skip)
        for name in component_settings.keys():
            if first_workflow:
                workflow = self.builder.create(name = name)
                first_workflow = False
            else:
                workflow.combine(self.builder.create(name = name))
        return workflow
    
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

    def _validate_design(self, design: str) -> str:
        """Forces 'design' and 'contains' to both be None or not None."""
        if design is not None and self.contains is None:
            design = None
        elif design is None and self.contains is not None:
            self.contains = None
        return design

    def _validate_builder(self, builder: Any) -> Creator:
        """"""
        return Creator(manager = self)
    
    def _validate_contents(self) -> None:
        """[summary]
             
        """
        processed = self._process_section(name = self.name)
        self._inject_section(item = self, processed = processed)
        self._process_subcomponents(
            parent = self.name, 
            base = self.contains,
            components = self.contents)
        return self
    
    def _process_section(self, name: str, parent: str = None) -> None:
        """[summary]

        Args:
            name (str): [description]
            parent (str): [description]

        Returns:
            [type]: [description]
        """
        suffixes = self.bases.component.library.suffixes
        if parent:
            try:
                section = self.project.settings[parent]
            except KeyError:
                section = self.project.settings[self.name]
        else:
            section = self.project.settings[name]
        components_keys = [k for k in section.keys() if k.endswith(suffixes)]
        try:
            contents_key = [k for k in components_keys if k.startswith(name)][0]
        except IndexError:
            contents_key = None
        if contents_key is None:
            contents = None
            contains = None
        else:
            contents = sourdough.tools.listify(section[contents_key])
            contains = contents_key.split('_')[-1][:-1]
        design = self._get_design(name = name)
        attributes = {
                k: v for k, v in section.items() if k not in components_keys}
        attributes = {
            k: v for k, v in attributes.items() if not k.endswith('_design')}
        return ProcessedSection(
            contents = contents, 
            design = design, 
            contains = contains, 
            attributes = attributes)
    
    def _inject_section(self, 
            item: object, 
            processed: ProcessedSection) -> object:
        """[summary]

        Args:
            item (object): [description]
            processed (ProcessedSection): [description]

        Returns:
            object: [description]
        """
        if processed.contents:
            if item.contents is None:
                item.contents = []
            if isinstance(processed.contents, list):
                item.contents.extend(processed.contents)
            else:
                item.contents.append(processed.contents)
            if processed.design:
                item.design = processed.design
            elif hasattr(item, 'design') and not item.design:
                item.design = self.project.settings['sourdough']['default_design']
            item.contains = processed.contains
            for key, value in processed.attributes.items():
                setattr(item, key, value)
        return item
    
    def _process_subcomponents(self, 
            parent: str, 
            base: str, 
            components: List[str]) -> None:
        """[summary]

        Args:
            parent (str): [description]
            components (List[str]): [description]
        """
        for name in components:
            if name in self.project.settings:
                processed = self._process_section(name = name)
            else:
                processed = self._process_section(name = name, parent = parent)
            if processed.design:
                keys = [name, processed.design, base]
            else:
                keys = [name, base]
            component = self.bases.component.library.borrow(name = keys)
            component = component(name = name)
            component = self._inject_section(
                item = component, 
                processed = processed)
            self.components[component.name] = component
            if component.contents:
                self._process_subcomponents(
                    parent = component.name,
                    base = component.contains,
                    components = component.contents)
        return self
    
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
