"""
resources: stores classes and objects created at runtime
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:

"""
from __future__ import annotations
import dataclasses
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)
import sourdough


@dataclasses.dataclass
class Options(object):
    """[summary]

    Args:
        
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
  
default_options = options = Options()


@dataclasses.dataclass
class Bases(sourdough.quirks.Loader):
    """Base classes for a sourdough manager.project.
    
    Args:
        settings (Union[str, Type]): the configuration class to use in a 
            sourdough manager.project. Defaults to 'sourdough.Settings'.
        clerk (Union[str, Type]): the file clerk class to use in a sourdough 
            manager.project. Defaults to 'sourdough.Clerk'.   
        creator (Union[str, Type]): the product/builder class to use in a 
            sourdough manager.project. Defaults to 'sourdough.Creator'.    
        product (Union[str, Type]): the product output class to use in a 
            sourdough manager.project. Defaults to 'sourdough.Product'. 
        component (Union[str, Type]): the node class to use in a sourdough 
            manager.project. Defaults to 'sourdough.Component'. 
        workflow (Union[str, Type]): the workflow to use in a sourdough 
            manager.project. Defaults to 'sourdough.products.Workflow'.      
            
    """
    settings: Union[str, Type] = 'sourdough.Settings'
    clerk: Union[str, Type] = 'sourdough.Clerk'
    manager: Union[str, Type] = 'sourdough.Manager'
    creator: Union[str, Type] = 'sourdough.Creator'
    product: Union[str, Type] = 'sourdough.Product'
    component: Union[str, Type] = 'sourdough.Component'
    workflow: Union[str, Type] = 'sourdough.products.Workflow'
    design: Union[str, Type] = 'sourdough.workflows.Pipeline'

default_bases = bases = Bases()  