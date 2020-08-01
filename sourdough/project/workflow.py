"""
workflow: sourdough workflow for manager creation and iteration
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Author (Action): creates a Hybrid instance from passed arguments and/or a 
        Settings instance.
    Publisher (Action): finalizes a Hybrid instance based upon the initial
        construction by an Author instance and/or runtime user editing.
    Reader (Action): executes a Hybrid instance, storing changes and results
        in the Reader instance and/or passed data object.

"""

import dataclasses
import inspect
from typing import Any, ClassVar, Iterable, Mapping, Sequence, Tuple, Union

import sourdough


@dataclasses.dataclass
class Author(sourdough.Action):
    """Constructs composite objects from user settings.
    
    Args:
        manager (sourdough.Manager): the related Manager instance.
    
    """
    manager: 'sourdough.Manager' = None  
    
    """ Public Methods """
    
    def perform(self, worker: 'sourdough.Hybrid') -> 'sourdough.Hybrid':
        """Drafts a worker with its 'contents' organized and instanced.
        
        Args:
            worker (sourdough.Hybrid): Hybrid instance to create and organize
                based on the information in 'contents' or 'settings'.

        Returns:
            sourdough.Hybrid: an instance with contents fully instanced.
                
        """
        attributes = {}
        # Finds and sets the 'structure' of 'worker'.
        worker = self._add_structure(worker = worker)
        # Divides settings into different subsections.
        component_settings, attributes = self._divide_settings(
            settings = self.manager.settings[worker.name],
            structure = worker.structure) 
        # Organizes 'contents' of 'worker' according to its 'structure'.
        worker.structure.organize(settings = component_settings)
        # Adds an extra settings as attributes to worker.
        for key, value in attributes.items():
            setattr(worker, key, value)
        return worker          

    """ Private Methods """

    def _add_structure(self, worker: 'sourdough.Worker') -> 'sourdough.Worker':
        """Returns Structure class based upon 'settings' or default option.
        
        Args:
            name (str): name of Hybrid for which the structure is sought.
            
        Returns:
            sourdough.Structure: the appropriate Structure based on
                'name' or the default option stored in 'manager'.
        
        """ 
        key = f'{worker.name}_structure'
        try:    
            worker.structure = self.manager.settings[worker.name][key]
        except KeyError:
            pass
        return sourdough.Structure.validate(hybrid = worker)

    def _divide_settings(self,
            settings: Mapping[str, Any],
            structure: 'sourdough.Structure') -> Tuple[
                Mapping[str, Any],
                Mapping[str, Any]]:
        """

        Args:


        Returns:
            Tuple
        
        """
        component_settings = {}
        attributes = {}
        for key, value in settings.items():
            # Stores settings related to available Component 'options' according
            # to 'structure'.
            if any(key.endswith(f'_{s}s') for s in structure.options.keys()):
                component_settings[key] = sourdough.utilities.listify(value)
            # Stores other settings in 'attributes'.        
            elif not key.endswith('_structure'):
                attributes[key] = value
        return component_settings, attributes
                
        
@dataclasses.dataclass
class Publisher(sourdough.Action):
    """Finalizes a composite object from user settings.
    
    Args:
        manager (sourdough.Manager): the related Manager instance.
    
    """    
    manager: 'sourdough.Manager' = None  

    """ Public Methods """
 
    def perform(self, worker: 'sourdough.Hybrid') -> 'sourdough.Hybrid':
        """Finalizes a worker with 'parameters' added.
        
        Args:
            worker (sourdough.Hybrid): Hybrid instance to finalize the objects in
                its 'contents'.

        Returns:
            sourdough.Hybrid: an instance with its 'contents' finalized and
                ready for application.
                
        """
        worker.apply(tool = self._set_parameters)
        return worker

    """ Private Methods """

    def _set_parameters(self, 
            component: 'sourdough.Component') -> 'sourdough.Component':
        """
        
        """
        if isinstance(component, sourdough.Technique):
            return self._set_technique_parameters(technique = component)
        elif isinstance(component, sourdough.Task):
            return self._set_task_parameters(task = component)
        else:
            return component
    
    def _set_technique_parameters(self, 
            technique: 'sourdough.Technique') -> 'sourdough.Technique':
        """
        
        """
        if technique.name not in ['none', None, 'None']:
            parameter_types = ['settings', 'selected', 'required', 'runtime']
            # Iterates through types of 'parameter_types'.
            for parameter_type in parameter_types:
                technique = getattr(self, f'_get_{parameter_type}')(
                    technique = technique)
        return technique
    
    def _set_task_parameters(self, task: 'sourdough.Task') -> 'sourdough.Task':
        """
        
        """
        if task.technique.name not in ['none', None, 'None']:
            task = self._get_settings(technique = task)
            try:
                task._set_conditional_parameters()
            except AttributeError:
                pass
            task.technique = self._set_technique_parameters(
                technique = task.technique)
        return task  
            
    def _get_settings(self,
            technique: Union[
                'sourdough.Technique', 
                'sourdough.Task']) -> Union[
                    'sourdough.Technique', 
                    'sourdough.Task']:
        """Acquires parameters from 'settings' of 'manager'.

        Args:
            technique (technique): an instance for parameters to be added to.

        Returns:
            technique: instance with parameters added.

        """
        key = f'{technique.name}_parameters'
        try: 
            technique.parameters.update(self.manager.settings[key])
        except KeyError:
            pass
        return technique

    def _get_selected(self,
            technique: 'sourdough.Technique') -> 'sourdough.Technique':
        """Limits parameters to those appropriate to the technique.

        Args:
            technique (technique): an instance for parameters to be selected.

        Returns:
            technique: instance with parameters selected.

        """
        if technique.selected:
            new_parameters = {}
            for key, value in technique.parameters.items():
                if key in technique.selected:
                    new_parameters[key] = value
            technique.parameters = new_parameters
        return technique

    def _get_required(self,
            technique: 'sourdough.Technique') -> 'sourdough.Technique':
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

    def _get_runtime(self,
            technique: 'sourdough.Technique') -> 'sourdough.Technique':
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
                        {key: getattr(self.manager.settings['general'], value)})
                except AttributeError:
                    raise AttributeError(' '.join(
                        ['no matching runtime parameter', key, 'found']))
        except (AttributeError, TypeError):
            pass
        return technique


@dataclasses.dataclass
class Reader(sourdough.Action):
    
    manager: 'sourdough.Manager' = None  
    
    def perform(self, worker: 'sourdough.Hybrid') -> 'sourdough.Hybrid':
        """[summary]

        Returns:
            [type] -- [description]
            
        """
        # worker.apply(tool = self._add_data_dependent)
        # if self.manager.data is None:
        #     worker.perform()
        # else:
        #     self.manager.data = worker.perform(item = self.manager.data)
        return worker

    """ Private Methods """
        
    def _get_data_dependent(self,
            component: 'sourdough.Component') -> 'sourdough.Component':
        """Gets parameters that are derived from data.

        Args:
            technique (technique): an instance for parameters to be added to.

        Returns:
            technique: instance with parameters added.

        """
        if isinstance(component, sourdough.Task):
            component.technique = self._add_data_dependent(
                technique = component.technique)
        elif isinstance(component, sourdough.Technique):
            component = self._add_data_dependent(technique = component)
        return component

    def _add_data_dependent(self,
            technique: 'sourdough.Technique') -> 'sourdough.Technique':
        """Adds parameters that are derived from data.

        Args:
            technique (technique): an instance for parameters to be added to.

        Returns:
            technique: instance with parameters added.

        """
        try:
            for key, value in technique.data_dependent.items():
                try:
                    technique.parameters.update(
                        {key: getattr(self.manager.data, value)})
                except KeyError:
                    print('no matching parameter found for', key, 'in data')
        except (AttributeError, TypeError):
            pass
        return technique
    