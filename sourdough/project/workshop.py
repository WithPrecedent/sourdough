"""
workshop:
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
import more_itertools
import multiprocessing
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


@dataclasses.dataclass
class Builder(sourdough.types.Base, abc.ABC):
    """Creates a sourdough object.

    Args:
        library (ClassVar[Library]): related Library instance that will store
            subclasses and allow runtime construction and instancing of those
            stored subclasses.
                       
    """
    library: ClassVar[sourdough.types.Library] = sourdough.types.Library()
    
    """ Initialization Methods """
    
    def __init_subclass__(cls, **kwargs):
        """Adds 'cls' to 'library' if it is a concrete class."""
        super().__init_subclass__(**kwargs)
        # Creates 'library' class attribute if it doesn't exist.
        if not hasattr(cls, 'library'):  
            cls.library = sourdough.types.Library()
        if not abc.ABC in cls.__bases__:
            key = sourdough.tools.snakify(cls.__name__)
            # Removes '_builder' from class name so that the key is consistent
            # with the key name for the class being constructed.
            try:
                key.replace('_builder', '')
            except ValueError:
                pass
            cls.library[key] = cls
                          
    """ Required Subclass Class Methods """
    
    @abc.abstractmethod
    def create(self, **kwargs) -> sourdough.types.Base:
        """Subclasses must provide their own methods."""
        pass
    

@dataclasses.dataclass
class Director(sourdough.quirks.Element, sourdough.types.Base, abc.ABC):
    """Directs actions of a stored Builder instance.

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Configuration instance, 
            'name' should match the appropriate section name in a Configuration 
            instance. Defaults to None. 
    
    """
    name: str = None
    library: ClassVar[sourdough.types.Library] = sourdough.types.Library()
    
    """ Initialization Methods """
    
    def __init_subclass__(cls, **kwargs):
        """Adds 'cls' to 'library' if it is a concrete class."""
        super().__init_subclass__(**kwargs)
        # Creates 'library' class attribute if it doesn't exist.
        if not hasattr(cls, 'library'):  
            cls.library = sourdough.types.Library()
        if not abc.ABC in cls.__bases__:
            key = sourdough.tools.snakify(cls.__name__)
            # Removes '_director' from class name so that the key is consistent
            # with the key name for the class being constructed.
            try:
                key.replace('_director', '')
            except ValueError:
                pass
            cls.library[key] = cls
                 
    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def create(self, **kwargs) -> sourdough.types.Base:
        """Subclasses must provide their own methods."""
        pass
    
    
@dataclasses.dataclass
class Creator(Builder):
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
    def components(self) -> sourdough.types.Library:
        return self.manager.bases.component.library

    @property
    def settings(self) -> sourdough.project.Settings:
        return self.manager.project.settings
         
    """ Required Public Methods """
    
    def create(self, name: str = None) -> sourdough.project.Workflow:
        """Creates a Creator instance from a section of a Settings instance.

        Args:
            name (str): starting name in the workflow being created.
                
        Returns:
            Workflow: derived from 'section'.
            
        """
        blueprint = self.parse_section(name = name)
        graph = self.create_graph(blueprint = blueprint)
        print('test graph', graph)
        components = self.create_components(blueprint = blueprint)
        return sourdough.project.Workflow(
            graph = graph, 
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
        print('test name', name)
        parameters = self._get_parameters(names = [name, design])
        for key, value in section.items():
            print('test name key value', name, key, value)
            prefix, suffix = self._divide_key(key = key)
            print('test prefix, suffix', prefix, suffix)
            if 'design' in [suffix]:
                pass
            elif suffix in self.components.suffixes:
                if suffix in ['steps']:
                    blueprint.parallel = True
                blueprint.designs.update(dict.fromkeys(value, suffix[:-1]))
                blueprint.components[prefix] = value 
            elif suffix in parameters:
                blueprint.parameters[suffix] = value 
            elif prefix in [name]:
                blueprint.attributes[suffix] = value
            else:
                blueprint.attributes[key] = value
        print('test blueprint', blueprint)
        return blueprint
   
    def create_components(self, 
            blueprint: Blueprint) -> Dict[str, sourdough.project.Component]:
        """
        """
        instances = {}
        design = blueprint.designs[blueprint.name]
        section_keys = [blueprint.name, design]
        section_component = self.components.borrow(name = section_keys)
        instances[blueprint.name] = section_component(
            name = blueprint.name, 
            **blueprint.parameters)
        for value in blueprint.components.values():
            for item in value:
                if not item in self.settings:
                    subcomponent_keys = [item, blueprint.designs[item]]
                    subcomponent = self.components.borrow(name = subcomponent_keys)
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
        organized = self._organize_components(
            name = blueprint.name, 
            blueprint = blueprint)
        print('test organized', organized)
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
        component = self.components.borrow(name = names)
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

    def _organize_components(self, name: str, blueprint: Blueprint) -> List:
        """

        Args:
            blueprint (Blueprint): [description]

        Returns:
            List[List[str]]: [description]
            
        """
        organized = []
        outer_components = blueprint.components[name]
        for outer_component in outer_components:
            organized_subcomponents = []
            if outer_component in blueprint.components:
                organized_subcomponents.append(outer_component)
                organized_subcomponents.append(self._organize_components(
                    name = outer_component, 
                    blueprint = blueprint))
            else:
                organized_subcomponents.append(outer_component)
            if len(organized_subcomponents) == 1:
                organized.append(organized_subcomponents[0])
            else:
                organized.append(organized_subcomponents)
        return organized
                
    def _create_parallel_graph(self,
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
        paths = [p + [blueprint.designs[blueprint.name]] for p in permutations]
        for path in paths:
            graph = self._add_plan(
                contents = path, 
                blueprint = blueprint, 
                graph = graph)
        print('test graph in parallel', graph)
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
            contents = blueprint.components[blueprint.name],
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
                edges = more_itertools.windowed(subcontents, 2)
                for edge_pair in edges:
                    graph.add_edge(start = edge_pair[0], stop = edge_pair[1])
            except KeyError:
                pass
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
class Manager(sourdough.quirks.Validator, Director):
    """Creates and executes portions of a workflow in a sourdough project.

    Args:
        library (ClassVar[Library]): related Library instance that will store
            subclasses and allow runtime construction and instancing of those
            stored subclasses.

    """
    name: str = None
    creator: Creator = None
    project: sourdough.Project = dataclasses.field(repr = False, default = None)
    bases: sourdough.project.Bases = dataclasses.field(
        repr = False, 
        default = None)
    workflow: Union[
        sourdough.project.Workflow, 
        Type[sourdough.project.Workflow], 
        str] = None
    validations: ClassVar[Sequence[str]] = ['bases', 'creator', 'workflow']
    
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent and/or mixin initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass
        self.validate()

    """ Properties """
    
    @property
    def settings(self) -> sourdough.project.Settings:
        return self.project.settings
         
    """ Public Methods """
    
    def create(self, **kwargs) -> sourdough.project.Workflow:
        """Builds and stores an instance based on 'name' and 'kwargs'.

        Args:
            
        """
        self.workflow = self.creator.create(name = self.name)
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
        if bases is None:
            bases = self.project.bases
        elif isinstance(bases, sourdough.project.Bases):
            pass
        elif (inspect.isclass(bases) 
                and issubclass(bases, sourdough.project.Bases)):
            bases = bases()
        else:
            raise TypeError('bases must be a Bases or None.')
        return bases 

    def _validate_creator(self, creator: Union[str, Creator]) -> Creator:
        """"""
        if creator is None:
            creator = Creator(manager = self)
        if isinstance(creator, str):
            creator = self.bases.creator.borrow(name = 'creator')
            creator = creator(manager = self)
        elif isinstance(creator, Creator):
            creator.manager = self
        elif (inspect.isclass(creator) and issubclass(creator, Creator)):
            creator = creator(manager = self)
        return creator

    def _validate_workflow(self, workflow: Union[
            sourdough.project.Workflow, 
            Type[sourdough.project.Workflow], 
            str]) -> sourdough.project.Workflow:
        """Validates 'workflow' or converts it to a Workflow instance.
        
        Args:
         
        """
        if workflow is None:
            workflow = self.bases.workflow()
        elif isinstance(workflow, str):
            workflow = self.bases.workflow.library.borrow(name = workflow)
        elif isinstance(workflow, self.bases.workflow):
            pass
        elif (inspect.isclass(workflow) 
                and issubclass(workflow, sourdough.bases.workflow)):
            workflow = workflow()
        else:
            raise TypeError('workflow must be a Workflow, str, or None.')
        return workflow
    

  
# @dataclasses.dataclass    
# class Parameters(sourdough.types.Lexicon):
#     """
#     """
#     contents: Mapping[str, Any] = dataclasses.field(default_factory = dict)
#     name: str = None
#     base: Union[Type, str] = None
#     required: Sequence[str] = dataclasses.field(default_factory = list)
#     runtime: Mapping[str, str] = dataclasses.field(default_factory = dict)
#     selected: Sequence[str] = dataclasses.field(default_factory = list)
#     default: ClassVar[Mapping[str, Any]] = {}
    
#     """ Public Methods """
    
#     def create(self, builder: sourdough.project.Creator, **kwargs) -> None:
#         """[summary]

#         Args:
#             builder (sourdough.project.Creator): [description]

#         """
#         if not kwargs:
#             kwargs = self.default
#         for kind in ['settings', 'required', 'runtime', 'selected']:
#             kwargs = getattr(self, f'_get_{kind}')(builder = builder, **kwargs)
#         self.contents = kwargs
#         return self
    
#     """ Private Methods """
    
#     def _get_settings(self, builder: sourdough.project.Creator, 
#                       **kwargs) -> Dict[str, Any]:
#         """[summary]

#         Args:
#             builder (sourdough.project.Creator): [description]

#         Returns:
#             Dict[str, Any]: [description]
            
#         """
#         try:
#             kwargs.update(builder.settings[f'{self.name}_parameters'])
#         except KeyError:
#             pass
#         return kwargs
    
#     def _get_required(self, builder: sourdough.project.Creator, 
#                       **kwargs) -> Dict[str, Any]:
#         """[summary]

#         Args:
#             builder (sourdough.project.Creator): [description]

#         Returns:
#             Dict[str, Any]: [description]
            
#         """
#         for item in self.required:
#             if item not in kwargs:
#                 kwargs[item] = self.default[item]
#         return kwargs
    
#     def _get_runtime(self, builder: sourdough.project.Creator, 
#                       **kwargs) -> Dict[str, Any]:
#         """[summary]

#         Args:
#             builder (sourdough.project.Creator): [description]

#         Returns:
#             Dict[str, Any]: [description]
            
#         """
#         for parameter, attribute in self.runtime.items():
#             try:
#                 kwargs[parameter] = getattr(builder, attribute)
#             except AttributeError:
#                 pass
#         return kwargs

#     def _get_selected(self, builder: sourdough.project.Creator, 
#                       **kwargs) -> Dict[str, Any]:
#         """[summary]

#         Args:
#             builder (sourdough.project.Creator): [description]

#         Returns:
#             Dict[str, Any]: [description]
            
#         """
#         if self.selected:
#             kwargs = {k: kwargs[k] for k in self.selected}
#         return kwargs
        