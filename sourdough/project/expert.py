"""
expert: 
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:



"""
from __future__ import annotations
import dataclasses
import multiprocessing
import textwrap
from types import ModuleType
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import sourdough


@dataclasses.dataclass
class Bases(sourdough.quirks.Loader):
    """Base classes for a sourdough projects.
    
    Args:
        manager (Union[str, Type]): class for organizing, implementing, and
            iterating the package's classes and functions. Defaults to 
            'sourdough.Manager'.
        workflow (Union[str, Type]): the workflow to use in a sourdough 
            project. Defaults to 'sourdough.products.Workflow'.
            
    """ 
    manager: Union[str, Type] = 'sourdough.Manager'
    component: Union[str, Type] = 'sourdough.Component'
    factory: Union[str, Type] = 'sourdough.Factory'
    default_design: Union[str, Type] = 'sourdough.workflows.Pipeline'


@dataclasses.dataclass
class Manager(sourdough.quirks.Registrar, sourdough.quirks.Loader, 
              sourdough.types.Lexicon):
    """Constructs, organizes, and implements a part of a sourdough project.
    
    Unlike an ordinary Hybrid, a Manager instance will iterate 'stages' 
    instead of 'contents'. However, all access methods still point to 
    'contents', which is where the results of iterating the class are stored.
        
    Args:
        contents (Mapping[str, object]]): stored objects created by the 
            'create' methods of 'stages'. Defaults to an empty dict.
        stages (Sequence[Union[Type, str]]): a Creator-compatible classes or
            strings corresponding to the keys in registry of the default
            'stage' in 'bases'. Defaults to a list of 'architect', 
            'builder', and 'worker'. 
        project (sourdough.Project)
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. If it is None, the 'name' will be attempted to be 
            inferred from the first section name in 'settings' after 'general' 
            and 'files'. If that fails, 'name' will be the snakecase name of the
            class. Defaults to None. 
        identification (str): a unique identification name for a Manager 
            instance. The name is used for creating file folders related to the 
            project. If it is None, a str will be created from 'name' and the 
            date and time. Defaults to None.   
        automatic (bool): whether to automatically advance 'director' (True) or 
            whether the director must be advanced manually (False). Defaults to 
            True.
        data (object): any data object for the project to be applied. If it is
            None, an instance will still execute its workflow, but it won't
            apply it to any external data. Defaults to None.  
        bases (ClassVar[object]): contains information about default base 
            classes used by a Manager instance. Defaults to an instance of 
            Bases.
        rules (ClassVar[object]):
        options (ClassVar[object]):
         
    """
    contents: Mapping[str, str] = dataclasses.field(
        default_factory = lambda: {
            'settings': 'outline', 
            'outline': 'workflow', 
            'workflow': 'results'})
    project: Union[object, Type] = None
    name: str = None
    automatic: bool = True
    data: object = None
    bases: ClassVar[Bases] = Bases()
    converters: ClassVar[Union[ModuleType, str]] = 'sourdough.converters'
    registry: ClassVar[Mapping[str, Manager]] = sourdough.types.Catalog()
    
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent and/or mixin initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass
        # Creates an empty 'deliverables' attribute for project deliverables.
        self.deliverables = self.bases.deliverables()
        # Sets index for iteration.
        self.index = 0
        # Advances through 'stages' if 'automatic' is True.
        if self.automatic:
            self.complete()

    """ Public Methods """
    
    def advance(self) -> Any:
        """Returns next product created in iterating a Manager instance."""
        return self.__next__()

    def complete(self) -> None:
        """Advances through the stored Creator instances.
        
        The results of the iteration is that each item produced is stored in 
        'content's with a key of the 'produces' attribute of each stage.
        
        """
        for start, stop in self.contents.items():
            self.__next__()
        return self
    
    """ Dunder Methods """
    
    def __next__(self) -> None:
        """Creates and stores project deliverable in 'deliverables'."""
        if self.index < len(self.contents):
            start = self.contents.keys()[self.index]
            finish = self.contents[start]
            if hasattr(self.project, 'verbose') and self.project.verbose:
                print(f'Converting {start} to {finish}')
            self.index += 1
            converter = getattr(self.converters, f'{start}_to_{finish}')
            self.deliverables[finish] = converter(manager = self)
        else:
            raise IndexError()
        return self


@dataclasses.dataclass
class Factory(object):

    manager: Manager = None
    
    """ Public Methods """
    
    def create(self, name: str) -> Workflow: 
        base = self._get_design(name = name)
        section = self.manager.settings[name]

    """ Private Methods """
    
    def _get_design(self, name: str) -> Workflow:
        """[summary]

        Args:
            name (str): [description]
            design (str): [description]
            manager (sourdough.Manager): [description]

        Returns:
            str: [description]
            
        """
        try:
            design = self.manager.settings[name][f'{name}_design']
        except KeyError:
            design = self.manager.bases.default_design
        return self.manager.bases.component.registry.select(key = design)

    def _get_parameters(self, name: str, 
                        manager: sourdough.Manager) -> Dict[Any, Any]:
        """[summary]

        Args:
            name (str): [description]
            project (sourdough.Manager): [description]

        Returns:
            sourdough.types.Lexicon: [description]
            
        """
        try:
            return manager.project.settings[f'{name}_parameters']
        except KeyError:
            return {}











@dataclasses.dataclass
class Workflow(sourdough.Component, sourdough.Hybrid):
    """Base iterable class for portions of a sourdough project.
    
    Args:
        contents (Any): stored item(s) which must have 'name' attributes. 
            Defaults to an empty list.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. 
        parameters (Mapping[Any, Any]]): parameters to be attached to 'contents' 
            when the 'apply' method is called. Defaults to an empty dict.
        iterations (Union[int, str]): number of times the 'apply' method should 
            be called. If 'iterations' is 'infinite', the 'apply' method will
            continue indefinitely unless the method stops further iteration.
            Defaults to 1.
        criteria (str): after iteration is complete, a 'criteria' determines
            what should be outputted. This should correspond to a key in the
            'algorithms' Catalog for the corresponding sourdough Manager. 
            Defaults to None.
        parallel (ClassVar[bool]): whether the 'contents' contain other 
            iterables (True) or static objects (False). If True, a subclass
            should include a custom iterable for navigating the stored 
            iterables. Defaults to False.
            
    """
    contents: Sequence[Any] = dataclasses.field(default_factory = list)
    name: str = None
    worker: Worker = dataclasses.field(repr = False, default = None)
    parameters: Mapping[Any, Any] = dataclasses.field(default_factory = dict)
    iterations: Union[int, str] = 1
    criteria: Union[str, Callable, Sequence[Union[Callable, str]]] = None
    parallel: ClassVar[bool] = False
        
    """ Public Methods """ 
        
    def apply(self, tool: Callable, recursive: bool = True, **kwargs) -> None:
        """Maps 'tool' to items stored in 'contents'.
        
        Args:
            tool (Callable): callable which accepts an object in 'contents' as
                its first argument and any other arguments in kwargs.
            recursive (bool): whether to apply 'tool' to nested items in
                'contents'. Defaults to True.
            kwargs: additional arguments to pass when 'tool' is used.
        
        """
        new_contents = []
        for child in iter(self.contents):
            if isinstance(child, Iterable):
                if recursive:
                    new_child = child.apply(tool = tool, recursive = True, 
                                            **kwargs)
                else:
                    new_child = child
            else:
                new_child = tool(child, **kwargs)
            new_contents.append(new_child)
        self.contents = new_contents
        return self
    
    def finalize(self, recursive: bool = True) -> None:
        """[summary]

        Args:
            recursive (bool, optional): [description]. Defaults to True.

        Returns:
            [type]: [description]
        """
        
        new_contents = []
        for child in self.contents:
            new_child = self._instancify(node = child)
            if recursive and isinstance(new_child, Iterable):
                new_child = new_child.finalize(recursive = recursive)
            new_contents.append(new_child)
        self.contents = new_contents
        return self 
    
    def find(self, tool: Callable, recursive: bool = True, 
             matches: Sequence[Any] = None, **kwargs) -> Sequence[Workflow]:
        """Finds items in 'contents' that match criteria in 'tool'.
        
        Args:
            tool (Callable): callable which accepts an object in 'contents' as
                its first argument and any other arguments in kwargs.
            recursive (bool): whether to apply 'tool' to nested items in
                'contents'. Defaults to True.
            matches (Sequence[Any]): items matching the criteria in 'tool'. This 
                should not be passed by an external call to 'find'. It is 
                included to allow recursive searching.
            kwargs: additional arguments to pass when 'tool' is used.
            
        Returns:
            Sequence[Any]: stored items matching the criteria in 'tool'. 
        
        """
        if matches is None:
            matches = []
        for item in iter(self.contents):
            matches.extend(sourdough.tools.listify(tool(item, **kwargs)))
            if isinstance(item, Iterable):
                if recursive:
                    matches.extend(item.find(tool = tool, recursive = True,
                                             matches = matches, **kwargs))
        return matches
         
    def implement(self, data: Any = None, **kwargs) -> Any:
        """[summary]

        Args:
            data (Any): [description]

        Returns:
            Any: [description]
        """
        if data is not None:
            kwargs['data'] = data
        try:
            self.contents.implement(**kwargs)
        except AttributeError:
            raise AttributeError(
                'stored object in Workflow lacks implement method')              

    """ Private Methods """

    def _instancify(self, node: Union[str, Workflow], **kwargs) -> Workflow:
        """Returns a Workflow instance based on 'node' and kwargs.

        Args:
            node (Union[str, Workflow]): a Workflow instance, a Workflow subclass, or a str
                matching a stored Workflow in the Workflow registry.

        Raises:
            KeyError: if 'node' is a str, but doesn't match a stored Workflow in the
                Workflow registry.
            TypeError: if 'node' is neither a str, a Workflow subclass, or a Workflow
                instance.

        Returns:
            Workflow: an instance with all kwargs added as attributes.
            
        """
        if isinstance(node, Workflow):
            for key, value in kwargs.items():
                setattr(node, key, value)
        else:
            if isinstance(node, str):
                try:
                    node = Workflow.registry.acquire(key = node)
                except KeyError:
                    raise KeyError('node not found in the Workflow registry ')
            elif issubclass(node, Workflow):
                pass
            else:
                raise TypeError('node must be a Workflow or str')
            node = node(**kwargs)
        return node 
     
    """ Dunder Methods """
  
    def __getitem__(self, key: Union[Any, int]) -> Any:
        """Returns value(s) for 'key' in 'contents'.
        
        If 'key' is not an int type, this method looks for a matching 'name'
        attribute in the stored instances.
        
        If 'key' is an int type, this method returns the stored item at the
        corresponding index.
        
        If only one match is found, a single item is returned. If more are 
        found, a Workflow or Workflow subclass with the matching 'name' attributes 
        is returned.

        Args:
            key (Union[Any, int]): key or index to search for in 'contents'.

        Returns:
            Any: value(s) stored in 'contents' that correspond to 'key'. If 
                there is more than one match, the return is a Workflow or Workflow 
                subclass with that matching stored items.

        """
        if isinstance(key, int):
            return self.contents[key]
        else:
            matches = [c for c in self.contents if c.name == key]
            if len(matches) == 0:
                raise KeyError(f'{key} is not in {self.__class__.__name__}')
            elif len(matches) == 1:
                return matches[0]
            else:
                return self.__class__(name = self.name, contents = matches)
            
    def __setitem__(self, key: Union[Any, int], value: Any) -> None:
        """Sets 'key' in 'contents' to 'value'.

        Args:
            key (Union[Any, int]): if key isn't an int, it is ignored (since the
                'name' attribute of the value will be acting as the key). In
                such a case, the 'value' is added to the end of 'contents'. If
                key is an int, 'value' is assigned at the that index number in
                'contents'.
            value (Any): value to be paired with 'key' in 'contents'.

        """
        if isinstance(key, int):
            self.contents[key] = value
        else:
            self.add(value)
        return self

    def __delitem__(self, key: Union[Any, int]) -> None:
        """Deletes item matching 'key' in 'contents'.

        If 'key' is not an int type, this method looks for a matching 'name'
        attribute in the stored instances and deletes all such items. If 'key'
        is an int type, only the item at that index is deleted.

        Args:
            key (Union[Any, int]): name or index in 'contents' to delete.

        """
        if isinstance(key, int):
            del self.contents[key]
        else:
            self.contents = [c for c in self.contents if c.name != key]
        return self

    def __iter__(self) -> Iterable:
        """Returns iterable of 'contents'.

        Returns:
            Iterable: 'contents'.

        """
        return iter(self.contents)

    def __len__(self) -> int:
        """Returns length of iterable of 'contents'

        Returns:
            int: length of iterable 'contents'.

        """
        return len(self.__iter__())
  
    def __contains__(self, name: str) -> bool:
        """[summary]

        Args:
            name (str): [description]

        Returns:
            bool: [description]
            
        """
        if isinstance(self.contents, (list, tuple, dict)):
            return name in self.contents
        else:
            try:
                return name == self.contents.name
            except (AttributeError, TypeError):
                return name == self.contents

    def __str__(self) -> str:
        """Returns default string representation of an instance.

        Returns:
            str: default string representation of an instance.

        """
        return '\n'.join([textwrap.dedent(f'''
            sourdough {self.__class__.__name__}
            name: {self.name}
            nodes:'''),
            f'''{textwrap.indent(str(self.contents), '    ')}
            edges:
            {textwrap.indent(str(self.edges), '    ')}'''])   
    

@dataclasses.dataclass
class Worker(sourdough.quirks.Registar, sourdough.quirks.Element, 
             collections.abc.MutableSequence):
    """Base container class for sourdough composite objects.
    
    A Workflow has a 'name' attribute for internal referencing and to allow 
    sourdough iterables to function propertly. Workflow instances can be used 
    to create a variety of composite workflows such as trees, cycles, contests, 
    studies, and graphs.
    
    Args:
        contents (Any): item(s) contained by a Workflow instance.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. 
        parameters (Mapping[Any, Any]]): parameters to be attached to 'contents' 
            when the 'apply' method is called. Defaults to an empty dict.
        iterations (Union[int, str]): number of times the 'apply' method should 
            be called. If 'iterations' is 'infinite', the 'apply' method will
            continue indefinitely unless the method stops further iteration.
            Defaults to 1.
        criteria (str): after iteration is complete, a 'criteria' determines
            what should be outputted. This should correspond to a key in the
            'algorithms' Catalog for the corresponding sourdough Manager. 
            Defaults to None.
        parallel (ClassVar[bool]): whether the 'contents' contain other 
            iterables (True) or static objects (False). If True, a subclass
            should include a custom iterable for navigating the stored 
            iterables. Defaults to False.
            
    """ 
    name: str = None
    parent: Workflow = None
    contents: Sequence[Workflow] = dataclasses.field(default_factory = list)
    parameters: Mapping[Any, Any] = dataclasses.field(default_factory = dict)

    
    """ Public Methods """

    def implement(self, data: Any) -> Any:
        """[summary]

        Args:
            data (Any): [description]

        Returns:
            Any: [description]
        """
        datasets = []
        for i in self.iterations:
            if self.parallel:
                if sourdough.settings.parallelize:
                    datasets.append(self.implementation(data = data))
            else:
                data = self.implementation(data = data)
        return data     

    """ Private Methods """

    def _implement_parallel(self, data: Any) -> Any:
        """Applies 'implementation' to data.
        
        Args:
            data (Any): any item needed for the class 'implementation' to be
                applied.
                
        Returns:
            Any: item after 'implementation has been applied.

        """  
        return data 

    def _implement_parallel_in_parallel(self, data: Any) -> Any:
        """Applies 'implementation' to data.
        
        Args:
            data (Any): any item needed for the class 'implementation' to be
                applied.
                
        Returns:
            Any: item after 'implementation has been applied.

        """
        all_data = []  
        multiprocessing.set_start_method('spawn')
        with multiprocessing.Pool() as pool:
            all_data = pool.starmap(self.implementation, data)
        return all_data  
    
    def _implement_parallel_in_serial(self, data: Any) -> Any:
        """Applies 'implementation' to data.
        
        Args:
            data (Any): any item needed for the class 'implementation' to be
                applied.
                
        Returns:
            Any: item after 'implementation has been applied.

        """  
        all_data = []
        all_data.append(self.implementation(data = data))
        return data   
                    

@dataclasses.dataclass
class Contest(Worker):
    """Stores Workflows in a comparative parallel workflow and chooses the best.

    Distinguishing characteristics of a Contest:
        1) Applies different components in parallel.
        2) Chooses the best stored Component based upon 'criteria'.
        3) Each stored Component is only attached to the Contest with exactly 
            one connection (these connections are not defined separately - they
            are simply part of the parallel workflow).
        
    Args:
        contents (Sequence[Component]): Component subclass instances. Defaults 
            to an empty list.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes.
        iterations (Union[int, str]): number of times the 'apply' method should 
            be called. If 'iterations' is 'infinite', the 'apply' method will
            continue indefinitely unless the method stops further iteration.
            Defaults to 1.
        criteria (str): after iteration is complete, a 'criteria' determines
            what should be outputted. This should correspond to a key in the
            'algorithms' Catalog for the sourdough manager.project. Defaults to None.
        parallel (ClassVar[bool]): whether the 'contents' contain other 
            iterables (True) or static objects (False). If True, a subclass
            should include a custom iterable for navigating the stored 
            iterables. Defaults to True.
                            
    """
    contents: Sequence[sourdough.Component] = dataclasses.field(
        default_factory = list)
    name: str = None
    iterations: Union[int, str] = 1
    criteria: str = None
    parallel: ClassVar[bool] = True
    
    
@dataclasses.dataclass
class Study(Worker):
    """Stores Flows in a comparative parallel workflow.

    Distinguishing characteristics of a Study:
        1) Applies different components and creates new branches of the overall
            Project workflow.
        2) Maintains all of the repetitions without selecting or averaging the 
            results.
        3) Each stored Component is only attached to the Study with exactly 
            one connection (these connections are not defined separately - they
            are simply part of the parallel workflow).
                      
    Args:
        contents (Sequence[Component]): Component subclass instances. Defaults 
            to an empty list.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes.
        iterations (Union[int, str]): number of times the 'apply' method should 
            be called. If 'iterations' is 'infinite', the 'apply' method will
            continue indefinitely unless the method stops further iteration.
            Defaults to 1.
        criteria (str): after iteration is complete, a 'criteria' determines
            what should be outputted. This should correspond to a key in the
            'algorithms' Catalog for the sourdough manager.project. Defaults to None.
        parallel (ClassVar[bool]): whether the 'contents' contain other 
            iterables (True) or static objects (False). If True, a subclass
            should include a custom iterable for navigating the stored 
            iterables. Defaults to True.
                            
    """
    contents: Sequence[sourdough.Component] = dataclasses.field(
        default_factory = list)
    name: str = None
    iterations: Union[int, str] = 1
    criteria: str = None
    parallel: ClassVar[bool] = True
        
    
@dataclasses.dataclass
class Survey(Worker):
    """Stores Flows in a comparative parallel workflow and averages results.

    Distinguishing characteristics of a Survey:
        1) Applies different components in parallel.
        2) Averages or otherwise combines the results based upon selected 
            criteria.
        3) Each stored Component is only attached to the Survey with exactly 
            one connection (these connections are not defined separately - they
            are simply part of the parallel workflow).    
                    
    Args:
        contents (Sequence[Component]): Component subclass instances. Defaults 
            to an empty list.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes.
        iterations (Union[int, str]): number of times the 'apply' method should 
            be called. If 'iterations' is 'infinite', the 'apply' method will
            continue indefinitely unless the method stops further iteration.
            Defaults to 1.
        criteria (str): after iteration is complete, a 'criteria' determines
            what should be outputted. This should correspond to a key in the
            'algorithms' Catalog for the sourdough manager.project. Defaults to None.
        parallel (ClassVar[bool]): whether the 'contents' contain other 
            iterables (True) or static objects (False). If True, a subclass
            should include a custom iterable for navigating the stored 
            iterables. Defaults to True.
                            
    """
    contents: Sequence[sourdough.Component] = dataclasses.field(
        default_factory = list)
    name: str = None
    iterations: Union[int, str] = 1
    criteria: str = None
    parallel: ClassVar[bool] = True   
       