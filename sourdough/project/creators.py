"""
creators: sourdough workflow stages for object creation
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Author (Creator): creates a Project instance from passed arguments,
        including a Settings instance.
    Publisher (Creator): finalizes a Project instance based upon the initial
        construction by an Author instance and/or runtime user editing.
    Reader (Creator): executes a Project instance, storing changes and results
        in the Reader instance and/or passed data object.

"""
import dataclasses
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union

import sourdough


@dataclasses.dataclass
class Author(sourdough.Creator):
    """Constructs tree objects from user settings.
    
    Args:
        settings (sourdough.Settings): 
    
    """  
    settings: 'sourdough.Settings'
    
    """ Public Methods """
    
    def create(self, 
            Worker: 'sourdough.Worker') -> 'sourdough.Worker':
        """Drafts a Worker with its 'contents' organized and instanced.

        The method first determines if the contents are already finalized. If 
        not, it creates them from 'settings'.
        
        Subclasses can call this method and then arrange the 'contents' of
        'Worker' based upon a specific structural design.
        
        Args:
            Worker (sourdough.Worker): Worker instance to organize the 
                information in 'contents' or 'settings'.

        Returns:
            sourdough.Worker: an instance with contents fully instanced.
                
        """
        Worker = self._create_from_settings(Worker = Worker)
        Worker = self._initialize_Worker_contents(Worker = Worker)
        return Worker      

    """ Private Methods """

    def _draft_from_settings(self, 
            Worker: 'sourdough.Worker') -> 'sourdough.Worker':
        """Returns a single Worker instance created based on 'settings'.

        Args:
            Worker (sourdough.Worker): Worker instance to populate its 
                'contents' with information in 'settings'.

        Returns:
            sourdough.Worker: n Worker or subclass Worker with attributes 
                derived from a section of 'settings'.
                
        """
        Workers = []
        steps = []
        techniques = {}
        attributes = {}
        Worker.contents = []
        for key, value in Worker.settings[Worker.name].items():
            if key.endswith('_design'):
                Worker.design = value
            elif key.endswith('_Workers'):
                Workers = sourdough.utilities.listify(value)
            elif key.endswith('_steps'):
                steps = sourdough.utilities.listify(value)
            elif key.endswith('_techniques'):
                new_key = key.replace('_techniques', '')
                techniques[new_key] = sourdough.utilities.listify(value)
            else:
                attributes[key] = value
        if Workers:
            Worker = self._draft_Workers(
                Workers = Workers, 
                techniques = techniques,
                Worker = Worker)
        elif Workers:
            Worker = self._draft_Workers(
                Workers = Workers,
                project = Worker)
        for key, value in attributes.items():
            setattr(Worker, key, value)
        return Worker      
    
    def _initialize_Worker_contents(self, 
            Worker: 'sourdough.Worker') -> 'sourdough.Worker':
        """
        
        Args:
            Worker (sourdough.Worker): Worker instance with str, Step, or Worker
                stored in contents.

        Raises:
            TypeError: if an item in 'contents' is not a str, Step, or Worker
                type.

        Returns:
            sourdough.Worker: an instance with contents fully instanced.
                
        """
        new_contents = []
        for Task in Worker.contents:
            if isinstance(Task, str):
                new_contents.append(self._draft_unknown(
                    Task = Task, 
                    Worker = Worker))
            elif isinstance(Task, sourdough.Worker):
                self.create(Worker = Task)
            elif isinstance(Task, sourdough.Task):
                new_contents.append(Task)
            else:
                raise TypeError(
                    f'{Worker.name} contents must be str, Worker, or Step type')
        Worker.contents = new_contents
        return Worker
    
    def _draft_unknown(self,
            Task: str,
            Worker: 'sourdough.Worker') -> Union[
                'sourdough.Step', 
                'sourdough.Worker']:
        """[summary]

        Raises:
            KeyError: [description]

        Returns:
            [type]: [description]
        """
        try:
            test_instance = Worker.options[Task](name = 'test only')
        except KeyError:
            raise KeyError(f'{Task} not found in {Worker.name}')
        if isinstance(test_instance, sourdough.Step):
            return self._draft_Worker(
                Worker = Task, 
                technique = None, 
                Worker = Worker)
        else:
            return self._draft_Worker(Worker = Task, project = Worker)

    def _draft_Workers(self,
            Workers: Sequence[str],
            project: 'sourdough.Worker') -> 'sourdough.Worker':
        """[summary]

        Returns:
            [type]: [description]
            
        """
        new_Workers = []
        for Worker in Workers:
            new_Workers.append(self._draft_Worker(
                Worker = Worker, 
                project = project))
        project.contents.append(new_Workers)
        return project

    def _draft_Worker(self,
            Worker: str,
            project: 'sourdough.Worker') -> 'sourdough.Worker':
        """[summary]

        Returns:
            [type]: [description]
            
        """
        try:
            new_Worker = project.options[Worker](name = Worker)
        except KeyError:
            new_Worker = sourdough.Worker(name = Worker)
        return self.organize(Worker = new_Worker)
                  
    # def _draft_Workers(self, 
    #         Worker: 'sourdough.Worker',
    #         Workers: Sequence[str],
    #         techniques: Mapping[str, Sequence[str]]) -> 'sourdough.Worker':
    #     """[summary]

    #     Returns:
    #         [type]: [description]
    #     """
    #     new_Workers = []
    #     for Worker in Workers:
    #         new_techniques = []
    #         for technique in techniques[Worker]:
    #             new_techniques.append(self._draft_Worker(
    #                 Worker = Worker,
    #                 technique = technique,
    #                 Worker = Worker.name))
    #         new_Workers.append(new_techniques)
    #     Worker.contents.append(new_Workers)
    #     return Worker
            
    # def _draft_Worker(self,
    #         Worker: str,
    #         technique: str,
    #         Worker: str,
    #         options: 'sourdough.Catalog') -> 'sourdough.Step':
    #     """[summary]

    #     Returns:
    #         [type]: [description]
            
    #     """
    #     try:
    #         return Worker.options[Worker](
    #             name = Worker,
    #             Worker = Worker,
    #             technique = Worker.options[technique])
    #     except KeyError:
    #         try:
    #             return sourdough.Step(
    #                 name = Worker,
    #                 Worker = Worker,
    #                 technique = Worker.options[technique])
    #         except KeyError:
    #             try:
    #                 return Worker.options[Worker](
    #                     name = Worker,
    #                     Worker = Worker,
    #                     technique = sourdough.Technique(name = technique))
    #             except KeyError:
    #                 return sourdough.Step(
    #                     name = Worker,
    #                     Worker = Worker,
    #                     technique = sourdough.Technique(name = technique))


@dataclasses.dataclass
class Publisher(sourdough.Creator):
    
    settings: 'sourdough.Settings'

    """ Public Methods """
    
    def add(self, 
            manager: 'sourdough.Manager', 
            Worker: str, 
            Workers: Union[Sequence[str], str]) -> 'sourdough.Manager':
        """Adds 'Workers' to 'manager' 'contents' with a 'Worker' key.
        
        Args:
            manager (sourdough.Manager): manager to which 'Worker' and 'Workers'
                should be added.
            Worker (str): key to use to store 'Workers':
            Workers (Union[Sequence[str], str]): name(s) of Worker(s) to add to 
                'manager'.
            
        Returns:
            sourdough.Manager: with 'Workers' added at 'Worker'.
        
        """
        manager.contents[Worker] = sourdough.utilities.listify(Workers)
        return manager
 
    def create(self, Worker: 'sourdough.Worker') -> 'sourdough.Worker':
        """[summary]

        Returns:
            [type] -- [description]
            
        """
        Worker = self._parameterize_Workers(Worker = Worker)
        
        return Worker

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
            Worker = technique.Worker,
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
class Reader(sourdough.Creator):
    
    settings: 'sourdough.Settings'
    
    def create(self, Worker: 'sourdough.Worker') -> 'sourdough.Worker':
        """[summary]

        Returns:
            [type] -- [description]
            
        """
        Worker = self._parameterize_Workers(Worker = Worker)
        
        return Worker


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
#         return self.settings.get_parameters(
#             Worker = technique.Worker,
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
#             outer_Worker: sourdough.base.Worker,
#             data: Union[sourdough.Dataset, sourdough.base.Worker]) -> sourdough.base.Worker:
#         """Applies 'outer_Worker' instance in 'manager' to 'data' or other stored outer_Worker.

#         Args:
#             outer_Worker ('outer_Worker'): instance with stored technique instances (either
#                 stored in the 'techniques' or 'inner_Worker' attributes).
#             data ([Union['Dataset', 'outer_Worker']): a data source with information to
#                 finalize 'parameters' for each technique instance in 'outer_Worker'

#         Returns:
#             'outer_Worker': with 'parameters' for each technique instance finalized
#                 and connected to 'algorithm'.

#         """
#         if hasattr(outer_Worker, 'techniques'):
#             outer_Worker = self._finalize_techniques(manuscript = outer_Worker, data = data)
#         else:
#             outer_Worker = self._finalize_inner_Worker(outer_Worker = outer_Worker, data = data)
#         return outer_Worker

#     """ Private Methods """

#     def _finalize_inner_Worker(self, outer_Worker: 'outer_Worker', data: 'Dataset') -> 'outer_Worker':
#         """Finalizes 'inner_Worker' instances in 'outer_Worker'.

#         Args:
#             outer_Worker ('outer_Worker'): instance containing 'inner_Worker' with 'techniques' that
#                 have 'data_dependent' and/or 'conditional' 'parameters' to
#                 add.
#             data ('Dataset): instance with potential information to use to
#                 finalize 'parameters' for 'outer_Worker'.

#         Returns:
#             'outer_Worker': with any necessary modofications made.

#         """
#         new_inner_Worker = [
#             self._finalize_techniques(inner_Worker = inner_Worker, data = data)
#             for inner_Worker in outer_Worker.inner_Worker]

#         outer_Worker.inner_Worker = new_inner_Worker
#         return outer_Worker

#     def _finalize_techniques(self,
#             manuscript: Union['outer_Worker', 'inner_Worker'],
#             data: ['Dataset', 'outer_Worker']) -> Union['outer_Worker', 'inner_Worker']:
#         """Subclasses may provide their own methods to finalize 'techniques'.

#         Args:
#             manuscript (Union['outer_Worker', 'inner_Worker']): manuscript containing
#                 'techniques' to create.
#             data (['Dataset', 'outer_Worker']): instance with information used to
#                 finalize 'parameters' and/or 'algorithm'.

#         Returns:
#             Union['outer_Worker', 'inner_Worker']: with any necessary modofications made.

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
#             manuscript: 'outer_Worker',
#             technique: technique,
#             data: Union['Dataset', 'outer_Worker']) -> technique:
#         """Adds any conditional parameters to a technique instance.

#         Args:
#             manuscript ('outer_Worker'): outer_Worker instance with algorithms to create to 'data'.
#             technique (technique): instance with parameters which can take
#                 new conditional parameters.
#             data (Union['Dataset', 'outer_Worker']): a data source which might
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
#             data: Union['Dataset', 'outer_Worker']) -> technique:
#         """Completes parameter dictionary by adding data dependent parameters.

#         Args:
#             technique (technique): instance with information about data
#                 dependent parameters to add.
#             data (Union['Dataset', 'outer_Worker']): a data source which contains
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
#         self = self.settings.create(instance = self)
#         return self

#     """ Private Methods """

#     def _create_inner_Worker(self,
#             outer_Worker: 'outer_Worker',
#             data: Union['Dataset', 'outer_Worker']) -> 'outer_Worker':
#         """Applies 'inner_Worker' in 'outer_Worker' instance in 'manager' to 'data'.

#         Args:
#             outer_Worker ('outer_Worker'): instance with stored 'inner_Worker' instances.
#             data ('Dataset'): primary instance used by 'manager'.

#         Returns:
#             'outer_Worker': with modifications made and/or 'data' incorporated.

#         """
#         new_inner_Worker = []
#         for i, inner_Worker in enumerate(outer_Worker.inner_Worker):
#             if self.verbose:
#                 print('Applying', inner_Worker.name, str(i + 1), 'to', data.name)
#             new_inner_Worker.append(self._create_techniques(
#                 manuscript = inner_Worker,
#                 data = data))
#         outer_Worker.inner_Worker = new_inner_Worker
#         return outer_Worker

#     def _create_techniques(self,
#             manuscript: Union['outer_Worker', 'inner_Worker'],
#             data: Union['Dataset', 'outer_Worker']) -> Union['outer_Worker', 'inner_Worker']:
#         """Applies 'techniques' in 'manuscript' to 'data'.

#         Args:
#             manuscript (Union['outer_Worker', 'inner_Worker']): instance with stored
#                 'techniques'.
#             data ('Dataset'): primary instance used by 'manuscript'.

#         Returns:
#             Union['outer_Worker', 'inner_Worker']: with modifications made and/or 'data'
#                 incorporated.

#         """
#         for technique in manuscript.techniques:
#             if self.verbose:
#                 print('Applying', technique.name, 'to', data.name)
#             if isinstance(data, Dataset):
#                 data = technique.create(data = data)
#             else:
#                 for inner_Worker in data.inner_Worker:
#                     manuscript.inner_Worker.append(technique.create(data = inner_Worker))
#         if isinstance(data, Dataset):
#             setattr(manuscript, 'data', data)
#         return manuscript

#     """ Core sourdough Methods """

#     def create(self, outer_Worker: 'outer_Worker', data: Union['Dataset', 'outer_Worker']) -> 'outer_Worker':
#         """Applies 'outer_Worker' instance in 'manager' to 'data' or other stored outer_Worker.

#         Args:
#             outer_Worker ('outer_Worker'): instance with stored technique instances (either
#                 stored in the 'techniques' or 'inner_Worker' attributes).
#             data ([Union['Dataset', 'outer_Worker']): a data source with information to
#                 finalize 'parameters' for each technique instance in 'outer_Worker'

#         Returns:
#             'outer_Worker': with 'parameters' for each technique instance finalized
#                 and connected to 'algorithm'.

#         """
#         if hasattr(outer_Worker, 'techniques'):
#             outer_Worker = self._create_techniques(manuscript = outer_Worker, data = data)
#         else:
#             outer_Worker = self._create_inner_Worker(outer_Worker = outer_Worker, data = data)
#         return outer_Worker