"""
.. module:: project
:synopsis: sourdough project
:author: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import dataclasses
from typing import (
    Any, Callable, ClassVar, Dict, Iterable, List, Optional, Tuple, Union)

import sourdough
    
    
@dataclasses.dataclass
class Project(sourdough.Worker):
    """Basic sourdough project container.
    
    a Subclasses can easily expand upon the basic
    design and functionality of this class. For instance, the CompositeProject
    provides the means to construct large dynamic tree-like structures which
    are then applied to 'data'

    Args:
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. If the class instance
            needs settings from the shared Settings instance, 'name' should
            match the appropriate section name in that Settings instance. When
            subclassing, it is a good settings to use the same 'name' attribute
            as the base class for effective coordination between sourdough
            classes. Defaults to None or __class__.__name__.lower().
        worker (Optional[List[Worker]]): stored iterable of actions 
            to take as part of the SequenceBase. Defaults to an empty list.    
        identification (Optional[str]): a unique identification name for a 
            Project instance. The name is used for creating file folders
            related to the 'Project'. If not provided, a string is created from
            'name' and the date and time. Defaults to None.    
        data (Optional[Any]): a data object to apply any constructed objects to.
            This need only be provided when the class is instanced for
            automatic execution. Defaults to None. If you are working on a data-
            focused Project, consider using siMpLify instead 
            (https://github.com/WithPrecedent/simplify). It applies sourdough
            in the data science context. sourdough itself treats 'data' as an
            unknown object of any type which offers more flexibility of design.
                             
    """  
    name: Optional[str] = None
    contents: Optional[List[Union[
        'Worker', 
        'sourdough.Task', 
        str]]] = dataclasses.field(default_factory = list) 
    design: Optional[str] = dataclasses.field(
        default_factory = lambda: 'chained')
    settings: Optional[Union['sourddough.Settings', str]] = None
    data: Optional[Any] = None
    manager: Optional[str] = None
    identification: Optional[str] = None
    filer: Optional[Union['sourdough.Filer', str]] = None
    options: ClassVar['sourdough.Options'] = sourdough.Options()

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls inherited initialization method.
        super().__post_init__()
        # Creates unique 'identification' based upon date and time if none 
        # exists.
        self.identification = (
            self.identification or sourdough.utilities.datetime_string(
                prefix = self.name))
