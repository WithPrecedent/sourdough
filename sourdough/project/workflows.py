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
class Workflow(sourdough.composites.Graph):
    """Stores lightweight workflow and corresponding components.
    
    Args:
        contents (Dict[str, List[str]]): an adjacency list where the keys are 
            the names of nodes and the values are names of nodes which the key 
            is connected to. Defaults to an empty dict.
        default (Any): default value to use when a key is missing and a new
            one is automatically corrected. Defaults to an empty list.
        copy_components (bool): whether to make copies of stored components
            before calling their 'execute' methods (True) or whether to simply
            use the stored Component instance as is (False). Defaults to False.
        components (ClassVar[Library]): stores Component instances that 
            correspond to nodes in the Workflow. Defaults to an empty Library.
            
    """  
    contents: Dict[str, List[str]] = dataclasses.field(default_factory = dict)
    default: Any = dataclasses.field(default_factory = list)
    copy_components: bool = False
    components: ClassVar[sourdough.types.Library] = sourdough.types.Library()

    """ Public Methods """
    
    def execute(self, project: sourdough.Project, **kwargs) -> sourdough.Project:
        """[summary]

        Args:
            project (sourdough.Project): [description]

        Returns:
            sourdough.Project: [description]
        """
        for path in self.paths:
            for node in path:
                if self.copy_components:
                    component = copy.deepcopy(self.components[node])
                else:
                    component = self.components[node]
                project = component.execute(project = project, **kwargs)    
        return project
    