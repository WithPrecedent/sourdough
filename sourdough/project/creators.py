"""
Creators: interim classes for sourdough Directors
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:

"""
from __future__ import annotations
import copy
import dataclasses
import itertools
import pprint
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Union)

import sourdough


@dataclasses.dataclass
class Instructions(sourdough.types.Progression):
    """Information to construct a sourdough Component.
    
    Args:
        contents (Sequence[str]): stored list of str. Included items should 
            correspond to keys in an Outline and/or Component subclasses. 
            Defaults to an empty list.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. 
        base (str): name of base class associated with the Component to be 
            created.
        design (str): name of design base class associated with the Component
            to be created.
        parameters (Mapping[str, Any]): parameters to be used for the stored
            object(s) in its/their creation.
        attributes (Mapping[str, Any]): attributes to add to the created
            Component object. The keys should be name of the attribute and the
            values should be the value stored for that attribute.
            
    """
    contents: Sequence[str] = dataclasses.field(default_factory = list)
    name: str = None
    base: str = None
    design: str = None
    parameters: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    attributes: Mapping[str, Any] = dataclasses.field(default_factory = dict)

    """ Dunder Methods """

    def __str__(self) -> str:
        """Returns pretty string representation of a class instance.
        
        Returns:
            str: normal representation of a class instance.
        
        """
        return pprint.pformat(self, sort_dicts = False, compact = True)


@dataclasses.dataclass
class Architect(sourdough.Creator):
    """Creates a blueprint of a workflow.

    Architect creates a dictionary representation, a blueprint, of the overall 
    project workflow. In the blueprint produced, keys are the names of 
    components and values are Instruction instances.
    
    Args:
                        
    """
    action: ClassVar[str] = 'Drafting'
    needs: ClassVar[Union[str, Tuple[str]]] = 'settings'
    produces: ClassVar[str] = 'blueprint'

    """ Public Methods """
    
    def create(self, project: sourdough.Project) -> sourdough.types.Lexicon:
        """Creates a blueprint based on 'project.settings'.

        Args:
            project (sourdough.Project): a Project instance with resources and
                other information needed for blueprint construction.

        Returns:
            Project: with modifications made to its 'design' attribute.
            
        """ 
        blueprint = sourdough.types.Lexicon()
        suffixes = project.resources.components.keys()
        suffixes = tuple(item + 's' for item in suffixes)
        for name, section in project.settings.items():
            # Tests whether the section in 'project.settings' is related to the 
            # construction of a project object by examining the key names to see
            # if any end in a suffix corresponding to a known base type. If so, 
            # that section is harvested for information which is added to 
            # 'blueprint'.
            if any([i.endswith(suffixes) for i in section.keys()]):
                blueprint = self._process_section(
                    name = name,
                    blueprint = blueprint,
                    project = project,
                    suffixes = suffixes,
                    base = 'workflow')
        return blueprint
        
    """ Private Methods """
    
    def _process_section(self, name: str, blueprint: sourdough.types.Lexicon,
                         project: sourdough.Project, suffixes: Tuple[str],
                         base: str) -> sourdough.types.Lexicon:
        """[summary]

        Args:
            name (str): [description]
            blueprint (sourdough.types.Lexicon): [description]
            project (sourdough.Project): [description]

        Returns:
            sourdough.types.Lexicon: [description]
            
        """
        # Iterates through each key, value pair in section and stores or 
        # extracts the information as appropriate.
        for key, value in project.settings[name].items():
            # keys ending with specific suffixes trigger further parsing and 
            # searching throughout 'project.settings'.
            if key.endswith(suffixes):
                # Each key contains a prefix which is the parent Component name 
                # and a suffix which is what that parent Component contains.
                key_name, key_suffix = self._divide_key(key = key)
                contains = key_suffix.rstrip('s')
                contents = sourdough.tools.listify(value) 
                blueprint = self._add_instructions(
                    name = key_name, 
                    blueprint = blueprint,
                    contents = contents,
                    base = base)
                for item in contents:
                    if item in project.settings:
                        blueprint = self._process_section(
                            name = item,
                            blueprint = blueprint,
                            project = project,
                            suffixes = suffixes,
                            base = contains)
                    else:
                        blueprint = self._add_instructions(
                            name = item, 
                            blueprint = blueprint,
                            base = contains)
            # keys ending with 'design' hold values of a Component's design.
            elif key.endswith('design'):
                blueprint = self._add_instructions(
                    name = name, 
                    blueprint = blueprint, 
                    design = value)
            # All other keys are presumed to be attributes to be added to a
            # Component instance.
            else:
                blueprint = self._add_instructions(
                    name = name,
                    blueprint = blueprint,
                    attributes = {key: value})
        return blueprint

    @staticmethod
    def _divide_key(key: str) -> Sequence[str, str]:
        """[summary]

        Args:
            key (str): [description]

        Returns:
            
            Sequence[str, str]: [description]
            
        """
        suffix = key.split('_')[-1][:-1]
        prefix = key[:-len(suffix) - 2]
        return prefix, suffix
    
    @staticmethod    
    def _add_instructions(name: str, blueprint: sourdough.types.Lexicon, 
                     **kwargs) -> sourdough.types.Lexicon:
        """[summary]

        Args:
            name (str): [description]
            blueprint (sourdough.types.Lexicon): [description]

        Returns:
            sourdough.types.Lexicon: [description]
            
        """
        # Stores a mostly empty Instructions instance in 'blueprint' if none 
        # currently exists corresponding to 'name'. This check is performed to 
        # prevent overwriting of existing information in 'blueprint' during 
        # recursive calls.
        if name not in blueprint:
            blueprint[name] = Instructions(name = name)
        # Adds any kwargs to 'blueprint' as appropriate.
        for key, value in kwargs.items():
            if isinstance(getattr(blueprint[name], key), str):
                pass
            elif isinstance(getattr(blueprint[name], key), dict):
                getattr(blueprint[name], key).update(value) 
            else:
                setattr(blueprint[name], key, value)           
        return blueprint

    """ Dunder Methods """
    
    def __str__(self) -> str:
        return pprint.pformat(self, sort_dicts = False, compact = True)


@dataclasses.dataclass
class Builder(sourdough.Creator):
    """Constructs finalized workflow.
    
    Args:
                        
    """
    action: ClassVar[str] = 'Creating'
    needs: ClassVar[Union[str, Tuple[str]]] = 'blueprint'
    produces: ClassVar[str] = 'workflow'

    """ Public Methods """

    def create(self, project: sourdough.Project) -> sourdough.Component:
        """Drafts a Workflow instance based on 'blueprint' in 'project'.
            
        """ 
        return self._create_component(name = project.name, project = project)
    
    """ Private Methods """

    def _create_component(self, name: str, 
                          project: sourdough.Project) -> sourdough.Component:
        """[summary]

        Args:
            name (str): [description]
            project (sourdough.Project): [description]

        Returns:
            sourdough.Component: [description]
            
        """
        component = self._get_component(name = name, project = project)
        return self._finalize_component(component = component, project = project)

    def _get_component(self, name: str,
                       project: sourdough.Project) -> sourdough.Component:
        """[summary]

        Args:
            name (str): [description]
            components (Mapping[str, sourdough.Component]): [description]
            project (sourdough.Project): [description]

        Raises:
            KeyError: [description]

        Returns:
            Mapping[str, sourdough.Component]: [description]
            
        """
        instructions = project['blueprint'][name]
        kwargs = {'name': name, 'contents': instructions.contents}
        try:
            component = copy.deepcopy(project.resources.instances[name])
            for key, value in kwargs.items():
                if value:
                    setattr(component, key, value)
        except KeyError:
            try:
                component = project.resources.components[name]
                component = component(**kwargs)
            except KeyError:
                try:
                    component = project.resources.components[instructions.design]
                    component = component(**kwargs)
                except KeyError:
                    try:
                        component = project.resources.components[instructions.base]
                        component = component(**kwargs)
                    except KeyError:
                        raise KeyError(f'{name} component does not exist')
        return component

    def _finalize_component(self, component: sourdough.Component,
                            project: sourdough.Project) -> sourdough.Component:
        """[summary]

        Args:
            component (sourdough.Component): [description]
            project (sourdough.Project): [description]

        Returns:
            sourdough.Component: [description]
            
        """
        if isinstance(component, Iterable):
            if component.branches:
                component = self._create_parallel(
                    component = component, 
                    project = project)
            else:
                component = self._create_serial(
                    component = component, 
                    project = project)
        else:
            pass
        return component

    def _create_parallel(self, component: sourdough.Component,
                         project: sourdough.Project) -> sourdough.Workflow:
        """[summary]

        Args:
            component (sourdough.Component): [description]
            components (Mapping[str, sourdough.Component]): [description]
            project (sourdough.Project): [description]

        Returns:
            sourdough.WorkFlow: [description]
            
        """
        possible = []
        for item in component.contents:
            possible.append(project['blueprint'][item].contents)
        combos = list(map(list, itertools.product(*possible)))
        wrappers = [self._get_component(i, project) for i in component.contents]
        new_contents = []
        for combo in combos:
            combo = [self._get_component(i, project) for i in combo]
            steps = []
            for i, step in enumerate(wrappers):
                step.contents = combo[i]
                steps.append(step)
            new_contents.append(steps)
        component.contents = new_contents
        component = self._add_attributes(
            component = component, 
            project = project)
        return component

    def _create_serial(self, component: sourdough.Component, 
                       project: sourdough.Project) -> sourdough.Workflow:
        """[summary]

        Args:
            component (sourdough.Component): [description]
            components (Mapping[str, sourdough.Component]): [description]
            project (sourdough.Project): [description]

        Returns:
            sourdough.Workflow: [description]
            
        """
        new_contents = []
        for item in component.contents:
            instance = self._get_component(
                name = item, 
                project = project)
            instance = self._finalize_component(
                component = instance, 
                project = project)
            new_contents.append(instance)
        component.contents = new_contents
        return component

    def _add_attributes(self, component: sourdough.Component,
                        project: sourdough.Project) -> sourdough.Component:
        """[summary]

        Returns:
            [type]: [description]
            
        """
        attributes = project['blueprint'][component.name].attributes
        for key, value in attributes.items():
            setattr(component, key, value)
        return component    


@dataclasses.dataclass
class Worker(sourdough.Creator):
    """Applies a project Workflow and produces results.

    Args:

    """
    action: ClassVar[str] = 'Computing'
    needs: ClassVar[Union[str, Tuple[str]]] = 'workflow'
    produces: ClassVar[str] = 'results'
    
    """ Public Methods """
 
    def create(self, project: sourdough.Project, 
               **kwargs) -> sourdough.types.Lexicon:        
        """Computes results based on a workflow.
            
        """
        results = sourdough.types.Lexicon()
        if project.data is not None:
            kwargs['data'] = project.data
        for component in project['workflow']:
            results.update({component.name: component.apply(**kwargs)})
        return results
