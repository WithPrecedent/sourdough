"""
workshop: classes for building a sourdough project
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:

    
"""
from __future__ import annotations
import abc
import copy
import dataclasses
import itertools
import pprint
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import sourdough  
                       
   
@dataclasses.dataclass
class Creator(sourdough.types.Base, abc.ABC):
    """Creates a Structure subclass instance.

    All Creator subclasses should follow the naming convention of:
            '{Class being built}Creator'. 
    This allows the Creator to be properly matched with the class being 
    constructed without using an extraneous mapping to link the two.

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
                key.remove('_builder')
            except ValueError:
                pass
            cls.library[key] = cls
            
    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def create(self, source: Any, **kwargs) -> sourdough.types.Base:
        """Creates a Base subclass instance from 'source'.
        
        Subclasses must provide their own methods.

        Args:
            source (Any): source object from which to create an instance of a
                Base subclass.
            kwargs: additional arguments to pass when a Base subclass is
                instanced.
        
        Returns:
            Base: a sourdough Base subclass instance.
            
        """
        pass  
    
    """ Public Methods """
    
    def borrow(self, base: Type[sourdough.types.Base], 
               keys: Union[str, Sequence[str]]) -> Type[sourdough.types.Base]:
        """[summary]

        Args:
            name (str): [description]

        Returns:
            Type: [description]
            
        """
        product = None
        for key in sourdough.tools.tuplify(keys):
            try:
                product = base.library.borrow(name = key)
                break
            except (AttributeError, KeyError):
                pass
        if product is None:
            raise KeyError(f'No match for {keys} was found in the '
                           f'{base.__name__} library.')
        return product 

   
@dataclasses.dataclass
class Director(sourdough.types.Lexicon, sourdough.types.Base, abc.ABC):
    """Uses stored creators to create new items.
    
    A Director differs from a Lexicon in 3 significant ways:
        1) It stores a separate Lexicon called 'creators' which have classes
            used to create other items.
        2) It iterates 'creators' and stores its output in 'contents.' General
            access methods still point to 'contents'.
        3) It has an additional convenience methods called 'add_creator' for
            adding new items to 'creators', 'advance' for iterating one step,
            and 'complete' which completely iterates the instance and stores
            all results in 'contents'.
    
    Args:
        contents (Mapping[Any, Any]]): stored dictionary. Defaults to an empty 
            dict.
              
    """
    contents: Mapping[Any, Any] = dataclasses.field(default_factory = dict)
    creators: sourdough.types.Lexicon[str, Creator] = dataclasses.field(
        default_factory = sourdough.types.Lexicon)

    """ Public Methods """
     
    def add(self, item: Mapping[Any, Any], **kwargs) -> None:
        """Adds 'item' to the 'contents' attribute.
        
        Args:
            item (Mapping[Any, Any]): items to add to 'contents' attribute.
            kwargs: creates a consistent interface even when subclasses have
                additional parameters.
                
        """
        self.contents.update(item)
        return self

    def add_creator(self, item: Mapping[Any, Any], **kwargs) -> None:
        """Adds 'item' to the 'creators' attribute.
        
        Args:
            item (Mapping[Any, Any]): items to add to 'creators' attribute.
            kwargs: creates a consistent interface even when subclasses have
                additional parameters.
                
        """
        self.creators.add(item = item)
        return self

    def advance(self) -> Any:
        """Returns next product of an instance iterable.'
        
        Returns:
            Any: item created by a single iteration."""
        return self.__next__()

    def complete(self) -> None:
        """Executes each step in an instance's iterable."""
        for item in iter(self):
            self.__next__()
        return self

    """ Dunder Methods """
    
    def __iter__(self) -> Iterable[Any]:
        """Returns iterable of 'creators'.

        Returns:
            Iterable: of 'creators'.

        """
        return iter(self.creators)

    def __len__(self) -> int:
        """Returns length of iterable of 'creators'

        Returns:
            int: length of iterable 'creators'.

        """
        return len(self.__iter__()) 

@dataclasses.dataclass
class ComponentCreator(sourdough.workshop.Creator, abc.ABC):
    
    project: sourdough.Project = None
    skip: ClassVar[Sequence[str]] = ['name', 'contents', 'parameters']
    
    """ Public Methods """

    
    def create(self, name: str, component: sourdough.nodes.Component, 
               section: Mapping[str, Any]) -> None:
        """
        
        """
        suffixes = self._get_suffixes(item = self.base)
        for item in validations:
            try:
                kwargs = {item: getattr(self, item)}
                setattr(self, item, getattr(
                    self, f'_validate_{item}')(**kwargs))
            except AttributeError:
                pass
        return self     

    """ Private Methods """
           
    def _get_suffixes(self, item: Type[sourdough.nodes.Component]) -> Tuple[str]:
        """
        """
        parameters = list(item.__annotations__.keys())
        return tuple(i for i in parameters if i not in self.skip)
    
    def _get_node(self, name: Union[str, Sequence[str]]) -> (
            Type[sourdough.base.Node]):
        """[summary]

        Args:
            name (str): [description]

        Returns:
            Type: [description]
            
        """
        keys = [name]
        try:
            keys.append(self.project.settings[name][f'{name}_design'])
        except KeyError:
            keys.append(self.project.settings['general']['default_node_design'])
        return self.borrow(keys = keys)


""" Structural Creator Classes """ 

@dataclasses.dataclass
class StructureCreator(sourdough.workshop.Creator, abc.ABC):
    
    
    def _get_parameters(self, name: str, **kwargs) -> Mapping[str, Any]:
        """[summary]

        Args:
            name (str): [description]

        Returns:
            Parameters: [description]
        """
        try:
            kwargs.update(self.project.settings[f'{name}_parameters'])
        except KeyError:
            pass
        return kwargs

       
@dataclasses.dataclass
class GraphCreator(StructureCreator):
    """Builds a sourdough Graph
    
    """  
    contents: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    project: sourdough.Project = dataclasses.field(repr = False, default = None)
    
    """ Public Methods """
    
    def create(self, source: Union[sourdough.base.Configuration,
                                   Mapping[str, Sequence[str]],
                                   Sequence[Sequence[str]]]) -> Graph:
        """
        """
        if isinstance(source, sourdough.types.Configuration):
            return self._from_configuration(source = source)
        elif isinstance(source, sourdough.types.Configuration):
            return self._from_adjacency_list(source = source)
        elif isinstance(source, sourdough.types.Configuration):
            return self._from_adjacency_matrix(source = source)
        else:
            raise TypeError('source must be a Configuration, adjacency list, '
                            'or adjacency matrix')   
            
    """ Private Methods """
    
    def _from_configuration(self, 
                            source: sourdough.base.Configuration) -> Graph:
        return source
    
    def _from_adjacency_list(self, 
                            source: sourdough.base.Configuration) -> Graph:
        return source
    
    def _from_adjacency_matrix(self, 
                            source: sourdough.base.Configuration) -> Graph:
        return source



@dataclasses.dataclass
class PipelineCreator(StructureCreator):
    """Builds a sourdough Pipeline
    
    """  
    
    
@dataclasses.dataclass
class TreeCreator(StructureCreator):
    """Builds a sourdough Tree
    
    """  
         
  
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
    
    def create(self, creator: sourdough.project.Creator, **kwargs) -> None:
        """[summary]

        Args:
            creator (sourdough.project.Creator): [description]

        """
        if not kwargs:
            kwargs = self.default
        for kind in ['settings', 'required', 'runtime', 'selected']:
            kwargs = getattr(self, f'_get_{kind}')(creator = creator, **kwargs)
        self.contents = kwargs
        return self
    
    """ Private Methods """
    
    def _get_settings(self, creator: sourdough.project.Creator, 
                      **kwargs) -> Dict[str, Any]:
        """[summary]

        Args:
            creator (sourdough.project.Creator): [description]

        Returns:
            Dict[str, Any]: [description]
            
        """
        try:
            kwargs.update(creator.settings[f'{self.name}_parameters'])
        except KeyError:
            pass
        return kwargs
    
    def _get_required(self, creator: sourdough.project.Creator, 
                      **kwargs) -> Dict[str, Any]:
        """[summary]

        Args:
            creator (sourdough.project.Creator): [description]

        Returns:
            Dict[str, Any]: [description]
            
        """
        for item in self.required:
            if item not in kwargs:
                kwargs[item] = self.default[item]
        return kwargs
    
    def _get_runtime(self, creator: sourdough.project.Creator, 
                      **kwargs) -> Dict[str, Any]:
        """[summary]

        Args:
            creator (sourdough.project.Creator): [description]

        Returns:
            Dict[str, Any]: [description]
            
        """
        for parameter, attribute in self.runtime.items():
            try:
                kwargs[parameter] = getattr(creator, attribute)
            except AttributeError:
                pass
        return kwargs

    def _get_selected(self, creator: sourdough.project.Creator, 
                      **kwargs) -> Dict[str, Any]:
        """[summary]

        Args:
            creator (sourdough.project.Creator): [description]

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

    def create(self, manager: sourdough.Manager) -> sourdough.Component:
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
                          manager: sourdough.Manager) -> sourdough.Component:
        """[summary]

        Args:
            name (str): [description]
            manager (sourdough.Manager): [description]

        Returns:
            sourdough.Component: [description]
            
        """
        component = self._get_component(name = name, manager = manager)
        return self._finalize_component(component = component, 
                                        manager = manager)

    def _get_component(self, name: str,
                       manager: sourdough.Manager) -> sourdough.Component:
        """[summary]

        Args:
            name (str): [description]
            manager (sourdough.Manager): [description]

        Raises:
            KeyError: [description]

        Returns:
            Mapping[str, sourdough.Component]: [description]
            
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

    def _finalize_component(self, component: sourdough.Component,
                            manager: sourdough.Manager) -> sourdough.Component:
        """[summary]

        Args:
            component (sourdough.Component): [description]
            manager (sourdough.Manager): [description]

        Returns:
            sourdough.Component: [description]
            
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

    def _finalize_parallel(self, component: sourdough.Component,
                           manager: sourdough.Manager) -> sourdough.Component:
        """[summary]

        Args:
            component (sourdough.Component): [description]
            manager (sourdough.Manager): [description]

        Returns:
            sourdough.Component: [description]
            
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

    def _finalize_serial(self, component: sourdough.Component, 
                         manager: sourdough.Manager) -> sourdough.Component:
        """[summary]

        Args:
            component (sourdough.Component): [description]
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

    def _finalize_element(self, component: sourdough.Component, 
                          manager: sourdough.Manager) -> sourdough.Component:
        """[summary]

        Args:
            component (sourdough.Component): [description]
            manager (sourdough.Manager): [description]

        Returns:
            Component: [description]
            
        """
        try:
            component.contents = sourdough.base.options.algorithms[component.name]
        except KeyError:
            component.contents = None
        return component
    
    def _add_attributes(self, component: sourdough.Component,
                        manager: sourdough.Manager) -> sourdough.Component:
        """[summary]

        Returns:
            [type]: [description]
            
        """
        attributes = manager['blueprint'][component.name].attributes
        for key, value in attributes.items():
            setattr(component, key, value)
        return component    


@dataclasses.dataclass
class Worker(sourdough.Creator):
    """Applies a project Workflow and produces results.

    Args:

    """
    action: ClassVar[str] = 'Computing'
    needs: ClassVar[Union[str, Tuple[str]]] = 'plan'
    produces: ClassVar[str] = 'results'
    
    """ Public Methods """
 
    def create(self, manager: sourdough.Manager, 
               **kwargs) -> sourdough.types.Lexicon:        
        """Computes results based on a plan.
            
        """
        results = manager.basesproduct.acquire(key = self.produces)(
            identification = manager.project.identification)
        if manager.project.data is not None:
            kwargs['data'] = manager.project.data
        for component in manager['plan']:
            results.update({component.name: component.apply(**kwargs)})
        return results
