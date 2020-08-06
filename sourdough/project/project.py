"""
manager: interface for sourdough project construction and iteration
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Project (Hybrid): interface for sourdough projects.

"""

import collections.abc
import dataclasses
import inspect
import pathlib
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union
import warnings

import sourdough

 
@dataclasses.dataclass
class Project(sourdough.Element, collections.abc.Iterable):
    """Constructs, organizes, and implements a sourdough project.
    
    A Project inherits all of the differences between a Worker and a Hybrid.

    A Project differs from a Worker in 5 significant ways:
        1) The Manager is the public interface to composite object construction 
            and application. It may store the composite object instance(s) as 
            well as any required classes (such as those stored in the 'data' 
            attribute). This includes Settings and Filer, stored in the 
            'settings' and 'filer' attributes, respectively.
        2) Manager stores Component subclass instances in 'contents'. Those 
            instances are used to assemble and apply the parts of Hybrid 
            instances.
        3) Manager includes an 'automatic' attribute which can be set to perform
            all of its methods if all of the necessary arguments are passed.
        4) It has an OptionsMixin, which contains a Catalog instance storing
            default Component instances in 'options'.
        5)
        
    Args:
        contents (Sequence[Union[sourdough.Component, str]]]): list of 
            Component subclass instances or strings which correspond to keys in 
            'options'. Defaults to 'default', which will use the 'defaults' 
            attribute of 'options' to select Component instances.
        name (str): roleates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Component is called, 'name' is set based upon
            the '_get_name' method in Component. If that method is not 
            overridden by a subclass instance, 'name' will be assigned to the 
            snake case version of the class name ('__class__.__name__').
        settings (Union[sourdough.Settings, str, pathlib.Path]]): 
            an instance of Settings or a str or pathlib.Path containing the 
            file path where a file of a supported file type with settings for a 
            Settings instance is located. Defaults to None.
        filer (Union[sourdough.Filer, str, pathlib.Path]]): an instance of 
            Filer or a str or pathlib.Path containing the full path of where the 
            root folder should be located for file input and output. A Filer
            instance contains all file path and import/export methods for use 
            throughout sourdough. Defaults to None.
        role (str): type of role for the project's composite object.
            Defaults to 'tree'.
        identification (str): a unique identification name for a 
            Project instance. The name is used for creating file folders
            related to the 'Project'. If not provided, a string is created from
            'name' and the date and time. This is a notable difference
            between an ordinary Worker instancce and a Project instance. Other
            Workers are not given unique identification. Defaults to None.   
        automatic (bool): whether to automatically advance 'contents' (True) or 
            whether the contents must be changed manually by using the 'advance' 
            or '__iter__' methods (False). Defaults to True.
        roles (ClassVar[sourdough.Catalog]): a class attribute storing
            composite role options.            
        options (ClassVar[sourdough.Catalog]): a class attribute storing
            elements of a composite role.
    
    Attributes:
        manager (sourdough.Worker): the iterable composite object created by
            Project.
        index (int): the current index of the iterator in the instance. It is
            set to -1 in the '__post_init__' method.
        stage (str): name of the last stage that has been implemented. It is set
            to 'initialize' in the '__post_init__' method.
        previous_stage (str): name of the previous stage to the last stage that
            has been implemented. It is set by the 'advance' method.
            
    """
    settings: Union['sourdough.Settings', str, pathlib.Path] = None
    filer: Union['sourdough.Filer', str, pathlib.Path] = None
    manager: 'sourdough.Manager' = sourdough.Manager
    workflow: Union[
        'sourdough.Workflow',
        Sequence['sourdough.Workflow'],
        Sequence[str]] = sourdough.Workflow
    role: 'sourdough.Role' = sourdough.Role
    component: 'sourdough.Component' = sourdough.Component
    name: str = None
    identification: str = None
    automatic: bool = True
    data: object = None
    structures: ClassVar[Mapping[str, sourdough.Component]] = {
        'worker': sourdough.Worker, 
        'task': sourdough.Task, 
        'technique': sourdough.Technique}

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent initialization method(s).
        super().__post_init__()
        # Removes various python warnings from console output.
        warnings.filterwarnings('ignore')
        # Sets unique project 'identification', if not passed.
        self.identification = self.identification or self._set_identification()
        # Validates various attributes or converts them to the proper type.
        attributes = [
            'settings', 
            'filer', 
            'workflow', 
            'role', 
            'manager', 
            'component']
        for attribute in attributes :
            getattr(self, f'_validate_{attribute}')()
        # Adds 'general' section attributes from 'settings'.
        self.settings.inject(instance = self)
        # Advances through 'contents' if 'automatic' is True.
        if self.automatic:
            self.manager = self._auto_contents(manager = self.manager)

    """ Dunder Methods """
    
    def __iter__(self) -> Iterable:
        return iter(self.workflow)

    """ Private Methods """

    def _set_identification(self) -> None:
        """Sets unique 'identification' str based upon date and time."""
        return sourdough.utilities.datetime_string(prefix = self.name)
    
    def _validate_settings(self) -> None:
        """Validates 'settings' or converts it to a Settings instance."""
        if not isinstance(self.settings, sourdough.Settings):
            self.settings = sourdough.Settings(contents = self.settings)
        return self

    def _validate_filer(self) -> None:
        """Validates 'filer' or converts it to a Filer instance."""
        if not isinstance(self.filer, sourdough.Filer):
            self.filer = sourdough.Filer(
                root_folder = self.filer, 
                settings = self.settings)
        return self

    def _validate_workflow(self) -> None:
        """Validates 'workflow' or converts it to a list of Workflow subclasses.
        """
        if (inspect.isclass(self.workflow) 
                and (issubclass(self.workflow, sourdough.Workflow)
                     or self.workflow == sourdough.Workflow)):
            workflow = self.workflow.registry['default']
            new_workflow = []
            for item in workflow:
                new_workflow.append(item(project = self))
            self.workflow = new_workflow
        elif (isinstance(self.workflow, Sequence) 
                and all(isinstance(w, str) for w in self.workflow)):
            new_workflow = []
            for item in self.workflow:
                new_workflow.append(
                    sourdough.Workflow.build(item, project = self))
        elif not (isinstance(self.workflow, Sequence) 
                and all(isinstance(w, sourdough.Workflow) 
                    for w in self.workflow)):
            raise TypeError('workflow must be Workflow or its subclass')

    def _validate_role(self) -> None:
        """Validates 'role' as Role or its subclass."""
        if not (inspect.isclass(self.role) 
                and (issubclass(self.role, sourdough.Role)
                     or self.Role == sourdough.Role)):
            raise TypeError('role must be Role or its subclass')

    def _validate_manager(self) -> None:
        """Initializes a Manager instance for the 'manager' attribute."""
        if (inspect.isclass(self.manager) 
                and (issubclass(self.manager, sourdough.Manager)
                     or self.manager == sourdough.Manager)):
            self.manager = self.manager(
                name = self.name,
                identification = self.identification)
        elif not isinstance(self.manager, sourdough.Manager):
            raise TypeError('manager must be a Manager type')
        return self

    def _validate_component(self) -> None:
        """Validates 'component' as Component or its subclass."""
        if not (inspect.isclass(self.component) 
                and (issubclass(self.component, sourdough.Component)
                     or self.Role == sourdough.Component)):
            raise TypeError('component must be Component or its subclass')
                     
    def _auto_contents(self, 
            manager: 'sourdough.Manager') -> 'sourdough.Manager':
        """Advances through the stored Workflow instances.

        Args:
            manager (sourdough.Manager): an instance containing a composite
                object.
                
        Returns:
            sourdough.Manager: a composite object accessed and possibly modified
                by the stored Workflow instances.
            
        """
        for stage in self:
            if hasattr(self, 'verbose') and self.verbose:
                print(f'Beginning {stage.name} process')
            manager = stage.create(worker = manager)
            print('test manager', manager.contents)
            # print('test stage overview', manager.overview)
        return manager
    