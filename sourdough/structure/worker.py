"""
.. module:: worker
:synopsis: sourdough project workers
:publisher: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import abc
import dataclasses
import copy
import inspect
from typing import (
    Any, Callable, ClassVar, Dict, Iterable, List, Optional, Tuple, Union)

import sourdough


@dataclasses.dataclass
class Overview(sourdough.base.MappingBase):
    """Base class for outlining a sourdough project.

    Args:
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. If the class instance
            needs settings from the shared Settings instance, 'name' should
            match the appropriate section name in that Settings instance. When
            subclassing, it is a good settings to use the same 'name' attribute
            as the base class for effective coordination between sourdough
            classes. Defaults to None or __class__.__name__.lower().
        contents (Dict[str, List[str]]): a dictionary with keys corresponding
            to worker names and a list of tasks in the values. Defaults to an
            empty dictionary.

    """
    name: Optional[str] = None
    contents: Optional[Dict[str, 'Overview']] = dataclasses.field(
            default_factory = dict)

    """ Public Methods """
    
    def add(self, 
            worker: str, 
            tasks: Union[List[str], str]) -> None:
        """Adds 'tasks' to 'contents' with a 'worker' key.
        
        Args:
            worker (str): key to use to store 'tasks':
            tasks (Union[List[str], str]): name(s) of task(s) to add to 
                'contents'.
        
        """
        self.contents[worker] = sourdough.utilities.listify(tasks)
        return self
    
    # def add(self, 
    #         section: str,
    #         component: 'sourdough.Component', 
    #         key: Optional[str] = None) -> None:
    #     """Adds 'component' to 'contents'.

    #     Args:
    #         component ('sourdough.Component'): component object to add to add
    #         key {Optional[str]} -- [description] (default: {None})

    #     Returns:
    #         [type] -- [description]
    #     """
    #     if key is None:
    #         key = component.name
    #     self.contents[key] = component
    #     return self
    
    # def convert_settings(self, 
    #         settings: Union['sourdough.Settings', Dict[str, Any]],
    #         name: Optional[str] = None) -> None:
    #     """
    #     """
    #     if not name:
    #         name = 'project'
    #     project_workers = sourdough.utilities.listify(
    #         settings[name][f'{name}_workers'])
    #     for worker in project_workers:
    #         self._parse_section(section = settings[worker], name = worker)
    #     return self
        
    # """ Private Methods """

    # def _parse_section(self, section: Dict[str, Any], name: str) -> None:
    #     self.contents[name] = {}
    #     try:
    #         workers = sourdough.utilities.listify(section[f'{name}_workers'])
    #     except KeyError:
    #         workers = []
    #     task_keys = [k for k in section.keys() if k.endswith('_techniques')]
    #     self.contents[name]['workers'] = workers
    #     try:
    #         self.contents[name]['design'] = section[f'{name}_design']
    #     except KeyError:
    #         self.contents[name]['design'] = None
    #     if len(task_keys) > 0:
    #         self.contents[name]['stores_tasks'] = True
    #         for task_key in task_keys:
    #             task_name = task_key.replace('_techniques', '')
    #             if task_name in workers:
    #                 techniques = sourdough.utilities.listify(section[task_key])
    #                 self.contents[name][task_name] = techniques
    #     else:
    #         self.contents[name]['stores_tasks'] = False
    #     return self
    

@dataclasses.dataclass
class Worker(sourdough.base.SequenceBase):
    """Contains information and objects to create parts of a Project.
    
    Args:
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. For example if a 
            class instance needs settings from the shared Settings instance, 
            'name' should match the appropriate section name in that Settings 
            instance. When subclassing, it is sometimes a good idea to use the 
            same 'name' attribute as the base class for effective coordination 
            between sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Component is called, 'name' is set to a snake 
            case version of the class name ('__class__.__name__').
        contents (Optional[List[Union[Worker, sourdough.Task, str]]]): stored 
            Worker or Task instancesm or strings corresponding to keys in 
            'options'. Defaults to an empty list.  
        design (Optional[str]): the name of the structural design that should
            be used to create objects in an instance. This should correspond
            to a key in a Director instance's 'designs' class attribute.
        data (Optional[Any]): a data object to apply any constructed objects to.
            This need only be provided when the class is instanced for
            automatic execution. Defaults to None. If you are working on a data-
            focused project, consider using siMpLify instead 
            (https://github.com/WithPrecedent/simplify). It applies sourdough
            in the data science context. sourdough itself treats 'data' as an
            unknown object of any type which offers more flexibility of design.
        options (ClassVar[sourdough.Options]): an Options instance containing
            either Worker or Technique instances. Defaults to an empty Options 
            instance.
            
    """
    name: Optional[str] = None
    contents: Optional[List[Union[
        'Worker', 
        'sourdough.Task', 
        str]]] = dataclasses.field(default_factory = list)    
    design: Optional[str] = dataclasses.field(
        default_factory = lambda: 'chained')
    data: Optional[Any] = None
    options: ClassVar['sourdough.Options'] = sourdough.Options()

    """ Class Methods """
    
    @classmethod
    def add_option(cls, 
            name: str, 
            option: Union['Worker', 'sourdough.Task']) -> None:
        """Adds an Worker or Task to 'options'.

        Args:
            name (str): key to use for storing 'option'.
            option (Worker, sourdough.Task): the subclass to store in the 
                'options' class attribute.

        Raises:
            TypeError: if 'option' is not a Worker or Task subclass.
            
        """
        if issubclass(option, (Worker, sourdough.Task)):
            cls.options[name] = option
        elif isinstance(option, (Worker, sourdough.Task)):
            cls.options[name] = option.__class__
        else:
            raise TypeError('option must be a Worker or Task subclass')
        return cls  
             
    """ Overview Property """
    
    @property
    def overview(self) -> 'Overview':
        """Returns string snapshot of a SequenceBase subclass instance.
        
        Returns:
            Overview: configured according to the '_get_overview' method.
        
        """
        return self._get_overview() 
    
    """ Private Methods """
           
    def _get_overview(self) -> Union['Overview', List[str]]:
        """Returns names of Worker and Task instances below this instance.
                
        Returns:
            Union['Overview', List[str]]: an Overview instance or list of 
                strings describing the 'contents' attribute.
    
        """
        if isinstance(self.contents, Overview):
            return self.contents
        elif not self.contents:
            self.contents = Overview(name = f'{self.name}_overview')
            return self.contents
        else:
            overview = Overview(name = f'{self.name}_overview')
            for item in self.contents:
                try:
                    overview[item.name] = item._get_overview()
                except AttributeError:
                    overview[item.name] = [i.name for i in item.contents]
            return overview
    