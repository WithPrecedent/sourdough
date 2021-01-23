"""
workflows: 
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:


"""
from __future__ import annotations
import abc
import dataclasses
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import sourdough


@dataclasses.dataclass
class Workflow(sourdough.types.Base, abc.ABC):
    """Base class for composite structures in a sourdough project.

    Subclasses must have an 'execute' method that follow the criteria described 
    in the docstring for that method.
    
    All Workflow subclasses should follow the naming convention of:
            '{Name of Structure}Flow'. 
    This allows the Workflow to be properly matched with the class being 
    constructed without using an extraneous mapping to link the two.
    
    Args:
        library (ClassVar[Library]): related Library instance that will store
            subclasses and allow runtime construction and instancing of those
            stored subclasses.
        
    """
    contains: Type[sourdough.types.Base]
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
            # Removes '_flow' from class name so that the key is consistent
            # with the key name for the class being constructed.
            try:
                key.remove('_flow')
            except ValueError:
                pass
            cls.library[key] = cls
            
    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def execute(self, **kwargs) -> Any:
        """Subclasses must provide their own methods."""
        pass

       
@dataclasses.dataclass
class GraphFlow(sourdough.composites.Graph, Workflow):
    """Stores a workflow in a directed acyclic graph (DAG).
    
    Internally, the graph nodes are stored in 'contents'. And the edges are
    stored as an adjacency dict in 'edges' with the 'name' attributes of the
    nodes in 'contents' acting as the starting and stopping nodes in 
    'edges'.
    
    Args:
        contents (Mapping[str, sourdough.project.Component]): keys are the names 
            of Element instances that are stored in values.
        edges (Mapping[str, Sequence[str]]): an adjacency list where the keys
            are the names of nodes and the values are names of nodes 
            which the key is connected to.
    
    """
  
    def create(self, source: Union[sourdough.project.Settings,
                                   Mapping[str, Sequence[str]],
                                   Sequence[Sequence[str]]],
            catalog: Mapping[str, sourdough.project.Component] = None) -> None:
        """[summary]

        Args:
            source (Union[sourdough.project.Settings, Mapping[str, 
                Sequence[str]], Sequence[Sequence[str]]]): [description]
            catalog (Mapping[str, sourdough.quirks.Element], optional): 
                Defaults to None.

        Raises:
            TypeError: [description]

        Returns:
            [type]: [description]
            
        """
        if isinstance(source, sourdough.project.Settings):
            self.contents, self.edges = self._convert_settings(
                source = source, 
                catalog = catalog)
        else:
            try:
                super().create(source = source, catalog = catalog)
            except TypeError:
                raise TypeError(
                    'source must be an adjacency dict, adjacency matrix, or '
                    'Settings')   
        return self
    
    def execute(self, **kwargs) -> Any:
        """Subclasses must provide their own methods."""
        pass
 
    """ Private Methods """
    
    def _convert_settings(self, source: sourdough.project.Settings,
            catalog: Mapping[str, sourdough.quirks.Element] = None) -> Tuple[
                Mapping[str, sourdough.quirks.Element], 
                Mapping[str, Sequence[str]]]:
        """
        """
        contents = {}
        edges = {}
        settings = self._get_component_settings(settings = source)
        name = settings[settings.keys()[0]]
        section = settings.pop(name)
        component_names = [
            k for k in section.keys() if k.endswith(self.contains.suffixes)]
        base = component_names[0].split('_')[-1][:-1]
        components = section[component_names[0]]
        for item in sourdough.tools.tuplify(components):
            component = self.borrow(name = tuple(item, base))
            component_parameters = self._get_component_parameters(
                item = component)
            kwargs = {'name': item}
            for parameter in component_parameters:
                try:
                    kwargs[parameter] = section[f'{name}_{parameter}']
                except KeyError:
                    try:
                        kwargs[parameter] = section[parameter]
                    except KeyError:
                        pass
            self.add_node(component(**kwargs))
            self.add_edge(start = name, stop = item)
        return contents, edges

 
@dataclasses.dataclass
class PipelineFlow(sourdough.composites.Pipeline, Workflow):

    def execute(self, **kwargs) -> Any:
        """Subclasses must provide their own methods."""
        pass


@dataclasses.dataclass
class TreeFlow(sourdough.composites.Tree, Workflow):

    def execute(self, **kwargs) -> Any:
        """Subclasses must provide their own methods."""
        pass

     
  
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
        
        
@dataclasses.dataclass
class Architect(sourdough.Creator):
    """Creates a blueprint of a sourdough Plan.

    Architect creates a dictionary representation, a blueprint, of the overall 
    manager Plan. In the blueprint produced, keys are the names of components 
    and values are Instruction instances.
    
    Args:
                        
    """
    action: ClassVar[str] = 'Drafting'
    needs: ClassVar[Union[str, Tuple[str]]] = 'settings'
    produces: ClassVar[Type] = 'blueprint'

    """ Public Methods """
    
    def create(self, manager: sourdough.Manager) -> sourdough.types.Lexicon:
        """Creates a blueprint based on 'manager.project.settings'.

        Args:
            manager (sourdough.Manager): a Project instance with options and
                other information needed for blueprint construction.

        Returns:
            Project: with modifications made to its 'design' attribute.
            
        """ 
        blueprint = manager.bases.product.acquire(key = self.produces)(
            identification = manager.project.identification)
        for name, section in manager.project.settings.items():
            # Tests whether the section in 'manager.project.settings' is related to the 
            # construction of a project object by examining the key names to see
            # if any end in a suffix corresponding to a known base type. If so, 
            # that section is harvested for information which is added to 
            # 'blueprint'.
            if (not name.endswith(tuple(manager.project.settings.rules.skip_suffixes))
                    and name not in manager.project.settings.rules.skip_sections
                    and any(
                        [i.endswith(sourdough.base.options.component_suffixes) 
                        for i in section.keys()])):
                blueprint = self._add_instructions(
                    name = name,
                    design = None,
                    blueprint = blueprint,
                    manager = manager)
        return blueprint
        
    """ Private Methods """
    
    def _add_instructions(self, name: str, design: str,
                          blueprint: sourdough.products.Blueprint,
                          manager: sourdough.Manager, **kwargs) -> (
                              sourdough.products.Blueprint):
        """[summary]

        Args:
            name (str): [description]
            blueprint (sourdough.types.Lexicon): [description]
            manager (sourdough.Manager): [description]

        Returns:
            sourdough.types.Lexicon: [description]
            
        """
        if name not in blueprint:
            blueprint[name] = sourdough.products.Instructions(name = name)
        # Adds appropraite design type to 'blueprint' for 'name'.
        blueprint[name].design = self._get_design(
            name = name, 
            design = design,
            manager = manager)
        # Adds any appropriate parameters to 'blueprint' for 'name'.
        blueprint[name].parameters = self._get_parameters(
            name = name, 
            manager = manager)
        # If 'name' is in 'settings', this method iterates through each key, 
        # value pair in section and stores or extracts the information needed
        # to fill out the appropriate Instructions instance in blueprint.
        if name in manager.project.settings:
            instructions_attributes = {}
            for key, value in manager.project.settings[name].items():
                # If a 'key' has an underscore, text after the last underscore 
                # becomes the 'suffix' and text before becomes the 
                # 'prefix'. If there is no underscore, 'prefix' and
                # 'suffix' are both assigned to 'key'.
                prefix, suffix = self._divide_key(key = key)
                # A 'key' ending with one of the component-related suffixes 
                # triggers recursive searching throughout 'manager.project.settings'.
                if suffix in sourdough.base.options.component_suffixes:
                    contains = suffix.rstrip('s')
                    blueprint[prefix].contents = sourdough.tools.listify(value)
                    for item in blueprint[prefix].contents:
                        blueprint = self._add_instructions(
                            name = item,
                            design = contains,
                            blueprint = blueprint,
                            manager = manager)
                elif suffix in manager.project.settings.rules.special_section_suffixes:
                    instruction_kwargs = {suffix: value}
                    blueprint = self._add_instruction(
                        name = prefix, 
                        blueprint = blueprint,
                        **instruction_kwargs)
                # All other keys are presumed to be attributes to be added to a
                # Component instance.
                else:
                    blueprint[name].attributes.update({key: value})
        return blueprint

    def _get_design(self, name: str, design: str, 
                    manager: sourdough.Manager) -> str:
        """[summary]

        Args:
            name (str): [description]
            design (str): [description]
            manager (sourdough.Manager): [description]

        Returns:
            str: [description]
            
        """
        try:
            return manager.project.settings[name][f'{name}_design']
        except KeyError:
            if design is None:
                return manager.project.settings.rules.default_design
            else:
                return design

    def _get_parameters(self, name: str, 
                        manager: sourdough.Manager) -> Dict[Any, Any]:
        """[summary]

        Args:
            name (str): [description]
            project (sourdough.Manager): [description]

        Returns:
            sourdough.types.Lexicon: [description]
            
        """
        try:
            return manager.project.settings[f'{name}_parameters']
        except KeyError:
            return {}
        
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
            suffix = key.split('_')[-1]
            prefix = key[:-len(suffix) - 1]
        else:
            prefix = suffix = key
        return prefix, suffix
       
    def _add_instruction(self, name: str, 
                         blueprint: sourdough.products.Blueprint, 
                         **kwargs) -> sourdough.products.Blueprint:
        """[summary]

        Args:
            name (str): [description]
            blueprint (sourdough.types.Lexicon): [description]

        Returns:
            sourdough.types.Lexicon: [description]
            
        """
        # Adds any kwargs to 'blueprint' as appropriate.
        for key, value in kwargs.items():
            if isinstance(getattr(blueprint[name], key), list):
                getattr(blueprint[name].key).extend(
                    sourdough.tools.listify(value))
            elif isinstance(getattr(blueprint[name], key), dict):
                getattr(blueprint[name], key).update(value) 
            else:
                setattr(blueprint[name], key, value)           
        return blueprint

    """ Dunder Methods """
    
    def __str__(self) -> str:
        return pprint.pformat(self, sort_dicts = False, compact = True)
           
      
@dataclasses.dataclass
class Factory(sourdough.Creator):
    """Constructs finalized plan.
    
    Args:
                        
    """
    action: ClassVar[str] = 'Creating'
    needs: ClassVar[Union[str, Tuple[str]]] = 'blueprint'
    produces: ClassVar[Type] = 'plan'

    """ Public Methods """

    def create(self, manager: sourdough.Manager) -> sourdough.project.Component:
        """Drafts a Workflow instance based on 'blueprint' in 'manager'.
            
        """ 
        plan = manager.bases.product.acquire(key = self.produces)(
            identification = manager.project.identification)
        plan.contents = self._create_component(
            name = manager.project.name, 
            manager = manager)
        return plan
    
    """ Private Methods """

    def _create_component(self, name: str, 
                          manager: sourdough.Manager) -> sourdough.project.Component:
        """[summary]

        Args:
            name (str): [description]
            manager (sourdough.Manager): [description]

        Returns:
            sourdough.project.Component: [description]
            
        """
        component = self._get_component(name = name, manager = manager)
        return self._finalize_component(component = component, 
                                        manager = manager)

    def _get_component(self, name: str,
                       manager: sourdough.Manager) -> sourdough.project.Component:
        """[summary]

        Args:
            name (str): [description]
            manager (sourdough.Manager): [description]

        Raises:
            KeyError: [description]

        Returns:
            Mapping[str, sourdough.project.Component]: [description]
            
        """
        instructions = manager['blueprint'][name]
        kwargs = {'name': name, 'contents': instructions.contents}
        try:
            component = manager.basescomponent.borrow(key = name)
            for key, value in kwargs.items():
                if value:
                    setattr(component, key, value)
        except KeyError:
            try:
                component = manager.basescomponent.acquire(key = name)
                component = component(**kwargs)
            except KeyError:
                try:
                    component = manager.basescomponent.acquire(
                        key = instructions.design)
                    component = component(**kwargs)
                except KeyError:
                    raise KeyError(f'{name} component does not exist')
        return component

    def _finalize_component(self, component: sourdough.project.Component,
                            manager: sourdough.Manager) -> sourdough.project.Component:
        """[summary]

        Args:
            component (sourdough.project.Component): [description]
            manager (sourdough.Manager): [description]

        Returns:
            sourdough.project.Component: [description]
            
        """
        if isinstance(component, Iterable):
            if component.parallel:
                finalizer = self._finalize_parallel
            else:
                finalizer = self._finalize_serial
        else:
            finalizer = self._finalize_element
        component = finalizer(component = component, manager = manager)
        component = self._add_attributes(
            component = component, 
            manager = manager)
        return component

    def _finalize_parallel(self, component: sourdough.project.Component,
                           manager: sourdough.Manager) -> sourdough.project.Component:
        """[summary]

        Args:
            component (sourdough.project.Component): [description]
            manager (sourdough.Manager): [description]

        Returns:
            sourdough.project.Component: [description]
            
        """
        # Creates empy list of lists for all possible permutations to be stored.
        possible = []
        # Populates list of lists with different options.
        for item in component.contents:
            possible.append(manager['blueprint'][item].contents)
        # Computes Cartesian product of possible permutations.
        combos = list(map(list, itertools.product(*possible)))
        wrappers = [
            self._create_component(i, manager) for i in component.contents]
        new_contents = []
        for combo in combos:
            new_combo = [self._create_component(i, manager) for i in combo]
            steps = []
            for i, step in enumerate(wrappers):
                new_step = copy.deepcopy(step)
                new_step.contents = new_combo[i]
                steps.append(new_step)
            new_contents.append(steps)
        component.contents = new_contents
        component = self._add_attributes(
            component = component, 
            manager = manager)
        return component

    def _finalize_serial(self, component: sourdough.project.Component, 
                         manager: sourdough.Manager) -> sourdough.project.Component:
        """[summary]

        Args:
            component (sourdough.project.Component): [description]
            manager (sourdough.Manager): [description]

        Returns:
            Component: [description]
            
        """
        new_contents = []
        for item in component.contents:
            instance = self._create_component(
                name = item, 
                manager = manager)
            new_contents.append(instance)
        component.contents = new_contents
        return component

    def _finalize_element(self, component: sourdough.project.Component, 
                          manager: sourdough.Manager) -> sourdough.project.Component:
        """[summary]

        Args:
            component (sourdough.project.Component): [description]
            manager (sourdough.Manager): [description]

        Returns:
            Component: [description]
            
        """
        try:
            component.contents = sourdough.base.options.algorithms[component.name]
        except KeyError:
            component.contents = None
        return component
    
    def _add_attributes(self, component: sourdough.project.Component,
                        manager: sourdough.Manager) -> sourdough.project.Component:
        """[summary]

        Returns:
            [type]: [description]
            
        """
        attributes = manager['blueprint'][component.name].attributes
        for key, value in attributes.items():
            setattr(component, key, value)
        return component    
