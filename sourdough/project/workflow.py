"""
workflow: base classes for sourdough project workflows
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:

"""
from __future__ import annotations
import abc
import dataclasses
from typing import (Any, Callable, ClassVar, Container, Generic, Iterable, 
                    Iterator, Mapping, Sequence, Tuple, TypeVar, Union)

import sourdough


@dataclasses.dataclass
class Flow(
        sourdough.base.mixins.RegistryMixin, 
        sourdough.base.core.Action, 
        abc.ABC):
    """Base class for a stage in a Workflow.
    
    Args:
    
    """
    name: str = None
    needs: ClassVar[Sequence[str]] = dataclasses.field(default_factory = list) 
    registry: ClassVar[sourdough.Inventory] = sourdough.Inventory()

    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def perform(self, item: object = None, **kwargs) -> object:
        """Performs some action related to passed 'item'.
        
        Subclasses must provide their own methods.
        
        """
        pass
        

@dataclasses.dataclass
class Workflow(
        sourdough.base.mixins.RegistryMixin, 
        sourdough.base.core.Hybrid, 
        abc.ABC):
    """Base class for sourdough workflows.
    
    Args:
        
    """
    contents: Sequence[Union[str, sourdough.Flow]] = dataclasses.field(
        default_factory = list)
    name: str = None
    registry: ClassVar[sourdough.Inventory] = sourdough.Inventory()
     
    """ Public Methods """
    
    def validate(self, 
            contents: Sequence[Union[str, sourdough.Flow]]) -> Sequence[Flow]:
        """Validates 'contents' or converts 'contents' to proper type.
        
        Args:
            contents (Sequence[Union[str, sourdough.Flow]]): items to validate 
                or convert to a list of Flow instances.
            
        Raises:
            TypeError: if 'contents' argument is not of a supported datatype.
            
        Returns:
            Sequence[Flow]: validated or converted argument that is 
                compatible with an instance.
        
        """
        new_contents = []
        for item in contents:
            if isinstance(item, str):
                new_contents.append(Flow.build(key = item))
            elif isinstance(item, Flow):
                new_contents.append(item)
            else:
                raise TypeError('contents must be a list of Flow or str types')
        return new_contents

    def perform(self, project: sourdough.Project) -> sourdough.Project:
        """[summary]

        Args:
            project (sourdough.Project): [description]

        Returns:
            sourdough.Project: [description]
        """
        for step in self.contents:
            instance = step()
            parameters = self._get_flow_parameters(
                flow = step, 
                project = project)
            result = instance.perform(**parameters)
            setattr(project, result.name, result)
        return project
    
    """ Private Methods """
    
    def _get_flow_parameters(self, 
            flow: sourdough.Flow,
            project: sourdough.Project) -> Mapping[str, Any]:
        """[summary]

        Args:
            flow (sourdough.Flow): [description]

        Returns:
            Mapping[str, Any]: [description]
            
        """
        parameters = {}
        for need in flow.needs:
            if need in ['project']:
                parameters['project'] = project
            else:
                parameters[need] = getattr(project, need)
        return parameters
           