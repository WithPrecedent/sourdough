"""
creators: sourdough workflow stages for object creation
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Author (Creator): creates a Plan instance from passed arguments and/or a 
        Settings instance.
    Publisher (Creator): finalizes a Plan instance based upon the initial
        construction by an Author instance and/or runtime user editing.
    Reader (Creator): executes a Plan instance, storing changes and results
        in the Reader instance and/or passed data object.

"""
import dataclasses
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union

import sourdough


@dataclasses.dataclass
class Author(sourdough.Creator):
    """Constructs composite objects from user settings.
    
    Args:
        project (sourdough.Project): the related Project instance.
    
    """
    project: 'sourdough.Project' 
    
    """ Public Methods """
    
    def create(self, plan: 'sourdough.Plan') -> 'sourdough.Plan':
        """Drafts a plan with its 'contents' organized and instanced.
        
        Args:
            plan (sourdough.Plan): Plan instance to organize the 
                information in 'contents' or 'settings'.

        Returns:
            sourdough.Plan: an instance with contents fully instanced.
                
        """
        plan = self._initialize_plan_contents(plan = plan)
        plan = self._create_from_settings(plan = plan)
        return plan      

    """ Private Methods """

    def _create_from_settings(self, plan: 'sourdough.Plan') -> 'sourdough.Plan':
        """Returns a single Plan instance created based on 'project.settings'.

        Args:
            plan (sourdough.Plan): Plan instance to populate its 'contents' with 
                information in 'settings'.

        Returns:
            sourdough.Plan: n plan or subclass plan with attributes derived from 
                a section of 'settings'.
                
        """
        attributes = {}
        for key, value in self.project.settings[plan.name].items():
            if key.endswith('_design'):
                plan.design = value
            elif key.endswith('_plan'):
                for item in sourdough.utilities.listify(value):
                    plan.append(self.create(plan = item))
            elif key.endswith('_tasks'):
                plan.extend(self._create_tasks(
                    tasks = sourdough.utilities.listify(value)))
            elif key.endswith('_techniques'):
                new_key = key.replace('_techniques', '')
                plan.extend(self._create_techniques(
                    techniques = sourdough.utilities.listify(value)))
            else:
                attributes[key] = value
        # Adds an extra settings as attributes to plan.
        for key, value in attributes.items():
            setattr(plan, key, value)
        return plan      
    
    def _initialize_plan_contents(self, 
            plan: 'sourdough.Plan') -> 'sourdough.Plan':
        """
        
        Args:
            plan (sourdough.Plan): Plan instance with str or Action 
                subclass.

        Raises:
            TypeError: if an item in 'contents' is not a str or Action subclass.

        Returns:
            sourdough.Plan: an instance with contents fully instanced.
                
        """
        new_contents = []
        try:
            for component in plan.contents:
                if isinstance(component, str):
                    new_contents.append(
                        self._draft_unknown(component = component))
                elif isinstance(component, sourdough.Plan):
                    self.create(plan = component)
                elif isinstance(component, sourdough.Action):
                    new_contents.append(component)
                else:
                    raise TypeError(
                        f'{plan.name} contents must be str or Action subclass')
            plan.contents = new_contents
        except TypeError:
            plan.contents = []
        return plan
    
    def _draft_unknown(self,
            action: str,
            plan: 'sourdough.Plan') -> Union[
                'sourdough.Task', 
                'sourdough.Plan']:
        """[summary]

        Raises:
            KeyError: [description]

        Returns:
            [type]: [description]
        """
        try:
            test_instance = plan.options[action](name = 'test only')
        except KeyError:
            raise KeyError(f'{action} not found in {plan.name}')
        if isinstance(test_instance, sourdough.Task):
            return self._draft_plan(
                plan = action, 
                technique = None, 
                plan = plan)
        else:
            return self._draft_plan(plan = action, project = plan)

    def _draft_plans(self,
            plans: Sequence[str],
            project: 'sourdough.Plan') -> 'sourdough.Plan':
        """[summary]

        Returns:
            [type]: [description]
            
        """
        new_plans = []
        for plan in plans:
            new_plans.append(self._draft_plan(
                plan = plan, 
                project = project))
        project.contents.append(new_plans)
        return project

    def _draft_plan(self,
            plan: str,
            project: 'sourdough.Plan') -> 'sourdough.Plan':
        """[summary]

        Returns:
            [type]: [description]
            
        """
        try:
            new_plan = project.options[plan](name = plan)
        except KeyError:
            new_plan = sourdough.Plan(name = plan)
        return self.organize(plan = new_plan)
                  
    # def _draft_plans(self, 
    #         plan: 'sourdough.Plan',
    #         plans: Sequence[str],
    #         techniques: Mapping[str, Sequence[str]]) -> 'sourdough.Plan':
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
    #         options: 'sourdough.Catalog') -> 'sourdough.Task':
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
    #             return sourdough.Task(
    #                 name = plan,
    #                 plan = plan,
    #                 technique = plan.options[technique])
    #         except KeyError:
    #             try:
    #                 return plan.options[plan](
    #                     name = plan,
    #                     plan = plan,
    #                     technique = sourdough.Technique(name = technique))
    #             except KeyError:
    #                 return sourdough.Task(
    #                     name = plan,
    #                     plan = plan,
    #                     technique = sourdough.Technique(name = technique))


@dataclasses.dataclass
class Publisher(sourdough.Creator):
    
    project: 'sourdough.Project'  

    """ Public Methods """
    
    def add(self, 
            manager: 'sourdough.Manager', 
            plan: str, 
            plans: Union[Sequence[str], str]) -> 'sourdough.Manager':
        """Adds 'plans' to 'manager' 'contents' with a 'plan' key.
        
        Args:
            manager (sourdough.Manager): manager to which 'plan' and 'plans'
                should be added.
            plan (str): key to use to store 'plans':
            plans (Union[Sequence[str], str]): name(s) of plan(s) to add to 
                'manager'.
            
        Returns:
            sourdough.Manager: with 'plans' added at 'plan'.
        
        """
        manager.contents[plan] = sourdough.utilities.listify(plans)
        return manager
 
    def create(self, plan: 'sourdough.Plan') -> 'sourdough.Plan':
        """[summary]

        Returns:
            [type] -- [description]
            
        """
        plan = self._parameterize_plans(plan = plan)
        
        return plan

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
        return self.project.settings.get_parameters(
            plan = technique.plan,
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
                        {key: getattr(self.project.settings['general'], value)})
                except AttributeError:
                    raise AttributeError(' '.join(
                        ['no matching runtime parameter', key, 'found']))
        except (AttributeError, TypeError):
            pass
        return technique



@dataclasses.dataclass
class Reader(sourdough.Creator):
    
    project: 'sourdough.Project'  
    
    def create(self, plan: 'sourdough.Plan') -> 'sourdough.Plan':
        """[summary]

        Returns:
            [type] -- [description]
            
        """
        plan = self._parameterize_plans(plan = plan)
        
        return plan


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
#         settings (Settings]): shared manager settings settings.
#         instructions (Instructions]): an instance with information to
#             create and create the essential components of a sourdough.Creator. Defaults to
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
#         return self.project.settings.get_parameters(
#             plan = technique.plan,
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
#                         {key: getattr(self.project.settings['general'], value)})
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
#         Settings (Settings]): shared manager settings settings.
#         instructions (Instructions]): an instance with information to
#             create and create the essential components of a sourdough.Creator. Defaults to
#             None.

#     """
#     name: str = None
#     Settings: sourdough.Settings] = None
#     instructions: Instructions] = None

#     """ Public Methods """

#     def create(self,
#             outer_plan: sourdough.base.plan,
#             data: Union[sourdough.Dataset, sourdough.base.plan]) -> sourdough.base.plan:
#         """Applies 'outer_plan' instance in 'manager' to 'data' or other stored outer_plan.

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
#             manuscript ('outer_plan'): outer_Plan instance with algorithms to create to 'data'.
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
# class Scholar(sourdough.Technique):
#     """Base class for createing technique instances to data.

#     Args:
#         name (str): designates the name of the class instance used
#             for internal referencing throughout sourdough. If the class instance
#             needs settings from the shared Settings instance, 'name' should
#             match the appropriate section name in that Settings instance. When
#             subclassing, it is a good settings to use the same 'name' attribute
#             as the base class for effective coordination between sourdough
#             classes. Defaults to None or __class__.__name__.lower().
#         Settings (Settings]): shared manager settings settings.
#         instructions (Instructions]): an instance with information to
#             create and create the essential components of a sourdough.Creator. Defaults to
#             None.

#     """
#     name: str = None
#     instructions: Instructions] = None
#     Settings: sourdough.Settings] = None

#     def __post_init__(self) -> None:
#         """Initializes class instance attributes."""
#         self = self.project.settings.create(instance = self)
#         return self

#     """ Private Methods """

#     def _create_inner_plan(self,
#             outer_plan: 'outer_plan',
#             data: Union['Dataset', 'outer_plan']) -> 'outer_plan':
#         """Applies 'inner_plan' in 'outer_plan' instance in 'manager' to 'data'.

#         Args:
#             outer_plan ('outer_plan'): instance with stored 'inner_plan' instances.
#             data ('Dataset'): primary instance used by 'manager'.

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
#         """Applies 'outer_plan' instance in 'manager' to 'data' or other stored outer_plan.

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