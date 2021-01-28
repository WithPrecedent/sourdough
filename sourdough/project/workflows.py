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
class Workflow(sourdough.types.Proxy):
    """Stores lightweight graph workflow and corresponding components.
    
    Args:
        contents (sourdough.composites.Graph): a directed acylic graph using an
            adjacency list to represented the graph. Defaults to an Graph.
        components (Library): stores Component instances that correspond to 
            nodes in 'contents'. Defaults to an empty Library.
            
    """  
    contents: sourdough.composites.Graph = dataclasses.field(
        default_factory = sourdough.composites.Graph)
    components: sourdough.types.Library = sourdough.types.Library()

    """ Public Methods """
    
    def execute(self, project: sourdough.Project, **kwargs) -> sourdough.Project:
        """[summary]

        Args:
            project (sourdough.Project): [description]

        Returns:
            sourdough.Project: [description]
            
        """
        for path in self.contents.paths:
            for node in path:
                if self.contents.copy_components:
                    component = copy.deepcopy(self.components[node])
                else:
                    component = self.components[node]
                project = component.execute(project = project, **kwargs)    
        return project
    