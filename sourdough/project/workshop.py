"""
workflows:
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)
Contents:
    
"""
from __future__ import annotations
import copy
import dataclasses
import inspect
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import sourdough  


@dataclasses.dataclass
class Blueprint(object):
    """Stores information from a Settings section about a Workflow

    Args:
        
        
    """
    name: str = None
    parallel: bool = False
    components: Dict[str, List] = dataclasses.field(default_factory = dict)
    designs: Dict[str, str] = dataclasses.field(default_factory = dict)
    parameters: Dict[str, Any] = dataclasses.field(default_factory = dict)
    attributes: Dict[str, Any] = dataclasses.field(default_factory = dict)
    other: Dict[str, Any] = dataclasses.field(default_factory = dict)


@dataclasses.dataclass
class WorkflowCreator(sourdough.project.Creator):
    """Creates a sourdough object.
    
    Args:
        manager (Manager): associated project manager containing needed data
            for creating objects.
                       
    """
    manager: sourdough.project.Manager = dataclasses.field(
        repr = False, 
        default = None)

    """ Properties """
    
    @property
    def library(self) -> sourdough.types.Library:
        return self.manager.bases.workflow.library
     
    """ Required Public Methods """
    
    def create(self, node: str) -> sourdough.project.Workflow:
        """Creates a Creator instance from a section of a Settings instance.

        Args:
            node (str): starting node in the workflow being created.
                
        Returns:
            Workflow: derived from 'section'.
            
        """
        blueprint = self.parse_section(name = node)
        graph = self.create_graph(blueprint = blueprint)
        components = self.create_components(blueprint = blueprint)
        return sourdough.project.Workflow(
            contents = graph, 
            components = components)

    def parse_section(self, name: str) -> Blueprint:
        """[summary]

        Args:

        Returns:
            Blueprint
            
        """
        section = self.settings[name]
        blueprint = Blueprint(name = name)
        design = self._get_design(name = name, section = section)
        blueprint.designs[name] = design
        parameters = self._get_parameters(names = [name, design])
        for key, value in section.items():
            prefix, suffix = self._divide_key(key = key)
            if 'design' == suffix:
                pass
            elif suffix in self.library.suffixes:
                blueprint.bases.update(dict.fromkeys(value, suffix[:-1]))
                blueprint.components[prefix] = value 
            elif suffix in parameters:
                blueprint.parameters[suffix] = value 
            elif prefix == name:
                blueprint.attributes[suffix] = value
            elif suffix == 'steps':
                blueprint.parallel = True
            else:
                blueprint.other[key] = value
        return blueprint
   
    def create_components(self, 
            blueprint: Blueprint) -> Dict[str, sourdough.project.Component]:
        """
        """
        instances = {}
        design = blueprint.designs[blueprint.name]
        section_keys = [blueprint.name, design]
        section_component = self.library.borrow(name = [section_keys])
        instances[blueprint.name] = section_component(
            name = blueprint.name, 
            **blueprint.parameters)
        for value in blueprint.components.values():
            for item in value:
                if not item in self.settings:
                    subcomponent_keys = [item, blueprint.designs[item]]
                    subcomponent = self.library.borrow(name = subcomponent_keys)
                    instance = subcomponent(name = item)
                    instances[item] = self._inject_attributes(
                        component = instance, 
                        blueprint = blueprint)
        return instances

    def create_graph(self, 
            blueprint: Blueprint) -> Dict[str, List[str]]:
        """[summary]

        Args:
            blueprint (Blueprint): [description]

        Returns:
            Dict[str, List[str]]: [description]
            
        """
        if blueprint.parallel:
            graph = self._create_parallel_graph(blueprint = blueprint)
        else:
            graph = self._create_serial_graph(blueprint = blueprint)
        return graph
                     
    """ Private Methods """

    def _get_design(self, name: str, section: Mapping[str, Any]) -> str:
        """
        """
        try:
            design = section[f'{name}_design']
        except KeyError:
            try:
                design = section[f'design']
            except KeyError:
                try:
                    design = self.settings['sourdough'][f'default_design']
                except KeyError:
                    design = None
        return design

    def _get_parameters(self, 
            names: List[str], 
            skip: List[str] = lambda: [
                'name', 'contents', 'design']) -> Tuple[str]:
        """
        """
        component = self.library.borrow(name = names)
        parameters = list(component.__annotations__.keys())
        return tuple(i for i in parameters if i not in [skip])

    def _divide_key(self, key: str, divider: str = None) -> Tuple[str, str]:
        """[summary]

        Args:
            key (str): [description]

        Returns:
            
            Tuple[str, str]: [description]
            
        """
        if divider is None:
            divider = '_'
        if divider in key:
            suffix = key.split(divider)[-1]
            prefix = key[:-len(suffix) - 1]
        else:
            prefix = suffix = key
        return prefix, suffix

    def create_parallel_graph(self,
                              blueprint: Blueprint) -> Dict[str, List[str]]:
        """Creates a Creator instance from a section of a Settings instance.

        Args:
            section (Mapping[str, Any]): section of a Settings instance to
                use to create a Creator.
                
        Returns:
            Creator: derived from 'section'
            
        """
        graph = sourdough.composites.Graph()
        steps = blueprint.components[blueprint.name]
        possible = [blueprint.components[s] for s in steps]
        # Computes Cartesian product of possible paths.
        permutations = list(map(list, itertools.product(*possible)))
        paths = [p + blueprint.designs[blueprint.name] for p in permutations]
        for path in paths:
            graph = self._add_plan(
                contents = path, 
                blueprint = blueprint, 
                graph = graph)
        return graph

    def _create_serial_graph(self, blueprint: Blueprint) -> Dict[str, List[str]]:
        """[summary]

        Args:
            blueprint (Blueprint): [description]

        Returns:
            Dict[str, List[str]]: [description]
            
        """
        graph = sourdough.composites.Graph()
        graph = self._add_plan(
            contents = blueprint.contents[blueprint.name],
            blueprint = blueprint,
            graph = graph)
        return graph

    def _add_plan(self, 
            contents: List[str], 
            blueprint: Blueprint,
            graph: sourdough.composites.Graph) -> sourdough.composites.Graph:
        """[summary]

        Args:
            contents (List[str]): [description]
            blueprint (Blueprint): [description]
            graph (sourdough.composites.Graph): [description]

        Returns:
            sourdough.composites.Graph: [description]
            
        """
        for item in contents:
            try:
                subcontents = blueprint.components[item]
                graph = self._add_plan(
                    contents = subcontents,
                    blueprint = blueprint,
                    graph = graph)
            except KeyError:
                graph.extend(contents)
        return graph
      
    def _inject_attributes(self, 
            component: sourdough.project.Component, 
            blueprint: Blueprint) -> sourdough.project.Component:
        """[summary]

        Args:
            component (sourdough.project.Component): [description]
            blueprint (Blueprint): [description]

        Returns:
            sourdough.project.Component: [description]
        """
        for key, value in blueprint.attributes.items():
            setattr(component, key, value)
        return component


@dataclasses.dataclass
class WorkflowManager(sourdough.quirks.Validator, sourdough.project.Manager):
    """Creates and executes portions of a workflow in a sourdough project.

    Args:
        library (ClassVar[Library]): related Library instance that will store
            subclasses and allow runtime construction and instancing of those
            stored subclasses.

    """
    name: str = None
    creator: sourdough.project.Creator = None
    project: sourdough.Project = dataclasses.field(repr = False, default = None)
    bases: sourdough.project.Bases = dataclasses.field(
        repr = False, 
        default = None)
    validations: ClassVar[Sequence[str]] = ['bases', 'creator']
    
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
    
    def create(self, **kwargs) -> sourdough.project.Workflow:
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
        if self.bases is None:
            self.bases = self.project.bases
        elif isinstance(bases, sourdough.project.Bases):
            pass
        elif (inspect.isclass(bases) 
                and issubclass(bases, sourdough.project.Bases)):
            bases = bases()
        else:
            raise TypeError('bases must be a Bases or None.')
        return bases 

    def _validate_creator(self, 
            creator: Union[str, WorkflowCreator]) -> WorkflowCreator:
        """"""
        if isinstance(creator, str):
            creator = self.bases.creator.borrow(name = 'workflow')
        elif isinstance(creator, WorkflowCreator):
            creator.manager = self
        elif (inspect.isclass(creator) and issubclass(creator, WorkflowCreator):
            creator = creator(manager = self)
        return creator


  
@dataclasses.dataclass    
class Parameters(sourdough.types.Lexicon):
    """
    """
    contents: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    name: str = None
    base: Union[Type, str] = None
    required: Sequence[str] = dataclasses.field(default_factory = list)
    runtime: Mapping[str, str] = dataclasses.field(default_factory = dict)
    selected: Sequence[str] = dataclasses.field(default_factory = list)
    default: ClassVar[Mapping[str, Any]] = {}
    
    """ Public Methods """
    
    def create(self, builder: sourdough.project.Creator, **kwargs) -> None:
        """[summary]

        Args:
            builder (sourdough.project.Creator): [description]

        """
        if not kwargs:
            kwargs = self.default
        for kind in ['settings', 'required', 'runtime', 'selected']:
            kwargs = getattr(self, f'_get_{kind}')(builder = builder, **kwargs)
        self.contents = kwargs
        return self
    
    """ Private Methods """
    
    def _get_settings(self, builder: sourdough.project.Creator, 
                      **kwargs) -> Dict[str, Any]:
        """[summary]

        Args:
            builder (sourdough.project.Creator): [description]

        Returns:
            Dict[str, Any]: [description]
            
        """
        try:
            kwargs.update(builder.settings[f'{self.name}_parameters'])
        except KeyError:
            pass
        return kwargs
    
    def _get_required(self, builder: sourdough.project.Creator, 
                      **kwargs) -> Dict[str, Any]:
        """[summary]

        Args:
            builder (sourdough.project.Creator): [description]

        Returns:
            Dict[str, Any]: [description]
            
        """
        for item in self.required:
            if item not in kwargs:
                kwargs[item] = self.default[item]
        return kwargs
    
    def _get_runtime(self, builder: sourdough.project.Creator, 
                      **kwargs) -> Dict[str, Any]:
        """[summary]

        Args:
            builder (sourdough.project.Creator): [description]

        Returns:
            Dict[str, Any]: [description]
            
        """
        for parameter, attribute in self.runtime.items():
            try:
                kwargs[parameter] = getattr(builder, attribute)
            except AttributeError:
                pass
        return kwargs

    def _get_selected(self, builder: sourdough.project.Creator, 
                      **kwargs) -> Dict[str, Any]:
        """[summary]

        Args:
            builder (sourdough.project.Creator): [description]

        Returns:
            Dict[str, Any]: [description]
            
        """
        if self.selected:
            kwargs = {k: kwargs[k] for k in self.selected}
        return kwargs
        