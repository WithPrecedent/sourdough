"""
base: essential classes executeing sourdough's core to a project
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Bases
    Settings
    Filer
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
class Settings(sourdough.resources.Configuration):
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
class Filer(sourdough.resources.Clerk):
    pass  


@dataclasses.dataclass
class Workflow(object):
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
class Results(sourdough.Product):
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

