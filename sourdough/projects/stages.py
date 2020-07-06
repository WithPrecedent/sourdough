"""
.. module:: stages
:synopsis: sourdough workflow stages
:publisher: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import abc
import dataclasses
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union

import sourdough
from sourdough import utilities

 
@dataclasses.dataclass
class Stage(abc.ABC):
    """Base class for workflow steps controlled by a Manager instance.
    
    All subclasses must have 'apply' methods. 
    
    """
    settings: 'sourdough.Settings'
    
    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def apply(self, *args, **kwargs) -> NotImplementedError:
        """Subclasses must provide their own methods."""
        raise NotImplementedError('Stage subclasses must include apply methods')


@dataclasses.dataclass
class Author(Stage):
    """Initializes a Project instance based upon a Settings instance."""  
    
    settings: 'sourdough.Settings'
    
    """ Public Methods """
    
    def apply(self, worker: 'sourdough.Worker') -> 'sourdough.Worker':
        """Returns a Worker with its 'contents' organized and instanced.

        The method first determines if the contents are already finalized. If 
        not, it creates them from 'settings'.
        
        Subclasses can call this method and then arrange the 'contents' of
        'worker' based upon a specific structural design.
        
        Args:
            worker (sourdough.Worker): Worker instance to organize the 
                information in 'contents' or 'settings'.

        Returns:
            sourdough.Worker: an instance with contents fully instanced.
                
        """
        worker = self._draft_existing_contents(worker = worker)
        worker = self._draft_from_settings(worker = worker)           
        return worker      

    """ Private Methods """

    def _draft_existing_contents(self, 
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
                new_contents.append(self._draft_unknown(
                    labor = labor, 
                    worker = worker))
            elif isinstance(labor, (sourdough.Worker, sourdough.Task)):
                new_contents.append(labor)
            else:
                raise TypeError(
                    f'{worker.name} contents must be str, Worker, or Task type')
        worker.contents = new_contents
        return worker
    
    def _draft_unknown(self,
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
            return self._draft_task(
                task = labor, 
                technique = None, 
                worker = worker)
        else:
            return self._draft_worker(worker = labor, manager = worker)

    def _draft_from_settings(self, 
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
                workers = sourdough.tools.listify(value)
            elif key.endswith('_tasks'):
                tasks = sourdough.tools.listify(value)
            elif key.endswith('_techniques'):
                new_key = key.replace('_techniques', '')
                techniques[new_key] = sourdough.tools.listify(value)
            else:
                attributes[key] = value
        if tasks:
            worker = self._draft_tasks(
                tasks = tasks, 
                techniques = techniques,
                worker = worker)
        elif workers:
            worker = self._draft_workers(
                workers = workers,
                manager = worker)
        for key, value in attributes.items():
            setattr(worker, key, value)
        return worker      

    def _draft_workers(self,
            workers: Sequence[str],
            manager: 'sourdough.Worker') -> 'sourdough.Worker':
        """[summary]

        Returns:
            [type]: [description]
            
        """
        new_workers = []
        for worker in workers:
            new_workers.append(self._draft_worker(
                worker = worker, 
                manager = manager))
        manager.contents.append(new_workers)
        return manager

    def _draft_worker(self,
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
                  
    def _draft_tasks(self, 
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
                new_techniques.append(self._draft_task(
                    task = task,
                    technique = technique,
                    worker = worker.name))
            new_tasks.append(new_techniques)
        worker.contents.append(new_tasks)
        return worker
            
    def _draft_task(self,
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
class Publisher(Stage):
    
    settings: 'sourdough.Settings'

    """ Public Methods """
    
    def add(self, 
            project: 'sourdough.Project', 
            worker: str, 
            tasks: Union[Sequence[str], str]) -> 'sourdough.Project':
        """Adds 'tasks' to 'project' 'contents' with a 'worker' key.
        
        Args:
            project (sourdough.Project): project to which 'worker' and 'tasks'
                should be added.
            worker (str): key to use to store 'tasks':
            tasks (Union[Sequence[str], str]): name(s) of task(s) to add to 
                'project'.
            
        Returns:
            sourdough.Project: with 'tasks' added at 'worker'.
        
        """
        project.contents[worker] = sourdough.tools.listify(tasks)
        return project
 
    def apply(self, worker: 'sourdough.Worker') -> 'sourdough.Worker':
        """[summary]

        Returns:
            [type] -- [description]
            
        """
        worker = self._parameterize_tasks(worker = worker)
        
        return worker

    """ Private Methods """
    
    def get(self, technique: sourdough.technique) -> sourdough.technique:
        """Adds appropriate parameters to technique.

        Args:
            technique (technique): instance for parameters to be added.

        Returns:
            technique: instance ready for application.

        """
        if technique.name not in ['none', None, 'None']:
            parameter_types = ['settings', 'selected', 'required', 'runtime']
            # Iterates through types of 'parameter_types'.
            for parameter_type in parameter_types:
                technique = getattr(self, f'_get_{parameter_type}')(
                    technique = technique)
        return technique

    """ Private Methods """

    def _get_settings(self,
            technique: sourdough.technique) -> sourdough.technique:
        """Acquires parameters from 'Settings' instance.

        Args:
            technique (technique): an instance for parameters to be added to.

        Returns:
            technique: instance with parameters added.

        """
        return self.settings.get_parameters(
            worker = technique.worker,
            technique = technique.name)

    def _get_selected(self,
            technique: sourdough.technique) -> sourdough.technique:
        """Limits parameters to those appropriate to the technique.

        If 'technique.selected' is True, the keys from 'technique.defaults' are
        used to select the final returned parameters.

        If 'technique.selected' is a list of parameter keys, then only those
        parameters are selected for the final returned parameters.

        Args:
            technique (technique): an instance for parameters to be added to.

        Returns:
            technique: instance with parameters added.

        """
        if technique.selected:
            if isinstance(technique.selected, list):
                parameters_to_use = technique.selected
            else:
                parameters_to_use = list(technique.default.keys())
            new_parameters = {}
            for key, value in technique.parameters.items():
                if key in parameters_to_use:
                    new_parameters[key] = value
            technique.parameters = new_parameters
        return technique

    def _get_required(self,
            technique: sourdough.technique) -> sourdough.technique:
        """Adds required parameters (mandatory additions) to 'parameters'.

        Args:
            technique (technique): an instance for parameters to be added to.

        Returns:
            technique: instance with parameters added.

        """
        try:
            technique.parameters.update(technique.required)
        except TypeError:
            pass
        return technique

    def _get_search(self,
            technique: sourdough.technique) -> sourdough.technique:
        """Separates variables with multiple options to search parameters.

        Args:
            technique (technique): an instance for parameters to be added to.

        Returns:
            technique: instance with parameters added.

        """
        technique.parameter_space = {}
        new_parameters = {}
        for parameter, values in technique.parameters.items():
            if isinstance(values, list):
                if any(isinstance(i, float) for i in values):
                    technique.parameter_space.update(
                        {parameter: uniform(values[0], values[1])})
                elif any(isinstance(i, int) for i in values):
                    technique.parameter_space.update(
                        {parameter: randint(values[0], values[1])})
            else:
                new_parameters.update({parameter: values})
        technique.parameters = new_parameters
        return technique

    def _get_runtime(self,
            technique: sourdough.technique) -> sourdough.technique:
        """Adds parameters that are determined at runtime.

        The primary example of a runtime parameter throughout sourdough is the
        addition of a random seed for a consistent, replicable state.

        Args:
            technique (technique): an instance for parameters to be added to.

        Returns:
            technique: instance with parameters added.

        """
        try:
            for key, value in technique.runtime.items():
                try:
                    technique.parameters.update(
                        {key: getattr(self.settings['general'], value)})
                except AttributeError:
                    raise AttributeError(' '.join(
                        ['no matching runtime parameter', key, 'found']))
        except (AttributeError, TypeError):
            pass
        return technique



@dataclasses.dataclass
class Reader(Stage):
    
    settings: 'sourdough.Settings'
    
    def apply(self, worker: 'sourdough.Worker') -> 'sourdough.Worker':
        """[summary]

        Returns:
            [type] -- [description]
            
        """
        worker = self._parameterize_tasks(worker = worker)
        
        return worker


# @dataclasses.dataclass
# class Parametizer(sourdough.Component):
#     """Constructs technique with an 'algorithm' and 'parameters'.

#     Args:
#         name (str): designates the name of the class instance used
#             for internal referencing throughout sourdough. If the class instance
#             needs settings from the shared Settings instance, 'name' should
#             match the appropriate section name in that Settings instance. When
#             subclassing, it is a good settings to use the same 'name' attribute
#             as the base class for effective coordination between sourdough
#             classes. Defaults to None or __class__.__name__.lower().
#         settings (Settings]): shared project configuration settings.
#         instructions (Instructions]): an instance with information to
#             create and apply the essential components of a Stage. Defaults to
#             None.

#     """
#     name: str = None
#     settings: sourdough.Settings] = None
#     instructions: Instructions] = None

#     """ Public Methods """

#     def get(self, technique: sourdough.technique) -> sourdough.technique:
#         """Adds appropriate parameters to technique.

#         Args:
#             technique (technique): instance for parameters to be added.

#         Returns:
#             technique: instance ready for application.

#         """
#         if technique.name not in ['none', None, 'None']:
#             parameter_types = ['settings', 'selected', 'required', 'runtime']
#             # Iterates through types of 'parameter_types'.
#             for parameter_type in parameter_types:
#                 technique = getattr(self, f'_get_{parameter_type}')(
#                     technique = technique)
#         return technique

#     """ Private Methods """

#     def _get_settings(self,
#             technique: sourdough.technique) -> sourdough.technique:
#         """Acquires parameters from 'Settings' instance.

#         Args:
#             technique (technique): an instance for parameters to be added to.

#         Returns:
#             technique: instance with parameters added.

#         """
#         return self.settings.get_parameters(
#             worker = technique.worker,
#             technique = technique.name)

#     def _get_selected(self,
#             technique: sourdough.technique) -> sourdough.technique:
#         """Limits parameters to those appropriate to the technique.

#         If 'technique.selected' is True, the keys from 'technique.defaults' are
#         used to select the final returned parameters.

#         If 'technique.selected' is a list of parameter keys, then only those
#         parameters are selected for the final returned parameters.

#         Args:
#             technique (technique): an instance for parameters to be added to.

#         Returns:
#             technique: instance with parameters added.

#         """
#         if technique.selected:
#             if isinstance(technique.selected, list):
#                 parameters_to_use = technique.selected
#             else:
#                 parameters_to_use = list(technique.default.keys())
#             new_parameters = {}
#             for key, value in technique.parameters.items():
#                 if key in parameters_to_use:
#                     new_parameters[key] = value
#             technique.parameters = new_parameters
#         return technique

#     def _get_required(self,
#             technique: sourdough.technique) -> sourdough.technique:
#         """Adds required parameters (mandatory additions) to 'parameters'.

#         Args:
#             technique (technique): an instance for parameters to be added to.

#         Returns:
#             technique: instance with parameters added.

#         """
#         try:
#             technique.parameters.update(technique.required)
#         except TypeError:
#             pass
#         return technique

#     def _get_search(self,
#             technique: sourdough.technique) -> sourdough.technique:
#         """Separates variables with multiple options to search parameters.

#         Args:
#             technique (technique): an instance for parameters to be added to.

#         Returns:
#             technique: instance with parameters added.

#         """
#         technique.parameter_space = {}
#         new_parameters = {}
#         for parameter, values in technique.parameters.items():
#             if isinstance(values, list):
#                 if any(isinstance(i, float) for i in values):
#                     technique.parameter_space.update(
#                         {parameter: uniform(values[0], values[1])})
#                 elif any(isinstance(i, int) for i in values):
#                     technique.parameter_space.update(
#                         {parameter: randint(values[0], values[1])})
#             else:
#                 new_parameters.update({parameter: values})
#         technique.parameters = new_parameters
#         return technique

#     def _get_runtime(self,
#             technique: sourdough.technique) -> sourdough.technique:
#         """Adds parameters that are determined at runtime.

#         The primary example of a runtime parameter throughout sourdough is the
#         addition of a random seed for a consistent, replicable state.

#         Args:
#             technique (technique): an instance for parameters to be added to.

#         Returns:
#             technique: instance with parameters added.

#         """
#         try:
#             for key, value in technique.runtime.items():
#                 try:
#                     technique.parameters.update(
#                         {key: getattr(self.settings['general'], value)})
#                 except AttributeError:
#                     raise AttributeError(' '.join(
#                         ['no matching runtime parameter', key, 'found']))
#         except (AttributeError, TypeError):
#             pass
#         return technique


# @dataclasses.dataclass
# class Finisher(sourdough.Technique):
#     """Finalizes technique instances with data-dependent parameters.

#     Args:
#         name (str): designates the name of the class instance used
#             for internal referencing throughout sourdough. If the class instance
#             needs settings from the shared Settings instance, 'name' should
#             match the appropriate section name in that Settings instance. When
#             subclassing, it is a good settings to use the same 'name' attribute
#             as the base class for effective coordination between sourdough
#             classes. Defaults to None or __class__.__name__.lower().
#         Settings (Settings]): shared project configuration settings.
#         instructions (Instructions]): an instance with information to
#             create and apply the essential components of a Stage. Defaults to
#             None.

#     """
#     name: str = None
#     Settings: sourdough.Settings] = None
#     instructions: Instructions] = None

#     """ Public Methods """

#     def apply(self,
#             outer_worker: sourdough.base.Plan,
#             data: Union[sourdough.Dataset, sourdough.base.Plan]) -> sourdough.base.Plan:
#         """Applies 'outer_worker' instance in 'project' to 'data' or other stored outer_worker.

#         Args:
#             outer_worker ('outer_worker'): instance with stored technique instances (either
#                 stored in the 'techniques' or 'inner_worker' attributes).
#             data ([Union['Dataset', 'outer_worker']): a data source with information to
#                 finalize 'parameters' for each technique instance in 'outer_worker'

#         Returns:
#             'outer_worker': with 'parameters' for each technique instance finalized
#                 and connected to 'algorithm'.

#         """
#         if hasattr(outer_worker, 'techniques'):
#             outer_worker = self._finalize_techniques(manuscript = outer_worker, data = data)
#         else:
#             outer_worker = self._finalize_inner_worker(outer_worker = outer_worker, data = data)
#         return outer_worker

#     """ Private Methods """

#     def _finalize_inner_worker(self, outer_worker: 'outer_worker', data: 'Dataset') -> 'outer_worker':
#         """Finalizes 'inner_worker' instances in 'outer_worker'.

#         Args:
#             outer_worker ('outer_worker'): instance containing 'inner_worker' with 'techniques' that
#                 have 'data_dependent' and/or 'conditional' 'parameters' to
#                 add.
#             data ('Dataset): instance with potential information to use to
#                 finalize 'parameters' for 'outer_worker'.

#         Returns:
#             'outer_worker': with any necessary modofications made.

#         """
#         new_inner_worker = [
#             self._finalize_techniques(inner_worker = inner_worker, data = data)
#             for inner_worker in outer_worker.inner_worker]

#         outer_worker.inner_worker = new_inner_worker
#         return outer_worker

#     def _finalize_techniques(self,
#             manuscript: Union['outer_worker', 'inner_worker'],
#             data: ['Dataset', 'outer_worker']) -> Union['outer_worker', 'inner_worker']:
#         """Subclasses may provide their own methods to finalize 'techniques'.

#         Args:
#             manuscript (Union['outer_worker', 'inner_worker']): manuscript containing
#                 'techniques' to apply.
#             data (['Dataset', 'outer_worker']): instance with information used to
#                 finalize 'parameters' and/or 'algorithm'.

#         Returns:
#             Union['outer_worker', 'inner_worker']: with any necessary modofications made.

#         """
#         new_techniques = []
#         for technique in manuscript.techniques:
#             if technique.name not in ['none']:
#                 new_technique = self._add_conditionals(
#                     manuscript = manuscript,
#                     technique = technique,
#                     data = data)
#                 new_technique = self._add_data_dependent(
#                     technique = technique,
#                     data = data)
#                 new_techniques.append(self._add_parameters_to_algorithm(
#                     technique = technique))
#         manuscript.techniques = new_techniques
#         return manuscript

#     def _add_conditionals(self,
#             manuscript: 'outer_worker',
#             technique: technique,
#             data: Union['Dataset', 'outer_worker']) -> technique:
#         """Adds any conditional parameters to a technique instance.

#         Args:
#             manuscript ('outer_worker'): outer_worker instance with algorithms to apply to 'data'.
#             technique (technique): instance with parameters which can take
#                 new conditional parameters.
#             data (Union['Dataset', 'outer_worker']): a data source which might
#                 contain information for condtional parameters.

#         Returns:
#             technique: instance with any conditional parameters added.

#         """
#         try:
#             if technique is not None:
#                 return getattr(manuscript, '_'.join(
#                     ['_add', technique.name, 'conditionals']))(
#                         technique = technique,
#                         data = data)
#         except AttributeError:
#             return technique

#     def _add_data_dependent(self,
#             technique: technique,
#             data: Union['Dataset', 'outer_worker']) -> technique:
#         """Completes parameter dictionary by adding data dependent parameters.

#         Args:
#             technique (technique): instance with information about data
#                 dependent parameters to add.
#             data (Union['Dataset', 'outer_worker']): a data source which contains
#                 'data_dependent' variables.

#         Returns:
#             technique: with any data dependent parameters added.

#         """
#         if technique is not None and technique.data_dependent is not None:

#             for key, value in technique.data_dependent.items():
#                 try:
#                     technique.parameters.update({key: getattr(data, value)})
#                 except KeyError:
#                     print('no matching parameter found for', key, 'in data')
#         return technique

#     def _add_parameters_to_algorithm(self,
#             technique: technique) -> technique:
#         """Instances 'algorithm' with 'parameters' in technique.

#         Args:
#             technique (technique): with completed 'algorith' and 'parameters'.

#         Returns:
#             technique: with 'algorithm' instanced with 'parameters'.

#         """
#         if technique is not None:
#             try:
#                 technique.algorithm = technique.algorithm(
#                     **technique.parameters)
#             except AttributeError:
#                 try:
#                     technique.algorithm = technique.algorithm(
#                         technique.parameters)
#                 except AttributeError:
#                     technique.algorithm = technique.algorithm()
#             except TypeError:
#                 try:
#                     technique.algorithm = technique.algorithm()
#                 except TypeError:
#                     pass
#         return technique


# @dataclasses.dataclass
# class Scholar(sourdough.Technique):
#     """Base class for applying technique instances to data.

#     Args:
#         name (str): designates the name of the class instance used
#             for internal referencing throughout sourdough. If the class instance
#             needs settings from the shared Settings instance, 'name' should
#             match the appropriate section name in that Settings instance. When
#             subclassing, it is a good settings to use the same 'name' attribute
#             as the base class for effective coordination between sourdough
#             classes. Defaults to None or __class__.__name__.lower().
#         Settings (Settings]): shared project configuration settings.
#         instructions (Instructions]): an instance with information to
#             create and apply the essential components of a Stage. Defaults to
#             None.

#     """
#     name: str = None
#     instructions: Instructions] = None
#     Settings: sourdough.Settings] = None

#     def __post_init__(self) -> None:
#         """Initializes class instance attributes."""
#         self = self.settings.apply(instance = self)
#         return self

#     """ Private Methods """

#     def _apply_inner_worker(self,
#             outer_worker: 'outer_worker',
#             data: Union['Dataset', 'outer_worker']) -> 'outer_worker':
#         """Applies 'inner_worker' in 'outer_worker' instance in 'project' to 'data'.

#         Args:
#             outer_worker ('outer_worker'): instance with stored 'inner_worker' instances.
#             data ('Dataset'): primary instance used by 'project'.

#         Returns:
#             'outer_worker': with modifications made and/or 'data' incorporated.

#         """
#         new_inner_worker = []
#         for i, inner_worker in enumerate(outer_worker.inner_worker):
#             if self.verbose:
#                 print('Applying', inner_worker.name, str(i + 1), 'to', data.name)
#             new_inner_worker.append(self._apply_techniques(
#                 manuscript = inner_worker,
#                 data = data))
#         outer_worker.inner_worker = new_inner_worker
#         return outer_worker

#     def _apply_techniques(self,
#             manuscript: Union['outer_worker', 'inner_worker'],
#             data: Union['Dataset', 'outer_worker']) -> Union['outer_worker', 'inner_worker']:
#         """Applies 'techniques' in 'manuscript' to 'data'.

#         Args:
#             manuscript (Union['outer_worker', 'inner_worker']): instance with stored
#                 'techniques'.
#             data ('Dataset'): primary instance used by 'manuscript'.

#         Returns:
#             Union['outer_worker', 'inner_worker']: with modifications made and/or 'data'
#                 incorporated.

#         """
#         for technique in manuscript.techniques:
#             if self.verbose:
#                 print('Applying', technique.name, 'to', data.name)
#             if isinstance(data, Dataset):
#                 data = technique.apply(data = data)
#             else:
#                 for inner_worker in data.inner_worker:
#                     manuscript.inner_worker.append(technique.apply(data = inner_worker))
#         if isinstance(data, Dataset):
#             setattr(manuscript, 'data', data)
#         return manuscript

#     """ Core sourdough Methods """

#     def apply(self, outer_worker: 'outer_worker', data: Union['Dataset', 'outer_worker']) -> 'outer_worker':
#         """Applies 'outer_worker' instance in 'project' to 'data' or other stored outer_worker.

#         Args:
#             outer_worker ('outer_worker'): instance with stored technique instances (either
#                 stored in the 'techniques' or 'inner_worker' attributes).
#             data ([Union['Dataset', 'outer_worker']): a data source with information to
#                 finalize 'parameters' for each technique instance in 'outer_worker'

#         Returns:
#             'outer_worker': with 'parameters' for each technique instance finalized
#                 and connected to 'algorithm'.

#         """
#         if hasattr(outer_worker, 'techniques'):
#             outer_worker = self._apply_techniques(manuscript = outer_worker, data = data)
#         else:
#             outer_worker = self._apply_inner_worker(outer_worker = outer_worker, data = data)
#         return outer_worker