"""
.. module:: project
:synopsis: basic sourdough project
:author: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import dataclasses
from typing import (
    Any, Callable, ClassVar, Dict, Iterable, List, Optional, Tuple, Union)

import sourdough


@dataclasses.dataclass
class Project(sourdough.Plan):
    """Basic project organization class.
    
    It contains all of the needed settings ('settings' and 'filer'), 
    coordination information ('name' and 'identification'), and data ('data')
    to complete a basic project. Subclasses can easily expand upon the basic
    design and functionality of this class. For instance, the CompositeProject
    provides the means to construct large dynamic tree-like structures which
    are then applied to 'data'

    Arguments:
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. If the class instance
            needs settings from the shared Settings instance, 'name' should
            match the appropriate section name in that Settings instance. When
            subclassing, it is a good settings to use the same 'name' attribute
            as the base class for effective coordination between sourdough
            classes. Defaults to None or __class__.__name__.lower().
        identification (Optional[str]): a unique identification name for a 
            Project instance. The name is used for creating file folders
            related to the 'Project'. If not provided, a string is created from
            'name' and the date and time. Defaults to None.
        items (Optional[List[Component]]): stored iterable of actions to take
            as part of the Plan. Defaults to an empty list.        
        settings (Optional[Union[sourdough.Settings, str]]): an instance of 
            Settings or a string containing the file path where a file of a 
            supported file type with settings for an Settings instance is 
            located. Defaults to None.
        filer (Optional[Union[sourdough.Filer, str]]): an instance of Filer or a 
            string containing the full path of where the root folder should be 
            located for file input and output. A Filer instance contains all 
            file path and import/export methods for use throughout sourdough. 
            Defaults to None.
        data (Optional[Any]): a data object to apply any constructed objects to.
            This need only be provided when the class is instanced for
            automatic execution. Defaults to None. If you are working on a data-
            focused Project, consider using siMpLify instead 
            (https://github.com/WithPrecedent/simplify). It applies sourdough
            in the data science context. sourdough itself treats 'data' as an
            unknown object of any type which offers more flexibility of design.
                             
    """  
    name: Optional[str] = None
    identification: Optional[str] = None
    items: Optional[List[sourdough.Component]] = dataclasses.field(
        default_factory = list)
    settings: Optional[Union['sourddough.Settings', str]] = None
    filer: Optional[Union['sourdough.Filer', str]] = None
    data: Optional[Any] = None

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        super().__post_init__()
        # Creates unique 'identification' based upon date and time if none 
        # exists.
        self.identification = (
            self.identification or sourdough.utilities.datetime_string(
                prefix = self.name))
        # Validates or creates a 'Settings' instance.
        self.settings = sourdough.Settings(contents = self.settings)
        # Validates or creates a Filer' instance.
        self.filer = sourdough.Filer(
            root_folder = self.filer, 
            settings = self.settings)
    