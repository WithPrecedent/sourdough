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
        
    Args:
        settings (Union[sourdough.Settings, str, pathlib.Path]]): 
            an instance of Settings or a str or pathlib.Path containing the 
            file path where a file of a supported file type with settings for a 
            Settings instance is located. Defaults to None.
        filer (Union[sourdough.Filer, str, pathlib.Path]]): an instance of 
            Filer or a str or pathlib.Path containing the full path of where the 
            root folder should be located for file input and output. A Filer
            instance contains all file path and import/export methods for use 
            throughout sourdough. Defaults to None.
        workflow (Union[sourdough.Workflow, Sequence[Union[sourdough.Workflow, 
            str]]]): base Workflow class, a list of Workflow subclasses, or 
            a list of str corresponding to Workflow subclasses in 
            Workflow.registry. These classes are used for the construction and
            application of a sourdough project. Defaults to sourdough.Workflow
            which will use the default subclasses of Draft, Publish, Apply.
        components (sourdough.Component): base class for the pieces of the 
            project's composite object. Defaults to sourdough.Component.
            Component.registry will automatically contain all imported 
            subclasses and those will be the only permitted pieces of a 
            sourdough composite object. One imported component must be Manager
            or a subclass.
        name (str): designates the name of a class instance that is used for 
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
        identification (str): a unique identification name for a 
            Project instance. The name is used for creating file folders
            related to the 'Project'. If not provided, a string is created from
            'name' and the date and time. This is a notable difference
            between an ordinary Worker instancce and a Project instance. Other
            Workers are not given unique identification. Defaults to None.   
        automatic (bool): whether to automatically advance 'contents' (True) or 
            whether the contents must be changed manually by using the 'advance' 
            or '__iter__' methods (False). Defaults to True.
        data (object): any data object for the project to be applied.         

    
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
    workflow: Union[
        'sourdough.Workflow',
        Sequence[Union['sourdough.Workflow', str]]] = sourdough.Workflow
    components: 'sourdough.Component' = sourdough.Component
    name: str = None
    identification: str = None
    automatic: bool = True
    data: object = None

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
        attributes = ['settings', 'filer', 'workflow', 'roles', 'components']
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
        return self

    def _validate_roles(self) -> None:
        """Validates 'role' as Role or its subclass."""
        if not (inspect.isclass(self.roles) 
                and (issubclass(self.roles, sourdough.Role)
                     or self.roles == sourdough.Role)):
            raise TypeError('roles must be Role or its subclass')
        return self

    def _validate_components(self) -> None:
        """Validates 'component' as Component or its subclass."""
        if not (inspect.isclass(self.components) 
                and (issubclass(self.components, sourdough.Component)
                     or self.components == sourdough.Component)):
            raise TypeError('components must be Component or its subclass')
        else:
            self.manager = self._get_manager()
        return self
  
    def _get_manager(self) -> None:
        """Returns a Manager instance from 'component' attribute."""
        managers = self.components._get_values_by_type(sourdough.Manager)
        if len(managers) == 0:
            raise ValueError(
                'There must a Manager or Manager subclass imported')
        elif len(managers) > 1:
            raise ValueError(
                'There cannot be more than one Manager or Manager subclass ' 
                'imported')            
        else:
            return managers[0](
                name = self.name,
                identification = self.identification)       
                     
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
