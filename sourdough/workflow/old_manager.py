"""
.. module:: manager
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
class Manager(sourdough.SequenceBase):
    """Base class for sourdough project workflows.

    A Manager maintains a progress state stored in the attribute 'stage'. The
    'stage' corresponds to whether one of the core workflow methods has been
    called. The string stored in 'stage' can then be used by instances to alter
    instance behavior, call methods, or change access method functionality.

    Arguments:
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. If the class instance
            needs settings from the shared Settings instance, 'name' should
            match the appropriate section name in that Settings instance. When
            subclassing, it is a good settings to use the same 'name' attribute
            as the base class for effective coordination between sourdough
            classes. Defaults to None or __class__.__name__.lower().
        items (Optional[List[sourdough.Stage]]): list of recognized
            states which correspond to methods within a class instance or a dict
            with keys of stage names and values of method names. Defaults to
            {'initialize': None, 'draft': sourdough.Author, 'pubish': 
            sourdough.Publisher, 'publish': sourdough.Reader}.
        
        auto_advance (Optional[bool]): whether to automatically advance 'stage'
            when one of the stage methods is called (True) or whether 'stage'
            must be changed manually by using the 'advance' method (False).
            Defaults to True.

    """
    name: Optional[str] = None
    items: Optional[List[sourdough.Stage]] = dataclasses.field(
        default_factory = list)
    auto_advance: Optional[bool] = True
    settings: Optional[Settings] = None
    design: Optional[str] = dataclasses.field(
        default_factory = lambda: 'sequencer')
    hierarchy: Optional[List[str]] = dataclasses.field(
        default_factory = ['stages', 'steps', 'tasks'])
    data: Optional[Any] = None

    """Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Sets 'name' to the default value if it is not passed.
        super().__post_init__()
        # Uses default items if 'items' weren't passed.
        self.items = self.items or self._get_default_items()
        # Sets initial index and name of the active stage.
        self.index = 0
        self.stage = self.items[0].name   
        # Automatically calls stage methods if attributes named 'auto_{stage}'
        # are set to True. For example, if there is an attribute named
        # 'auto_draft' and it is True, the 'draft' method will be called.
        if self.auto_advance:
            self._auto_items()
        return self

    """ Public Methods """

    def advance(self, stage: Optional[str] = None) -> None:
        """Advances to next stage in 'items' or to 'stage' argument.

        This method only needs to be called manually if 'auto_advance' is False.
        Otherwise, this method is automatically called when individual stage
        methods are called via '__getattribute__'.

        If this method is called at the last stage, it does not raise an
        IndexError. It simply leaves 'stage' at the last item in the list.

        Arguments:
            stage(Optional[str]): name of stage in 'items'.
                Defaults to None. If not passed, the method goes to the next
                'stage' in items.

        Raises:
            ValueError: if 'stage' is neither None nor in 'items'.

        """
        if stage is None:
            try:
                new_index = self.index + 1
                self.stage = self.items[new_index].name
                self.index = new_index
                self.previous_stage = self.stage
            except IndexError:
                pass
        elif stage in [w.name for w in self.items]:
            self.stage = stage
            self.index = self.items.index(self[stage.name])
            self.previous_stage = self.stage
        else:
            raise ValueError(f'{stage} is not a recognized stage')
        return self

    def apply(self, data: Optional[Any] = None) -> None:
        """Applies 'stage' with appropriate parameters and return values.
        
        Arguments:
            data (Optional[Any]): external data of any type to be passed to
                the 'apply' method of a Stage instance.
        
        """
        if data:
            self.data = data
        parameters = self._get_parameters(recieves = self.stage.receives)
        values = self.items[self.index].apply(**parameters)
        self._set_returned_values(
            attributes = self.stage.returns,
            values = values)
        return self

    """ Private Methods """
    
    def _get_default_items(self) -> List[sourdough.Stage]:
        """Returns a default list of stage Stage instances.
        
        If you do not wish to use the default Stage instances, you can either
        pass a list of instances to 'items' when Manager is instanced or 
        override this method in a subclass.
        
        Returns:
            List[Stage]: instances of Stage which define the characteristics 
                of each stage in a Manager.
                
        """
        return [
            None,
            sourdough.Author(
                name = 'author',
                receives = ('name', 'settings'),
                returns = 'overview',
                design = self.design),
            sourdough.Publisher(
                name = 'publisher',
                receives = 'overview',
                returns = 'plan',
                design = self.design),
            sourdough.Reader(
                name = 'reader',
                receives = ('plan', 'data'),
                returns = ('plan', 'data'),
                design = self.design)]

    def _auto_items(self) -> None:
        """Calls stage method if corresponding boolean is True.
        
        For example, if there is an attribute named 'auto_author', then the
        apply method of the Stage subclass with the 'name' of 'author' will
        automatically be called.Any
        
        """
        for stage in self.items[1:]:
            try:
                if getattr(self, f'auto_{stage.name}'):
                    self.advance(stage = stage.name)
                    self.apply()
            except AttributeError:
                pass
        return self
    
    def _get_parameters(self, 
            receives: Union[str, Tuple[str]]) -> Dict[str, Any]:
        """Returns a parameters dictionary for a Stage 'apply' method.
        
        Arguments:
            receives (Union[str, Tuple[str]]): the name(s) of local attribute(s)
                which should be used to create parameters for the 'apply'
                method.
                
        Returns:
            Dict[str, Any]: dictionary with appropriate parameters for an 
                'apply' method.
                
        """
        if isinstance(receives, tuple):
            parameters = {}
            for parameter in receives:
                parameters[parameter] = getattr(self, parameter)
            return parameters
        elif not receives:
            return {}
        else:
            return {receives: getattr(self, receives)}
           
    def _set_return_values(self, 
            attributes: Union[str, Tuple[str]],
            values: Union[Any, Tuple[Any]]) -> None:
        """Sets returned values as local attributes.
        
        Arguments:
            attributes (Union[str, Tuple[str]]): name(s) of local attribute(s)
                to assigned 'values' to.
            values (Union[str, Tuple[str]]): returned values from calling a 
                Stage 'apply' method.
        
        Raises:
            ValueError: if attributes and values are tuples, but are not of the
                same length.
                
        """
        if isinstance(attributes, tuple):
            if len(attributes) == len(values):
                for i, attribute in enumerate(attributes):
                    setattr(self, attribute, values[i])
            else:
                raise ValueError(
                    'attributes and values must be the same length')
        elif attributes:
            setattr(self, attributes, values)
        return self
  


@dataclasses.dataclass
class Stage(sourdough.component):
    
    name: Optional[str] = None
    design: Optional[str] = None
    
    """ Required Subclass Methods """
    
    def apply(self, *args, **kwargs) -> NotImplementedError:
        """Subclasses must provide their own methods."""
        raise NotImplementedError(
            'Stage subclasses must include apply methods')


@dataclasses.dataclass
class Author(Stage):

    name: Optional[str] = None
    design: Optional[str] = dataclasses.field(
        default_factory = lambda: 'sequencer')

    def apply(self, project: 'sourdough.Project') -> 'sourdough.Project':
        """[summary]

        Returns:
            [type] -- [description]
            
        """
        return project.draft(settings = project.settings)



    

@dataclasses.dataclass
class Publisher(Stage):

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
            create and apply the essential components of a Stage. Defaults to
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
            create and apply the essential components of a Stage. Defaults to
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
            create and apply the essential components of a Stage. Defaults to
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