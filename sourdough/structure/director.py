"""
.. module:: director
:synopsis: sourdough project workflow
:publisher: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import copy
import dataclasses
from typing import (
    Any, Callable, ClassVar, Dict, Iterable, List, Optional, Tuple, Union)
import warnings

import sourdough
 
 
@dataclasses.dataclass
class Director(sourdough.base.SequenceBase, sourdough.mixins.ProxyMixin):
    """Basic project construction and management class.

    Args:
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. If the class instance
            needs settings from the shared Settings instance, 'name' should
            match the appropriate section name in that Settings instance. When
            subclassing, it is a good settings to use the same 'name' attribute
            as the base class for effective coordination between sourdough
            classes. Defaults to None or __class__.__name__.lower().
        contents (Optional[List[sourdough.Stage]]): list of recognized
            states which correspond to methods within a class instance. 
            Defaults to ['draft', 'edit', 'publish', 'apply'].
        automatic (Optional[bool]): whether to automatically advance 'item'
            when one of the item methods is called (True) or whether 'item'
            must be changed manually by using the 'advance' method (False).
            Defaults to True.

    """
    name: Optional[str] = None
    stages: List[Union['sourdough.Stage', str]] = dataclasses.field(
        default_factory = lambda: ['draft', 'edit', 'publish', 'apply'])
    automatic: Optional[bool] = True
    project: Optional['sourdough.Project'] = dataclasses.field(
        default_factory = sourdough.Project)
    factories: ClassVar[Dict[str, 'sourdough.Component']] = {
        'stage': sourdough.Stage,
        'design': sourdough.Design,
        'task': sourdough.Task}
    
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls inherited initialization method.
        super().__post_init__()
        # Removes various python warnings from console output.
        warnings.filterwarnings('ignore')
        # Creates proxy property referring 'stages' access to 'contents'. This 
        # allows this instance to use inherited access methods which refer to
        # 'contents'.
        self.contents = copy.copy(self.stages)
        self.proxify(proxy = 'stages', attribute = 'contents')
        # Adds 'general' section attributes from 'settings' in 'project'.
        self.project.settings.inject(instance = self)
        # Initializes 'contents' to regulate an instance's workflow.
        self.contents = self._initialize_stages(stages = self.contents)
        # Sets current 'stage' and 'index' for that 'stage'.
        self.index = -1
        self.stage = 'initialize' 
        # Advances through 'stages' if 'automatic' is True.
        if self.automatic:
            self.project = self._auto_stages(project = self.project)
      
    """ Class Methods """
    
    @classmethod
    def add_factory(cls, 
            name: str, 
            factory: 'sourdough.core.base.FactoryBase') -> None:
        """Adds a factory to the 'factories'.

        Args:
            name (str): key to use for storing 'factory'.
            stage (sourdough.core.base.FactoryBase): the subclass to store in 
                the 'factories' attribute.

        Raises:
            TypeError: if 'factory' is not a FactoryBase subclass.
            
        """
        if issubclass(factory, sourdough.core.base.FactoryBase):
            cls.factories[name] = factory
        else:
            raise TypeError('factory must be a sourdough FactoryBase subclass')
        return cls  
            
    """ Public Methods """
          
    def add_stage_option(self, 
            name: str, 
            stage: 'sourdough.structure.stages.StageBase') -> None:
        """Adds a stage to the self.factories['stage'].

        Args:
            name (str): key to use for storing 'stage'.
            stage (sourdough.structure.stages.StageBase): the subclass to store 
                in the 'options' class attribute of self.factories['stage'].

        Raises:
            TypeError: if 'stage' is not a StageBase subclass.
            
        """
        if not hasattr(self, self.factories['stage']):
            self.self.factories['stage'] = self.factories['stage']()
        if issubclass(stage, sourdough.structure.stages.StageBase):
            self.self.factories['stage'].options[name] = stage
        else:
            raise TypeError('stage must be a sourdough StageBase subclass')

    def add_design_option(self, 
            name: str, 
            design: 'sourdough.structure.designs.DesignBase') -> None:
        """Adds a design to the self.factories['design'].

        Args:
            design (DesignBase): the subclass to store in the options' class 
                attribute of self.factories['design'].

        Raises:
            TypeError: if 'design' is not a DesignBase subclass.
            
        """
        if not hasattr(self, self.factories['design']):
            self.self.factories['design'] = self.factories['design']()
        if isinstance(design, sourdough.structure.designs.DesignBase):
            self.self.factories['design'].options[name] = design
        else:
            raise TypeError('design must be a sourdough DesignBase subclass')

    def add_task_option(self, 
            name: str, 
            task: 'sourdough.structure.tasks.TaskBase') -> None:
        """Adds a task to the self.factories['task'].

        Args:
            task (TaskBase): the subclass to store in the options' class 
                attribute of self.factories['task'].

        Raises:
            TypeError: if 'task' is not a TaskBase subclass.
            
        """
        if not hasattr(self, self.factories['task']):
            self.self.factories['task'] = self.factories['task']()
        if isinstance(task, sourdough.structure.TaskBase):
            self.self.factories['task'].options[name] = task
        else:
            raise TypeError('task must be a sourdough TaskBase subclass')
                 
    def advance(self, stage: Optional[str] = None) -> None:
        """Advances to next item in 'contents' or to 'item' argument.

        This method only needs to be called manually if 'automatic' is False.
        Otherwise, this method is automatically called when individual item
        methods are called via '__getattribute__'.

        If this method is called at the last item, it does not raise an
        IndexError. It simply leaves 'item' at the last item in the list.

        Args:
            item(Optional[str]): name of item in 'contents'.
                Defaults to None. If not passed, the method goes to the next
                'item' in contents.

        Raises:
            ValueError: if 'item' is neither None nor in 'contents'.

        """
        if stage is None or stage in self.self.factories['stage'].options:
            if stage is None:
                try:
                    new_stage = self.contents[self.index + 1]
                except IndexError:
                    new_stage = None
            else:
                new_stage = self.self.factories['stage'].options[new_stage]
            if new_stage:
                self.index += 1
                self.previous_stage = self.stage
                self.stage = new_stage
        else:
            raise ValueError(f'{stage} is not a recognized stage')
        return self

    def iterate(self, project: 'sourdough.Project') -> 'sourdough.Project':
        """Advances to next stage and applies that stage to 'project'.

        Args:
            project (sourdough.Project): instance to apply the next stage's
                methods to.
                
        Raises:
            IndexError: if this instance is already at the last stage.

        Returns:
            sourdough.Project: with the last stage applied.
            
        """
        if self.index == len(self.contents) - 1:
            raise IndexError(
                f'{self.name} is at the last stage and cannot further iterate')
        else:
            self.advance()
            self.contents[self.index].apply(project = project)
        return project
            
    """ Dunder Methods """
    
    def __iter__(self) -> Iterable:
        """Returns iterable of methods of 'contents'.
        
        Returns:
            Iterable: 'apply' methods of 'contents'.
            
        """
        return iter([getattr(s, 'apply') for s in self.contents])

    def __next__(self) -> Callable:
        """Returns next method after method matching 'item'.
        
        Returns:
            Callable: next method corresponding to those listed in 
                self.factories['stage'].options'.
            
        """
        if self.index < len(self.contents):
            self.advance()
            return getattr(self.contents[self.index], 'apply')
        else:
            raise StopIteration()
     
    """ Private Methods """

    def _initialize_stages(self, 
            stages: List[Union[str, 'sourdough.StageBase']],
            **kwargs) -> List['sourdough.StageBase']:
        """Creates Stage instances, when necessary, in 'stages'

        Args:
            stages (List[Union[str, StageBase]]): a list of strings
                corresponding to keys in the 'options' class attribute of 
                self.factories['stage'] or StageBase subclass instancces.
            kwargs: any extra arguments to send to each created Stage instance.
                These will have no effect on StageBase subclass instances 
                already stored in the 'options' class attribute of 
                self.factories['stage'].

        Raises:
            KeyError: if 'stages' contains a string which does not match a key 
                in the 'options' class attribute of self.factories['stage'].
            
        Returns:
            List[Stage]: a list with only StageBase instances.
                  
        """       
        new_stages = []
        for stage in stages:
            if isinstance(stage, str):
                try:
                    new_stages.append(
                        self.factories['stage'](product = stage, **kwargs))
                except KeyError:
                    KeyError(f'{stage} is not a recognized stage')
            elif isinstance(stage, sourdough.StageBase):
                new_stages.append(stage)
            elif issubclass(stage, sourdough.StageBase):
                new_stages.append(stage(**kwargs))
            else:
                raise TypeError(f'{stage} must be a str or StageBase type')
        return new_stages
        
    def _auto_stages(self, project: 'sourdough.Project') -> 'sourdough.Project':
        """Automatically advances through and iterates stored Stage instances.

        Args:
            project (Project): an instance containing settings and any data for 
                the project methods to be applied to.
                
        Returns:
            Project: modified by the stored Stage instance's apply methods.
            
        """
        for stage in self.contents:
            self.iterate(project = project)
        return project
