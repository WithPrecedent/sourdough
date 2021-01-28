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
import textwrap
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import sourdough  


@dataclasses.dataclass
class Workflow(object):
    """Stores lightweight graph workflow and corresponding components.
    
    Args:
        graph (sourdough.composites.Graph): a directed acylic graph using an
            adjacency list to represented the graph. Defaults to a Graph.
        components (Library): stores Component instances that correspond to 
            nodes in 'graph'. Defaults to an empty Library.
            
    """  
    graph: sourdough.composites.Graph = dataclasses.field(
        default_factory = sourdough.composites.Graph)
    components: sourdough.types.Library = sourdough.types.Library()
        
    """ Public Methods """

    def combine(self, workflow: Workflow) -> None:
        """Adds 'other' Workflow to this Workflow.

        Combining creates an edge between every endpoint of this instance's
        Workflow and the every root of 'workflow'.

        Args:
            workflow (Workflow): a second Workflow to combine with this one.
            
        Raises:
            ValueError: if 'workflow' has nodes that are also in 'graph'.
            
        """
        if any(k in workflow.components.keys() for k in self.components.keys()):
                raise ValueError('Cannot combine Workflows with the same nodes')
        else:
            self.components.update(workflow.components)
        self.graph.combine(graph = workflow.graph)
        return self
   
    def execute(self, project: sourdough.Project, copy_components: bool = False,
                **kwargs) -> sourdough.Project:
        """[summary]

        Args:
            project (sourdough.Project): [description]

        Returns:
            sourdough.Project: [description]
            
        """
        for path in self.graph.paths:
            for node in path:
                if copy_components:
                    component = copy.deepcopy(self.components[node])
                else:
                    component = self.components[node]
                project = component.execute(project = project, **kwargs)    
        return project
    