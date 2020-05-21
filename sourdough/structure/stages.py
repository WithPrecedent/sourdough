"""
.. module:: stages
:synopsis: sourdough workflow stages
:publisher: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import abc
import dataclasses
from typing import (
    Any, Callable, ClassVar, Dict, Iterable, List, Optional, Tuple, Union)

import sourdough
from sourdough import utilities

 
@dataclasses.dataclass
class StageBase(abc.ABC):
    """Base class for Components stored by a Director.
    
    All subclasses must have an 'apply' method.
    
    """
 
    """ Required Subclass Methods """
    
    def apply(self, *args, **kwargs) -> NotImplementedError:
        """Subclasses must provide their own methods."""
        raise NotImplementedError('Stage subclasses must include apply methods')


@dataclasses.dataclass
class Author(StageBase):
    """Initializes a Project instance based upon a Settings instance."""  
    
    """ Public Methods """
    
    def apply(self, project: 'sourdough.Project') -> 'sourdough.Project':
        """Creates a rough draft of a Project instance.
        
        Args:
            project (Project): a sourdough Project instance with sa Settings
                instance which is used to create the initial configuration of
                the sourdough project.
                
        Returns:
            Project: with its 'contents' attribute populated with Employee instances
                and strings which describe the basic aspects of a sourdough
                project.
                
        """
        project = self._get_employees(manager = project)
        # project = self._initialize_employees(manager = project)
        # project = self._populate_hierarchy(manager = project)
        return project
    
    """ Private Methods """
    
    def _get_employees(self, 
            manager: 'sourdough.Manager') -> 'sourdough.Manager':   
        """[summary]

        Returns:
            [type]: [description]
        """
        try: 
            manager.contents = manager.settings.get_managers(
                section = manager.name, 
                name = manager.name)
            manager = self._initialize_managers(manager = manager)
            lower_managers = []
            for lower_manager in utilities.listify(manager.contents):
                lower_managers.append(
                    self._get_employees(manager = lower_manager))
            manager.contents = lower_managers
        except KeyError:
            try:
                manager.contents = manager.settings.get_tasks(
                    section = manager.manager, 
                    name = manager.name)
                manager.contents = self._initialize_workers(manager = manager)
            except KeyError:
                pass
                # manager.contents = manager.options.keys()
        return manager
    
    def _initialize_managers(self, 
            manager: 'sourdough.Manager') -> 'sourdough.Manager':   
        """[summary]

        Raises:
            TypeError: [description]

        Returns:
            [type]: [description]
        """
        new_managers = []
        for employee in utilities.listify(manager.contents):
            new_managers.append(manager.options[employee](
                name = employee, 
                settings = manager.settings,
                manager = manager.name))
        manager.contents = new_managers
        return manager  
    
    def _initialize_workers(self, 
            manager: 'sourdough.Manager') -> 'sourdough.Manager':   
        """[summary]

        Raises:
            TypeError: [description]

        Returns:
            [type]: [description]
        """
        new_managers = []
        for employee in utilities.listify(manager.contents):
            new_managers.append(manager.options[employee](
                name = employee, 
                settings = manager.settings))
        manager.contents = new_managers
        return manager  
    
    def _create_comparer_employee(self, 
            overview: Dict[str, List[str]]) -> sourdough.base.SequenceBase:
        """Creates a 'SequenceBase' with a comparative structure.

        Returns:
            'SequenceBase': configured to specifications in 'overview'.

        """
        outer_name = self.name
        inner_name = 'employee'
        # Creates a 'SequenceBase' instance to store other 'SequenceBase' instances.
        outer_employee = sourdough.base.SequenceBase(name = outer_name)
        # Creates list of workers from 'outline'.
        workers = list(overview.keys())
        # Creates 'possible' list of lists of 'tasks'.
        possible = list(overview.values())
        # Creates a list of lists of the Cartesian product of 'possible'.
        combinations = list(map(list, itertools.product(*possible)))
        # Creates a 'inner_employee' for each combination of tasks and adds that
        # 'inner_employee' to 'outer_employee'.
        for i, tasks in enumerate(combinations):
            inner_employee = sourdough.base.SequenceBase(
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
 
    def _create_sequencer_employee(self,
            overview: Optional[Dict[str,str]] = None,
            outer_name: Optional[str] = None,
            inner_name: Optional[str] = None) -> sourdough.base.SequenceBase:
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
class Editor(StageBase):

    """ Public Methods """

    def apply(self, project: 'sourdough.Project') -> 'sourdough.Project':
        """[summary]

        Returns:
            [type] -- [description]
            
        """
        return project


@dataclasses.dataclass
class Publisher(StageBase):
    
    def apply(self, project: 'sourdough.Project') -> 'sourdough.Project':
        """[summary]

        Returns:
            [type] -- [description]
            
        """
        return project


@dataclasses.dataclass
class Reader(StageBase):
    
    def apply(self, project: 'sourdough.Project') -> 'sourdough.Project':
        """[summary]

        Returns:
            [type] -- [description]
            
        """
        return project
    

@dataclasses.dataclass
class Stage(sourdough.core.base.FactoryBase):
    """A factory for creating and returning StageBase subclass instances.

    Args:
        product (Optional[str]): name of sourdough object to return. 'product' 
            must correspond to a key in 'products'. Defaults to None.
        default (ClassVar[str]): the name of the default object to instance. If 
            'product' is not passed, 'default' is used. 'default' must 
            correspond  to a key in 'products'. Defaults to None. If 'default'
            is to be used, it should be specified by a subclass, declared in an
            instance, or set via the class attribute.
        options (Dict[str, 'StageBase']): a dictionary of available options for 
            object creation. Keys are the names of the 'product'. Values are the 
            objects to create. Defaults to an a dictionary with the stage
            included in sourdough.

    Returns:
        Any: the factory uses the '__new__' method to return a different object 
            instance with kwargs as the parameters.

    """
    product: Optional[str] = None
    default: ClassVar[str] = None
    options: ClassVar[Dict[str, 'StageBase']] = {
        'draft': Author,
        'edit': Editor,
        'publish': Publisher,
        'apply': Reader}


# @dataclasses.dataclass
# class Parametizer(sourdough.Component):
#     """Constructs task with an 'algorithm' and 'parameters'.

#     Args:
#         name (Optional[str]): designates the name of the class instance used
#             for internal referencing throughout sourdough. If the class instance
#             needs settings from the shared Settings instance, 'name' should
#             match the appropriate section name in that Settings instance. When
#             subclassing, it is a good settings to use the same 'name' attribute
#             as the base class for effective coordination between sourdough
#             classes. Defaults to None or __class__.__name__.lower().
#         settings (Optional[Settings]): shared project configuration settings.
#         instructions (Optional[Instructions]): an instance with information to
#             create and apply the essential components of a Stage. Defaults to
#             None.

#     """
#     name: Optional[str] = None
#     settings: Optional[sourdough.Settings] = None
#     instructions: Optional[Instructions] = None

#     """ Public Methods """

#     def get(self, task: sourdough.task) -> sourdough.task:
#         """Adds appropriate parameters to task.

#         Args:
#             task (task): instance for parameters to be added.

#         Returns:
#             task: instance ready for application.

#         """
#         if task.name not in ['none', None, 'None']:
#             parameter_types = ['settings', 'selected', 'required', 'runtime']
#             # Iterates through types of 'parameter_types'.
#             for parameter_type in parameter_types:
#                 task = getattr(self, f'_get_{parameter_type}')(
#                     task = task)
#         return task

#     """ Private Methods """

#     def _get_settings(self,
#             task: sourdough.task) -> sourdough.task:
#         """Acquires parameters from 'Settings' instance.

#         Args:
#             task (task): an instance for parameters to be added to.

#         Returns:
#             task: instance with parameters added.

#         """
#         return self.settings.get_parameters(
#             worker = task.worker,
#             task = task.name)

#     def _get_selected(self,
#             task: sourdough.task) -> sourdough.task:
#         """Limits parameters to those appropriate to the task.

#         If 'task.selected' is True, the keys from 'task.defaults' are
#         used to select the final returned parameters.

#         If 'task.selected' is a list of parameter keys, then only those
#         parameters are selected for the final returned parameters.

#         Args:
#             task (task): an instance for parameters to be added to.

#         Returns:
#             task: instance with parameters added.

#         """
#         if task.selected:
#             if isinstance(task.selected, list):
#                 parameters_to_use = task.selected
#             else:
#                 parameters_to_use = list(task.default.keys())
#             new_parameters = {}
#             for key, value in task.parameters.items():
#                 if key in parameters_to_use:
#                     new_parameters[key] = value
#             task.parameters = new_parameters
#         return task

#     def _get_required(self,
#             task: sourdough.task) -> sourdough.task:
#         """Adds required parameters (mandatory additions) to 'parameters'.

#         Args:
#             task (task): an instance for parameters to be added to.

#         Returns:
#             task: instance with parameters added.

#         """
#         try:
#             task.parameters.update(task.required)
#         except TypeError:
#             pass
#         return task

#     def _get_search(self,
#             task: sourdough.task) -> sourdough.task:
#         """Separates variables with multiple options to search parameters.

#         Args:
#             task (task): an instance for parameters to be added to.

#         Returns:
#             task: instance with parameters added.

#         """
#         task.parameter_space = {}
#         new_parameters = {}
#         for parameter, values in task.parameters.items():
#             if isinstance(values, list):
#                 if any(isinstance(i, float) for i in values):
#                     task.parameter_space.update(
#                         {parameter: uniform(values[0], values[1])})
#                 elif any(isinstance(i, int) for i in values):
#                     task.parameter_space.update(
#                         {parameter: randint(values[0], values[1])})
#             else:
#                 new_parameters.update({parameter: values})
#         task.parameters = new_parameters
#         return task

#     def _get_runtime(self,
#             task: sourdough.task) -> sourdough.task:
#         """Adds parameters that are determined at runtime.

#         The primary example of a runtime parameter throughout sourdough is the
#         addition of a random seed for a consistent, replicable state.

#         Args:
#             task (task): an instance for parameters to be added to.

#         Returns:
#             task: instance with parameters added.

#         """
#         try:
#             for key, value in task.runtime.items():
#                 try:
#                     task.parameters.update(
#                         {key: getattr(self.settings['general'], value)})
#                 except AttributeError:
#                     raise AttributeError(' '.join(
#                         ['no matching runtime parameter', key, 'found']))
#         except (AttributeError, TypeError):
#             pass
#         return task


# @dataclasses.dataclass
# class Finisher(sourdough.Task):
#     """Finalizes task instances with data-dependent parameters.

#     Args:
#         name (Optional[str]): designates the name of the class instance used
#             for internal referencing throughout sourdough. If the class instance
#             needs settings from the shared Settings instance, 'name' should
#             match the appropriate section name in that Settings instance. When
#             subclassing, it is a good settings to use the same 'name' attribute
#             as the base class for effective coordination between sourdough
#             classes. Defaults to None or __class__.__name__.lower().
#         Settings (Optional[Settings]): shared project configuration settings.
#         instructions (Optional[Instructions]): an instance with information to
#             create and apply the essential components of a Stage. Defaults to
#             None.

#     """
#     name: Optional[str] = None
#     Settings: Optional[sourdough.Settings] = None
#     instructions: Optional[Instructions] = None

#     """ Public Methods """

#     def apply(self,
#             outer_employee: sourdough.base.SequenceBase,
#             data: Union[sourdough.Dataset, sourdough.base.SequenceBase]) -> sourdough.base.SequenceBase:
#         """Applies 'outer_employee' instance in 'project' to 'data' or other stored outer_employees.

#         Args:
#             outer_employee ('outer_employee'): instance with stored task instances (either
#                 stored in the 'tasks' or 'inner_employees' attributes).
#             data ([Union['Dataset', 'outer_employee']): a data source with information to
#                 finalize 'parameters' for each task instance in 'outer_employee'

#         Returns:
#             'outer_employee': with 'parameters' for each task instance finalized
#                 and connected to 'algorithm'.

#         """
#         if hasattr(outer_employee, 'tasks'):
#             outer_employee = self._finalize_tasks(manuscript = outer_employee, data = data)
#         else:
#             outer_employee = self._finalize_inner_employees(outer_employee = outer_employee, data = data)
#         return outer_employee

#     """ Private Methods """

#     def _finalize_inner_employees(self, outer_employee: 'outer_employee', data: 'Dataset') -> 'outer_employee':
#         """Finalizes 'inner_employee' instances in 'outer_employee'.

#         Args:
#             outer_employee ('outer_employee'): instance containing 'inner_employees' with 'tasks' that
#                 have 'data_dependent' and/or 'conditional' 'parameters' to
#                 add.
#             data ('Dataset): instance with potential information to use to
#                 finalize 'parameters' for 'outer_employee'.

#         Returns:
#             'outer_employee': with any necessary modofications made.

#         """
#         new_inner_employees = [
#             self._finalize_tasks(inner_employee = inner_employee, data = data)
#             for inner_employee in outer_employee.inner_employees]

#         outer_employee.inner_employees = new_inner_employees
#         return outer_employee

#     def _finalize_tasks(self,
#             manuscript: Union['outer_employee', 'inner_employee'],
#             data: ['Dataset', 'outer_employee']) -> Union['outer_employee', 'inner_employee']:
#         """Subclasses may provide their own methods to finalize 'tasks'.

#         Args:
#             manuscript (Union['outer_employee', 'inner_employee']): manuscript containing
#                 'tasks' to apply.
#             data (['Dataset', 'outer_employee']): instance with information used to
#                 finalize 'parameters' and/or 'algorithm'.

#         Returns:
#             Union['outer_employee', 'inner_employee']: with any necessary modofications made.

#         """
#         new_tasks = []
#         for task in manuscript.tasks:
#             if task.name not in ['none']:
#                 new_task = self._add_conditionals(
#                     manuscript = manuscript,
#                     task = task,
#                     data = data)
#                 new_task = self._add_data_dependent(
#                     task = task,
#                     data = data)
#                 new_tasks.append(self._add_parameters_to_algorithm(
#                     task = task))
#         manuscript.tasks = new_tasks
#         return manuscript

#     def _add_conditionals(self,
#             manuscript: 'outer_employee',
#             task: task,
#             data: Union['Dataset', 'outer_employee']) -> task:
#         """Adds any conditional parameters to a task instance.

#         Args:
#             manuscript ('outer_employee'): outer_employee instance with algorithms to apply to 'data'.
#             task (task): instance with parameters which can take
#                 new conditional parameters.
#             data (Union['Dataset', 'outer_employee']): a data source which might
#                 contain information for condtional parameters.

#         Returns:
#             task: instance with any conditional parameters added.

#         """
#         try:
#             if task is not None:
#                 return getattr(manuscript, '_'.join(
#                     ['_add', task.name, 'conditionals']))(
#                         task = task,
#                         data = data)
#         except AttributeError:
#             return task

#     def _add_data_dependent(self,
#             task: task,
#             data: Union['Dataset', 'outer_employee']) -> task:
#         """Completes parameter dictionary by adding data dependent parameters.

#         Args:
#             task (task): instance with information about data
#                 dependent parameters to add.
#             data (Union['Dataset', 'outer_employee']): a data source which contains
#                 'data_dependent' variables.

#         Returns:
#             task: with any data dependent parameters added.

#         """
#         if task is not None and task.data_dependent is not None:

#             for key, value in task.data_dependent.items():
#                 try:
#                     task.parameters.update({key: getattr(data, value)})
#                 except KeyError:
#                     print('no matching parameter found for', key, 'in data')
#         return task

#     def _add_parameters_to_algorithm(self,
#             task: task) -> task:
#         """Instances 'algorithm' with 'parameters' in task.

#         Args:
#             task (task): with completed 'algorith' and 'parameters'.

#         Returns:
#             task: with 'algorithm' instanced with 'parameters'.

#         """
#         if task is not None:
#             try:
#                 task.algorithm = task.algorithm(
#                     **task.parameters)
#             except AttributeError:
#                 try:
#                     task.algorithm = task.algorithm(
#                         task.parameters)
#                 except AttributeError:
#                     task.algorithm = task.algorithm()
#             except TypeError:
#                 try:
#                     task.algorithm = task.algorithm()
#                 except TypeError:
#                     pass
#         return task


# @dataclasses.dataclass
# class Scholar(sourdough.Task):
#     """Base class for applying task instances to data.

#     Args:
#         name (Optional[str]): designates the name of the class instance used
#             for internal referencing throughout sourdough. If the class instance
#             needs settings from the shared Settings instance, 'name' should
#             match the appropriate section name in that Settings instance. When
#             subclassing, it is a good settings to use the same 'name' attribute
#             as the base class for effective coordination between sourdough
#             classes. Defaults to None or __class__.__name__.lower().
#         Settings (Optional[Settings]): shared project configuration settings.
#         instructions (Optional[Instructions]): an instance with information to
#             create and apply the essential components of a Stage. Defaults to
#             None.

#     """
#     name: Optional[str] = None
#     instructions: Optional[Instructions] = None
#     Settings: Optional[sourdough.Settings] = None

#     def __post_init__(self) -> None:
#         """Initializes class instance attributes."""
#         self = self.settings.apply(instance = self)
#         return self

#     """ Private Methods """

#     def _apply_inner_employees(self,
#             outer_employee: 'outer_employee',
#             data: Union['Dataset', 'outer_employee']) -> 'outer_employee':
#         """Applies 'inner_employees' in 'outer_employee' instance in 'project' to 'data'.

#         Args:
#             outer_employee ('outer_employee'): instance with stored 'inner_employee' instances.
#             data ('Dataset'): primary instance used by 'project'.

#         Returns:
#             'outer_employee': with modifications made and/or 'data' incorporated.

#         """
#         new_inner_employees = []
#         for i, inner_employee in enumerate(outer_employee.inner_employees):
#             if self.verbose:
#                 print('Applying', inner_employee.name, str(i + 1), 'to', data.name)
#             new_inner_employees.append(self._apply_tasks(
#                 manuscript = inner_employee,
#                 data = data))
#         outer_employee.inner_employees = new_inner_employees
#         return outer_employee

#     def _apply_tasks(self,
#             manuscript: Union['outer_employee', 'inner_employee'],
#             data: Union['Dataset', 'outer_employee']) -> Union['outer_employee', 'inner_employee']:
#         """Applies 'tasks' in 'manuscript' to 'data'.

#         Args:
#             manuscript (Union['outer_employee', 'inner_employee']): instance with stored
#                 'tasks'.
#             data ('Dataset'): primary instance used by 'manuscript'.

#         Returns:
#             Union['outer_employee', 'inner_employee']: with modifications made and/or 'data'
#                 incorporated.

#         """
#         for task in manuscript.tasks:
#             if self.verbose:
#                 print('Applying', task.name, 'to', data.name)
#             if isinstance(data, Dataset):
#                 data = task.apply(data = data)
#             else:
#                 for inner_employee in data.inner_employees:
#                     manuscript.inner_employees.append(task.apply(data = inner_employee))
#         if isinstance(data, Dataset):
#             setattr(manuscript, 'data', data)
#         return manuscript

#     """ Core sourdough Methods """

#     def apply(self, outer_employee: 'outer_employee', data: Union['Dataset', 'outer_employee']) -> 'outer_employee':
#         """Applies 'outer_employee' instance in 'project' to 'data' or other stored outer_employees.

#         Args:
#             outer_employee ('outer_employee'): instance with stored task instances (either
#                 stored in the 'tasks' or 'inner_employees' attributes).
#             data ([Union['Dataset', 'outer_employee']): a data source with information to
#                 finalize 'parameters' for each task instance in 'outer_employee'

#         Returns:
#             'outer_employee': with 'parameters' for each task instance finalized
#                 and connected to 'algorithm'.

#         """
#         if hasattr(outer_employee, 'tasks'):
#             outer_employee = self._apply_tasks(manuscript = outer_employee, data = data)
#         else:
#             outer_employee = self._apply_inner_employees(outer_employee = outer_employee, data = data)
#         return outer_employee