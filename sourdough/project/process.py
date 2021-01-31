"""
process:
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Workflow

"""
from __future__ import annotations
import abc
import collections.abc
import copy
import dataclasses
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import sourdough


@dataclasses.dataclass
class Workflow(sourdough.Base, collections.abc.Iterator):
    """Stores lightweight graph workflow and corresponding components.
    
    Args:
        graph (sourdough.Graph): a directed acylic graph using an
            adjacency list to represented the graph. Defaults to a Graph.
        components (Library): stores Component instances that correspond to 
            nodes in 'graph'. Defaults to an empty Library.
            
    """  
    graph: sourdough.Graph = dataclasses.field(
        default_factory = sourdough.Graph)
    components: sourdough.Library = sourdough.Library()
    paths: Mapping[str: str] = dataclasses.field(default_factory = dict)
    copy_components: ClassVar[bool] = False
    copy_data: ClassVar[bool] = False
        
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
        try:
            self.graph.combine(graph = workflow.graph)
        except ValueError:
            self.graph = workflow.graph
        return self
   
    def execute(self, 
                project: sourdough.Project, 
                copy_components: bool = False,
                separate_data: bool = False,
                **kwargs) -> sourdough.Project:
        """Iterates over 'graph', using 'components'.
        
        Args:
            project (sourdough.Project): [description]
            
        Returns:
            sourdough.Project: [description]
            
        """
        print('test execute', self.graph)
        for path in self.graph.paths:
            for node in path:
                if copy_components:
                    component = copy.deepcopy(self.components[node])
                else:
                    component = self.components[node]
                project = component.execute(project = project, **kwargs)    
        return project

    """ Private Methods """
   
    # def _implement_parallel_in_parallel(self, data: Any) -> Any:
    #     """Applies 'implementation' to data.
        
    #     Args:
    #         data (Any): any item needed for the class 'implementation' to be
    #             applied.
                
    #     Returns:
    #         Any: item after 'implementation has been applied.

    #     """
    #     all_data = []  
    #     multiprocessing.set_start_method('spawn')
    #     with multiprocessing.Pool() as pool:
    #         all_data = pool.starmap(self.implementation, data)
    #     return all_data  
    
    """ Dunder Methods """
    
    def __iter__(self) -> Iterable:
        """Returns iterable of 'contents'.

        Returns:
            Iterable: 'contents'.

        """
        return iter(self.contents)
    
    
    def __next__(self) -> Iterable:
        """Returns iterable of 'contents'.

        Returns:
            Iterable: 'contents'.

        """
        return iter(self.contents)
        

@dataclasses.dataclass
class Component(sourdough.quirks.Element, sourdough.Base, abc.ABC):
    """Abstract base for parts of a sourdough composite workflow.
    
    All subclasses must have an 'implement' method.
    
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Configuration instance, 
            'name' should match the appropriate section name in a Configuration 
            instance. Defaults to None.
        contents (Any): stored item for use by a Component subclass instance.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        parameters (Mapping[Any, Any]]): parameters to be attached to 'contents' 
            when the 'implement' method is called. Defaults to an empty dict.
        parallel (ClassVar[bool]): indicates whether this Component design is
            meant to be at the end of a parallel workflow structure. Defaults to 
            False.
        library (ClassVar[Library]): related Library instance that will store
            subclasses and allow runtime construction and instancing of those
            stored subclasses.
                
    """
    name: str = None
    contents: Any = None
    iterations: Union[int, str] = 1
    parameters: Mapping[Any, Any] = dataclasses.field(default_factory = dict)
    parallel: ClassVar[bool] = False
    library: ClassVar[sourdough.Library] = sourdough.Library()

    """ Public Methods """
    
    def execute(self, project: sourdough.Project, **kwargs) -> sourdough.Project:
        """Calls 'implement' a number of times based on 'iterations'.
        
        Args:
            project (Project): sourdough project to apply changes to and/or
                gather needed data from.
                
        Returns:
            Project: with possible alterations made.       
        
        """
        if self.iterations in ['infinite']:
            while True:
                project = self.implement(project = project, **kwargs)
        else:
            for iteration in self.iterations:
                project = self.implement(project = project, **kwargs)
        return project

    def implement(self, project: sourdough.Project, **kwargs) -> sourdough.Project:
        """Applies stored 'contents' with 'parameters'.
        
        Args:
            project (Project): sourdough project to apply changes to and/or
                gather needed data from.
                
        Returns:
            Project: with possible alterations made.       
        
        """
        if self.contents not in [None, 'None', 'none']:
            project = self.contents.implement(
                project = project, 
                **self.parameters, 
                **kwargs)
        return project
        
        
@dataclasses.dataclass
class Technique(sourdough.Proxy, Component):
    """Base class for primitive objects in a sourdough composite object.
    
    The 'contents' and 'parameters' attributes are combined at the last moment
    to allow for runtime alterations.
    
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Configuration instance, 
            'name' should match the appropriate section name in a Configuration 
            instance. Defaults to None.
        contents (Any): stored item for use by a Component subclass instance.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        parameters (Mapping[Any, Any]]): parameters to be attached to 'contents' 
            when the 'implement' method is called. Defaults to an empty dict.
        parallel (ClassVar[bool]): indicates whether this Component design is
            meant to be at the end of a parallel workflow structure. Defaults to 
            False.
                                               
    """
    name: str = None
    contents: Callable = None
    iterations: Union[int, str] = 1
    parameters: Mapping[Any, Any] = dataclasses.field(default_factory = dict)
    parallel: ClassVar[bool] = False

    """ Properties """
    
    @property
    def algorithm(self) -> Union[object, str]:
        return self.contents
    
    @algorithm.setter
    def algorithm(self, value: Union[object, str]) -> None:
        self.contents = value
        return self
    
    @algorithm.deleter
    def algorithm(self) -> None:
        self.contents = None
        return self

        
@dataclasses.dataclass
class Step(sourdough.Proxy, Component):
    """Wrapper for a Technique.

    Subclasses of Step can store additional methods and attributes to implement to 
    all possible technique instances that could be used. This is often useful 
    when using parallel Worklow instances which test a variety of strategies 
    with similar or identical parameters and/or methods.

    A Step instance will try to return attributes from Technique if the
    attribute is not found in the Step instance. 

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Configuration instance, 
            'name' should match the appropriate section name in a Configuration 
            instance. Defaults to None.
        contents (Technique): stored Technique instance used by the 'implement' 
            method.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        parameters (Mapping[Any, Any]]): parameters to be attached to 'contents' 
            when the 'implement' method is called. Defaults to an empty dict.
        parallel (ClassVar[bool]): indicates whether this Component design is
            meant to be at the end of a parallel workflow structure. Defaults to 
            False.
                                                
    """
    name: str = None
    contents: Technique = None
    iterations: Union[int, str] = 1
    parameters: Mapping[Any, Any] = dataclasses.field(default_factory = dict)
    parallel: ClassVar[bool] = False
                
    """ Properties """
    
    @property
    def technique(self) -> Technique:
        return self.contents
    
    @technique.setter
    def technique(self, value: Technique) -> None:
        self.contents = value
        return self
    
    @technique.deleter
    def technique(self) -> None:
        self.contents = None
        return self

    """ Public Methods """
    
    def implement(self, project: sourdough.Project, **kwargs) -> sourdough.Project:
        """Applies stored 'contents' with 'parameters'.
        
        Args:
            project (Project): sourdough project to apply changes to and/or
                gather needed data from.
                
        Returns:
            Project: with possible alterations made.       
        
        """
        if self.contents not in [None, 'None', 'none']:
            project = self.contents.implement(
                project = project, 
                **self.parameters, 
                **kwargs)
        return project


@dataclasses.dataclass
class Pipeline(Component):
    """
        
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Configuration instance, 
            'name' should match the appropriate section name in a Configuration 
            instance. Defaults to None.
        contents (Callable): stored item used by the 'implement' method.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        parameters (Mapping[Any, Any]]): parameters to be attached to 'contents' 
            when the 'implement' method is called. Defaults to an empty dict.
        parallel (ClassVar[bool]): indicates whether this Component design is
            meant to be at the end of a parallel workflow structure. Defaults to 
            True.    
                        
    """
    name: str = None
    contents: Callable = None
    iterations: Union[int, str] = 1
    parameters: Mapping[Any, Any] = dataclasses.field(default_factory = dict)
    parallel: ClassVar[bool] = False

    """ Public Methods """
    
    def implement(self, project: sourdough.Project, **kwargs) -> sourdough.Project:
        """Applies stored 'contents' with 'parameters'.
        
        Args:
            project (Project): sourdough project to apply changes to and/or
                gather needed data from.
                
        Returns:
            Project: with possible alterations made.       
        
        """
        if 'bases' in kwargs:
            bases = kwargs.pop('bases')
        else:
            bases = project.bases
        if isinstance(project.workflow.active, List):
            components = [
                bases.Component.library.borrow(c) 
                for c in project.workflow.active]
            project.results.best = self.contents(components)      
        return project
    
    
@dataclasses.dataclass
class Contest(Component):
    """Resolves a parallel workflow by selecting the best option.

    It resolves a parallel workflow based upon criteria in 'contents'
        
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Configuration instance, 
            'name' should match the appropriate section name in a Configuration 
            instance. Defaults to None.
        contents (Callable): stored item used by the 'implement' method.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        parameters (Mapping[Any, Any]]): parameters to be attached to 'contents' 
            when the 'implement' method is called. Defaults to an empty dict.
        parallel (ClassVar[bool]): indicates whether this Component design is
            meant to be at the end of a parallel workflow structure. Defaults to 
            True.    
                        
    """
    name: str = None
    contents: Callable = None
    iterations: Union[int, str] = 1
    parameters: Mapping[Any, Any] = dataclasses.field(default_factory = dict)
    parallel: ClassVar[bool] = True

    """ Public Methods """
    
    def implement(self, project: sourdough.Project, **kwargs) -> sourdough.Project:
        """Applies stored 'contents' with 'parameters'.
        
        Args:
            project (Project): sourdough project to apply changes to and/or
                gather needed data from.
                
        Returns:
            Project: with possible alterations made.       
        
        """
        if 'bases' in kwargs:
            bases = kwargs.pop('bases')
        else:
            bases = project.bases
        if isinstance(project.workflow.active, List):
            components = [
                bases.Component.library.borrow(c) 
                for c in project.workflow.active]
            project.results.best = self.contents(components)      
        return project
 
    
@dataclasses.dataclass
class Study(Component):
    """Allows parallel workflow to continue

    A Study might be wholly passive or implement some reporting or alterations
    to all parallel workflows.
        
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Configuration instance, 
            'name' should match the appropriate section name in a Configuration 
            instance. Defaults to None.
        contents (Callable): stored item used by the 'implement' method.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        parameters (Mapping[Any, Any]]): parameters to be attached to 'contents' 
            when the 'implement' method is called. Defaults to an empty dict.
        parallel (ClassVar[bool]): indicates whether this Component design is
            meant to be at the end of a parallel workflow structure. Defaults to 
            True.   
                         
    """
    name: str = None
    contents: Callable = None
    iterations: Union[int, str] = 1
    parameters: Mapping[Any, Any] = dataclasses.field(default_factory = dict)
    parallel: ClassVar[bool] = True

    """ Public Methods """
    
    def implement(self, project: sourdough.Project, **kwargs) -> sourdough.Project:
        """Applies stored 'contents' with 'parameters'.
        
        Args:
            project (Project): sourdough project to apply changes to and/or
                gather needed data from.
                
        Returns:
            Project: with possible alterations made.       
        
        """    
        return project    
        
@dataclasses.dataclass
class Survey(Component):
    """Resolves a parallel workflow by averaging.

    It resolves a parallel workflow based upon the averaging criteria in 
    'contents'
        
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Configuration instance, 
            'name' should match the appropriate section name in a Configuration 
            instance. Defaults to None.
        contents (Callable): stored item used by the 'implement' method.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        parameters (Mapping[Any, Any]]): parameters to be attached to 'contents' 
            when the 'implement' method is called. Defaults to an empty dict.
        parallel (ClassVar[bool]): indicates whether this Component design is
            meant to be at the end of a parallel workflow structure. Defaults to 
            True.   
                          
    """
    name: str = None
    contents: Callable = None
    iterations: Union[int, str] = 1
    parameters: Mapping[Any, Any] = dataclasses.field(default_factory = dict)
    parallel: ClassVar[bool] = True

    """ Public Methods """
    
    def implement(self, project: sourdough.Project, **kwargs) -> sourdough.Project:
        """Applies stored 'contents' with 'parameters'.
        
        Args:
            project (Project): sourdough project to apply changes to and/or
                gather needed data from.
                
        Returns:
            Project: with possible alterations made.       
        
        """
        if 'bases' in kwargs:
            bases = kwargs.pop('bases')
        else:
            bases = project.bases
        if isinstance(project.workflow.active, List):
            components = [
                bases.Component.library.borrow(c) 
                for c in project.workflow.active]
            project.results.best = self.contents(components)      
        return project
    