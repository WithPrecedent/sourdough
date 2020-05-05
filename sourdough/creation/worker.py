"""
.. module:: worker
:synopsis: project management made simple
:publisher: Corey Rayburn Yung
:copyright: 2019-2020
:license: Apache-2.0
"""

import collections.abc
import dataclasses
import importlib
import itertools
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Union

import sourdough


@dataclasses.dataclass
class Instructions(sourdough.Loader):
    """Instructions for 'Worker' construction and usage.

    Args:
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. If the class instance
            needs settings from the shared Settings instance, 'name' should
            match the appropriate section name in that Settings instance. When
            subclassing, it is a good settings to use the same 'name' attribute
            as the base class for effective coordination between sourdough
            classes. Defaults to None or __class__.__name__.lower().
        module (Optional[str]): name of module where object to use is located
            (can either be a sourdough or non-sourdough module). Defaults to
            'sourdough.worker'.
        default_module (Optional[str]): a backup name of module where object to
            use is located (can either be a sourdough or non-sourdough module).
            Defaults to 'sourdough.worker'.
        worker (Optional[str]): name of Worker object in 'module' to load.
            Defaults to 'Worker'.
        technique (Optional[str]): name of Technique object in 'module' to load.
            Defaults to Technique.
        options (Optional[Union[str, Repository]]): name of a
            Repository instance with various options available to a
            particular 'Worker' instance or a Repository instance.
            Defaults to an empty Repository.
        comparer (Optional[bool]): whether the 'Worker' has a parallel structure
            allowing for comparison of different alternatives (True) or is a
            singular sequence of steps (False). Defaults to False.

    """
    name: Optional[str] = None
    module: Optional[str] = dataclasses.field(
        default_factory = lambda: 'sourdough.worker')
    default_module: Optional[str] = dataclasses.field(
        default_factory = lambda: 'sourdough.worker')
    worker: Optional[str] = dataclasses.field(
        default_factory = lambda: 'Worker')
    technique: Optional[str] = dataclasses.field(
        default_factory = lambda: Technique)
    options: Optional[Union[str, sourdough.Repository]] = dataclasses.field(
        default_factory = sourdough.Repository)
    comparer: Optional[bool] = False
    input_folder: Optional[str] = None
    output_folder: Optional[str] = None
    input_file_name: Optional[str] = None
    output_file_name: Optional[str] = None
    input_file_format: Optional[str] = None
    output_file_format: Optional[str] = None

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        super().__post_init__()
        for attribute in ['worker', Technique, 'options']:
            setattr(self, attribute, self.load(attribute))
        self.options = self.options()
        return self


@dataclasses.dataclass
class Worker(sourdough.System):
    """Base class for sourdough project management.

    Args:
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

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        super().__post_init__()
        # Creates Parametizer instance to gather and select parameters for
        # created 'Plan' instances.
        self.parametizer = Parametizer(
            settings = self.settings,
            instructions = self.instructions)
        # Returns appropriate subclass base on 'comparer' attribute of
        # 'instructions'.
        if not issubclass(self, self.__class__):
            if self.instructions.comparer:
                return Comparer(
                    name = self.name,
                    instructions = self.instructions,
                    Settings = self.settings)
            else:
                return Sequencer(
                    name = self.name,
                    instructions = self.instructions,
                    Settings = self.settings)

    """ Overview Property """

    @property
    def overview(self) -> Dict[str, List[str]]:
        """Returns snapshot of current state of selected options.

        Returns:
            Dict[str, List[str]]: keys are steps and values are lists of
                selected options.

        """
        try:
            return self._overview
        except AttributeError:
            self._overview = self._get_overview()
            return self._overview

    @overview.setter
    def overview(self, overview: Dict[str, List[str]]) -> None:
        """Sets snapshot of selected options.

        Setting 'overview' will affect other methods which use 'overview' to
        identify which options have been selected.

        Args:
            overview (Dict[str, List[str]]): keys are steps and values are lists
                of selected options.

        """
        if (isinstance(overview, dict)
                and all(isinstance(v, list) for v in overview.values())):
            self._overview = overview
        else:
            raise TypeError(f'overview must be dict of lists')
        return self

    @overview.deleter
    def overview(self) -> None:
        """Sets snapshot of selected options to an empty dictionary.

        There are few, if any reasons, to use the 'overview' deleter. It is
        included in case a user wants the option to clear out current selections
        and add more manually.

        """
        self._overview = {}
        return self

    """ Private Methods """

    def _get_overview(self) -> Dict[str, List[str]]:
        """Creates dictionary with techniques for each step.

        Returns:
            Dict[str, Dict[str, List[str]]]: dictionary with keys of steps and
                values of lists of techniques.

        """
        steps = self.settings.get_steps(section = self.instructions.name)
        overview = {}
        for step in steps:
            overview[step] = self.settings.get_techniques(
                section = self.instructions.name,
                step = step)
        return overview


@dataclasses.dataclass
class Comparer(Worker):
    """Base class for sourdough project management with parallel structure.

    Args:
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

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        super().__post_init__()
        return self

    """ Public Methods """

    def create_plan(self,
            overview: Optional[Dict[str,str]] = None,
            outer_name: Optional[str] = None,
            inner_name: Optional[str] = None) -> sourdough.Plan:
        """Creates a 'Plan' with a parallel structure.

        Returns:
            'Plan': configured to spefications in 'instructions'.

        """
        if overview is None:
            overview = self.overview
        if outer_name is None:
            outer_name = self.instructions.name
        if inner_name is None:
            inner_name = 'plan'
        # Creates a 'Plan' instance to store other 'Plan' instances.
        outer_plan = sourdough.Plan(name = outer_name)
        # Creates list of steps from 'outline'.
        steps = list(overview.keys())
        # Creates 'possible' list of lists of 'techniques'.
        possible = list(overview.values())
        # Creates a list of lists of the Cartesian product of 'possible'.
        combinations = list(map(list, itertools.product(*possible)))
        # Creates a 'inner_plan' for each combination of techniques and adds that
        # 'inner_plan' to 'outer_plan'.
        for i, techniques in enumerate(combinations):
            inner_plan = sourdough.Plan(
                name = f'{inner_name}_{i}',
                extender = False)
            step_techniques = tuple(zip(steps, techniques))
            for technique in step_techniques:
                technique = self.instructions.technique.load()(
                    name = technique[0],
                    technique = technique[1])
                technique = self.parametizer.get(technique = technique)
                inner_plan.add(contents = technique)
            outer_plan.add(contents = inner_plan)
        return outer_plan


@dataclasses.dataclass
class Sequencer(Worker):
    """Base class for sourdough project management with serial structure.

    Args:
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

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        super().__post_init__()
        return self

    """ Public Methods """

    def create_plan(self,
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
        for step, techniques in self.overview.items():
            inner_plan = sourdough.Plan(name = step)
            for technique in techniques:
                technique = self.instructions.technique(
                    name = step,
                    technique = technique)
                technique = self.parametizer.get(technique = technique)
                inner_plan.add(contents = technique)
            outer_plan.add(contents = inner_plan)
        return outer_plan


@dataclasses.dataclass
class Parametizer(sourdough.Component):
    """Constructs Technique with an 'algorithm' and 'parameters'.

    Args:
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

    def get(self, technique: sourdough.Technique) -> sourdough.Technique:
        """Adds appropriate parameters to Technique.

        Args:
            technique (Technique): instance for parameters to be added.

        Returns:
            Technique: instance ready for application.

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
            technique: sourdough.Technique) -> sourdough.Technique:
        """Acquires parameters from 'Settings' instance.

        Args:
            technique (Technique): an instance for parameters to be added to.

        Returns:
            Technique: instance with parameters added.

        """
        return self.settings.get_parameters(
            step = technique.step,
            technique = technique.name)

    def _get_selected(self,
            technique: sourdough.Technique) -> sourdough.Technique:
        """Limits parameters to those appropriate to the Technique.

        If 'technique.selected' is True, the keys from 'technique.defaults' are
        used to select the final returned parameters.

        If 'technique.selected' is a list of parameter keys, then only those
        parameters are selected for the final returned parameters.

        Args:
            technique (Technique): an instance for parameters to be added to.

        Returns:
            Technique: instance with parameters added.

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
            technique: sourdough.Technique) -> sourdough.Technique:
        """Adds required parameters (mandatory additions) to 'parameters'.

        Args:
            technique (Technique): an instance for parameters to be added to.

        Returns:
            Technique: instance with parameters added.

        """
        try:
            technique.parameters.update(technique.required)
        except TypeError:
            pass
        return technique

    def _get_search(self,
            technique: sourdough.Technique) -> sourdough.Technique:
        """Separates variables with multiple options to search parameters.

        Args:
            technique (Technique): an instance for parameters to be added to.

        Returns:
            Technique: instance with parameters added.

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
            technique: sourdough.Technique) -> sourdough.Technique:
        """Adds parameters that are determined at runtime.

        The primary example of a runtime parameter throughout sourdough is the
        addition of a random seed for a consistent, replicable state.

        Args:
            technique (Technique): an instance for parameters to be added to.

        Returns:
            Technique: instance with parameters added.

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
class Finisher(sourdough.Task):
    """Finalizes Technique instances with data-dependent parameters.

    Args:
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

        Args:
            outer_plan ('outer_plan'): instance with stored Technique instances (either
                stored in the 'techniques' or 'inner_plans' attributes).
            data ([Union['Dataset', 'outer_plan']): a data source with information to
                finalize 'parameters' for each Technique instance in 'outer_plan'

        Returns:
            'outer_plan': with 'parameters' for each Technique instance finalized
                and connected to 'algorithm'.

        """
        if hasattr(outer_plan, 'techniques'):
            outer_plan = self._finalize_techniques(manuscript = outer_plan, data = data)
        else:
            outer_plan = self._finalize_inner_plans(outer_plan = outer_plan, data = data)
        return outer_plan

    """ Private Methods """

    def _finalize_inner_plans(self, outer_plan: 'outer_plan', data: 'Dataset') -> 'outer_plan':
        """Finalizes 'inner_plan' instances in 'outer_plan'.

        Args:
            outer_plan ('outer_plan'): instance containing 'inner_plans' with 'techniques' that
                have 'data_dependent' and/or 'conditional' 'parameters' to
                add.
            data ('Dataset): instance with potential information to use to
                finalize 'parameters' for 'outer_plan'.

        Returns:
            'outer_plan': with any necessary modofications made.

        """
        new_inner_plans = [
            self._finalize_techniques(inner_plan = inner_plan, data = data)
            for inner_plan in outer_plan.inner_plans]

        outer_plan.inner_plans = new_inner_plans
        return outer_plan

    def _finalize_techniques(self,
            manuscript: Union['outer_plan', 'inner_plan'],
            data: ['Dataset', 'outer_plan']) -> Union['outer_plan', 'inner_plan']:
        """Subclasses may provide their own methods to finalize 'techniques'.

        Args:
            manuscript (Union['outer_plan', 'inner_plan']): manuscript containing
                'techniques' to apply.
            data (['Dataset', 'outer_plan']): instance with information used to
                finalize 'parameters' and/or 'algorithm'.

        Returns:
            Union['outer_plan', 'inner_plan']: with any necessary modofications made.

        """
        new_techniques = []
        for technique in manuscript.techniques:
            if technique.name not in ['none']:
                new_technique = self._add_conditionals(
                    manuscript = manuscript,
                    technique = technique,
                    data = data)
                new_technique = self._add_data_dependent(
                    technique = technique,
                    data = data)
                new_techniques.append(self._add_parameters_to_algorithm(
                    technique = technique))
        manuscript.techniques = new_techniques
        return manuscript

    def _add_conditionals(self,
            manuscript: 'outer_plan',
            technique: Technique,
            data: Union['Dataset', 'outer_plan']) -> Technique:
        """Adds any conditional parameters to a Technique instance.

        Args:
            manuscript ('outer_plan'): outer_plan instance with algorithms to apply to 'data'.
            technique (Technique): instance with parameters which can take
                new conditional parameters.
            data (Union['Dataset', 'outer_plan']): a data source which might
                contain information for condtional parameters.

        Returns:
            Technique: instance with any conditional parameters added.

        """
        try:
            if technique is not None:
                return getattr(manuscript, '_'.join(
                    ['_add', technique.name, 'conditionals']))(
                        technique = technique,
                        data = data)
        except AttributeError:
            return technique

    def _add_data_dependent(self,
            technique: Technique,
            data: Union['Dataset', 'outer_plan']) -> Technique:
        """Completes parameter dictionary by adding data dependent parameters.

        Args:
            technique (Technique): instance with information about data
                dependent parameters to add.
            data (Union['Dataset', 'outer_plan']): a data source which contains
                'data_dependent' variables.

        Returns:
            Technique: with any data dependent parameters added.

        """
        if technique is not None and technique.data_dependent is not None:

            for key, value in technique.data_dependent.items():
                try:
                    technique.parameters.update({key: getattr(data, value)})
                except KeyError:
                    print('no matching parameter found for', key, 'in data')
        return technique

    def _add_parameters_to_algorithm(self,
            technique: Technique) -> Technique:
        """Instances 'algorithm' with 'parameters' in Technique.

        Args:
            technique (Technique): with completed 'algorith' and 'parameters'.

        Returns:
            Technique: with 'algorithm' instanced with 'parameters'.

        """
        if technique is not None:
            try:
                technique.algorithm = technique.algorithm(
                    **technique.parameters)
            except AttributeError:
                try:
                    technique.algorithm = technique.algorithm(
                        technique.parameters)
                except AttributeError:
                    technique.algorithm = technique.algorithm()
            except TypeError:
                try:
                    technique.algorithm = technique.algorithm()
                except TypeError:
                    pass
        return technique


@dataclasses.dataclass
class Scholar(sourdough.Task):
    """Base class for applying Technique instances to data.

    Args:
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

        Args:
            outer_plan ('outer_plan'): instance with stored 'inner_plan' instances.
            data ('Dataset'): primary instance used by 'project'.

        Returns:
            'outer_plan': with modifications made and/or 'data' incorporated.

        """
        new_inner_plans = []
        for i, inner_plan in enumerate(outer_plan.inner_plans):
            if self.verbose:
                print('Applying', inner_plan.name, str(i + 1), 'to', data.name)
            new_inner_plans.append(self._apply_techniques(
                manuscript = inner_plan,
                data = data))
        outer_plan.inner_plans = new_inner_plans
        return outer_plan

    def _apply_techniques(self,
            manuscript: Union['outer_plan', 'inner_plan'],
            data: Union['Dataset', 'outer_plan']) -> Union['outer_plan', 'inner_plan']:
        """Applies 'techniques' in 'manuscript' to 'data'.

        Args:
            manuscript (Union['outer_plan', 'inner_plan']): instance with stored
                'techniques'.
            data ('Dataset'): primary instance used by 'manuscript'.

        Returns:
            Union['outer_plan', 'inner_plan']: with modifications made and/or 'data'
                incorporated.

        """
        for technique in manuscript.techniques:
            if self.verbose:
                print('Applying', technique.name, 'to', data.name)
            if isinstance(data, Dataset):
                data = technique.apply(data = data)
            else:
                for inner_plan in data.inner_plans:
                    manuscript.inner_plans.append(technique.apply(data = inner_plan))
        if isinstance(data, Dataset):
            setattr(manuscript, 'data', data)
        return manuscript

    """ Core sourdough Methods """

    def apply(self, outer_plan: 'outer_plan', data: Union['Dataset', 'outer_plan']) -> 'outer_plan':
        """Applies 'outer_plan' instance in 'project' to 'data' or other stored outer_plans.

        Args:
            outer_plan ('outer_plan'): instance with stored Technique instances (either
                stored in the 'techniques' or 'inner_plans' attributes).
            data ([Union['Dataset', 'outer_plan']): a data source with information to
                finalize 'parameters' for each Technique instance in 'outer_plan'

        Returns:
            'outer_plan': with 'parameters' for each Technique instance finalized
                and connected to 'algorithm'.

        """
        if hasattr(outer_plan, 'techniques'):
            outer_plan = self._apply_techniques(manuscript = outer_plan, data = data)
        else:
            outer_plan = self._apply_inner_plans(outer_plan = outer_plan, data = data)
        return outer_plan