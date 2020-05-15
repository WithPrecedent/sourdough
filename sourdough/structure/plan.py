"""
.. module:: structure
:synopsis: sourdough composite objects
:author: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import abc
import dataclasses
import itertools
import re
from typing import (
    Any, Callable, ClassVar, Dict, Iterable, List, Optional, Tuple, Union)

import sourdough


@dataclasses.dataclass
class Overview(sourdough.base.MappingBase):
    """Base class for outlining a sourdough project.

    Arguments:
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. If the class instance
            needs settings from the shared Settings instance, 'name' should
            match the appropriate section name in that Settings instance. When
            subclassing, it is a good settings to use the same 'name' attribute
            as the base class for effective coordination between sourdough
            classes. Defaults to None or __class__.__name__.lower().
        contents (Dict[str, List[str]]): a dictionary with keys corresponding
            to step names and a list of tasks in the values. Defaults to an
            empty dictionary.

    """
    name: Optional[str] = None
    contents: Optional[Dict[str, 'Overview']] = dataclasses.field(
            default_factory = dict)

    def add(self, component: 'sourdough.Component') -> None:
        """[summary]

        Arguments:
            level {[type]} -- [description]

        Returns:
            [type] -- [description]
            
        """
        self.contents[component.name] = component
        return self


@dataclasses.dataclass
class Plan(sourdough.base.MappingBase):
    """Base class for lists storing sourdough Component instances.

    Plan takes advantage of the 'name' attribute of Component instances. It
    allows flexible access methods using the 'name' attributes of stored items.
    Each 'name' acts as a index to create the facade of a dictionary with the 
    items in the stored list serving as values. This allows for duplicate indexs 
    for storing class instances at the expense of lookup speed. Since normal
    use cases do not include repeat accessing of Plan instances, the loss of 
    lookup speed should have negligible effect on overall performance.
    
    By allowing some dictionary functionality, but storing a list, complicated
    iteration can be more easily implemented. For example, the Manager subclass
    implements a state-tracking iterable that could not easily be implemented
    by a dictionary (even with ordered dictionaries after python 3.6).

    Arguments:
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. If the class instance
            needs settings from the shared Settings instance, 'name' should
            match the appropriate section name in that Settings instance. When
            subclassing, it is a good settings to use the same 'name' attribute
            as the base class for effective coordination between sourdough
            classes. Defaults to None or __class__.__name__.lower().
        items (Optional[List[Component]]): stored iterable of actions to take
            as part of the Plan. Defaults to an empty list.

    """
    name: Optional[str] = None
    items: Optional[List[sourdough.Component]] = dataclasses.field(
        default_factory = list)

    """ Overview Property """
    
    @property
    def overview(self) -> 'Overview':
        """Returns string snapshot of current state of the Plan.
        
        With a basic plan, the overview just appears as a simple dictionary of
        item 'name' attributes as keys and items as values. When using more
        complicated Plan subclasses, such as CompositeProject, the overview
        includes the entire composite structure, appearing as a tree-like
        object.
        
        Returns:
            Overview: configured according to the '_get_overview' method.
        
        """
        return self._get_overview() 
            
    """ Private Methods """
    
    def _get_overview(self) -> Union['sourdough.Overview', List[str]]:
        """Returns Overview instance filled with stored Plan items.
                
        Returns:
            Overview: with 'contents' determined by the Plan 'items'.
        
        """
        overview = sourdough.Overview(name = f'{self.name}_overview')
        for item in self.items:
            overview.add(item)
        return overview

    """ Public Methods """
       
    def add(self, items: Union['Plan', 'sourdough.Component']) -> None:
        """Appends arguments to 'items'.

        If you wish to instead extend 'items' with a Plan, please use the
        normal python 'extend' method. The default implementation of Plan
        assumes that passed Plan instances will be stored as single items, via
        the 'append' method.
        
        Arguments:
            items (Union['Plan', sourdough.Component]): Component(s) to add
                to 'items'.

        """
        self.items.append(items)
        return self    

    """ Dunder Methods """

    def __getitem__(self, 
            index: Union[str, int]) -> Union['Plan', 'sourdough.Component']:
        """Returns value(s) for 'index' in 'items'.
        
        If 'index' is a str type, this method looks for a matching 'name'
        attribute in the stored instances.

        Arguments:
            index (Union[str, int]): name or index to search for in 'items'.

        Returns:
            Union['Plan', sourdough.Component]: value(s) stored in 'items' 
                that corresponder to 'index'.

        """
        if isinstance(index, int):
            return self.items[index]
        else:
            matches = [c for c in self.items if c.name == index]
            if len(matches) == 1:
                return matches[0]
            else:
                return self.__class__(name = self.name, items = matches)

    def __delitem__(self, index: Union[str, int]) -> None:
        """Deletes item matching 'index' in 'items'.

        If 'index' is a str type, this method looks for a matching 'name'
        attribute in the stored instances.

        Arguments:
            index (Union[str, int]): name or index in 'items' to delete.

        """
        if isinstance(index, int):
            del self.items[index]
        else:
            try:
                self.items = [c for c in self.items if c.name != index]
            except AttributeError:
                raise TypeError(
                    f'{self.name} requires a value with a name atttribute')
        return self

    def __iter__(self) -> Iterable:
        """Returns chained iterable of 'items'.
     
        Returns:
            Iterable: using the itertools method which automatically iterates
                all stored iterables within 'items'.Any
               
        """
        return iter(itertools.chain.from_iterable(self.items))


# @dataclasses.dataclass
# class PlanDesigner(abc.ABC):
#     """[summary]

#     Arguments:
#         sourdough {[type]} -- [description]
        
#     """
#     name: Optional[str] = None

#     """ Required Subclass Methods """
    
#     @abc.abstractmethod
#     def create(self, *args, **kwargs) -> NotImplementedError:
#         """Subclasses must provide their own methods."""
#         raise NotImplementedError(
#             'PlanDesigner subclasses must include create methods')


@dataclasses.dataclass
class ParallelPlan(Plan):
    """[summary]

    Arguments:
        sourdough {[type]} -- [description]
        
    """
    name: Optional[str] = None

    """ Public Methods """
    
    def reorganize(self, overview: 'Overview') -> 'Plan':
        """Creates a 'Plan' with a parallel structure.

        Returns:
            'Plan': configured to specifications in 'overview'.

        """
        outer_name = self.name
        inner_name = 'plan'
        # Creates a 'Plan' instance to store other 'Plan' instances.
        outer_plan = sourdough.SerialPlan(name = outer_name)
        # Creates list of steps from 'overview'.
        steps = list(overview.keys())
        # Creates 'possible' list of lists.
        possible = list(overview.values())
        # Creates a list of lists of the Cartesian product of 'possible'.
        combinations = list(map(list, itertools.product(*possible)))
        # Creates a 'inner_plan' for each combination of tasks and adds that
        # 'inner_plan' to 'outer_plan'.
        for i, tasks in enumerate(combinations):
            inner_plan = sourdough.SerialPlan(
                name = f'{inner_name}_{i}',
                extender = False)
            step_tasks = tuple(zip(steps, tasks))
            for task in step_tasks:
                task = self.instructions.task.load()(
                    name = task[0],
                    task = task[1])
                task = self.parametizer.get(task = task)
                inner_plan.add(contents = task)
            outer_plan.add(contents = inner_plan)
        return outer_plan


@dataclasses.dataclass
class SerialPlan(Plan):
    """[summary]

    Arguments:
        sourdough {[type]} -- [description]
        
    """
    name: Optional[str] = None
    
    """ Public Methods """
 
    def create(self,
            overview: Optional[Dict[str,str]] = None,
            outer_name: Optional[str] = None,
            inner_name: Optional[str] = None) -> 'Plan':
        """Drafts a outer_plan with a serial inner_plan structure.

        Returns:
            'Plan': configured to spefications in 'instructions'.

        """
        if overview is None:
            overview = self.overview
        if outer_name is None:
            outer_name = self.instructions.name
        # Creates a 'Plan' instance to store other 'Plan' instances.
        outer_plan = sourdough.Plan(name = outer_name)
        # Creates a 'inner_plan' for each step in 'overview'.
        for step, tasks in self.overview.items():
            inner_plan = sourdough.Plan(name = step)
            for task in tasks:
                task = self.instructions.task(
                    name = step,
                    task = task)
                task = self.parametizer.get(task = task)
                inner_plan.add(contents = task)
            outer_plan.add(contents = inner_plan)
        return outer_plan


# @dataclasses.dataclass
# class PlanFactory(sourdough.base.FactoryBase):
#     """The PlanFactory interface instances a class from available options.

#     Arguments:
#         product (Optional[str]): name of sourdough object to return. 'product' 
#             must correspond to a key in 'products'. Defaults to None.
#         default (ClassVar[str]): the name of the default object to instance. If 
#             'product' is not passed, 'default' is used. 'default' must 
#             correspond  to a key in 'products'. Defaults to None. If 'default'
#             is to be used, it should be specified by a subclass, declared in an
#             instance, or set via the class attribute.
#         products (ClassVar[MutableMapping]): a dictionary or other mapping of 
#             available options for object creation. Keys are the names of the 
#             'product'. Values are the objects to create. Defaults to an 
#             empty dictionary.

#     Returns:
#         Any: the factory uses the '__new__' method to return a different object 
#             instance with kwargs as the parameters.

#     """    
#     product: Optional[str] = None
#     default: ClassVar[str] = 'serial'
#     products: ClassVar[collections.abc.MutableMapping] = {
#         'parallel': ParallelPlan,
#         'serial': SerialPlan,
#         'project': sourdough.Project}