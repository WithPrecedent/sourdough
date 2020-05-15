"""
.. module:: manager
:synopsis: sourdough project workflow
:publisher: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import dataclasses
from typing import (
    Any, Callable, ClassVar, Dict, Iterable, List, Optional, Tuple, Union)
import warnings

import sourdough

 
@dataclasses.dataclass
class Stage(sourdough.Component):
    """Base class for Components stored by a Manager.
    
    All subclasses must have an 'apply' method.Any
    
    Arguments:
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. If the class instance
            needs settings from the shared Settings instance, 'name' should
            match the appropriate section name in that Settings instance. When
            subclassing, it is a good settings to use the same 'name' attribute
            as the base class for effective coordination between sourdough
            classes. Defaults to None or __class__.__name__.lower().    
    
    """
    name: Optional[str] = None
    
    """ Required Subclass Methods """
    
    def apply(self, *args, **kwargs) -> NotImplementedError:
        """Subclasses must provide their own methods."""
        raise NotImplementedError('Stage subclasses must include apply methods')

 
@dataclasses.dataclass
class Manager(sourdough.Plan, sourdough.mixins.ProxyMixin):
    """Basic project construction and management class.

    Arguments:
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. If the class instance
            needs settings from the shared Settings instance, 'name' should
            match the appropriate section name in that Settings instance. When
            subclassing, it is a good settings to use the same 'name' attribute
            as the base class for effective coordination between sourdough
            classes. Defaults to None or __class__.__name__.lower().
        items (Optional[List[sourdough.Stage]]): list of recognized
            states which correspond to methods within a class instance. 
            Defaults to ['initialize', 'draft', 'publish', 'apply'].
        auto_advance (Optional[bool]): whether to automatically advance 'item'
            when one of the item methods is called (True) or whether 'item'
            must be changed manually by using the 'advance' method (False).
            Defaults to True.

    """

    """ Class Attributes """
    
    stage_options: ClassVar[Dict[str, 'sourdough.Stage']] = {}

    """ Instance Attributes """
    
    name: Optional[str] = None
    stages: List[Union['sourdough.Stage', str]] = dataclasses.field(
        default_factory = list)
    auto_advance: Optional[bool] = True
    project: Optional['sourdough.Project'] = dataclasses.field(
        default_factory = sourdough.Project)
    
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls inherited initialization method.
        super().__post_init__()
        # Removes various python warnings from console output.
        warnings.filterwarnings('ignore')
        # Creates proxy property referring 'stages' access to 'items'. This 
        # allows this instance to use inherited access methods which refer to
        # items.
        self.items = self.stages
        self.proxify(proxy = 'stages', attribute = 'items')
        # Adds 'general' section attributes from 'settings' in 'project'.
        self.project.settings.inject(instance = self)
        # Initializes 'items' to regulate an instance's workflow.
        self.items = self._initialize_stage_options(stages = self.items)
        # Sets current 'stage' and 'index' for that 'stage'.
        self.index = 0
        self.stage = self.items[0].name
        # Advances through 'stages' if 'auto_advance' is True.
        if self.auto_advance:
            self.project = self._auto_stages(project = self.project)

    """ Class Methods """
 
    @classmethod
    def add_stage(cls, name: str, stage: Stage) -> None:
        """Adds a stage to the class variable 'stage_options'.
        
        This allows you to use the 'name' in 'items' to access this new Stage
        subclass.

        Arguments:
            name (key): key to use for storing 'stage'.
            stage (Stage): the subclass to store in 'stage_options'.

        Raises:
            TypeError: if 'stage' is not a Stage subclass.
            
        """
        if issubclass(stage, Stage):
            cls.stage_options[name] = stage
        else:
            raise TypeError('stage must be a sourdough Stage subclass')
        
    """ Public Methods """
    
    def advance(self, stage: Optional[str] = None) -> None:
        """Advances to next item in 'items' or to 'item' argument.

        This method only needs to be called manually if 'auto_advance' is False.
        Otherwise, this method is automatically called when individual item
        methods are called via '__getattribute__'.

        If this method is called at the last item, it does not raise an
        IndexError. It simply leaves 'item' at the last item in the list.

        Arguments:
            item(Optional[str]): name of item in 'items'.
                Defaults to None. If not passed, the method goes to the next
                'item' in items.

        Raises:
            ValueError: if 'item' is neither None nor in 'items'.

        """
        if stage is None or stage in self.stage_options:
            if stage is None:
                try:
                    new_stage = self.items[self.index + 1]
                except IndexError:
                    new_stage = None
            else:
                new_stage = self.stage_options[stage]
            if new_stage:
                self.index += 1
                self.previous_stage = self.stage
                self.stage = new_stage.name
        else:
            raise ValueError(f'{stage} is not a recognized stage')
        return self
    
    """ Dunder Methods """
    
    def __iter__(self) -> Iterable:
        """Returns iterable of methods of 'items'.
        
        Returns:
            Iterable: 'apply' methods of 'items'.
            
        """
        return iter([getattr(s, 'apply') for s in self.items])

    def __next__(self) -> Callable:
        """Returns next method after method matching 'item'.
        
        Returns:
            Callable: next method corresponding to those listed in 
                'stage_options'.
            
        """
        if self.index < len(self.items):
            self.advance()
            return getattr(self.items[self.index], 'apply')
        else:
            raise StopIteration()
     
    """ Private Methods """
        
    def _initialize_stage_options(self, 
            stages: List[Union[str, 'Stage']],
            **kwargs) -> List['Stage']:
        """Creates Stage instances, when necessary, in 'stagess'

        Arguments:
            stages (List[Union[str, Stage]]): a list of strings corresponding to
                keys in the 'stage_options' class attribute, Stage subclasses, 
                or Stage subclass instancces.
            kwargs: any extra arguments to send to each created Stage instance.
                These will have no effect on Stage instances already stored in
                'stage_options'.

        Raises:
            KeyError: if 'stage_options' contains a string which does not match 
                a key in the 'stage_options' class attribute.
            
        Returns:
            List[Stage]: a list with only Stage instances.
                  
        """       
        new_stages = []
        for stage in stages:
            if isinstance(stage, str):
                try:
                    new_stages.append(self.stage_options[stage](**kwargs))
                except KeyError:
                    KeyError(f'{stage} is not a recognized stage')
            elif isinstance(stage, Stage):
                new_stages.append(stage)
            elif issubclass(stage, Stage):
                new_stages.append(stage(**kwargs))
            else:
                raise TypeError(f'{stage} must be a str or Stage type')
        return new_stages

    def _auto_stages(self, project: 'sourdough.Project') -> 'sourdough.Project':
        """Automatically advances through and iterates stored Stage instances.

        Arguments:
            project (Project): an instance containing settings and any data for 
                the project methods to be applied to.
                
        Returns:
            Project: modified by the stored Stage instance's apply methods.
            
        """
        for stage in self.items[1:]:
            self.advance(stage = stage.name)
            project = self.items[self.index].apply(project = project)
        return project
    