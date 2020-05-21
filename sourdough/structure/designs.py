"""
.. module:: designs
:synopsis: customizes sourdough Employee instances
:author: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import abc
import dataclasses
from typing import (
    Any, Callable, ClassVar, Dict, Iterable, List, Optional, Tuple, Union)

import sourdough


@dataclasses.dataclass
class DesignBase(abc.ABC):
    """[summary]

    Args:
        sourdough {[type]} -- [description]
        
    """
    name: Optional[str] = None

    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def apply(self, *args, **kwargs) -> NotImplementedError:
        """Subclasses must provide their own methods."""
        raise NotImplementedError(
            'Design subclasses must include apply methods')


@dataclasses.dataclass
class ComparativeDesign(DesignBase):
    """[summary]

    Args:
        sourdough {[type]} -- [description]
        
    """
    name: Optional[str] = None

    """ Public Methods """
    
    def apply(self, overview: 'Overview') -> 'SequenceBase':
        """Creates a 'SequenceBase' with a comparative structure.

        Returns:
            'SequenceBase': configured to specifications in 'overview'.

        """
        outer_name = self.name
        inner_name = 'employee'
        # Creates a 'SequenceBase' instance to store other 'SequenceBase' instances.
        outer_employee = sourdough.ChainedSequenceBase(name = outer_name)
        # Creates list of workers from 'overview'.
        workers = list(overview.keys())
        # Creates 'possible' list of lists.
        possible = list(overview.values())
        # Creates a list of lists of the Cartesian product of 'possible'.
        combinations = list(map(list, itertools.product(*possible)))
        # Creates a 'inner_employee' for each combination of tasks and adds that
        # 'inner_employee' to 'outer_employee'.
        for i, tasks in enumerate(combinations):
            inner_employee = sourdough.ChainedSequenceBase(
                name = f'{inner_name}_{i}',
                extender = False)
            worker_tasks = tuple(zip(workers, tasks))
            for task in worker_tasks:
                task = self.instructions.task.load()(
                    name = task[0],
                    task = task[1])
                task = self.parametizer.get(task = task)
                inner_employee.add(contents = task)
            outer_employee.add(contents = inner_employee)
        return outer_employee


@dataclasses.dataclass
class ChainedDesign(DesignBase):
    """[summary]

    Args:
        sourdough {[type]} -- [description]
        
    """
    name: Optional[str] = None
    
    """ Public Methods """
 
    def apply(self,
            overview: Optional[Dict[str,str]] = None,
            outer_name: Optional[str] = None,
            inner_name: Optional[str] = None) -> 'SequenceBase':
        """Drafts a outer_employee with a chained inner_employee structure.

        Returns:
            'SequenceBase': configured to spefications in 'instructions'.

        """
        if overview is None:
            overview = self.overview
        if outer_name is None:
            outer_name = self.instructions.name
        # Creates a 'SequenceBase' instance to store other 'SequenceBase' instances.
        outer_employee = sourdough.base.SequenceBase(name = outer_name)
        # Creates a 'inner_employee' for each worker in 'overview'.
        for worker, tasks in self.overview.items():
            inner_employee = sourdough.base.SequenceBase(name = worker)
            for task in tasks:
                task = self.instructions.task(
                    name = worker,
                    task = task)
                task = self.parametizer.get(task = task)
                inner_employee.add(contents = task)
            outer_employee.add(contents = inner_employee)
        return outer_employee
    

@dataclasses.dataclass
class Design(sourdough.core.base.FactoryBase):
    """A factory for creating and returning DesigneBase subclass instances.

    Args:
        product (Optional[str]): name of sourdough object to return. 'product' 
            must correspond to a key in 'products'. Defaults to None.
        default (ClassVar[str]): the name of the default object to instance. If 
            'product' is not passed, 'default' is used. 'default' must 
            correspond  to a key in 'products'. Defaults to None. If 'default'
            is to be used, it should be specified by a subclass, declared in an
            instance, or set via the class attribute.
        options (Dict[str, 'DesignBase']): a dictionary of available options for 
            object creation. Keys are the names of the 'product'. Values are the 
            objects to create. Defaults to an a dictionary with the managers 
            included in sourdough.

    Returns:
        Any: the factory uses the '__new__' method to return a different object 
            instance with kwargs as the parameters.

    """
    product: Optional[str] = None
    default: ClassVar[str] = 'chained'
    options: ClassVar[Dict[str, 'DesignBase']] = {
        'comparative': ComparativeDesign,
        'chained': ChainedDesign}
