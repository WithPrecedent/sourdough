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
class Stage(sourdough.Component):
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
    
    def apply(self, step: 'sourdough.Plan') -> 'sourdough.Plan':
        """Returns a Plan with its 'contents' organized and instanced.

        The method first determines if the contents are already finalized. If 
        not, it creates them from 'settings'.
        
        Subclasses can call this method and then arrange the 'contents' of
        'step' based upon a specific structural design.
        
        Args:
            step (sourdough.Plan): Plan instance to organize the 
                information in 'contents' or 'settings'.

        Returns:
            sourdough.Plan: an instance with contents fully instanced.
                
        """
        step = self._draft_existing_contents(step = step)
        step = self._draft_from_settings(step = step)           
        return step      

    """ Private Methods """

    def _draft_existing_contents(self, 
            step: 'sourdough.Plan') -> 'sourdough.Plan':
        """
        
        Args:
            step (sourdough.Plan): Plan instance with str, Step, or Plan
                stored in contents.

        Raises:
            TypeError: if an item in 'contents' is not a str, Step, or Plan
                type.

        Returns:
            sourdough.Plan: an instance with contents fully instanced.
                
        """
        new_contents = []
        for labor in step.contents:
            if isinstance(labor, str):
                new_contents.append(self._draft_unknown(
                    labor = labor, 
                    step = step))
            elif isinstance(labor, (sourdough.Plan, sourdough.Step)):
                new_contents.append(labor)
            else:
                raise TypeError(
                    f'{step.name} contents must be str, Plan, or Step type')
        step.contents = new_contents
        return step
    
    def _draft_unknown(self,
            labor: str,
            step: 'sourdough.Plan') -> Union[
                'sourdough.Step', 
                'sourdough.Plan']:
        """[summary]

        Raises:
            KeyError: [description]

        Returns:
            [type]: [description]
        """
        try:
            test_instance = step.options[labor](name = 'test only')
        except KeyError:
            raise KeyError(f'{labor} not found in {step.name}')
        if isinstance(test_instance, sourdough.Step):
            return self._draft_step(
                step = labor, 
                technique = None, 
                step = step)
        else:
            return self._draft_step(step = labor, manager = step)

    def _draft_from_settings(self, 
            step: 'sourdough.Plan') -> 'sourdough.Plan':
        """Returns a single Plan instance created based on 'settings'.

        Args:
            step (sourdough.Plan): Plan instance to populate its 
                'contents' with information in 'settings'.

        Returns:
            sourdough.Plan: an step or subclass step with attributes 
                derived from a section of 'settings'.
                
        """
        steps = []
        steps = []
        techniques = {}
        attributes = {}
        step.contents = []
        for key, value in self.settings.contents[step.name].items():
            if key.endswith('_design'):
                step.design = value
            elif key.endswith('_steps'):
                steps = sourdough.tools.listify(value)
            elif key.endswith('_steps'):
                steps = sourdough.tools.listify(value)
            elif key.endswith('_techniques'):
                new_key = key.replace('_techniques', '')
                techniques[new_key] = sourdough.tools.listify(value)
            else:
                attributes[key] = value
        if steps:
            step = self._draft_steps(
                steps = steps, 
                techniques = techniques,
                step = step)
        elif steps:
            step = self._draft_steps(
                steps = steps,
                manager = step)
        for key, value in attributes.items():
            setattr(step, key, value)
        return step      

    def _draft_steps(self,
            steps: Sequence[str],
            manager: 'sourdough.Plan') -> 'sourdough.Plan':
        """[summary]

        Returns:
            [type]: [description]
            
        """
        new_steps = []
        for step in steps:
            new_steps.append(self._draft_step(
                step = step, 
                manager = manager))
        manager.contents.append(new_steps)
        return manager

    def _draft_step(self,
            step: str,
            manager: 'sourdough.Plan') -> 'sourdough.Plan':
        """[summary]

        Returns:
            [type]: [description]
            
        """
        try:
            new_step = manager.options[step](name = step)
        except KeyError:
            new_step = sourdough.Plan(name = step)
        return self.organize(step = new_step)
                  
    def _draft_steps(self, 
            step: 'sourdough.Plan',
            steps: Sequence[str],
            techniques: Mapping[str, Sequence[str]]) -> 'sourdough.Plan':
        """[summary]

        Returns:
            [type]: [description]
        """
        new_steps = []
        for step in steps:
            new_techniques = []
            for technique in techniques[step]:
                new_techniques.append(self._draft_step(
                    step = step,
                    technique = technique,
                    step = step.name))
            new_steps.append(new_techniques)
        step.contents.append(new_steps)
        return step
            
    def _draft_step(self,
            step: str,
            technique: str,
            step: str,
            options: 'sourdough.Catalog') -> 'sourdough.Step':
        """[summary]

        Returns:
            [type]: [description]
            
        """
        try:
            return step.options[step](
                name = step,
                step = step,
                technique = step.options[technique])
        except KeyError:
            try:
                return sourdough.Step(
                    name = step,
                    step = step,
                    technique = step.options[technique])
            except KeyError:
                try:
                    return step.options[step](
                        name = step,
                        step = step,
                        technique = sourdough.Technique(name = technique))
                except KeyError:
                    return sourdough.Step(
                        name = step,
                        step = step,
                        technique = sourdough.Technique(name = technique))


@dataclasses.dataclass
class Publisher(Stage):
    
    settings: 'sourdough.Settings'

    """ Public Methods """
    
    def add(self, 
            project: 'sourdough.Project', 
            step: str, 
            steps: Union[Sequence[str], str]) -> 'sourdough.Project':
        """Adds 'steps' to 'project' 'contents' with a 'step' key.
        
        Args:
            project (sourdough.Project): project to which 'step' and 'steps'
                should be added.
            step (str): key to use to store 'steps':
            steps (Union[Sequence[str], str]): name(s) of step(s) to add to 
                'project'.
            
        Returns:
            sourdough.Project: with 'steps' added at 'step'.
        
        """
        project.contents[step] = sourdough.tools.listify(steps)
        return project
 
    def apply(self, step: 'sourdough.Plan') -> 'sourdough.Plan':
        """[summary]

        Returns:
            [type] -- [description]
            
        """
        step = self._parameterize_steps(step = step)
        
        return step

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
            step = technique.step,
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
    
    def apply(self, step: 'sourdough.Plan') -> 'sourdough.Plan':
        """[summary]

        Returns:
            [type] -- [description]
            
        """
        step = self._parameterize_steps(step = step)
        
        return step


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
#             step = technique.step,
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
#             outer_step: sourdough.base.Plan,
#             data: Union[sourdough.Dataset, sourdough.base.Plan]) -> sourdough.base.Plan:
#         """Applies 'outer_step' instance in 'project' to 'data' or other stored outer_step.

#         Args:
#             outer_step ('outer_step'): instance with stored technique instances (either
#                 stored in the 'techniques' or 'inner_step' attributes).
#             data ([Union['Dataset', 'outer_step']): a data source with information to
#                 finalize 'parameters' for each technique instance in 'outer_step'

#         Returns:
#             'outer_step': with 'parameters' for each technique instance finalized
#                 and connected to 'algorithm'.

#         """
#         if hasattr(outer_step, 'techniques'):
#             outer_step = self._finalize_techniques(manuscript = outer_step, data = data)
#         else:
#             outer_step = self._finalize_inner_step(outer_step = outer_step, data = data)
#         return outer_step

#     """ Private Methods """

#     def _finalize_inner_step(self, outer_step: 'outer_step', data: 'Dataset') -> 'outer_step':
#         """Finalizes 'inner_step' instances in 'outer_step'.

#         Args:
#             outer_step ('outer_step'): instance containing 'inner_step' with 'techniques' that
#                 have 'data_dependent' and/or 'conditional' 'parameters' to
#                 add.
#             data ('Dataset): instance with potential information to use to
#                 finalize 'parameters' for 'outer_step'.

#         Returns:
#             'outer_step': with any necessary modofications made.

#         """
#         new_inner_step = [
#             self._finalize_techniques(inner_step = inner_step, data = data)
#             for inner_step in outer_step.inner_step]

#         outer_step.inner_step = new_inner_step
#         return outer_step

#     def _finalize_techniques(self,
#             manuscript: Union['outer_step', 'inner_step'],
#             data: ['Dataset', 'outer_step']) -> Union['outer_step', 'inner_step']:
#         """Subclasses may provide their own methods to finalize 'techniques'.

#         Args:
#             manuscript (Union['outer_step', 'inner_step']): manuscript containing
#                 'techniques' to apply.
#             data (['Dataset', 'outer_step']): instance with information used to
#                 finalize 'parameters' and/or 'algorithm'.

#         Returns:
#             Union['outer_step', 'inner_step']: with any necessary modofications made.

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
#             manuscript: 'outer_step',
#             technique: technique,
#             data: Union['Dataset', 'outer_step']) -> technique:
#         """Adds any conditional parameters to a technique instance.

#         Args:
#             manuscript ('outer_step'): outer_step instance with algorithms to apply to 'data'.
#             technique (technique): instance with parameters which can take
#                 new conditional parameters.
#             data (Union['Dataset', 'outer_step']): a data source which might
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
#             data: Union['Dataset', 'outer_step']) -> technique:
#         """Completes parameter dictionary by adding data dependent parameters.

#         Args:
#             technique (technique): instance with information about data
#                 dependent parameters to add.
#             data (Union['Dataset', 'outer_step']): a data source which contains
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

#     def _apply_inner_step(self,
#             outer_step: 'outer_step',
#             data: Union['Dataset', 'outer_step']) -> 'outer_step':
#         """Applies 'inner_step' in 'outer_step' instance in 'project' to 'data'.

#         Args:
#             outer_step ('outer_step'): instance with stored 'inner_step' instances.
#             data ('Dataset'): primary instance used by 'project'.

#         Returns:
#             'outer_step': with modifications made and/or 'data' incorporated.

#         """
#         new_inner_step = []
#         for i, inner_step in enumerate(outer_step.inner_step):
#             if self.verbose:
#                 print('Applying', inner_step.name, str(i + 1), 'to', data.name)
#             new_inner_step.append(self._apply_techniques(
#                 manuscript = inner_step,
#                 data = data))
#         outer_step.inner_step = new_inner_step
#         return outer_step

#     def _apply_techniques(self,
#             manuscript: Union['outer_step', 'inner_step'],
#             data: Union['Dataset', 'outer_step']) -> Union['outer_step', 'inner_step']:
#         """Applies 'techniques' in 'manuscript' to 'data'.

#         Args:
#             manuscript (Union['outer_step', 'inner_step']): instance with stored
#                 'techniques'.
#             data ('Dataset'): primary instance used by 'manuscript'.

#         Returns:
#             Union['outer_step', 'inner_step']: with modifications made and/or 'data'
#                 incorporated.

#         """
#         for technique in manuscript.techniques:
#             if self.verbose:
#                 print('Applying', technique.name, 'to', data.name)
#             if isinstance(data, Dataset):
#                 data = technique.apply(data = data)
#             else:
#                 for inner_step in data.inner_step:
#                     manuscript.inner_step.append(technique.apply(data = inner_step))
#         if isinstance(data, Dataset):
#             setattr(manuscript, 'data', data)
#         return manuscript

#     """ Core sourdough Methods """

#     def apply(self, outer_step: 'outer_step', data: Union['Dataset', 'outer_step']) -> 'outer_step':
#         """Applies 'outer_step' instance in 'project' to 'data' or other stored outer_step.

#         Args:
#             outer_step ('outer_step'): instance with stored technique instances (either
#                 stored in the 'techniques' or 'inner_step' attributes).
#             data ([Union['Dataset', 'outer_step']): a data source with information to
#                 finalize 'parameters' for each technique instance in 'outer_step'

#         Returns:
#             'outer_step': with 'parameters' for each technique instance finalized
#                 and connected to 'algorithm'.

#         """
#         if hasattr(outer_step, 'techniques'):
#             outer_step = self._apply_techniques(manuscript = outer_step, data = data)
#         else:
#             outer_step = self._apply_inner_step(outer_step = outer_step, data = data)
#         return outer_step