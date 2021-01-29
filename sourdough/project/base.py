"""
base: essential base classes for a sourdough project
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Settings
    Filer
    Workflow
    
    Creator
    Component

"""
from __future__ import annotations
import abc
import dataclasses
import inspect
import pathlib
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import sourdough


@dataclasses.dataclass
class Settings(sourdough.types.Base, sourdough.resources.Configuration):
    """Loads and Stores configuration settings for a Project.

    Args:
        contents (Union[str, pathlib.Path, Mapping[str, Mapping[str, Any]]]): a 
            dict, a str file path to a file with settings, or a pathlib Path to
            a file with settings. Defaults to en empty dict.
        infer_types (bool): whether values in 'contents' are converted to other 
            datatypes (True) or left alone (False). If 'contents' was imported 
            from an .ini file, a False value will leave all values as strings. 
            Defaults to True.
        defaults (Mapping[str, Mapping[str]]): any default options that should
            be used when a user does not provide the corresponding options in 
            their configuration settings. Defaults to a dict with 'general'
            and 'files' section listed in the class annotations.
        skip (Sequence[str]): names of suffixes to skip when constructing nodes
            for a sourdough project.

    """
    contents: Union[str, pathlib.Path, Mapping[str, Mapping[str, Any]]] = (
        dataclasses.field(default_factory = dict))
    infer_types: bool = True
    defaults: Mapping[str, Mapping[str, Any]] = dataclasses.field(
        default_factory = lambda: {
            'general': {
                'verbose': False,
                'parallelize': True,
                'conserve_memery': False},
            'files': {
                'source_format': 'csv',
                'interim_format': 'csv',
                'final_format': 'csv',
                'file_encoding': 'windows-1252'},
            'sourdough': {
                'default_design': 'pipeline'}})
    skip: Sequence[str] = dataclasses.field(
        default_factory = lambda: [
            'general', 
            'files', 
            'sourdough', 
            'parameters'])


@dataclasses.dataclass
class Filer(sourdough.types.Base, sourdough.resources.Clerk):
    pass  


@dataclasses.dataclass
class Workflow(sourdough.types.Base):
    """Stores lightweight graph workflow and corresponding components.
    
    Args:
        graph (sourdough.composites.Graph): a directed acylic graph using an
            adjacency list to represented the graph. Defaults to a Graph.
        components (Library): stores Component instances that correspond to 
            nodes in 'graph'. Defaults to an empty Library.
            
    """  
    graph: sourdough.composites.Graph = dataclasses.field(
        default_factory = sourdough.composites.Graph)
    components: sourdough.types.Library = sourdough.types.Library()
        
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
        self.graph.combine(graph = workflow.graph)
        return self
   
    def execute(self, project: sourdough.Project, copy_components: bool = False,
                **kwargs) -> sourdough.Project:
        """[summary]
        Args:
            project (sourdough.Project): [description]
        Returns:
            sourdough.Project: [description]
            
        """
        for path in self.graph.paths:
            for node in path:
                if copy_components:
                    component = copy.deepcopy(self.components[node])
                else:
                    component = self.components[node]
                project = component.execute(project = project, **kwargs)    
        return project
    
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



@dataclasses.dataclass
class Component(sourdough.quirks.Element, sourdough.types.Base, abc.ABC):
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
    library: ClassVar[sourdough.types.Library] = sourdough.types.Library()

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
class Results(sourdough.quirks.Element, sourdough.types.Lexicon):
    """Stores output of Worker.
    
    Args:
        contents (Mapping[str, Any]]): stored dictionary which contains results
            from a Project workflow's execution. Defaults to an empty dict.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Configuration instance, 
            'name' should match the appropriate section name in a Configuration 
            instance. Defaults to None. 
        identification (str): a unique identification name for a sourdough
            Project. The name is used for creating file folders related to the 
            project. It is attached to a Results instance so that it can be 
            connected pack to other related files from the Project which 
            produced the contained results. Defaults to None.            
            
    """
    contents: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    name: str = None
    identification: str = None
