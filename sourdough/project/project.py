"""
project: interface for sourdough projects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Project (OptionsMixin, Hybrid): iterable which contains the needed
        information and data for constructing and executing tree objects.

"""
import dataclasses
import pathlib
import textwrap
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union
import warnings

import sourdough


@dataclasses.dataclass
class Plan(sourdough.Hybrid):
    """Iterable container for a composite sourdough object.
    
   It includes a metadata label for a unique project in the 'identification' 
   attribute. By default, this will combine the 'name' attribute with the date 
   and time when this class is instanced.
   
   A 'data' attribute is added for storing any data object(s) that are needed 
   when automatic processing is chosen.

    Args:
        contents (Sequence[sourdough.Component]): instances which form the
            structure of a composite object. Defaults to an empty list. 
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Component is called, 'name' is set based upon
            the 'get_name' method in Component. If that method is not 
            overridden by a subclass instance, 'name' will be assigned to the 
            snake case version of the class name ('__class__.__name__').
        design (str): the name of the structural design that should
            be used to create objects in an instance. This should correspond
            to a key in a Project instance's 'designs' class attribute. 
            Defaults to 'chained'.
        data (Any]): a data object to apply any constructed objects to.
            This need only be provided when the class is instanced for
            automatic execution. Defaults to None. If you are working on a data-
            focused Manager, consider using siMpLify instead 
            (https://github.com/WithPrecedent/simplify). It applies sourdough
            in the data science context. sourdough itself treats 'data' as an
            unknown object of any type which offers more flexibility of design.
            
    """
    contents: Sequence['sourdough.Component'] = dataclasses.field(
        default_factory = list) 
    name: str = None
    design: str = 'chained'
    data: Any = None    

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent initialization method(s).
        super().__post_init__()


    """ Public Methods """
        
    def perform(self, data: object = None) -> object:
        """Applies stored Action instances to 'data'.

        Args:
            data (object): an object to be modified and/or analyzed by stored 
                Action instances. Defaults to None.

        Returns:
            object: data, possibly with modifications made by Operataor 
                instances. If data is not passed, no object is returned.
            
        """
        if data is None:
            for action in iter(self):
                action.perform()
            return self
        else:
            for action in iter(self):
                data = action.perform(data = data)
            return data
    
    def apply(self, tool: Callable, recursive: bool = True, **kwargs) -> None:
        """
        
        """
        new_contents = []
        for item in iter(self.contents):
            if isinstance(item, sourdough.Hybrid):
                if recursive:
                    new_item = item.apply(
                        tool = tool, 
                        recursive = True, 
                        **kwargs)
                else:
                    new_item = item
            else:
                new_item = tool(item, **kwargs)
            new_contents.append(new_item)
        self.contents = new_contents
        return self

    def find(self, 
            tool: Callable, 
            recursive: bool = True, 
            matches: Sequence = None,
            **kwargs) -> Sequence['sourdough.Component']:
        """
        
        """
        if matches is None:
            matches = []
        for item in iter(self.contents):
            matches.extend(sourdough.utilities.listify(tool(item, **kwargs)))
            if isinstance(item, sourdough.Hybrid):
                if recursive:
                    matches.extend(item.find(
                        tool = tool, 
                        recursive = True,
                        matches = matches, 
                        **kwargs))
        return matches
               
    """ Properties """
    
    @property
    def overview(self) -> Mapping[str, Sequence[str]]:
        """Returns a dict snapshot of a Worker subclass instance.
        
        Returns:
            Mapping[str, Sequence[str]]: configured according to the 
                '_get_overview' method.
        
        """
        return self._get_overview() 

    @property    
    def workers(self) -> Sequence['Worker']:
        """Returns all instances of Worker in 'contents' (recursive).
        
        Returns:
            Sequence[Worker]: all Worker instances in the contained tree
                object.
                
        """
        return self.find(self._get_type, component = Worker)
 
    @property
    def tasks(self) -> Sequence['sourdough.Task']:
        """Returns all instances of Task in 'contents' (recursive).
        
        Returns:
            Sequence[Task]: all Task instances in the contained tree
                object.
                
        """
        return self.find(self._get_type, component = sourdough.Task)
    
    @property    
    def techniques(self) -> Sequence['sourdough.Technique']:
        """Returns all instances of Technique in 'contents' (recursive).
        
        Returns:
            Sequence[Technique]: all Technique instances in the contained 
                tree object.
                
        """
        return self.find(self._get_type, component = sourdough.Technique)
    
    """ Dunder Methods """
    
    def __iter__(self) -> Iterable:
        """Returns iterable selected by structural settings."""
        if isinstance(self.design.iterator, str):
            return getattr(self, self.design.iterator)(
                contents = self.contents)
        else:
            return self.design.iterator(self.contents)
        
    """ Private Methods """
        
    def _get_overview(self) -> Mapping[str, Union[str, Sequence[str]]]:
        """Returns outline of the overal project tree.
        
        Returns:  
            Mapping[str, Union[str, Sequence[str]]]: project identification and
                the names of the contained Worker, Task, and/or Technique
                instances.
                
        """
        overview = {'project': self.identification}
        overview['workers'] = [w.name for w in self.workers]
        overview['tasks'] = [s.name for s in self.tasks]
        overview['techniques'] = [t.name for t in self.techniques]
        return overview


   
 
@dataclasses.dataclass
class Project(sourdough.OptionsMixin, sourdough.Hybrid):
    """Constructs, organizes, and stores tree Workers and Actions.
    
    A Project inherits all of the differences between a Hybrid and a python
    list.

    A Project differs from a Hybrid in 5 significant ways:
        1) The Project is the public interface to composite object construction 
            and application. It may store the composite object instance(s) as 
            well as any required classes (such as those stored in the 'data' 
            attribute). This includes Settings and Filer, stored in the 
            'settings' and 'filer' attributes, respectively.
        2) Project stores Creator subclass instances in 'contents'. Those 
            instances are used to assemble and apply the parts of Hybrid 
            instances.
        3) Project includes an 'automatic' attribute which can be set to perform
            all of its methods if all of the necessary arguments are passed.
        4) It has an OptionsMixin, which contains a Catalog instance storing
            default Creator instances in 'options'.
        5)
        
    Args:
        contents (Sequence[Union[sourdough.Creator, str]]]): list of 
            Creator subclass instances or strings which correspond to keys in 
            'options'. Defaults to 'default', which will use the 'defaults' 
            attribute of 'options' to select Creator instances.
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
        settings (Union[sourdough.Settings, str, pathlib.Path]]): 
            an instance of Settings or a str or pathlib.Path containing the 
            file path where a file of a supported file type with settings for a 
            Settings instance is located. Defaults to None.
        filer (Union[sourdough.Filer, str, pathlib.Path]]): an instance of 
            Filer or a str or pathlib.Path containing the full path of where the 
            root folder should be located for file input and output. A Filer
            instance contains all file path and import/export methods for use 
            throughout sourdough. Defaults to None.
        design (str): type of design for the project's composite object.
            Defaults to 'tree'.
        identification (str): a unique identification name for a 
            Manager instance. The name is used for creating file folders
            related to the 'Manager'. If not provided, a string is created from
            'name' and the date and time. This is a notable difference
            between an ordinary Worker instancce and a Manager instance. Other
            Workers are not given unique identification. Defaults to None.   
        automatic (bool): whether to automatically advance 'contents' (True) or 
            whether the contents must be changed manually by using the 'advance' 
            or '__iter__' methods (False). Defaults to True.
        designs (ClassVar[sourdough.Catalog]): a class attribute storing
            composite design options.            
        options (ClassVar[sourdough.Catalog]): a class attribute storing
            components of a composite design.
    
    Attributes:
        plan (sourdough.Hybrid): the iterable composite object created by Project.
        index (int): the current index of the iterator in the instance. It is
            set to -1 in the '__post_init__' method.
        stage (str): name of the last stage that has been implemented. It is set
            to 'initialize' in the '__post_init__' method.
        previous_stage (str): name of the previous stage to the last stage that
            has been implemented. It is set by the 'advance' method.
            
    """
    contents: Sequence['sourdough.Creator'] = dataclasses.field(
        default_factory = lambda: [
            sourdough.Author, sourdough.Publisher, sourdough.Reader])
    name: str = None
    settings: Union['sourdough.Settings', str, pathlib.Path] = None
    filer: Union['sourdough.Filer', str, pathlib.Path] = None
    structure: str = 'tree'
    identification: str = None
    automatic: bool = True
    data: object = None
    structures: ClassVar['sourdough.Catalog'] = sourdough.Catalog(
        contents = {
            'graph': sourdough.structures.Graph, 
            'pipeline': sourdough.structures.Pipeline, 
            'tree': sourdough.structures.Tree})
    designs: ClassVar['sourdough.Catalog'] = sourdough.Catalog(
        contents = {
            'chained': sourdough.designs.Chained, 
            'comparative': sourdough.designs.Comparative,
            'cycle': sourdough.designs.Cycle,
            'graph': sourdough.designs.Graph,
            'flat': sourdough.designs.Flat})
    components: ClassVar['sourdough.Catalog'] = sourdough.Catalog(
        contents = {
            'component': sourdough.Component,
            'task': sourdough.components.Task,
            'technique': sourdough.components.Technique,
            'worker': sourdough.components.Worker})
    options: ClassVar['sourdough.Catalog'] = sourdough.Catalog()    
    
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent initialization method(s).
        super().__post_init__()
        # Removes various python warnings from console output.
        warnings.filterwarnings('ignore')
        # Sets unique project 'identification', if not passed.
        self.identification = self.identification or self._set_identification()
        # Validates or creates a 'Settings' instance.
        self.settings = sourdough.Settings(contents = self.settings)
        # Adds 'general' section attributes from 'settings'.
        self.settings.inject(instance = self)
        # Validates or creates a Filer' instance.
        self.filer = sourdough.Filer(
            root_folder = self.filer, 
            settings = self.settings)
        # Initializes a composite Hybrid subclass instance.
        self.plan = self._initialize_plan(design = self.design)
        # Initializes Creator instances stored in 'contents'.
        self.contents = self._initialize_creators(contents = self.contents)
        # Sets current 'stage' and 'index' for that 'stage'.
        self.index: int = -1
        self.stage: str = 'initialize' 
        # Advances through 'contents' if 'automatic' is True.
        if self.automatic:
            self.plan = self._auto_contents(plan = self.plan)

    """ Public Methods """

    def validate(self, 
            contents: 'sourdough.Creator') -> Sequence['sourdough.Creator']:
        """Validates that all 'contents' are Creator subclass instances.

        Args:
            contents (sourdough.Creator): list of Creator subclass instances.

        Raises:
            TypeError: if an item in 'contents' is not a Creator subclass 
                instance.
            
        Returns:
            Sequence[sourdough.Creator]: a list with Creator subclass instances.
                  
        """
        if all(issubclass(c, sourdough.Creator) for c in contents):
            return contents
        else:       
            raise TypeError(f'contents must only contain Creator subclasses')
                 
    def advance(self, stage: str = None) -> None:
        """Advances to next item in 'contents' or to 'stage' argument.

        This method only needs to be called manually if 'automatic' is False.
        Otherwise, this method is automatically called when the class is 
        instanced.

        Args:
            stage (str): name of item in 'contents'. Defaults to None. 
                If not passed, the method goes to the next item in contents.

        Raises:
            ValueError: if 'stage' is neither None nor in 'contents'.
            IndexError: if 'advance' is called at the last stage in 'contents'.

        """
        if stage is None:
            try:
                new_stage = self.contents[self.index + 1]
            except IndexError:
                raise IndexError(f'{self.name} cannot advance further')
        else:
            try:
                new_stage = self.contents[stage]
            except KeyError:
                raise ValueError(f'{stage} is not a recognized stage')
        self.index += 1
        self.previous_stage: str = self.stage
        self.stage = new_stage
        return self

    def iterate(self, plan: 'sourdough.Hybrid') -> 'sourdough.Hybrid':
        """Advances to next stage and applies that stage to 'plan'.

        Args:
            plan (sourdough.Hybrid): instance to apply the next stage's methods 
                to.
                
        Raises:
            IndexError: if this instance is already at the last stage.

        Returns:
            sourdough.Hybrid: with the last stage applied.
            
        """
        if self.index == len(self.contents) - 1:
            raise IndexError(
                f'{self.name} is at the last stage and cannot further iterate')
        else:
            self.advance()
            plan = self.contents[self.index].create(plan = plan)
        return plan
            
    """ Dunder Methods """
    
    def __iter__(self) -> Iterable:
        """Returns iterable of methods of 'contents'.
        
        Returns:
            Iterable: 'create' methods of 'contents'.
            
        """
        return iter([getattr(s, 'create') for s in self.contents])

    def __next__(self) -> Callable:
        """Returns next method after method matching 'item'.
        
        Returns:
            Callable: next method corresponding to those listed in 'options'.
            
        """
        if self.index < len(self.contents):
            self.advance()
            return getattr(self.contents[self.index], 'create')
        else:
            raise StopIteration()

    # def __str__(self) -> str:
    #     """Returns default string representation of an instance.

    #     Returns:
    #         str: default string representation of an instance.

    #     """
    #     if hasattr(self.design, 'name'):
    #         return textwrap.dedent(f'''
    #             sourdough {self.__class__.__name__}
    #             name: {self.name}
    #             automatic: {self.automatic}
    #             data: {self.data is not None}
    #             design: {self.design.name}
    #             defaults:
    #             {textwrap.indent(str(self.defaults), '    ')}
    #             contents:
    #             {textwrap.indent(str(self.contents), '    ')}
    #             settings:
    #             {textwrap.indent(str(self.settings), '    ')}
    #             filer:
    #             {textwrap.indent(str(self.filer), '    ')}
    #             options:
    #             {textwrap.indent(str(self.options), '    ')}
    #             designs:
    #             {textwrap.indent(str(self.designs), '    ')}''')
    #     else:
    #         return textwrap.dedent(f'''
    #             sourdough {self.__class__.__name__}
    #             name: {self.name}
    #             automatic: {self.automatic}
    #             data: {self.data is not None}
    #             design: {self.design}
    #             defaults:
    #             {textwrap.indent(str(self.defaults), '    ')}
    #             contents:
    #             {textwrap.indent(str(self.contents), '    ')}
    #             settings:
    #             {textwrap.indent(str(self.settings), '    ')}
    #             filer:
    #             {textwrap.indent(str(self.filer), '    ')}
    #             options:
    #             {textwrap.indent(str(self.options), '    ')}
    #             designs:
    #             {textwrap.indent(str(self.designs), '    ')}''')
        
    """ Private Methods """

    def _set_identification(self) -> None:
        """Sets unique 'identification' str based upon date and time."""
        return sourdough.utilities.datetime_string(prefix = self.name)
    
    def _initialize_creators(self, 
            contents: Sequence['sourdough.Creator']) -> Sequence[
                'sourdough.Creator']:
        """Instances each Creator in 'contents'.
        
        Args:
            contents (Sequence[sourdough.Creator]): list of Creator classes.
        
        Returns:
            Sequence[sourdough.Creator]: list of Creator classes.
        
        """
        new_contents = []
        for creator in contents:
            try:
                new_contents.append(creator(project = self))
            except TypeError:
                if isinstance(creator, sourdough.Creator):
                    new_contents.append(creator)
                else:
                    raise TypeError(f'{creator} is not a Creator type')
        return new_contents   
    
    def _initialize_plan(self, 
            design: Union[
                str, 
                sourdough.designs.Design]) -> sourdough.Hybrid:
        """Instances a Hybrid subclass based upon 'design'.
        
        Args:
            design (Union[str, sourdough.designs.Design]): str matching
                a key in 'designs' or a subclass of Design.
        
        Returns:
            sourdough.Hybrid: an instance created based upon 'design'.
        
        """
        design = self._initialize_design(design = design)
        return design.load(key = 'root')(name = self.name, data = self.data)
        
    def _initialize_design(self, 
            design: Union[
                str, 
                'sourdough.designs.Design']) -> (
                    'sourdough.designs.Design'):
        """Returns a Design instance based upon 'design'.

        Args:
            design (Union[str, sourdough.designs.Design]): str matching
                a key in 'designs', a Design subclass, or a Design
                subclass instance.

        Returns:
            sourdough.designs.Design: a Design subclass instance.
            
        """
        if isinstance(design, str):
            return self.designs[design]()
        elif isinstance(design, sourdough.designs.Design):
            return design
        else:
            return design()
                          
    def _auto_contents(self, plan: 'sourdough.Hybrid') -> 'sourdough.Hybrid':
        """Automatically advances through and iterates stored Creator instances.

        Args:
            plan (sourdough.Hybrid): an instance containing any data for the plan 
                methods to be applied to.
                
        Returns:
            sourdough.Hybrid: modified by the stored Creator instance's 
                'create' methods.
            
        """
        for stage in self.contents:
            plan = self.iterate(plan = plan)
            # print('test plan', plan)
            print('test plan workers', plan.workers)
            print('test stage overview', plan.overview)
        return plan
