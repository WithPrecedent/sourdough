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
from typing import Any, ClassVar, Iterable, Mapping, Sequence, Tuple, Union

import sourdough


@dataclasses.dataclass
class Designer(abc.ABC):
    """Base class for structuring different Worker instances.

    Args:
        settings (sourdough.Settings): an instance which contains information
            about how to design specific Worker instances.
        
    """
    settings: 'sourdough.Settings'
    options: ()

    """ Public Methods """
    
    def organize(self, worker: 'sourdough.Worker') -> 'sourdough.Worker':
        """Returns a Worker with its 'contents' organized and instanced.

        Organize first determines if the contents are already finalized. If not,
        it creates them from 'settings'.
        
        Subclasses can call this method and then arrange the 'contents' of
        'worker' based upon a specific structural design.
        
        Args:
            worker (sourdough.Worker): Worker instance to organize the 
                information in 'contents' or 'settings'.

        Returns:
            sourdough.Worker: an instance with contents fully instanced.
                
        """
        worker = self._process_existing_contents(worker = worker)
        worker = self._process_settings(worker = worker)           
        return worker      

    """ Private Methods """

    def _process_existing_contents(self, 
            worker: 'sourdough.Worker') -> 'sourdough.Worker':
        """
        
        Args:
            worker (sourdough.Worker): Worker instance with str, Task, or Worker
                stored in contents.

        Raises:
            TypeError: if an item in 'contents' is not a str, Task, or Worker
                type.

        Returns:
            sourdough.Worker: an instance with contents fully instanced.
                
        """
        new_contents = []
        for labor in worker.contents:
            if isinstance(labor, str):
                new_contents.append(self._process_unknown(
                    labor = labor, 
                    worker = worker))
            elif isinstance(labor, (sourdough.Worker, sourdough.Task)):
                new_contents.append(labor)
            else:
                raise TypeError(
                    f'{worker.name} contents must be str, Worker, or Task type')
        worker.contents = new_contents
        return worker
    
    def _process_unknown(self,
            labor: str,
            worker: 'sourdough.Worker') -> Union[
                'sourdough.Task', 
                'sourdough.Worker']:
        """[summary]

        Raises:
            KeyError: [description]

        Returns:
            [type]: [description]
        """
        try:
            test_instance = worker.options[labor](name = 'test only')
        except KeyError:
            raise KeyError(f'{labor} not found in {worker.name}')
        if isinstance(test_instance, sourdough.Task):
            return self._process_task(
                task = labor, 
                technique = None, 
                worker = worker)
        else:
            return self._process_worker(worker = labor, manager = worker)

    def _process_settings(self, 
            worker: 'sourdough.Worker') -> 'sourdough.Worker':
        """Returns a single Worker instance created based on 'settings'.

        Args:
            worker (sourdough.Worker): Worker instance to populate its 
                'contents' with information in 'settings'.

        Returns:
            sourdough.Worker: an worker or subclass worker with attributes 
                derived from a section of 'settings'.
                
        """
        tasks = []
        workers = []
        techniques = {}
        attributes = {}
        worker.contents = []
        for key, value in self.settings.contents[worker.name].items():
            if key.endswith('_design'):
                worker.design = value
            elif key.endswith('_workers'):
                workers = sourdough.utilities.listify(value)
            elif key.endswith('_tasks'):
                tasks = sourdough.utilities.listify(value)
            elif key.endswith('_techniques'):
                new_key = key.replace('_techniques', '')
                techniques[new_key] = sourdough.utilities.listify(value)
            else:
                attributes[key] = value
        if tasks:
            worker = self._process_tasks(
                tasks = tasks, 
                techniques = techniques,
                worker = worker)
        elif workers:
            worker = self._process_workers(
                workers = workers,
                manager = worker)
        for key, value in attributes.items():
            setattr(worker, key, value)
        return worker      

    def _process_workers(self,
            workers: Sequence[str],
            manager: 'sourdough.Worker') -> 'sourdough.Worker':
        """[summary]

        Returns:
            [type]: [description]
            
        """
        new_workers = []
        for worker in workers:
            new_workers.append(self._process_worker(
                worker = worker, 
                manager = manager))
        manager.contents.append(new_workers)
        return manager

    def _process_worker(self,
            worker: str,
            manager: 'sourdough.Worker') -> 'sourdough.Worker':
        """[summary]

        Returns:
            [type]: [description]
            
        """
        try:
            new_worker = manager.options[worker](name = worker)
        except KeyError:
            new_worker = sourdough.Worker(name = worker)
        return self.organize(worker = new_worker)
                  
    def _process_tasks(self, 
            worker: 'sourdough.Worker',
            tasks: Sequence[str],
            techniques: Mapping[str, Sequence[str]]) -> 'sourdough.Worker':
        """[summary]

        Returns:
            [type]: [description]
        """
        new_tasks = []
        for task in tasks:
            new_techniques = []
            for technique in techniques[task]:
                new_techniques.append(self._process_task(
                    task = task,
                    technique = technique,
                    worker = worker.name))
            new_tasks.append(new_techniques)
        worker.contents.append(new_tasks)
        return worker
            
    def _process_task(self,
            task: str,
            technique: str,
            worker: str,
            options: 'sourdough.Catalog') -> 'sourdough.Task':
        """[summary]

        Returns:
            [type]: [description]
            
        """
        try:
            return worker.options[task](
                name = task,
                worker = worker,
                technique = worker.options[technique])
        except KeyError:
            try:
                return sourdough.Task(
                    name = task,
                    worker = worker,
                    technique = worker.options[technique])
            except KeyError:
                try:
                    return worker.options[task](
                        name = task,
                        worker = worker,
                        technique = sourdough.Technique(name = technique))
                except KeyError:
                    return sourdough.Task(
                        name = task,
                        worker = worker,
                        technique = sourdough.Technique(name = technique))
     

@dataclasses.dataclass
class ComparativeDesign(Design):
    """[summary]

    Args:
        sourdough {[type]} -- [description]
        
    """
    settings: 'sourdough.Settings'

    """ Public Methods """
    
    def create(self, 
        worker: Optional[Union[
            'sourdough.Worker', 
            str]] = None) -> 'sourdough.Worker':
        """Creates a Worker instance with a comparative structure.

        Args:
            worker (Optional[sourdough.Worker]): a Worker subclass (not an 
                worker) to use when creating the returned worker.
                
        Returns:
            sourdough.Worker : configured according to 'settings'.

        """
        if isworker(worker, 'sourdough.Worker'):
            worker = self._settings_to_worker(
                name = worker.name,
                options = worker.options)
        else:
            
    def organize(self, worker: 'sourdough.Worker') -> 'sourdough.Worker':
        # Creates list of 'tasks' from 'settings_tasks'.
        tasks = list(settings_tasks.keys())
        # Creates 'techniques' list of lists.
        techniques = list(settings_tasks.values())
        # Creates a list of lists of the Cartesian product of 'techniques'.
        combinations = list(map(list, itertools.product(*techniques)))
        # Iterates through each combination to create Task and Technique 
        # workers.
        new_tasks = []
        for i, techniques in enumerate(combinations):
            new_techniques = []
            for technique in techniques:
                worker = self._get_task(
                    task = tasks[i], 
                    technique = technique, 
                    worker = worker)
                new_techniques.append(worker)
            new_techniques = sourdough.base.Plan(
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
        # workers.
        new_tasks = []
        for task, techniques in settings_tasks.items():
            new_techniques = []
            for technique in techniques:
                worker = self._get_task(
                    task = task, 
                    technique = technique, 
                    worker = worker)
                new_techniques.append(worker)
            new_techniques = sourdough.base.Plan(
                name = '_'.join(techniques),
                contents = new_techniques)
            new_tasks.append[new_techniques]
        worker.contents = new_tasks
        return worker

                
@dataclasses.dataclass
class DesignFactory(sourdough.core.base.Factory):
    """A factory for creating and returning DesigneBase subclass workers.

    Args:
        product (Optional[str]): name of sourdough object to return. 'product' 
            must correspond to a key in 'products'. Defaults to None.
        default (ClassVar[str]): the name of the default object to worker. If 
            'product' is not passed, 'default' is used. 'default' must 
            correspond  to a key in 'products'. Defaults to None. If 'default'
            is to be used, it should be specified by a subclass, declared in an
            worker, or set via the class attribute.
        options (MutableMapping[str, 'Design']): a dictionary of available options for 
            object creation. Keys are the names of the 'product'. Values are the 
            objects to create. Defaults to an a dictionary with the workers 
            included in sourdough.

    Returns:
        Any: the factory uses the '__new__' method to return a different object 
            worker with kwargs as the parameters.

    """
    product: Optional[str] = None
    default: ClassVar[str] = 'chained'
    options: ClassVar[Mapping[str, 'Design']] = {
        'comparative': ComparativeDesign,
        'chained': ChainedDesign}
