"""
.. module:: creators
:synopsis: sourdough workflow stages
:publisher: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import dataclasses
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union

import sourdough


@dataclasses.dataclass
class Author(sourdough.base.Creator):
    """Stores methods for constructing a Plan instance.
    
    Args:
        settings (sourdough.base.Settings): 
    
    """  
    settings: 'sourdough.base.Settings'
    
    """ Public Methods """
    
    def create(self, 
            plan: 'sourdough.project.Plan') -> 'sourdough.project.Plan':
        """Drafts a Plan with its 'contents' organized and instanced.

        The method first determines if the contents are already finalized. If 
        not, it creates them from 'settings'.
        
        Subclasses can call this method and then arrange the 'contents' of
        'plan' based upon a specific structural design.
        
        Args:
            plan (sourdough.project.Plan): Plan instance to organize the 
                information in 'contents' or 'settings'.

        Returns:
            sourdough.project.Plan: an instance with contents fully instanced.
                
        """
        plan = self._draft_existing_contents(plan = plan)
        plan = self._draft_from_settings(plan = plan)           
        return plan      

    """ Private Methods """

    def _draft_existing_contents(self, 
            plan: 'sourdough.project.Plan') -> 'sourdough.project.Plan':
        """
        
        Args:
            plan (sourdough.project.Plan): Plan instance with str, Step, or Plan
                stored in contents.

        Raises:
            TypeError: if an item in 'contents' is not a str, Step, or Plan
                type.

        Returns:
            sourdough.project.Plan: an instance with contents fully instanced.
                
        """
        new_contents = []
        for labor in plan.contents:
            if isinstance(labor, str):
                new_contents.append(self._draft_unknown(
                    labor = labor, 
                    plan = plan))
            elif isinstance(labor, sourdough.base.Task):
                new_contents.append(labor)
            else:
                raise TypeError(
                    f'{plan.name} contents must be str, Plan, or Step type')
        plan.contents = new_contents
        return plan
    
    def _draft_unknown(self,
            labor: str,
            plan: 'sourdough.project.Plan') -> Union[
                'sourdough.base.Step', 
                'sourdough.project.Plan']:
        """[summary]

        Raises:
            KeyError: [description]

        Returns:
            [type]: [description]
        """
        try:
            test_instance = plan.options[labor](name = 'test only')
        except KeyError:
            raise KeyError(f'{labor} not found in {plan.name}')
        if isinstance(test_instance, sourdough.base.Step):
            return self._draft_plan(
                plan = labor, 
                technique = None, 
                plan = plan)
        else:
            return self._draft_plan(plan = labor, manager = plan)

    def _draft_from_settings(self, 
            plan: 'sourdough.project.Plan') -> 'sourdough.project.Plan':
        """Returns a single Plan instance created based on 'settings'.

        Args:
            plan (sourdough.project.Plan): Plan instance to populate its 
                'contents' with information in 'settings'.

        Returns:
            sourdough.project.Plan: an plan or subclass plan with attributes 
                derived from a section of 'settings'.
                
        """
        plans = []
        steps = []
        techniques = {}
        attributes = {}
        plan.contents = []
        for key, value in self.settings.contents[plan.name].items():
            if key.endswith('_design'):
                plan.design = value
            elif key.endswith('_plans'):
                plans = sourdough.utilities.listify(value)
            elif key.endswith('steps'):
                steps = sourdough.utilities.listify(value)
            elif key.endswith('_techniques'):
                new_key = key.replace('_techniques', '')
                techniques[new_key] = sourdough.utilities.listify(value)
            else:
                attributes[key] = value
        if plans:
            plan = self._draft_plans(
                plans = plans, 
                techniques = techniques,
                plan = plan)
        elif plans:
            plan = self._draft_plans(
                plans = plans,
                manager = plan)
        for key, value in attributes.items():
            setattr(plan, key, value)
        return plan      

    def _draft_plans(self,
            plans: Sequence[str],
            manager: 'sourdough.project.Plan') -> 'sourdough.project.Plan':
        """[summary]

        Returns:
            [type]: [description]
            
        """
        new_plans = []
        for plan in plans:
            new_plans.append(self._draft_plan(
                plan = plan, 
                manager = manager))
        manager.contents.append(new_plans)
        return manager

    def _draft_plan(self,
            plan: str,
            manager: 'sourdough.project.Plan') -> 'sourdough.project.Plan':
        """[summary]

        Returns:
            [type]: [description]
            
        """
        try:
            new_plan = manager.options[plan](name = plan)
        except KeyError:
            new_plan = sourdough.project.Plan(name = plan)
        return self.organize(plan = new_plan)
                  
    # def _draft_plans(self, 
    #         plan: 'sourdough.project.Plan',
    #         plans: Sequence[str],
    #         techniques: Mapping[str, Sequence[str]]) -> 'sourdough.project.Plan':
    #     """[summary]

    #     Returns:
    #         [type]: [description]
    #     """
    #     new_plans = []
    #     for plan in plans:
    #         new_techniques = []
    #         for technique in techniques[plan]:
    #             new_techniques.append(self._draft_plan(
    #                 plan = plan,
    #                 technique = technique,
    #                 plan = plan.name))
    #         new_plans.append(new_techniques)
    #     plan.contents.append(new_plans)
    #     return plan
            
    # def _draft_plan(self,
    #         plan: str,
    #         technique: str,
    #         plan: str,
    #         options: 'sourdough.base.Catalog') -> 'sourdough.base.Step':
    #     """[summary]

    #     Returns:
    #         [type]: [description]
            
    #     """
    #     try:
    #         return plan.options[plan](
    #             name = plan,
    #             plan = plan,
    #             technique = plan.options[technique])
    #     except KeyError:
    #         try:
    #             return sourdough.base.Step(
    #                 name = plan,
    #                 plan = plan,
    #                 technique = plan.options[technique])
    #         except KeyError:
    #             try:
    #                 return plan.options[plan](
    #                     name = plan,
    #                     plan = plan,
    #                     technique = sourdough.base.Technique(name = technique))
    #             except KeyError:
    #                 return sourdough.base.Step(
    #                     name = plan,
    #                     plan = plan,
    #                     technique = sourdough.base.Technique(name = technique))


@dataclasses.dataclass
class Publisher(sourdough.base.Creator):
    
    settings: 'sourdough.base.Settings'

    """ Public Methods """
    
    def add(self, 
            project: 'sourdough.project.Project', 
            plan: str, 
            plans: Union[Sequence[str], str]) -> 'sourdough.project.Project':
        """Adds 'plans' to 'project' 'contents' with a 'plan' key.
        
        Args:
            project (sourdough.project.Project): project to which 'plan' and 'plans'
                should be added.
            plan (str): key to use to store 'plans':
            plans (Union[Sequence[str], str]): name(s) of plan(s) to add to 
                'project'.
            
        Returns:
            sourdough.project.Project: with 'plans' added at 'plan'.
        
        """
        project.contents[plan] = sourdough.utilities.listify(plans)
        return project
 
    def create(self, plan: 'sourdough.project.Plan') -> 'sourdough.project.Plan':
        """[summary]

        Returns:
            [type] -- [description]
            
        """
        plan = self._parameterize_plans(plan = plan)
        
        return plan

    """ Private Methods """
    
    def get(self, technique: sourdough.base.technique) -> sourdough.base.technique:
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
            technique: sourdough.base.technique) -> sourdough.base.technique:
        """Acquires parameters from 'Settings' instance.

        Args:
            technique (technique): an instance for parameters to be added to.

        Returns:
            technique: instance with parameters added.

        """
        return self.settings.get_parameters(
            plan = technique.plan,
            technique = technique.name)

    def _get_selected(self,
            technique: sourdough.base.technique) -> sourdough.base.technique:
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
            technique: sourdough.base.technique) -> sourdough.base.technique:
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
            technique: sourdough.base.technique) -> sourdough.base.technique:
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
            technique: sourdough.base.technique) -> sourdough.base.technique:
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
class Reader(sourdough.base.Creator):
    
    settings: 'sourdough.base.Settings'
    
    def create(self, plan: 'sourdough.project.Plan') -> 'sourdough.project.Plan':
        """[summary]

        Returns:
            [type] -- [description]
            
        """
        plan = self._parameterize_plans(plan = plan)
        
        return plan


# @dataclasses.dataclass
# class Parametizer(sourdough.base.Component):
#     """Constructs technique with an 'algorithm' and 'parameters'.

#     Args:
#         name (str): designates the name of the class instance used
#             for internal referencing throughout sourdough.base. If the class instance
#             needs settings from the shared Settings instance, 'name' should
#             match the appropriate section name in that Settings instance. When
#             subclassing, it is a good settings to use the same 'name' attribute
#             as the base class for effective coordination between sourdough
#             classes. Defaults to None or __class__.__name__.lower().
#         settings (Settings]): shared project settings settings.
#         instructions (Instructions]): an instance with information to
#             create and create the essential components of a sourdough.base.Creator. Defaults to
#             None.

#     """
#     name: str = None
#     settings: sourdough.base.Settings] = None
#     instructions: Instructions] = None

#     """ Public Methods """

#     def get(self, technique: sourdough.base.technique) -> sourdough.base.technique:
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
#             technique: sourdough.base.technique) -> sourdough.base.technique:
#         """Acquires parameters from 'Settings' instance.

#         Args:
#             technique (technique): an instance for parameters to be added to.

#         Returns:
#             technique: instance with parameters added.

#         """
#         return self.settings.get_parameters(
#             plan = technique.plan,
#             technique = technique.name)

#     def _get_selected(self,
#             technique: sourdough.base.technique) -> sourdough.base.technique:
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
#             technique: sourdough.base.technique) -> sourdough.base.technique:
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
#             technique: sourdough.base.technique) -> sourdough.base.technique:
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
#             technique: sourdough.base.technique) -> sourdough.base.technique:
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
# class Finisher(sourdough.base.Technique):
#     """Finalizes technique instances with data-dependent parameters.

#     Args:
#         name (str): designates the name of the class instance used
#             for internal referencing throughout sourdough.base. If the class instance
#             needs settings from the shared Settings instance, 'name' should
#             match the appropriate section name in that Settings instance. When
#             subclassing, it is a good settings to use the same 'name' attribute
#             as the base class for effective coordination between sourdough
#             classes. Defaults to None or __class__.__name__.lower().
#         Settings (Settings]): shared project settings settings.
#         instructions (Instructions]): an instance with information to
#             create and create the essential components of a sourdough.base.Creator. Defaults to
#             None.

#     """
#     name: str = None
#     Settings: sourdough.base.Settings] = None
#     instructions: Instructions] = None

#     """ Public Methods """

#     def create(self,
#             outer_plan: sourdough.base.base.Plan,
#             data: Union[sourdough.base.Dataset, sourdough.base.base.Plan]) -> sourdough.base.base.Plan:
#         """Applies 'outer_plan' instance in 'project' to 'data' or other stored outer_plan.

#         Args:
#             outer_plan ('outer_plan'): instance with stored technique instances (either
#                 stored in the 'techniques' or 'inner_plan' attributes).
#             data ([Union['Dataset', 'outer_plan']): a data source with information to
#                 finalize 'parameters' for each technique instance in 'outer_plan'

#         Returns:
#             'outer_plan': with 'parameters' for each technique instance finalized
#                 and connected to 'algorithm'.

#         """
#         if hasattr(outer_plan, 'techniques'):
#             outer_plan = self._finalize_techniques(manuscript = outer_plan, data = data)
#         else:
#             outer_plan = self._finalize_inner_plan(outer_plan = outer_plan, data = data)
#         return outer_plan

#     """ Private Methods """

#     def _finalize_inner_plan(self, outer_plan: 'outer_plan', data: 'Dataset') -> 'outer_plan':
#         """Finalizes 'inner_plan' instances in 'outer_plan'.

#         Args:
#             outer_plan ('outer_plan'): instance containing 'inner_plan' with 'techniques' that
#                 have 'data_dependent' and/or 'conditional' 'parameters' to
#                 add.
#             data ('Dataset): instance with potential information to use to
#                 finalize 'parameters' for 'outer_plan'.

#         Returns:
#             'outer_plan': with any necessary modofications made.

#         """
#         new_inner_plan = [
#             self._finalize_techniques(inner_plan = inner_plan, data = data)
#             for inner_plan in outer_plan.inner_plan]

#         outer_plan.inner_plan = new_inner_plan
#         return outer_plan

#     def _finalize_techniques(self,
#             manuscript: Union['outer_plan', 'inner_plan'],
#             data: ['Dataset', 'outer_plan']) -> Union['outer_plan', 'inner_plan']:
#         """Subclasses may provide their own methods to finalize 'techniques'.

#         Args:
#             manuscript (Union['outer_plan', 'inner_plan']): manuscript containing
#                 'techniques' to create.
#             data (['Dataset', 'outer_plan']): instance with information used to
#                 finalize 'parameters' and/or 'algorithm'.

#         Returns:
#             Union['outer_plan', 'inner_plan']: with any necessary modofications made.

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
#             manuscript: 'outer_plan',
#             technique: technique,
#             data: Union['Dataset', 'outer_plan']) -> technique:
#         """Adds any conditional parameters to a technique instance.

#         Args:
#             manuscript ('outer_plan'): outer_plan instance with algorithms to create to 'data'.
#             technique (technique): instance with parameters which can take
#                 new conditional parameters.
#             data (Union['Dataset', 'outer_plan']): a data source which might
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
#             data: Union['Dataset', 'outer_plan']) -> technique:
#         """Completes parameter dictionary by adding data dependent parameters.

#         Args:
#             technique (technique): instance with information about data
#                 dependent parameters to add.
#             data (Union['Dataset', 'outer_plan']): a data source which contains
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
# class Scholar(sourdough.base.Technique):
#     """Base class for createing technique instances to data.

#     Args:
#         name (str): designates the name of the class instance used
#             for internal referencing throughout sourdough.base. If the class instance
#             needs settings from the shared Settings instance, 'name' should
#             match the appropriate section name in that Settings instance. When
#             subclassing, it is a good settings to use the same 'name' attribute
#             as the base class for effective coordination between sourdough
#             classes. Defaults to None or __class__.__name__.lower().
#         Settings (Settings]): shared project settings settings.
#         instructions (Instructions]): an instance with information to
#             create and create the essential components of a sourdough.base.Creator. Defaults to
#             None.

#     """
#     name: str = None
#     instructions: Instructions] = None
#     Settings: sourdough.base.Settings] = None

#     def __post_init__(self) -> None:
#         """Initializes class instance attributes."""
#         self = self.settings.create(instance = self)
#         return self

#     """ Private Methods """

#     def _create_inner_plan(self,
#             outer_plan: 'outer_plan',
#             data: Union['Dataset', 'outer_plan']) -> 'outer_plan':
#         """Applies 'inner_plan' in 'outer_plan' instance in 'project' to 'data'.

#         Args:
#             outer_plan ('outer_plan'): instance with stored 'inner_plan' instances.
#             data ('Dataset'): primary instance used by 'project'.

#         Returns:
#             'outer_plan': with modifications made and/or 'data' incorporated.

#         """
#         new_inner_plan = []
#         for i, inner_plan in enumerate(outer_plan.inner_plan):
#             if self.verbose:
#                 print('Applying', inner_plan.name, str(i + 1), 'to', data.name)
#             new_inner_plan.append(self._create_techniques(
#                 manuscript = inner_plan,
#                 data = data))
#         outer_plan.inner_plan = new_inner_plan
#         return outer_plan

#     def _create_techniques(self,
#             manuscript: Union['outer_plan', 'inner_plan'],
#             data: Union['Dataset', 'outer_plan']) -> Union['outer_plan', 'inner_plan']:
#         """Applies 'techniques' in 'manuscript' to 'data'.

#         Args:
#             manuscript (Union['outer_plan', 'inner_plan']): instance with stored
#                 'techniques'.
#             data ('Dataset'): primary instance used by 'manuscript'.

#         Returns:
#             Union['outer_plan', 'inner_plan']: with modifications made and/or 'data'
#                 incorporated.

#         """
#         for technique in manuscript.techniques:
#             if self.verbose:
#                 print('Applying', technique.name, 'to', data.name)
#             if isinstance(data, Dataset):
#                 data = technique.create(data = data)
#             else:
#                 for inner_plan in data.inner_plan:
#                     manuscript.inner_plan.append(technique.create(data = inner_plan))
#         if isinstance(data, Dataset):
#             setattr(manuscript, 'data', data)
#         return manuscript

#     """ Core sourdough Methods """

#     def create(self, outer_plan: 'outer_plan', data: Union['Dataset', 'outer_plan']) -> 'outer_plan':
#         """Applies 'outer_plan' instance in 'project' to 'data' or other stored outer_plan.

#         Args:
#             outer_plan ('outer_plan'): instance with stored technique instances (either
#                 stored in the 'techniques' or 'inner_plan' attributes).
#             data ([Union['Dataset', 'outer_plan']): a data source with information to
#                 finalize 'parameters' for each technique instance in 'outer_plan'

#         Returns:
#             'outer_plan': with 'parameters' for each technique instance finalized
#                 and connected to 'algorithm'.

#         """
#         if hasattr(outer_plan, 'techniques'):
#             outer_plan = self._create_techniques(manuscript = outer_plan, data = data)
#         else:
#             outer_plan = self._create_inner_plan(outer_plan = outer_plan, data = data)
#         return outer_plan