"""
creators: sourdough workflow stages for object creation
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Author (Creator): creates a Hybrid instance from passed arguments and/or a 
        Settings instance.
    Publisher (Creator): finalizes a Hybrid instance based upon the initial
        construction by an Author instance and/or runtime user editing.
    Reader (Creator): executes a Hybrid instance, storing changes and results
        in the Reader instance and/or passed data object.

"""
import dataclasses
import inspect
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union

import sourdough


@dataclasses.dataclass
class Author(sourdough.Creator):
    """Constructs composite objects from user settings.
    
    Args:
        project (sourdough.Project): the related Project instance.
    
    """
    project: 'sourdough.Project' = None  
    
    """ Public Methods """
    
    def create(self, plan: 'sourdough.Hybrid') -> 'sourdough.Hybrid':
        """Drafts a plan with its 'contents' organized and instanced.
        
        Args:
            plan (sourdough.Hybrid): Hybrid instance to organize the 
                information in 'contents' or 'settings'.

        Returns:
            sourdough.Hybrid: an instance with contents fully instanced.
                
        """
        attributes = {}
        # Finds and sets the 'structure' of 'plan'.
        plan.structure = self._get_structure(name = plan.name)
        # Iterates through appropriate settings to create 'contents' of 'plan'.
        for key, value in self.project.settings[plan.name].items():
            # Finds settings that have suffixes matching keys in the 
            # 'components' of 'structure' of 'plan'.
            if any(key.endswith(s) for s in plan.structure.components.keys()):
                for item in sourdough.utilities.listify(value):
                    # Checks if special prebuilt instance exists.
                    try:
                        component = self.project.options[item]
                    # Otherwise uses the appropriate generic type.
                    except KeyError:
                        print('test key', key)
                        suffix = key.split('_')[-1]
                        name = plan.structure.components[suffix]
                        component = plan.structure.load(key = name)(name = item)
                    component = self._instance_component(component = component)
                    # Recursively calls the 'create' method if the 'component' 
                    # created is a Hybrid type.
                    if isinstance(component, sourdough.Hybrid):
                        component = self.create(plan = component)
                    plan.add(component)
            # Stores other settings in 'attributes'.        
            elif not key.endswith('_structure'):
                attributes[key] = value
        # Adds an extra settings as attributes to plan.
        for key, value in attributes.items():
            setattr(plan, key, value)
        return plan          

    """ Private Methods """
    
    def _get_structure(self, name: str) -> 'sourdough.structures.Structure':
        """
        
        """ 
        try:
            design = self.project.settings[name][f'{name}_structure']
        except KeyError:
            design = self.project.structure
        return self.project._initialize_structure(structure = design)    
    
    def _instance_component(self, 
            component: 'sourdough.Component') -> 'sourdough.Component':
        """[summary]

        Returns:
            [type]: [description]
        """
        try:
            return component()
        except TypeError:
            return component

        
@dataclasses.dataclass
class Publisher(sourdough.Creator):
    """Finalizes a composite object from user settings.
    
    Args:
        project (sourdough.Project): the related Project instance.
    
    """    
    project: 'sourdough.Project' = None  

    """ Public Methods """
 
    def create(self, plan: 'sourdough.Hybrid') -> 'sourdough.Hybrid':
        """[summary]

        Returns:
            [type] -- [description]
            
        """
        plan.apply(tool = self._set_parameters)
        return plan

    """ Private Methods """

    def _set_parameters(self, 
            component: 'sourdough.Component') -> 'sourdough.Component':
        """
        
        """
        thing = component.structure.load('technique')
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
class Reader(sourdough.Creator):
    
    project: 'sourdough.Project' = None  
    
    def create(self, plan: 'sourdough.Hybrid') -> 'sourdough.Hybrid':
        """[summary]

        Returns:
            [type] -- [description]
            
        """
        plan.apply(tool = self._add_data_dependent)
        if self.project.data is None:
            plan.perform()
        else:
            self.project.data = plan.perform(data = self.project.data)
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
    