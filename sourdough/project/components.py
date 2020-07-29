"""
components: static pieces of a sourdough composite object
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:


"""

import dataclasses
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union

import sourdough

    
@dataclasses.dataclass
class Edge(sourdough.Component):
    """An edge in a sourdough Graph.

    'start' and 'stop' are the ends of the Edge. However, which value is 
    assigned to each attribute only matters in a directional graph.

    By default Edge is slotted so that no other attributes can be added. This
    lowers memory consumption and increases speed. If you wish to add more 
    functionality to your Graph edges, you should subclass Edge.

    Args:
        start (str): name of the Component where the edge starts.
        stop (str): name of the Component where the edge ends.
        directed (bool): whether this edge is directed (True). Defaults to 
            False. 
        weight (float): a weight value assigned to this edge. Defaults to None.

    """
    start: 'sourdough.Node' = None
    stop: 'sourdough.Node' = None
    directed: bool = False
    weight: float = None
    name: str = None
    
    """ Public Methods """

    def get_name(self) -> str:
        """Returns 'name' based upon attached nodes.
        
        Returns:
            str: name of class for internal referencing.
        
        """
        return f'{self.start.name}_to_{self.stop.name}'


@dataclasses.dataclass
class Node(sourdough.Component):
    """An edge in a sourdough Graph.

    'start' and 'stop' are the ends of the Edge. However, which value is 
    assigned to each attribute only matters in a directional graph.

    By default Edge is slotted so that no other attributes can be added. This
    lowers memory consumption and increases speed. If you wish to add more 
    functionality to your Graph edges, you should subclass Edge.

    Args:
        start (str): name of the Component where the edge starts.
        stop (str): name of the Component where the edge ends.
        directed (bool): whether this edge is directed (True). Defaults to 
            False. 
        weight (float): a weight value assigned to this edge. Defaults to None.

    """

    name: str = None
    edges: Sequence['Edge'] = dataclasses.field(default_factory = list)
    