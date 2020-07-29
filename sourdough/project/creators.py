"""
creators: sourdough workflow stages for object creation
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
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union

import sourdough


@dataclasses.dataclass
class Author(sourdough.Action):
    """Constructs composite objects from user settings.
    
    Args:
        project (sourdough.Project): the related Project instance.
    
    """
    project: 'sourdough.Project' = None  
    
    """ Public Methods """
    
    def perform(self, 
            plan: 'sourdough.Hybrid', 
            parent: 'sourdough.Hybrid' = None) -> 'sourdough.Hybrid':
        """Drafts a plan with its 'contents' organized and instanced.
        
        Args:
            plan (sourdough.Hybrid): Hybrid instance to create and organize
                based on the information in 'contents' or 'settings'.

        Returns:
            sourdough.Hybrid: an instance with contents fully instanced.
                
        """
        attributes = {}
        # Finds and sets the 'structure' of 'plan'.
        plan.structure = self._get_structure(name = plan.name)
        # Iterates through appropriate settings to create 'contents' of 'plan'.
        for key, value in self.project.settings[plan.name].items():
            # Finds settings that have suffixes matching keys in the 
            # 'components' of 'project'.
            if any(key.endswith(f'{s}s') 
                    for s in self.project.options.keys()):
                suffix = key.split('_')[-1][:-1]
                # Iterates through listed items in 'value'.
                for item in sourdough.utilities.listify(value):
                    # Gets appropraite Component instance based on 'item'.
                    component = self._get_component(
                        plan = plan,
                        name = item,
                        key = suffix)
                    # Recursively calls the 'perform' method if the 'component' 
                    # created is a Hybrid type.
                    if isinstance(component, sourdough.Hybrid):
                        component = self.perform(plan = component)
                    plan.add(component)
            # Stores other settings in 'attributes'.        
            elif not key.endswith('_structure'):
                attributes[key] = value
        # Adds an extra settings as attributes to plan.
        for key, value in attributes.items():
            setattr(plan, key, value)
        return plan          

    """ Private Methods """
    
    def _get_structure(self, name: str) -> 'sourdough.structures.Design':
        """Returns Design class based upon 'settings' or default option.
        
        Args:
            name (str): name of Hybrid for which the structure is sought.
            
        Returns:
            sourdough.structures.Design: the appropriate Design based on
                'name' or the default option stored in 'project'.
        
        """ 
        try:
            structure = self.project.settings[name][f'{name}_structure']
        except KeyError:
            structure = self.project.structure
        return self._initialize_structure(structure = structure)  
      
    def _initialize_structure(self, 
            structure: Union[
                str, 
                'sourdough.structures.Structure']) -> (
                    'sourdough.structures.Structure'):
        """Returns a Structure instance based upon 'structure'.

        Args:
            structure (Union[str, sourdough.structures.Structure]): str matching
                a key in 'structures', a Structure subclass, or a Structure
                subclass instance.

        Returns:
            sourdough.structures.Structure: a Structure subclass instance.
            
        """
        if isinstance(structure, str):
            return self.project.structures[structure]()
        elif isinstance(structure, sourdough.Structure):
            return structure
        else:
            return structure()
        
    def _get_component(self, 
            plan: 'sourdough.Hybrid', 
            name: str,
            key: str) -> 'sourdough.Component':
        """[summary]
        """
        # Checks if special prebuilt instance exists.
        try:
            component = plan.select(name)
        except KeyError:
            component = self.project.select(name)
        # Otherwise uses the appropriate generic type.
        except KeyError:
            component = plan.structure.select(key)
        try:
            return component(name = name)
        except TypeError:
            return component
        
    def _initialize_component(self, 
            component: 'sourdough.Component', 
            **kwargs) -> 'sourdough.Component':
        """Returns a Component instance.
        
        If 'component' is already an instance, it is returned intact, Otherwise,
        it is instanced with kwargs.
        
        Args:
            component (sourdough.Component): a Component subclass or subclass
                instance.
            kwargs: arguments to use if 'component' is instanced.

        Returns:
            sourdough.Component: a Component instance.
            
        """


        
@dataclasses.dataclass
class Publisher(sourdough.Action):
    """Finalizes a composite object from user settings.
    
    Args:
        project (sourdough.Project): the related Project instance.
    
    """    
    project: 'sourdough.Project' = None  

    """ Public Methods """
 
    def perform(self, plan: 'sourdough.Hybrid') -> 'sourdough.Hybrid':
        """Finalizes a plan with 'parameters' added.
        
        Args:
            plan (sourdough.Hybrid): Hybrid instance to finalize the objects in
                its 'contents'.

        Returns:
            sourdough.Hybrid: an instance with its 'contents' finalized and
                ready for application.
                
        """
        plan.apply(tool = self._set_parameters)
        return plan

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
        """Acquires parameters from 'settings' of 'project'.

        Args:
            technique (technique): an instance for parameters to be added to.

        Returns:
            technique: instance with parameters added.

        """
        key = f'{technique.name}_parameters'
        try: 
            technique.parameters.update(self.project.settings[key])
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
                        {key: getattr(self.project.settings['general'], value)})
                except AttributeError:
                    raise AttributeError(' '.join(
                        ['no matching runtime parameter', key, 'found']))
        except (AttributeError, TypeError):
            pass
        return technique


@dataclasses.dataclass
class Reader(sourdough.Action):
    
    project: 'sourdough.Project' = None  
    
    def perform(self, plan: 'sourdough.Hybrid') -> 'sourdough.Hybrid':
        """[summary]

        Returns:
            [type] -- [description]
            
        """
        print('test plan reader', plan.overview)
        plan.apply(tool = self._add_data_dependent)
        if self.project.data is None:
            plan.perform()
        else:
            self.project.data = plan.perform(item = self.project.data)
        return plan

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
                        {key: getattr(self.project.data, value)})
                except KeyError:
                    print('no matching parameter found for', key, 'in data')
        except (AttributeError, TypeError):
            pass
        return technique
    