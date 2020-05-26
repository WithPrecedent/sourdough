"""
.. module:: designs
:synopsis: customizes sourdough Worker instances
:author: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import abc
import dataclasses
import itertools
from typing import (
    Any, Callable, ClassVar, Dict, Iterable, List, Optional, Tuple, Union)

import sourdough


@dataclasses.dataclass
class Design(abc.ABC):
    """Base class for structuring different Worker instances.

    Args:
        settings (sourdough.Settings): an instance which contains information
            about how to design specific Worker instances.
        
    """
    settings: 'sourdough.Settings'

    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def create(self, *args, **kwargs) -> NotImplementedError:
        """Subclasses must provide their own methods."""
        raise NotImplementedError(
            'Design subclasses must include apply methods')

    """ Private Methods """
    
    def _convert_settings(self, 
            section: Dict[str, Any]) -> Dict[str, List[str]]:
        """[summary]

        Args:
            section (Dict[str, Any]): [description]

        Returns:
            Dict[str, List[str]]: [description]
            
        """
        all_tasks = {}
        for key, value in section.items():
            if key.endswith('_tasks'):
                name = key.replace('_tasks', '')
                tasks = sourdough.utilities.listify(value)
                all_tasks[name] = tasks
        return all_tasks

    def _get_task(self, 
            task: str,
            technique: str,
            worker: 'sourdough.Worker') -> 'sourdough.Task':
        """[summary]
        """
        # For each 'technique', it tries to find a corresponding Task and 
        # Technique subclass in options. If one isn't found, a generic Task or 
        # Technique is used.
        try:
            return worker.options[task](
                name = task,
                worker = worker.name,
                technique = worker.options[technique])
        except KeyError:
            try:
                return sourdough.Task(
                    name = task,
                    worker = worker.name,
                    technique = worker.options[technique])
            except KeyError:
                try:
                    return worker.options[task](
                        name = task,
                        worker = worker.name,
                        technique = sourdough.Technique(
                            name = technique))
                except KeyError:
                    return sourdough.Task(
                        name = task,
                        worker = worker.name,
                        technique = sourdough.Technique(
                            name = technique))
      

@dataclasses.dataclass
class ComparativeDesign(Design):
    """[summary]

    Args:
        sourdough {[type]} -- [description]
        
    """
    settings: 'sourdough.Settings'

    """ Public Methods """
    
    def create(self, worker: 'sourdough.Worker') -> 'sourdough.Worker':
        """Creates a 'SequenceBase' with a comparative structure.

        Returns:
            'SequenceBase': configured to specifications in 'overview'.

        """
        # Gets all tasks in a section of settings.
        settings_tasks = self._convert_settings(
            section = self.settings[worker.name])
        # Creates list of 'tasks' from 'settings_tasks'.
        tasks = list(settings_tasks.keys())
        # Creates 'techniques' list of lists.
        techniques = list(settings_tasks.values())
        # Creates a list of lists of the Cartesian product of 'techniques'.
        combinations = list(map(list, itertools.product(*techniques)))
        # Iterates through each combination to create Task and Technique 
        # instances.
        new_tasks = []
        for i, techniques in enumerate(combinations):
            new_techniques = []
            for technique in techniques:
                instance = self._get_task(
                    task = tasks[i], 
                    technique = technique, 
                    worker = worker)
                new_techniques.append(instance)
            new_techniques = sourdough.base.SequenceBase(
                name = '_'.join(techniques),
                contents = new_techniques)
            new_tasks.append[new_techniques]
        worker.contents = new_tasks
        return worker


@dataclasses.dataclass
class ChainedDesign(Design):
    """[summary]

    Args:
        sourdough {[type]} -- [description]
        
    """
    settings: 'sourdough.Settings'
    
    """ Public Methods """
 
    def create(self, worker: 'sourdough.Worker') -> 'sourdough.Worker':
        """

        """
        # Gets all tasks in a section of settings.
        settings_tasks = self._convert_settings(
            section = self.settings[worker.name])
        # Iterates through each 'settings_task' to create Task and Technique 
        # instances.
        new_tasks = []
        for task, techniques in settings_tasks.items():
            new_techniques = []
            for technique in techniques:
                instance = self._get_task(
                    task = task, 
                    technique = technique, 
                    worker = worker)
                new_techniques.append(instance)
            new_techniques = sourdough.base.SequenceBase(
                name = '_'.join(techniques),
                contents = new_techniques)
            new_tasks.append[new_techniques]
        worker.contents = new_tasks
        return worker

                
@dataclasses.dataclass
class DesignFactory(sourdough.core.base.FactoryBase):
    """A factory for creating and returning DesigneBase subclass instances.

    Args:
        product (Optional[str]): name of sourdough object to return. 'product' 
            must correspond to a key in 'products'. Defaults to None.
        default (ClassVar[str]): the name of the default object to instance. If 
            'product' is not passed, 'default' is used. 'default' must 
            correspond  to a key in 'products'. Defaults to None. If 'default'
            is to be used, it should be specified by a subclass, declared in an
            instance, or set via the class attribute.
        options (Dict[str, 'Design']): a dictionary of available options for 
            object creation. Keys are the names of the 'product'. Values are the 
            objects to create. Defaults to an a dictionary with the workers 
            included in sourdough.

    Returns:
        Any: the factory uses the '__new__' method to return a different object 
            instance with kwargs as the parameters.

    """
    product: Optional[str] = None
    default: ClassVar[str] = 'chained'
    options: ClassVar[Dict[str, 'Design']] = {
        'comparative': ComparativeDesign,
        'chained': ChainedDesign}
