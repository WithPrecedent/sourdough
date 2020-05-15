"""
.. module:: composite
:synopsis: sourdough CompositeProject and related classes
:author: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import collections.abc
import copy
import dataclasses
import itertools
import re
from typing import (
    Any, Callable, ClassVar, Dict, Iterable, List, Optional, Tuple, Union)
import warnings

import sourdough


@dataclasses.dataclass
class Level(sourdough.Plan):
    
    name: Optional[str] = None
    items: Optional[Union['Level', 'Plan']] = dataclasses.field(
        default_factory = sourdough.Plan)
    section: Optional[str] = None
    hierarchy: Optional[List[str]] = dataclasses.field(default_factory = list)
  
    """ Public Methods """
              
    def draft(self, 
            settings: 'sourdough.Settings', 
            second_level: Optional[bool] = False) -> None:
        
        """[summary]

        Arguments:
            settings {[type]} -- [description]

        Keyword Arguments:
            second_level {Optional[bool]} -- [description] (default: {False})

        Returns:
            [type] -- [description]
            
        """
        if not self.items:
            relevant = self._get_relevant_settings(settings = settings)
        if second_level:
            section = self.name
        else:
            section = self.section
        if len(self.hierarchy) > 1:
            self.items = Level(
                name = self.name, 
                items = relevant,
                section = section,
                hierarchy = self.hierarchy[1:])
            self.items.draft(settings = settings, second_level = False)
        else:
            self.items = sourdough.Plan(
                name = self.name, 
                items = relevant)  
        return self
            
    """ Private Methods """
    
    def _get_overview(self) -> Union['sourdough.Overview', List[str]]:
        """Returns object for the 'overview' property.

        Raises:
            NotImplementedError: if the method is called at the base level of
                a hierarchy.
                
        Returns:
            Union['sourdough.Overview', List[str]]: returns an Overview instance
                unless the method it is called at the second-to-bottom level in
                a hierachy. In that case, a list of strings is returned.
        
        """
        if len(self.hierarchy) > 1:
            if len(self.hierarchy) > 2:
                overview = sourdough.Overview(name = f'{self.name}_overview')
                for item in self.items:
                    overview.add(item)
                return overview
            else:
                return [item.name for item in self.items]
            return overview
        else:
            raise NotImplementedError(
                '_get_overview is not implemented for the base level of a \
                hierarchy')

    def _get_relevant_settings(self, 
            settings: 'sourdough.Settings') -> Dict[str, List[str]]:
        """[summary]

        Arguments:
            settings {[type]} -- [description]

        Returns:
            Dict[str, List[str]] -- [description]
            
        """
        current = self.hierarchy[0]
        try:
            matching = settings[self.name][f'{self.name}_{current}']
        except KeyError:
            matching = settings[self.section][f'{self.name}_{current}']
        return sourdough.utilities.listify(matching)


@dataclasses.dataclass
class CompositeProject(sourdough.Project):
    """[summary]

    Arguments:
        sourdough {[type]} -- [description]
        
    """  
    name: Optional[str] = None
    identification: Optional[str] = None
    settings: Optional['sourddough.Settings'] = None
    filer: Optional['sourdough.Filer'] = None
    data: Optional[Any] = None
    items: Optional[Union['sourdough.Level', 'sourdough.Plan']] = None
    hierarchy: Optional[List[str]] = dataclasses.field(
        default_factory = lambda: ['workers', 'steps', 'tasks'])
    design: Optional[str] = dataclasses.field(
        default_factory = lambda: 'serial')
    
    """ Public Methods """
              
    def draft(self, 
            settings: 'sourdough.Settings', 
            second_level: Optional[bool] = False) -> None:
        """[summary]

        Arguments:
            settings {[type]} -- [description]

        Keyword Arguments:
            second_level {Optional[bool]} -- [description] (default: {False})

        Returns:
            [type] -- [description]
            
        """
        if not self.items:
            relevant = self._get_relevant_settings(settings = settings)
        if len(self.hierarchy) > 1:
            self.items = sourdough.Level(
                name = self.name, 
                items = relevant,
                section = self.name,
                hierarchy = self.hierarchy[1:])
            self.items.draft(settings = settings, second_level = True)
        else:
            self.items = sourdough.Plan(
                name = self.name, 
                items = relevant)  
        return self
                    
    
@dataclasses.dataclass
class CompositeManager(sourdough.Manager):
    """Main entry for Project construction and management.

    Arguments:
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. If the class instance
            needs settings from the shared Settings instance, 'name' should
            match the appropriate section name in that Settings instance. When
            subclassing, it is a good settings to use the same 'name' attribute
            as the base class for effective coordination between sourdough
            classes. Defaults to None or __class__.__name__.lower().
        stages (Optional[List[sourdough.Stage]]): list of recognized
            states which correspond to methods within a class instance. 
            Defaults to ['initialize', 'draft', 'publish', 'apply'].
        auto_advance (Optional[bool]): whether to automatically advance 'stage'
            when one of the stage methods is called (True) or whether 'stage'
            must be changed manually by using the 'advance' method (False).
            Defaults to True.

    """

    """ Class Attributes """
    
    designs: ClassVar[Dict[str, 'sourdough.Design']] = {}
        # 'serial': sourdough.SerialDesign,
        # 'parallel': sourdough.ParallelDesign}
    levels: ClassVar[Dict[str, 'sourdough.Level']] = {
        'workers': sourdough.Worker,
        'steps': sourdough.Step,
        'tasks': sourdough.Task}
    phases: ClassVar[Dict[str, 'sourdough.Stage']] = {
        'initialize': None,
        'draft': sourdough.Author,
        'publish': sourdough.Publisher,
        'apply': sourdough.Reader}

    """ Instance Attributes """
    
    name: Optional[str] = None
    contents: Optional['sourdough.Stages'] = dataclasses.field(
        default_factory = lambda: ['initialize', 'draft', 'publish', 'apply'])
    auto_advance: Optional[bool] = True
    project: Optional['Project'] = dataclasses.field(
        default_factory = sourdough.CompositeProject)
    
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Removes various python warnings from console output.
        warnings.filterwarnings('ignore')
        # Initializes 'project' based upon its attributes.
        self.project = self._initialize_project(project = self.project)
        # Adds 'general' section attributes from 'settings' in 'project'.
        self.project.settings.inject(instance = self)
        # Initializes 'stages' to regulate an instance's workflow.
        self.stages = self._initialize_stages(project = self.project)

    """ Class Methods """
    
    @classmethod
    def add_design(cls, name: str, design: 'sourdough.Design') -> None:
        """[summary]

        Arguments:
            name {str} -- [description]
            design {[type]} -- [description]

        Raises:
            TypeError: [description]
            
        """
        if isinstance(design, sourdough.Design):
            cls.designs[name] = design
        else:
            raise TypeError('design must be a sourdough Design subclass')
        
    @classmethod
    def add_level(cls, name: str, level: 'sourdough.Level') -> None:
        """[summary]

        Arguments:
            name {str} -- [description]
            design {[type]} -- [description]

        Raises:
            TypeError: [description]
            
        """
        if isinstance(level, sourdough.Level):
            cls.levels[name] = level
        else:
            raise TypeError('level must be a sourdough Level subclass')
 
    @classmethod
    def add_stage(cls, name: str, stage: 'sourdough.Stage') -> None:
        """[summary]

        Arguments:
            name {str} -- [description]
            design {[type]} -- [description]

        Raises:
            TypeError: [description]
            
        """
        if isinstance(stage, sourdough.stage):
            cls.stages[name] = stage
        else:
            raise TypeError('stage must be a sourdough Stage subclass')
        

    """ Public Methods """
    
    def advance(self, stage: Optional[str] = None) -> None:
        """Advances to next stage in 'items' or to 'stage' argument.

        This method only needs to be called manually if 'auto_advance' is False.
        Otherwise, this method is automatically called when individual stage
        methods are called via '__getattribute__'.

        If this method is called at the last stage, it does not raise an
        IndexError. It simply leaves 'stage' at the last item in the list.

        Arguments:
            stage(Optional[str]): name of stage in 'items'.
                Defaults to None. If not passed, the method goes to the next
                'stage' in items.

        Raises:
            ValueError: if 'stage' is neither None nor in 'items'.

        """
        if stage is None:
            try:
                new_index = self.index + 1
                self.stage = self.items[new_index].name
                self.index = new_index
                self.previous_stage = self.stage
            except IndexError:
                pass
        elif stage in [w.name for w in self.items]:
            self.stage = stage
            self.index = self.items.index(self[stage.name])
            self.previous_stage = self.stage
        else:
            raise ValueError(f'{stage} is not a recognized stage')
        return self
        
    """ Private Methods """
        
    def _initialize_stages(self, 
            project: Optional[Project] = None) -> Dict[str, 'sourdough.Stage']:
        """[summary]

        Arguments:
            project {Optional[Project]} -- [description] (default: {None})

        Raises:
            KeyError:
            
        Returns:
            Dict[str, sourdough.Stage]:
                  
        """       
        stages = {}
        for stage in project.stages:
            if stage in self.phases:
                stages[stage] = self.phases[stage]()
            else:
                raise KeyError(f'{stage} is not a recognized stage')
        return stages
                            
    def _get_default_items(self) -> List[sourdough.Stage]:
        """Returns a default list of stage Stage instances.
        
        If you do not wish to use the default Stage instances, you can either
        pass a list of instances to 'items' when Manager is instanced or 
        override this method in a subclass.
        
        Returns:
            List[Stage]: instances of Stage which define the characteristics 
                of each stage in a Manager.
                
        """
        return {
            'initialize': None,
            'draft': sourdough.Author(
                name = 'author',
                receives = ('name', 'settings'),
                returns = 'overview',
                design = self.design),
            'publish': sourdough.Publisher(
                name = 'publisher',
                receives = 'overview',
                returns = 'plan',
                design = self.design),
            'apply': sourdough.Reader(
                name = 'reader',
                receives = ('plan', 'data'),
                returns = ('plan', 'data'),
                design = self.design)}
        

