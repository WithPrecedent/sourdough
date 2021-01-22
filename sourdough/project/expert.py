"""
expert: 
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:



"""
from __future__ import annotations
import dataclasses
import multiprocessing
import textwrap
from types import ModuleType
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import sourdough

 

@dataclasses.dataclass
class Factory(object):

    project
    
    """ Public Methods """
    
    def draft(self, name: str) -> sourdough.types.Lexicon: 
        base = self._get_design(name = name)
        section = self.manager.settings[name]
        
    def build(self, name: str) -> Workflow:
        
        
    def apply(self, name: str) -> sourdough.types.Lexicon:
        

    """ Private Methods """
    
    def _get_design(self, name: str) -> Workflow:
        """[summary]

        Args:
            name (str): [description]
            design (str): [description]
            manager (sourdough.Manager): [description]

        Returns:
            str: [description]
            
        """
        try:
            design = self.manager.settings[name][f'{name}_design']
        except KeyError:
            design = self.manager.bases.default_design
        return self.manager.bases.component.registry.select(key = design)

    def _get_parameters(self, name: str, 
                        manager: sourdough.Manager) -> Dict[Any, Any]:
        """[summary]

        Args:
            name (str): [description]
            project (sourdough.Manager): [description]

        Returns:
            sourdough.types.Lexicon: [description]
            
        """
        try:
            return manager.project.settings[f'{name}_parameters']
        except KeyError:
            return {}


@dataclasses.dataclass
class Node(sourdough.quirks.Registrar, sourdough.quirks.Element, 
           sourdough.types.Progression):
    """Information to construct a sourdough Component.
    
    Args:
        contents (Sequence[str]): stored list of str. Included items should 
            correspond to keys in an Outline and/or Component subclasses. 
            Defaults to an empty list.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Configuration instance, 'name' 
            should match the appropriate section name in the Configuration instance.
            Defaults to None. 
        design (str): name of design base class associated with the Component
            to be created. Defaults to None.
        parameters (Mapping[str, Any]): parameters to be used for the stored
            object(s) in its/their product. Defaults to an empty dict.
        attributes (Mapping[str, Any]): attributes to add to the created
            Component object. The keys should be name of the attribute and the
            values should be the value stored for that attribute. Defaults to
            an empty dict.
            
    """
    contents: Sequence[str] = dataclasses.field(default_factory = list)
    name: str = None
    design: str = None
    parameters: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    attributes: Mapping[str, Any] = dataclasses.field(default_factory = dict)









@dataclasses.dataclass
class Workflow(sourdough.project.Component, sourdough.Hybrid):
    """Base iterable class for portions of a sourdough project.
    
    Args:
        contents (Any): stored item(s) which must have 'name' attributes. 
            Defaults to an empty list.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Configuration instance, 
            'name' should match the appropriate section name in a Configuration 
            instance. Defaults to None. 
        parameters (Mapping[Any, Any]]): parameters to be attached to 'contents' 
            when the 'apply' method is called. Defaults to an empty dict.
        iterations (Union[int, str]): number of times the 'apply' method should 
            be called. If 'iterations' is 'infinite', the 'apply' method will
            continue indefinitely unless the method stops further iteration.
            Defaults to 1.
        criteria (str): after iteration is complete, a 'criteria' determines
            what should be outputted. This should correspond to a key in the
            'algorithms' Catalog for the corresponding sourdough Manager. 
            Defaults to None.
        parallel (ClassVar[bool]): whether the 'contents' contain other 
            iterables (True) or static objects (False). If True, a subclass
            should include a custom iterable for navigating the stored 
            iterables. Defaults to False.
            
    """
    contents: Sequence[Any] = dataclasses.field(default_factory = list)
    name: str = None
    worker: Worker = dataclasses.field(repr = False, default = None)
    parameters: Mapping[Any, Any] = dataclasses.field(default_factory = dict)
    iterations: Union[int, str] = 1
    criteria: Union[str, Callable, Sequence[Union[Callable, str]]] = None
    parallel: ClassVar[bool] = False
 
    

@dataclasses.dataclass
class Worker(sourdough.quirks.Registar, sourdough.quirks.Element, 
             collections.abc.MutableSequence):
    """Base container class for sourdough composite objects.
    
    A Workflow has a 'name' attribute for internal referencing and to allow 
    sourdough iterables to function propertly. Workflow instances can be used 
    to create a variety of composite workflows such as trees, cycles, contests, 
    studies, and graphs.
    
    Args:
        contents (Any): item(s) contained by a Workflow instance.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Configuration instance, 
            'name' should match the appropriate section name in a Configuration 
            instance. Defaults to None. 
        parameters (Mapping[Any, Any]]): parameters to be attached to 'contents' 
            when the 'apply' method is called. Defaults to an empty dict.
        iterations (Union[int, str]): number of times the 'apply' method should 
            be called. If 'iterations' is 'infinite', the 'apply' method will
            continue indefinitely unless the method stops further iteration.
            Defaults to 1.
        criteria (str): after iteration is complete, a 'criteria' determines
            what should be outputted. This should correspond to a key in the
            'algorithms' Catalog for the corresponding sourdough Manager. 
            Defaults to None.
        parallel (ClassVar[bool]): whether the 'contents' contain other 
            iterables (True) or static objects (False). If True, a subclass
            should include a custom iterable for navigating the stored 
            iterables. Defaults to False.
            
    """ 
    name: str = None
    parent: Workflow = None
    contents: Sequence[Workflow] = dataclasses.field(default_factory = list)
    parameters: Mapping[Any, Any] = dataclasses.field(default_factory = dict)

    
    """ Public Methods """

    def implement(self, data: Any) -> Any:
        """[summary]

        Args:
            data (Any): [description]

        Returns:
            Any: [description]
        """
        datasets = []
        for i in self.iterations:
            if self.parallel:
                if sourdough.settings.parallelize:
                    datasets.append(self.implementation(data = data))
            else:
                data = self.implementation(data = data)
        return data     

    """ Private Methods """

    def _implement_parallel(self, data: Any) -> Any:
        """Applies 'implementation' to data.
        
        Args:
            data (Any): any item needed for the class 'implementation' to be
                applied.
                
        Returns:
            Any: item after 'implementation has been applied.

        """  
        return data 

    def _implement_parallel_in_parallel(self, data: Any) -> Any:
        """Applies 'implementation' to data.
        
        Args:
            data (Any): any item needed for the class 'implementation' to be
                applied.
                
        Returns:
            Any: item after 'implementation has been applied.

        """
        all_data = []  
        multiprocessing.set_start_method('spawn')
        with multiprocessing.Pool() as pool:
            all_data = pool.starmap(self.implementation, data)
        return all_data  
    
    def _implement_parallel_in_serial(self, data: Any) -> Any:
        """Applies 'implementation' to data.
        
        Args:
            data (Any): any item needed for the class 'implementation' to be
                applied.
                
        Returns:
            Any: item after 'implementation has been applied.

        """  
        all_data = []
        all_data.append(self.implementation(data = data))
        return data   
                    

@dataclasses.dataclass
class Contest(Worker):
    """Stores Workflows in a comparative parallel workflow and chooses the best.

    Distinguishing characteristics of a Contest:
        1) Applies different components in parallel.
        2) Chooses the best stored Component based upon 'criteria'.
        3) Each stored Component is only attached to the Contest with exactly 
            one connection (these connections are not defined separately - they
            are simply part of the parallel workflow).
        
    Args:
        contents (Sequence[Component]): Component subclass instances. Defaults 
            to an empty list.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Configuration instance, 'name' 
            should match the appropriate section name in the Configuration instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes.
        iterations (Union[int, str]): number of times the 'apply' method should 
            be called. If 'iterations' is 'infinite', the 'apply' method will
            continue indefinitely unless the method stops further iteration.
            Defaults to 1.
        criteria (str): after iteration is complete, a 'criteria' determines
            what should be outputted. This should correspond to a key in the
            'algorithms' Catalog for the sourdough manager.project. Defaults to None.
        parallel (ClassVar[bool]): whether the 'contents' contain other 
            iterables (True) or static objects (False). If True, a subclass
            should include a custom iterable for navigating the stored 
            iterables. Defaults to True.
                            
    """
    contents: Sequence[sourdough.project.Component] = dataclasses.field(
        default_factory = list)
    name: str = None
    iterations: Union[int, str] = 1
    criteria: str = None
    parallel: ClassVar[bool] = True
    
    
@dataclasses.dataclass
class Study(Worker):
    """Stores Flows in a comparative parallel workflow.

    Distinguishing characteristics of a Study:
        1) Applies different components and creates new branches of the overall
            Project workflow.
        2) Maintains all of the repetitions without selecting or averaging the 
            results.
        3) Each stored Component is only attached to the Study with exactly 
            one connection (these connections are not defined separately - they
            are simply part of the parallel workflow).
                      
    Args:
        contents (Sequence[Component]): Component subclass instances. Defaults 
            to an empty list.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Configuration instance, 'name' 
            should match the appropriate section name in the Configuration instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes.
        iterations (Union[int, str]): number of times the 'apply' method should 
            be called. If 'iterations' is 'infinite', the 'apply' method will
            continue indefinitely unless the method stops further iteration.
            Defaults to 1.
        criteria (str): after iteration is complete, a 'criteria' determines
            what should be outputted. This should correspond to a key in the
            'algorithms' Catalog for the sourdough manager.project. Defaults to None.
        parallel (ClassVar[bool]): whether the 'contents' contain other 
            iterables (True) or static objects (False). If True, a subclass
            should include a custom iterable for navigating the stored 
            iterables. Defaults to True.
                            
    """
    contents: Sequence[sourdough.project.Component] = dataclasses.field(
        default_factory = list)
    name: str = None
    iterations: Union[int, str] = 1
    criteria: str = None
    parallel: ClassVar[bool] = True
        
    
@dataclasses.dataclass
class Survey(Worker):
    """Stores Flows in a comparative parallel workflow and averages results.

    Distinguishing characteristics of a Survey:
        1) Applies different components in parallel.
        2) Averages or otherwise combines the results based upon selected 
            criteria.
        3) Each stored Component is only attached to the Survey with exactly 
            one connection (these connections are not defined separately - they
            are simply part of the parallel workflow).    
                    
    Args:
        contents (Sequence[Component]): Component subclass instances. Defaults 
            to an empty list.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Configuration instance, 'name' 
            should match the appropriate section name in the Configuration instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes.
        iterations (Union[int, str]): number of times the 'apply' method should 
            be called. If 'iterations' is 'infinite', the 'apply' method will
            continue indefinitely unless the method stops further iteration.
            Defaults to 1.
        criteria (str): after iteration is complete, a 'criteria' determines
            what should be outputted. This should correspond to a key in the
            'algorithms' Catalog for the sourdough manager.project. Defaults to None.
        parallel (ClassVar[bool]): whether the 'contents' contain other 
            iterables (True) or static objects (False). If True, a subclass
            should include a custom iterable for navigating the stored 
            iterables. Defaults to True.
                            
    """
    contents: Sequence[sourdough.project.Component] = dataclasses.field(
        default_factory = list)
    name: str = None
    iterations: Union[int, str] = 1
    criteria: str = None
    parallel: ClassVar[bool] = True   
       