"""
resources: stores classes and objects created at runtime
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Options (object): stores classes and objects that are subclasses of the
        core sourdough classes in a project.
    options (Options): an instance of Options
    Bases (Loader): base classes 
        
"""
from __future__ import annotations
import dataclasses
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)
import sourdough


@dataclasses.dataclass
class Options(object):
    """Stores classes and objects created by registries and libraries. 
    
    However, any of the items can be manually populated as well.

    Args:
        managers (Mapping[str, Type]): stores Manager subclasses. Defaults to an 
            empty Catalog.
        creators (Mapping[str, Type]): stores Creator subclasses. Defaults to an 
            empty Catalog.
        products (Mapping[str, Type]): stores Product subclasses. Defaults to an 
            empty Catalog.
        components (Mapping[str, Type]): stores Component subclasses. Defaults 
            to an empty Catalog.
        instances (Mapping[str, object]): stores Component subclass instances. 
            Defaults to an empty Catalog.
        algorithms (Mapping[str, Type]): stores third party and sourdough 
            algorithms. Defaults to an empty Catalog.
        criteria (Mapping[str, Callable]): stores third party and sourdough 
            algorithms. Defaults to an empty Catalog with 'always_return_list'
            set to true. This means that 'criteria' will always return a list
            of criteria even when there is only one item sought.
            
    """
    managers: Mapping[str, Type] = sourdough.types.Catalog()
    creators: Mapping[str, Type] = sourdough.types.Catalog()
    products: Mapping[str, Type] = sourdough.types.Catalog()
    components: Mapping[str, Type] = sourdough.types.Catalog()
    instances: Mapping[str, object] = sourdough.types.Catalog()
    algorithms: Mapping[str, Type] = sourdough.types.Catalog()
    criteria: Mapping[str, Callable] = sourdough.types.Catalog(
        always_return_list= True)

    """ Properties """
    
    @property
    def component_suffixes(self) -> Tuple[str]: 
        return tuple(k + 's' for k in self.components.keys()) 
  
options = Options()


@dataclasses.dataclass
class Bases(sourdough.quirks.Loader):
    """Base classes for a sourdough projects.
    
    Bases can be set at the Project and/or Manager level. This allows specific
    Managers to use alternatives to the default base classes.
    
    Args:
        settings (Union[str, Type]): the configuration class to use in a 
            sourdough project. Defaults to 'sourdough.Settings'.
        clerk (Union[str, Type]): the file clerk class to use in a sourdough 
            project. Defaults to 'sourdough.Clerk'.   
        creator (Union[str, Type]): the product builder class to use in a 
            sourdough project. Defaults to 'sourdough.Creator'.    
        product (Union[str, Type]): the product output class to use in a 
            sourdough project. Defaults to 'sourdough.Product'. 
        component (Union[str, Type]): the node class to use in a sourdough 
            project. Defaults to 'sourdough.Component'. 
        workflow (Union[str, Type]): the workflow to use in a sourdough 
            project. Defaults to 'sourdough.products.Workflow'.
        default_workflow (Union[str, Type]): the workflow to use in a sourdough 
            project. Defaults to 'sourdough.workflows.Pipeline'.  
            
    """
    settings: Union[str, Type] = 'sourdough.Settings'
    clerk: Union[str, Type] = 'sourdough.Clerk'
    manager: Union[str, Type] = 'sourdough.Manager'
    creator: Union[str, Type] = 'sourdough.Creator'
    product: Union[str, Type] = 'sourdough.Product'
    component: Union[str, Type] = 'sourdough.Component'
    algorithm: Union[str, Type] = 'sourdough.Algorithm'
    criteria: Union[str, Type] = 'sourdough.Criteria'
    workflow: Union[str, Type] = 'sourdough.products.Workflow'
    default_workflow: Union[str, Type] = 'sourdough.workflows.Pipeline'

bases = Bases()  