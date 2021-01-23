"""
nodes:
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:

    
"""
from __future__ import annotations
import abc
import copy
import dataclasses
import itertools
import pprint
import textwrap
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import sourdough  


@dataclasses.dataclass
class Component(sourdough.quirks.Element, sourdough.types.Base, abc.ABC):
    """Abstract base for parts of a sourdough composite workflow.
    
    All subclasses must have an 'execute' method.
    
    Args:
        contents (Any): stored item for use by a Component subclass instance.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Configuration instance, 
            'name' should match the appropriate section name in a Configuration 
            instance. Defaults to None.
        iterations (Union[int, str]): number of times the 'execute' method 
            should  be called. If 'iterations' is 'infinite', the 'execute' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        criteria (str): after iteration is complete, a 'criteria' determines
            what should be outputted. This should correspond to a key in the
            Component library. Defaults to None.
        parallel (ClassVar[bool]): whether the 'contents' contain other 
            iterables (True) or static objects (False). If True, a subclass
            should include a custom iterable for navigating the stored 
            iterables. Defaults to False.
        parameters (Mapping[Any, Any]]): parameters to be attached to 'contents' 
            when the 'execute' method is called. Defaults to an empty dict.
        library (ClassVar[Library]): related Library instance that will store
            subclasses and allow runtime construction and instancing of those
            stored subclasses.
                
    """
    contents: Any = None
    name: str = None
    iterations: Union[int, str] = 1
    criteria: str = None
    parameters: Mapping[Any, Any] = dataclasses.field(default_factory = dict)
    parallel: ClassVar[bool] = False
    library: ClassVar[sourdough.types.Library] = sourdough.types.Library()

    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def execute(self, data: Any = None, **kwargs) -> Any:
        """Subclasses must provide their own methods."""
        pass 

    """ Dunder Methods """
    
    def __str__(self) -> str:
        """Returns default string representation of an instance.

        Returns:
            str: default string representation of an instance.

        """
        return '\n'.join([textwrap.dedent(f'''
            sourdough {self.__class__.__name__}
            name: {self.name}
            components:'''),
            f'''{textwrap.indent(str(self.contents), '    ')}'''])   
         
   
@dataclasses.dataclass
class Worker(sourdough.composites.Pipeline, Component):
    """Applies a project Workflow and produces results.

    Args:
        contents (Any): stored item for use by a Component subclass instance.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Configuration instance, 
            'name' should match the appropriate section name in a Configuration 
            instance. Defaults to None.
        iterations (Union[int, str]): number of times the 'execute' method 
            should  be called. If 'iterations' is 'infinite', the 'execute' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        criteria (str): after iteration is complete, a 'criteria' determines
            what should be outputted. This should correspond to a key in the
            Component library. Defaults to None.
        parallel (ClassVar[bool]): whether the 'contents' contain other 
            iterables (True) or static objects (False). If True, a subclass
            should include a custom iterable for navigating the stored 
            iterables. Defaults to False.
        parameters (Mapping[Any, Any]]): parameters to be attached to 'contents' 
            when the 'execute' method is called. Defaults to an empty dict.
                
    """
    contents: Any = None
    name: str = None
    iterations: Union[int, str] = 1
    criteria: str = None
    parameters: Mapping[Any, Any] = dataclasses.field(default_factory = dict)
    parallel: ClassVar[bool] = False


@dataclasses.dataclass
class Aggregation(Worker):
    """Aggregates unordered objects.
    
    Distinguishing characteristics of an Aggregation:
        1) Order doesn't matter. Therefore, the 'execute' method will execute 
            the stored contents in an arbitary order.
        2) Stored Components do not need to be connected. If attributes of the
            stored Components created connections, those connections will be 
            left in tact.
        3) Many of Hybrid's inherited methods will return errors because the 
            stored 'contents' are a set and therefore immutable.
        
    Args:
        contents (Any): stored item for use by a Component subclass instance.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Configuration instance, 
            'name' should match the appropriate section name in a Configuration 
            instance. Defaults to None.
        iterations (Union[int, str]): number of times the 'execute' method 
            should  be called. If 'iterations' is 'infinite', the 'execute' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        criteria (str): after iteration is complete, a 'criteria' determines
            what should be outputted. This should correspond to a key in the
            Component library. Defaults to None.
        parallel (ClassVar[bool]): whether the 'contents' contain other 
            iterables (True) or static objects (False). If True, a subclass
            should include a custom iterable for navigating the stored 
            iterables. Defaults to False.
        parameters (Mapping[Any, Any]]): parameters to be attached to 'contents' 
            when the 'execute' method is called. Defaults to an empty dict.
                
    """
    contents: Any = None
    name: str = None
    iterations: Union[int, str] = 1
    criteria: str = None
    parameters: Mapping[Any, Any] = dataclasses.field(default_factory = dict)
    parallel: ClassVar[bool] = False
    

@dataclasses.dataclass
class SerialWorker(Worker, abc.ABC):
    """Base class for serially workflows Flows in sourdough projects.
        
    Args:
        contents (Any): stored item for use by a Component subclass instance.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Configuration instance, 
            'name' should match the appropriate section name in a Configuration 
            instance. Defaults to None.
        iterations (Union[int, str]): number of times the 'execute' method 
            should  be called. If 'iterations' is 'infinite', the 'execute' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        criteria (str): after iteration is complete, a 'criteria' determines
            what should be outputted. This should correspond to a key in the
            Component library. Defaults to None.
        parallel (ClassVar[bool]): whether the 'contents' contain other 
            iterables (True) or static objects (False). If True, a subclass
            should include a custom iterable for navigating the stored 
            iterables. Defaults to False.
        parameters (Mapping[Any, Any]]): parameters to be attached to 'contents' 
            when the 'execute' method is called. Defaults to an empty dict.
                
    """
    contents: Any = None
    name: str = None
    iterations: Union[int, str] = 1
    criteria: str = None
    parameters: Mapping[Any, Any] = dataclasses.field(default_factory = dict)
    parallel: ClassVar[bool] = False
    
    
@dataclasses.dataclass
class Cycle(SerialWorker):
    """Ordered sourdough Components which will be repetitively called.

    Distinguishing characteristics of a Plan:
        1) Follows a sequence of instructions (serial workflow).
        2) It may pass data or other arguments to the next step in the sequence.
        3) Only one connection or path exists between each object.
        4) It repeats the number of times set in the 'iterations' attribute.
            If 'iteratations' is 'infinite', the loop will repeat until stopped
            by a condition set in 'criteria'.
        
    Args:
        contents (Any): stored item for use by a Component subclass instance.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Configuration instance, 
            'name' should match the appropriate section name in a Configuration 
            instance. Defaults to None.
        iterations (Union[int, str]): number of times the 'execute' method 
            should  be called. If 'iterations' is 'infinite', the 'execute' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        criteria (str): after iteration is complete, a 'criteria' determines
            what should be outputted. This should correspond to a key in the
            Component library. Defaults to None.
        parallel (ClassVar[bool]): whether the 'contents' contain other 
            iterables (True) or static objects (False). If True, a subclass
            should include a custom iterable for navigating the stored 
            iterables. Defaults to False.
        parameters (Mapping[Any, Any]]): parameters to be attached to 'contents' 
            when the 'execute' method is called. Defaults to an empty dict.
                
    """
    contents: Any = None
    name: str = None
    iterations: Union[int, str] = 10
    criteria: str = None
    parameters: Mapping[Any, Any] = dataclasses.field(default_factory = dict)
    parallel: ClassVar[bool] = False

    """ Public Methods """
    
    def execute(self, manager: sourdough.Manager, **kwargs) -> sourdough.Manager:
        """[summary]

        Args:
            project (sourdough.Project): [description]

        Returns:
            sourdough.Project: [description]
            
        """
        if 'data' not in kwargs and manager.project.data:
            kwargs['data'] = manager.project.data
        for i in self.iterations:
            project = super().execute(project = project, **kwargs)
        return project   


@dataclasses.dataclass
class Plan(SerialWorker):
    """Ordered sourdough Components without branching.

    Distinguishing characteristics of a Plan:
        1) Follows a sequence of instructions (serial workflow).
        2) It may pass data or other arguments to the next step in the sequence.
        3) Only one connection or path exists between each object. There is no
            branching or looping.
        
    Args:
        contents (Any): stored item for use by a Component subclass instance.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Configuration instance, 
            'name' should match the appropriate section name in a Configuration 
            instance. Defaults to None.
        iterations (Union[int, str]): number of times the 'execute' method 
            should  be called. If 'iterations' is 'infinite', the 'execute' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        criteria (str): after iteration is complete, a 'criteria' determines
            what should be outputted. This should correspond to a key in the
            Component library. Defaults to None.
        parallel (ClassVar[bool]): whether the 'contents' contain other 
            iterables (True) or static objects (False). If True, a subclass
            should include a custom iterable for navigating the stored 
            iterables. Defaults to False.
        parameters (Mapping[Any, Any]]): parameters to be attached to 'contents' 
            when the 'execute' method is called. Defaults to an empty dict.
                
    """
    contents: Any = None
    name: str = None
    iterations: Union[int, str] = 1
    criteria: str = None
    parameters: Mapping[Any, Any] = dataclasses.field(default_factory = dict)
    parallel: ClassVar[bool] = False


@dataclasses.dataclass
class ParallelWorker(Worker, abc.ABC):
    """Base class for parallelly workflowd Flows in sourdough projects.
        
    Args:
        contents (Any): stored item for use by a Component subclass instance.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Configuration instance, 
            'name' should match the appropriate section name in a Configuration 
            instance. Defaults to None.
        iterations (Union[int, str]): number of times the 'execute' method 
            should  be called. If 'iterations' is 'infinite', the 'execute' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        criteria (str): after iteration is complete, a 'criteria' determines
            what should be outputted. This should correspond to a key in the
            Component library. Defaults to None.
        parallel (ClassVar[bool]): whether the 'contents' contain other 
            iterables (True) or static objects (False). If True, a subclass
            should include a custom iterable for navigating the stored 
            iterables. Defaults to False.
        parameters (Mapping[Any, Any]]): parameters to be attached to 'contents' 
            when the 'execute' method is called. Defaults to an empty dict.
                
    """
    contents: Any = None
    name: str = None
    iterations: Union[int, str] = 1
    criteria: str = None 
    parameters: Mapping[Any, Any] = dataclasses.field(default_factory = dict)
    parallel: ClassVar[bool] = True
          
    """ Public Methods """

    def execute(self, manager: sourdough.Manager, **kwargs) -> sourdough.Project:
        """[summary]

        Args:
            project (sourdough.Project): [description]

        Returns:
            sourdough.Project: [description]
            
        """
        if hasattr(manager.project, 'parallelize') and manager.project.parallelize:
            multiprocessing.set_start_method('spawn')
            with multiprocessing.Pool() as pool:
                components = zip(self.contents)
                all_projects = pool.starmap(super().execute, components)
            # queue = multiprocessing.Queue()
            # process = multiprocessing.Process(target = project, args = (queue,))
            # process.start()
            # process.join()
            return all_projects
        else:
            return super().execute(project = project, **kwargs)


@dataclasses.dataclass
class Contest(ParallelWorker):
    """Stores Workflows in a comparative parallel workflow and chooses the best.

    Distinguishing characteristics of a Contest:
        1) Applies different components in parallel.
        2) Chooses the best stored Component based upon 'criteria'.
        3) Each stored Component is only attached to the Contest with exactly 
            one connection (these connections are not defined separately - they
            are simply part of the parallel workflow).
        
    Args:
        contents (Any): stored item for use by a Component subclass instance.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Configuration instance, 
            'name' should match the appropriate section name in a Configuration 
            instance. Defaults to None.
        iterations (Union[int, str]): number of times the 'execute' method 
            should  be called. If 'iterations' is 'infinite', the 'execute' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        criteria (str): after iteration is complete, a 'criteria' determines
            what should be outputted. This should correspond to a key in the
            Component library. Defaults to None.
        parallel (ClassVar[bool]): whether the 'contents' contain other 
            iterables (True) or static objects (False). If True, a subclass
            should include a custom iterable for navigating the stored 
            iterables. Defaults to False.
        parameters (Mapping[Any, Any]]): parameters to be attached to 'contents' 
            when the 'execute' method is called. Defaults to an empty dict.
                
    """
    contents: Any = None
    name: str = None
    iterations: Union[int, str] = 1
    criteria: str = None
    parameters: Mapping[Any, Any] = dataclasses.field(default_factory = dict)
    parallel: ClassVar[bool] = True
    
    
@dataclasses.dataclass
class Study(ParallelWorker):
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
        contents (Any): stored item for use by a Component subclass instance.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Configuration instance, 
            'name' should match the appropriate section name in a Configuration 
            instance. Defaults to None.
        iterations (Union[int, str]): number of times the 'execute' method 
            should  be called. If 'iterations' is 'infinite', the 'execute' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        criteria (str): after iteration is complete, a 'criteria' determines
            what should be outputted. This should correspond to a key in the
            Component library. Defaults to None.
        parallel (ClassVar[bool]): whether the 'contents' contain other 
            iterables (True) or static objects (False). If True, a subclass
            should include a custom iterable for navigating the stored 
            iterables. Defaults to False.
        parameters (Mapping[Any, Any]]): parameters to be attached to 'contents' 
            when the 'execute' method is called. Defaults to an empty dict.
                
    """
    contents: Any = None
    name: str = None
    iterations: Union[int, str] = 1
    criteria: str = None
    parameters: Mapping[Any, Any] = dataclasses.field(default_factory = dict)
    parallel: ClassVar[bool] = True
        
    
@dataclasses.dataclass
class Survey(ParallelWorker):
    """Stores Flows in a comparative parallel workflow and averages results.

    Distinguishing characteristics of a Survey:
        1) Applies different components in parallel.
        2) Averages or otherwise combines the results based upon selected 
            criteria.
        3) Each stored Component is only attached to the Survey with exactly 
            one connection (these connections are not defined separately - they
            are simply part of the parallel workflow).    
                    
    Args:
        contents (Any): stored item for use by a Component subclass instance.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Configuration instance, 
            'name' should match the appropriate section name in a Configuration 
            instance. Defaults to None.
        iterations (Union[int, str]): number of times the 'execute' method 
            should  be called. If 'iterations' is 'infinite', the 'execute' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        criteria (str): after iteration is complete, a 'criteria' determines
            what should be outputted. This should correspond to a key in the
            Component library. Defaults to None.
        parallel (ClassVar[bool]): whether the 'contents' contain other 
            iterables (True) or static objects (False). If True, a subclass
            should include a custom iterable for navigating the stored 
            iterables. Defaults to False.
        parameters (Mapping[Any, Any]]): parameters to be attached to 'contents' 
            when the 'execute' method is called. Defaults to an empty dict.
                
    """
    contents: Any = None
    name: str = None
    iterations: Union[int, str] = 1
    criteria: str = None
    parameters: Mapping[Any, Any] = dataclasses.field(default_factory = dict)
    parallel: ClassVar[bool] = True


@dataclasses.dataclass
class Technique(sourdough.types.Proxy, Component):
    """Base class for primitive objects in a sourdough composite object.
    
    The 'contents' and 'parameters' attributes are combined at the last moment
    to allow for runtime alterations.
    
    Args:
        contents (Any): stored item for use by a Component subclass instance.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Configuration instance, 
            'name' should match the appropriate section name in a Configuration 
            instance. Defaults to None.
        iterations (Union[int, str]): number of times the 'execute' method 
            should  be called. If 'iterations' is 'infinite', the 'execute' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        criteria (str): after iteration is complete, a 'criteria' determines
            what should be outputted. This should correspond to a key in the
            Component library. Defaults to None.
        parallel (ClassVar[bool]): whether the 'contents' contain other 
            iterables (True) or static objects (False). If True, a subclass
            should include a custom iterable for navigating the stored 
            iterables. Defaults to False.
        parameters (Mapping[Any, Any]]): parameters to be attached to 'contents' 
            when the 'execute' method is called. Defaults to an empty dict.
                                    
    """
    contents: Any = None
    name: str = None
    iterations: Union[int, str] = 1
    criteria: str = None
    parameters: Mapping[Any, Any] = dataclasses.field(default_factory = dict)
    parallel: ClassVar[bool] = False

    """ Properties """
    
    @property
    def algorithm(self) -> Union[object, str]:
        return self.contents
    
    @algorithm.setter
    def algorithm(self, value: Union[object, str]) -> None:
        self.contents = value
        return self
    
    @algorithm.deleter
    def algorithm(self) -> None:
        self.contents = None
        return self
        
    """ Public Methods """
    
    def execute(self, data: object = None, **kwargs) -> object:
        """Applies stored 'contents' with 'parameters'.
        
        Args:
            data (object): optional object to execute 'contents' to. Defaults to
                None.
                
        Returns:
            object: with any modifications made by 'contents'. If data is not
                passed, nothing is returned.        
        
        """
        if data is None:
            if self.contents:
                data = self.contents.execute(**self.parameters, **kwargs)
            return data
        else:
            if self.contents:
                return self.contents.execute(data, **self.parameters, **kwargs)
            else:
                return None

        
@dataclasses.dataclass
class Step(sourdough.types.Proxy, Component):
    """Wrapper for a Technique.

    Subclasses of Step can store additional methods and attributes to execute to 
    all possible technique instances that could be used. This is often useful 
    when using parallel Worklow instances which test a variety of strategies 
    with similar or identical parameters and/or methods.

    A Step instance will try to return attributes from Technique if the
    attribute is not found in the Step instance. 

    Args:
        contents (Union[Technique, str]): technique instance to be used in a 
            Workflow or a str corresponding to an item in the Component Library.
            Defaults to None.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example, if a 
            sourdough instance needs settings from a Configuration instance, 
            'name' should match the appropriate section name in a Configuration 
            instance. Defaults to None.
        iterations (Union[int, str]): number of times the 'execute' method 
            should  be called. If 'iterations' is 'infinite', the 'execute' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        criteria (str): after iteration is complete, a 'criteria' determines
            what should be outputted. This should correspond to a key in the
            Component library. Defaults to None.
        parallel (ClassVar[bool]): whether the 'contents' contain other 
            iterables (True) or static objects (False). If True, a subclass
            should include a custom iterable for navigating the stored 
            iterables. Defaults to False.
        parameters (Mapping[Any, Any]]): parameters to be attached to 'contents' 
            when the 'execute' method is called. Defaults to an empty dict.
                                    
    """
    contents: Union[Technique, str] = None
    name: str = None
    iterations: Union[int, str] = 1
    criteria: str = None
    parameters: Mapping[Any, Any] = dataclasses.field(default_factory = dict)
    parallel: ClassVar[bool] = False
                
    """ Properties """
    
    @property
    def technique(self) -> Technique:
        return self.contents
    
    @technique.setter
    def technique(self, value: Technique) -> None:
        self.contents = value
        return self
    
    @technique.deleter
    def technique(self) -> None:
        self.contents = None
        return self
    
    """ Public Methods """
    
    def execute(self, data: object = None, **kwargs) -> object:
        """Applies Technique instance in 'contents'.
        
        The code below outlines a basic method that a subclass should build on
        for a properly functioning Step.
        
        Applies stored 'contents' with 'parameters'.
        
        Args:
            data (object): optional object to execute 'contents' to. Defaults to
                None.
                
        Returns:
            object: with any modifications made by 'contents'. If data is not
                passed, nothing is returned.        
        
        """
        if data is None:
            self.contents.execute(**kwargs)
            return self
        else:
            return self.contents.execute(data = data, **kwargs)

