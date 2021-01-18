"""
workshop: creator classes for building complex workflows
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
class Builder(sourdough.base.Creator, abc.ABC):
    """Stores a sourdough workflow.
    
    """  
    project: sourdough.Project = dataclasses.field(repr = False, default = None)

    """ Public Methods """
    
    def create(self, source: Any) -> sourdough.base.Node:
        return source

    """ Private Methods """
    
    def _create_from_settings() -> sourdough.Base.Node:
        pass
    
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
    
    def _get_node(self, name: str) -> Type[sourdough.base.Node]:
        """[summary]

        Args:
            name (str): [description]

        Returns:
            Type: [description]
            
        """
        keys = [name]
        try:
            keys.append(self.project.settings[name][f'{name}_structure'])
        except KeyError:
            keys.append(self.project.settings['general']['default_structure'])
        return self.project.bases.get_class(kind = 'component', name = keys)
       

@dataclasses.dataclass
class GraphCreator(Builder):
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
           
       