"""
workshop: classes for building composite sourdough objects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Builder (Base, ABC): base class for all sourdough constructors of composite
        structures. All subclasses must have a 'create' method. Its 'library'
        class attribute stores all subclasses.
        
"""
from __future__ import annotations
import abc
import dataclasses
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import sourdough 

  
@dataclasses.dataclass
class Builder(sourdough.types.Base, abc.ABC):
    """Creates a Structure subclass instance.

    All Builder subclasses should follow the naming convention of:
            '{Class being built}Builder'. 
    This allows the Builder to be properly matched with the class being 
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
class ComponentBuilder(Builder, abc.ABC):
    
    project: sourdough.Project = None
    skip: ClassVar[Sequence[str]] = ['name', 'contents', 'parameters']
    

@dataclasses.dataclass
class TechniqueBuilder(ComponentBuilder):
    
    project: sourdough.Project = None
    skip: ClassVar[Sequence[str]] = ['name', 'contents', 'parameters']
    

@dataclasses.dataclass
class StepBuilder(ComponentBuilder):
    
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
    

@dataclasses.dataclass
class StructureBuilder(Builder, abc.ABC):
    
    
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
class GraphBuilder(Builder):
    """Stores a sourdough workflow.
    
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
        