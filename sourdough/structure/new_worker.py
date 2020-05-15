"""
.. module:: worker
:synopsis: project management made simple
:publisher: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import abc
import collections.abc
import dataclasses
import importlib
import itertools
from typing import (
    Any, Callable, ClassVar, Dict, Iterable, List, Optional, Tuple, Union)

import sourdough


@dataclasses.dataclass
class Worker(sourdough.component):
    
    name: Optional[str] = None
    receives: Optional[List[str]] = None
    returns: Optional[List[str]] = None
    design: Optional[str] = None
    
    """ Required Subclass Methods """
    
    def apply(self, *args, **kwargs) -> NotImplementedError:
        """Subclasses must provide their own methods."""
        raise NotImplementedError(
            'Worker subclasses must include apply methods')


@dataclasses.dataclass
class Author(Worker):

    name: Optional[str] = None
    receives: Optional[List[str]] = None
    returns: Optional[List[str]] = 'overview'
    design: Optional[str] = dataclasses.field(
        default_factory = lambda: 'sequencer')
        
    def apply(self, 
            name: str, 
            settings: 'sourdough.Settings') -> Dict[str, List[str]]:
        """Creates dictionary with tasks for each step.

        Returns:
            Dict[str, Dict[str, List[str]]]: dictionary with keys of steps and
                values of lists of tasks.

        """        
        overview = sourdough.Overview(name = name)
        steps = settings.get_steps(section = name)
        for step in steps:
            overview.add(
                step = step, 
                tasks = settings.get_tasks(section = name, step = step))
        return overview
    

@dataclasses.dataclass
class Publisher(Worker):

    name: Optional[str] = None
    receives: Optional[List[str]] = 'overview'
    returns: Optional[List[str]] = 'plan'
    design: Optional[str] = dataclasses.field(
        default_factory = lambda: 'sequencer')
    
    def apply(self, overview: sourdough.Overview) -> sourdough.Plan:
        getattr(self, f'_create_{self.design}_plan')(
            overview = overview)
        return plan

    """ Private Methods """
    
    def _create_comparer_plan(self, 
            overview: Dict[str, List[str]]) -> sourdough.Plan:
        """Creates a 'Plan' with a parallel structure.

        Returns:
            'Plan': configured to specifications in 'overview'.

        """
        outer_name = self.name
        inner_name = 'plan'
        # Creates a 'Plan' instance to store other 'Plan' instances.
        outer_plan = sourdough.Plan(name = outer_name)
        # Creates list of steps from 'outline'.
        steps = list(overview.keys())
        # Creates 'possible' list of lists of 'tasks'.
        possible = list(overview.values())
        # Creates a list of lists of the Cartesian product of 'possible'.
        combinations = list(map(list, itertools.product(*possible)))
        # Creates a 'inner_plan' for each combination of tasks and adds that
        # 'inner_plan' to 'outer_plan'.
        for i, tasks in enumerate(combinations):
            inner_plan = sourdough.Plan(
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
 
    def _create_sequencer_plan(self,
            overview: Optional[Dict[str,str]] = None,
            outer_name: Optional[str] = None,
            inner_name: Optional[str] = None) -> sourdough.Plan:
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


@dataclasses.dataclass
class Parametizer(sourdough.Component):
    """Constructs task with an 'algorithm' and 'parameters'.

    Arguments:
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. If the class instance
            needs settings from the shared Settings instance, 'name' should
            match the appropriate section name in that Settings instance. When
            subclassing, it is a good settings to use the same 'name' attribute
            as the base class for effective coordination between sourdough
            classes. Defaults to None or __class__.__name__.lower().
        settings (Optional[Settings]): shared project configuration settings.
        instructions (Optional[Instructions]): an instance with information to
            create and apply the essential components of a Worker. Defaults to
            None.

    """
    name: Optional[str] = None
    settings: Optional[sourdough.Settings] = None
    instructions: Optional[Instructions] = None

    """ Public Methods """

    def get(self, task: sourdough.task) -> sourdough.task:
        """Adds appropriate parameters to task.

        Arguments:
            task (task): instance for parameters to be added.

        Returns:
            task: instance ready for application.

        """
        if task.name not in ['none', None, 'None']:
            parameter_types = ['settings', 'selected', 'required', 'runtime']
            # Iterates through types of 'parameter_types'.
            for parameter_type in parameter_types:
                task = getattr(self, f'_get_{parameter_type}')(
                    task = task)
        return task

    """ Private Methods """

    def _get_settings(self,
            task: sourdough.task) -> sourdough.task:
        """Acquires parameters from 'Settings' instance.

        Arguments:
            task (task): an instance for parameters to be added to.

        Returns:
            task: instance with parameters added.

        """
        return self.settings.get_parameters(
            step = task.step,
            task = task.name)

    def _get_selected(self,
            task: sourdough.task) -> sourdough.task:
        """Limits parameters to those appropriate to the task.

        If 'task.selected' is True, the keys from 'task.defaults' are
        used to select the final returned parameters.

        If 'task.selected' is a list of parameter keys, then only those
        parameters are selected for the final returned parameters.

        Arguments:
            task (task): an instance for parameters to be added to.

        Returns:
            task: instance with parameters added.

        """
        if task.selected:
            if isinstance(task.selected, list):
                parameters_to_use = task.selected
            else:
                parameters_to_use = list(task.default.keys())
            new_parameters = {}
            for key, value in task.parameters.items():
                if key in parameters_to_use:
                    new_parameters[key] = value
            task.parameters = new_parameters
        return task

    def _get_required(self,
            task: sourdough.task) -> sourdough.task:
        """Adds required parameters (mandatory additions) to 'parameters'.

        Arguments:
            task (task): an instance for parameters to be added to.

        Returns:
            task: instance with parameters added.

        """
        try:
            task.parameters.update(task.required)
        except TypeError:
            pass
        return task

    def _get_search(self,
            task: sourdough.task) -> sourdough.task:
        """Separates variables with multiple options to search parameters.

        Arguments:
            task (task): an instance for parameters to be added to.

        Returns:
            task: instance with parameters added.

        """
        task.parameter_space = {}
        new_parameters = {}
        for parameter, values in task.parameters.items():
            if isinstance(values, list):
                if any(isinstance(i, float) for i in values):
                    task.parameter_space.update(
                        {parameter: uniform(values[0], values[1])})
                elif any(isinstance(i, int) for i in values):
                    task.parameter_space.update(
                        {parameter: randint(values[0], values[1])})
            else:
                new_parameters.update({parameter: values})
        task.parameters = new_parameters
        return task

    def _get_runtime(self,
            task: sourdough.task) -> sourdough.task:
        """Adds parameters that are determined at runtime.

        The primary example of a runtime parameter throughout sourdough is the
        addition of a random seed for a consistent, replicable state.

        Arguments:
            task (task): an instance for parameters to be added to.

        Returns:
            task: instance with parameters added.

        """
        try:
            for key, value in task.runtime.items():
                try:
                    task.parameters.update(
                        {key: getattr(self.settings['general'], value)})
                except AttributeError:
                    raise AttributeError(' '.join(
                        ['no matching runtime parameter', key, 'found']))
        except (AttributeError, TypeError):
            pass
        return task


@dataclasses.dataclass
class Finisher(sourdough.Task):
    """Finalizes task instances with data-dependent parameters.

    Arguments:
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. If the class instance
            needs settings from the shared Settings instance, 'name' should
            match the appropriate section name in that Settings instance. When
            subclassing, it is a good settings to use the same 'name' attribute
            as the base class for effective coordination between sourdough
            classes. Defaults to None or __class__.__name__.lower().
        Settings (Optional[Settings]): shared project configuration settings.
        instructions (Optional[Instructions]): an instance with information to
            create and apply the essential components of a Worker. Defaults to
            None.

    """
    name: Optional[str] = None
    Settings: Optional[sourdough.Settings] = None
    instructions: Optional[Instructions] = None

    """ Public Methods """

    def apply(self,
            outer_plan: sourdough.Plan,
            data: Union[sourdough.Dataset, sourdough.Plan]) -> sourdough.Plan:
        """Applies 'outer_plan' instance in 'project' to 'data' or other stored outer_plans.

        Arguments:
            outer_plan ('outer_plan'): instance with stored task instances (either
                stored in the 'tasks' or 'inner_plans' attributes).
            data ([Union['Dataset', 'outer_plan']): a data source with information to
                finalize 'parameters' for each task instance in 'outer_plan'

        Returns:
            'outer_plan': with 'parameters' for each task instance finalized
                and connected to 'algorithm'.

        """
        if hasattr(outer_plan, 'tasks'):
            outer_plan = self._finalize_tasks(manuscript = outer_plan, data = data)
        else:
            outer_plan = self._finalize_inner_plans(outer_plan = outer_plan, data = data)
        return outer_plan

    """ Private Methods """

    def _finalize_inner_plans(self, outer_plan: 'outer_plan', data: 'Dataset') -> 'outer_plan':
        """Finalizes 'inner_plan' instances in 'outer_plan'.

        Arguments:
            outer_plan ('outer_plan'): instance containing 'inner_plans' with 'tasks' that
                have 'data_dependent' and/or 'conditional' 'parameters' to
                add.
            data ('Dataset): instance with potential information to use to
                finalize 'parameters' for 'outer_plan'.

        Returns:
            'outer_plan': with any necessary modofications made.

        """
        new_inner_plans = [
            self._finalize_tasks(inner_plan = inner_plan, data = data)
            for inner_plan in outer_plan.inner_plans]

        outer_plan.inner_plans = new_inner_plans
        return outer_plan

    def _finalize_tasks(self,
            manuscript: Union['outer_plan', 'inner_plan'],
            data: ['Dataset', 'outer_plan']) -> Union['outer_plan', 'inner_plan']:
        """Subclasses may provide their own methods to finalize 'tasks'.

        Arguments:
            manuscript (Union['outer_plan', 'inner_plan']): manuscript containing
                'tasks' to apply.
            data (['Dataset', 'outer_plan']): instance with information used to
                finalize 'parameters' and/or 'algorithm'.

        Returns:
            Union['outer_plan', 'inner_plan']: with any necessary modofications made.

        """
        new_tasks = []
        for task in manuscript.tasks:
            if task.name not in ['none']:
                new_task = self._add_conditionals(
                    manuscript = manuscript,
                    task = task,
                    data = data)
                new_task = self._add_data_dependent(
                    task = task,
                    data = data)
                new_tasks.append(self._add_parameters_to_algorithm(
                    task = task))
        manuscript.tasks = new_tasks
        return manuscript

    def _add_conditionals(self,
            manuscript: 'outer_plan',
            task: task,
            data: Union['Dataset', 'outer_plan']) -> task:
        """Adds any conditional parameters to a task instance.

        Arguments:
            manuscript ('outer_plan'): outer_plan instance with algorithms to apply to 'data'.
            task (task): instance with parameters which can take
                new conditional parameters.
            data (Union['Dataset', 'outer_plan']): a data source which might
                contain information for condtional parameters.

        Returns:
            task: instance with any conditional parameters added.

        """
        try:
            if task is not None:
                return getattr(manuscript, '_'.join(
                    ['_add', task.name, 'conditionals']))(
                        task = task,
                        data = data)
        except AttributeError:
            return task

    def _add_data_dependent(self,
            task: task,
            data: Union['Dataset', 'outer_plan']) -> task:
        """Completes parameter dictionary by adding data dependent parameters.

        Arguments:
            task (task): instance with information about data
                dependent parameters to add.
            data (Union['Dataset', 'outer_plan']): a data source which contains
                'data_dependent' variables.

        Returns:
            task: with any data dependent parameters added.

        """
        if task is not None and task.data_dependent is not None:

            for key, value in task.data_dependent.items():
                try:
                    task.parameters.update({key: getattr(data, value)})
                except KeyError:
                    print('no matching parameter found for', key, 'in data')
        return task

    def _add_parameters_to_algorithm(self,
            task: task) -> task:
        """Instances 'algorithm' with 'parameters' in task.

        Arguments:
            task (task): with completed 'algorith' and 'parameters'.

        Returns:
            task: with 'algorithm' instanced with 'parameters'.

        """
        if task is not None:
            try:
                task.algorithm = task.algorithm(
                    **task.parameters)
            except AttributeError:
                try:
                    task.algorithm = task.algorithm(
                        task.parameters)
                except AttributeError:
                    task.algorithm = task.algorithm()
            except TypeError:
                try:
                    task.algorithm = task.algorithm()
                except TypeError:
                    pass
        return task


@dataclasses.dataclass
class Scholar(sourdough.Task):
    """Base class for applying task instances to data.

    Arguments:
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. If the class instance
            needs settings from the shared Settings instance, 'name' should
            match the appropriate section name in that Settings instance. When
            subclassing, it is a good settings to use the same 'name' attribute
            as the base class for effective coordination between sourdough
            classes. Defaults to None or __class__.__name__.lower().
        Settings (Optional[Settings]): shared project configuration settings.
        instructions (Optional[Instructions]): an instance with information to
            create and apply the essential components of a Worker. Defaults to
            None.

    """
    name: Optional[str] = None
    instructions: Optional[Instructions] = None
    Settings: Optional[sourdough.Settings] = None

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        self = self.settings.apply(instance = self)
        return self

    """ Private Methods """

    def _apply_inner_plans(self,
            outer_plan: 'outer_plan',
            data: Union['Dataset', 'outer_plan']) -> 'outer_plan':
        """Applies 'inner_plans' in 'outer_plan' instance in 'project' to 'data'.

        Arguments:
            outer_plan ('outer_plan'): instance with stored 'inner_plan' instances.
            data ('Dataset'): primary instance used by 'project'.

        Returns:
            'outer_plan': with modifications made and/or 'data' incorporated.

        """
        new_inner_plans = []
        for i, inner_plan in enumerate(outer_plan.inner_plans):
            if self.verbose:
                print('Applying', inner_plan.name, str(i + 1), 'to', data.name)
            new_inner_plans.append(self._apply_tasks(
                manuscript = inner_plan,
                data = data))
        outer_plan.inner_plans = new_inner_plans
        return outer_plan

    def _apply_tasks(self,
            manuscript: Union['outer_plan', 'inner_plan'],
            data: Union['Dataset', 'outer_plan']) -> Union['outer_plan', 'inner_plan']:
        """Applies 'tasks' in 'manuscript' to 'data'.

        Arguments:
            manuscript (Union['outer_plan', 'inner_plan']): instance with stored
                'tasks'.
            data ('Dataset'): primary instance used by 'manuscript'.

        Returns:
            Union['outer_plan', 'inner_plan']: with modifications made and/or 'data'
                incorporated.

        """
        for task in manuscript.tasks:
            if self.verbose:
                print('Applying', task.name, 'to', data.name)
            if isinstance(data, Dataset):
                data = task.apply(data = data)
            else:
                for inner_plan in data.inner_plans:
                    manuscript.inner_plans.append(task.apply(data = inner_plan))
        if isinstance(data, Dataset):
            setattr(manuscript, 'data', data)
        return manuscript

    """ Core sourdough Methods """

    def apply(self, outer_plan: 'outer_plan', data: Union['Dataset', 'outer_plan']) -> 'outer_plan':
        """Applies 'outer_plan' instance in 'project' to 'data' or other stored outer_plans.

        Arguments:
            outer_plan ('outer_plan'): instance with stored task instances (either
                stored in the 'tasks' or 'inner_plans' attributes).
            data ([Union['Dataset', 'outer_plan']): a data source with information to
                finalize 'parameters' for each task instance in 'outer_plan'

        Returns:
            'outer_plan': with 'parameters' for each task instance finalized
                and connected to 'algorithm'.

        """
        if hasattr(outer_plan, 'tasks'):
            outer_plan = self._apply_tasks(manuscript = outer_plan, data = data)
        else:
            outer_plan = self._apply_inner_plans(outer_plan = outer_plan, data = data)
        return outer_plan