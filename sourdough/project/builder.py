"""
builder: produces workflows and their components
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:


"""
from __future__ import annotations
import copy
import dataclasses
import inspect
import itertools
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import sourdough


@dataclasses.dataclass
class ProcessedSection(object):
    
    contents: List[str]
    design: str
    contains: str
    attributes: Dict[str, Any]


@dataclasses.dataclass
class Creator(sourdough.types.Base):
    
    manager: Manager = dataclasses.field(repr = False, default = None)
    
    def create(self, 
            component: sourdough.project.Component,  
            workflow: sourdough.project.Workflow) -> sourdough.project.Workflow:
        """[summary]

        Args:
            manager (sourdough.project.Manager): [description]
            workflow (Workflow): [description]
            
        """
        workflow.add_node(node = component)
        if component.contents:
            if component.parallel:
                workflow = self._create_parallel(
                    contents = component.contents, 
                    workflow = workflow)
            else:
                workflow = self._create_serial(
                    contents = component.contents, 
                    workflow = workflow)
        return workflow
                
    """ Private Methods """
    
    def _create_parallel(self,
            contents: List[str], 
            workflow: sourdough.project.Workflow) -> sourdough.project.Workflow:
        """ """
        # Creates empy list of lists for all possible permutations to be stored.
        possible = []
        # Populates list of lists with different options.
        for item in contents:
            possible.append(self.manager.components[item].contents)
        # Computes Cartesian product of possible permutations.
        combos = list(map(list, itertools.product(*possible)))
        for combo in combos:
            workflow = self._create_serial(
                contents = combo, 
                workflow = workflow)
        return workflow
    
    def _create_serial(self,
            contents: List[str], 
            workflow: sourdough.project.Workflow) -> sourdough.project.Workflow:
        """ """
        previous = None
        for name in contents:
            if previous is not None:
                workflow.add_edge(start = previous, stop = name)
            previous = name
            subcomponent = self.manager.components[name]
            workflow = self.create(
                component = subcomponent, 
                workflow = workflow)
        return workflow    

  
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
    design: str = None
    contains: str = None
    creator: Creator = None
    components: sourdough.types.Catalog = dataclasses.field(
        default_factory = sourdough.types.Catalog)
    project: sourdough.Project = dataclasses.field(repr = False, default = None)
    bases: sourdough.project.Bases = dataclasses.field(
        repr = False, 
        default = None)
    validations: ClassVar[Sequence[str]] = ['bases', 'design', 'creator']
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
        design = self._get_design(name = self.name)
        manager_component = self.bases.component.library.borrow(name = design)(
            name = self.name,
            contents = self.contents)
        print('test manager workflow parallel', manager_component.parallel)
        print('test workflow before creator', manager_component)
        self.project.workflow = self.creator.create(
            component = manager_component, 
            workflow = self.project.workflow)
        print('test workflow after creator', self.project.workflow)
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

    def _validate_design(self, design: str) -> str:
        """Forces 'design' and 'contains' to both be None or not None."""
        if design is not None and self.contains is None:
            design = None
        elif design is None and self.contains is not None:
            self.contains = None
        return design

    def _validate_creator(self, creator: Any) -> Creator:
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
