"""
creators: classes for building and storing different steps in sourdough project
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Instructions (Progression): information needed to create a single Component.
    Architect (Creator):
    Builder (Creator):
    Worker (Creator):
    
"""
from __future__ import annotations
import copy
import dataclasses
import itertools
import pprint
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import sourdough  


@dataclasses.dataclass
class Instructions(sourdough.types.Progression):
    """Information to construct a sourdough Component.
    
    Args:
        contents (Sequence[str]): stored list of str. Included items should 
            correspond to keys in an Outline and/or Component subclasses. 
            Defaults to an empty list.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. 
        base (str): name of base class associated with the Component to be 
            created.
        design (str): name of design base class associated with the Component
            to be created.
        parameters (Mapping[str, Any]): parameters to be used for the stored
            object(s) in its/their creation.
        attributes (Mapping[str, Any]): attributes to add to the created
            Component object. The keys should be name of the attribute and the
            values should be the value stored for that attribute.
            
    """
    contents: Sequence[str] = dataclasses.field(default_factory = list)
    name: str = None
    design: str = None
    parameters: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    attributes: Mapping[str, Any] = dataclasses.field(default_factory = dict)

    """ Dunder Methods """

    def __str__(self) -> str:
        """Returns pretty string representation of a class instance.
        
        Returns:
            str: normal representation of a class instance.
        
        """
        return pprint.pformat(self, sort_dicts = False, compact = True)


@dataclasses.dataclass
class Blueprint(sourdough.Deliverable):
    """Class of essential information from Settings.
    
    Args:
        contents (Mapping[str, Instructions]]): stored dictionary which contains
            Instructions instances. Defaults to an empty dict.
        identification (str): a unique identification name for the related 
            Project instance.            
    """
    contents: Mapping[str, Instructions] = dataclasses.field(
        default_factory = dict)
    identification: str = None
                       

@dataclasses.dataclass
class Workflow(sourdough.Component, sourdough.types.Hybrid):
    """Iterable base class in a sourdough composite object.
            
    Args:
        contents (Sequence[Component]): Component subclass instances. Defaults 
            to an empty list.
        identification (str): a unique identification name for the related 
            Project instance.   
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes.
        iterations (Union[int, str]): number of times the 'apply' method should 
            be called. If 'iterations' is 'infinite', the 'apply' method will
            continue indefinitely unless the method stops further iteration.
            Defaults to 1.
        criteria (str): after iteration is complete, a 'criteria' determines
            what should be outputted. This should correspond to a key in the
            'algorithms' Catalog for the sourdough project. Defaults to None.
        parallel (ClassVar[bool]): whether the 'contents' contain other 
            iterables (True) or static objects (False). If True, a subclass
            should include a custom iterable for navigating the stored 
            iterables. Defaults to False.
                            
    """
    contents: Sequence[sourdough.Component] = dataclasses.field(
        default_factory = list)
    identification: str = None
    name: str = None
    iterations: Union[int, str] = 1
    criteria: str = None
    parallel: ClassVar[bool] = False 
    
    """ Public Methods """
    
    def apply(self, project: sourdough.Project, **kwargs) -> sourdough.Project:
        """[summary]

        Args:
            project (sourdough.Project): [description]

        Returns:
            sourdough.Project: [description]
            
        """
        if 'data' not in kwargs and project.data:
            kwargs['data'] = project.data
        for i in self.iterations:
            project = super().apply(project = project, **kwargs)
        return project   

  
@dataclasses.dataclass
class Report(sourdough.types.Lexicon):
    """Stores output of Worker.
    
    Args:
        contents (Mapping[str, Instructions]]): stored dictionary which contains
            Instructions instances. Defaults to an empty dict.
        identification (str): a unique identification name for the related 
            Project instance.            
            
    """
    contents: Mapping[str, Report] = dataclasses.field(default_factory = dict)
    name: str = None
    

@dataclasses.dataclass
class Results(sourdough.Deliverable):
    """Stores output of Worker.
    
    Args:
        contents (Mapping[str, Instructions]]): stored dictionary which contains
            Instructions instances. Defaults to an empty dict.
        identification (str): a unique identification name for the related 
            Project instance.            
            
    """
    contents: Mapping[str, Report] = dataclasses.field(
        default_factory = dict)
    identification: str = None

