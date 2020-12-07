"""
workflows: structured iterable classes for sourdough projects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:

"""
from __future__ import annotations
import abc
import dataclasses
import multiprocessing
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import sourdough


@dataclasses.dataclass
class Aggregation(sourdough.products.Workflow):
    """Aggregates unordered objects.
    
    Distinguishing characteristics of an Aggregation:
        1) Order doesn't matter. Therefore, the 'apply' method will execute the
            stored contents in an arbitary order.
        2) Stored Components do not need to be connected. If attributes of the
            stored Components created connections, those connections will be 
            left in tact.
        3) Many of Hybrid's inherited methods will return errors because the 
            stored 'contents' are a set and therefore immutable.
        
    Args:
        contents (Sequence[Component]): Component subclass instances. Defaults 
            to an empty set.
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
            'algorithms' Catalog for the sourdough project. Defaults to None.
        parallel (ClassVar[bool]): whether the 'contents' contain other 
            iterables (True) or static objects (False). If True, a subclass
            should include a custom iterable for navigating the stored 
            iterables. Defaults to False.
                            
    """
    contents: Sequence[sourdough.Component] = dataclasses.field(
        default_factory = set)
    name: str = None
    iterations: Union[int, str] = 1
    criteria: str = None
    parallel: ClassVar[bool] = False 
    

@dataclasses.dataclass
class SerialFlow(sourdough.products.Workflow, abc.ABC):
    """Base class for serially workflows Flows in sourdough projects.
        
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
            'algorithms' Catalog for the sourdough project. Defaults to None.
        parallel (ClassVar[bool]): whether the 'contents' contain other 
            iterables (True) or static objects (False). If True, a subclass
            should include a custom iterable for navigating the stored 
            iterables. Defaults to False.
                            
    """
    contents: Sequence[sourdough.Component] = dataclasses.field(
        default_factory = list)
    name: str = None
    iterations: Union[int, str] = 1
    criteria: str = None
    parallel: ClassVar[bool] = False  
    
    
@dataclasses.dataclass
class Cycle(SerialFlow):
    """Ordered sourdough Components which will be repetitively called.

    Distinguishing characteristics of a Pipeline:
        1) Follows a sequence of instructions (serial workflow).
        2) It may pass data or other arguments to the next step in the sequence.
        3) Only one connection or path exists between each object.
        4) It repeats the number of times set in the 'iterations' attribute.
            If 'iteratations' is 'infinite', the loop will repeat until stopped
            by a condition set in 'criteria'.
        
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
            Defaults to 10.
        criteria (str): after iteration is complete, a 'criteria' determines
            what should be outputted. This should correspond to a key in the
            'algorithms' Catalog for the sourdough project. Defaults to None.
        parallel (ClassVar[bool]): whether the 'contents' contain other 
            iterables (True) or static objects (False). If True, a subclass
            should include a custom iterable for navigating the stored 
            iterables. Defaults to False.
                            
    """
    contents: Sequence[sourdough.Component] = dataclasses.field(
        default_factory = list)
    name: str = None
    iterations: Union[int, str] = 10
    criteria: str = None
    parallel: ClassVar[bool] = False 

    """ Public Methods """
    
    def apply(self, project: sourdough.Project, **kwargs) -> sourdough.Project:
        """[summary]

        Args:
            project (sourdough.Project): [description]

        Returns:
            sourdough.Project: [description]
            
        """
        if 'data' not in kwargs and project.data:
            kwargs['data'] = project.data
        for i in self.iterations:
            project = super().apply(project = project, **kwargs)
        return project   


@dataclasses.dataclass
class Pipeline(SerialFlow):
    """Ordered sourdough Components without branching.

    Distinguishing characteristics of a Pipeline:
        1) Follows a sequence of instructions (serial workflow).
        2) It may pass data or other arguments to the next step in the sequence.
        3) Only one connection or path exists between each object. There is no
            branching or looping.
        
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
            'algorithms' Catalog for the sourdough project. Defaults to None.
        parallel (ClassVar[bool]): whether the 'contents' contain other 
            iterables (True) or static objects (False). If True, a subclass
            should include a custom iterable for navigating the stored 
            iterables. Defaults to False.
                            
    """
    contents: Sequence[sourdough.Component] = dataclasses.field(
        default_factory = list)
    name: str = None
    iterations: Union[int, str] = 1
    criteria: str = None
    parallel: ClassVar[bool] = False 


@dataclasses.dataclass
class ParallelFlow(sourdough.products.Workflow, abc.ABC):
    """Base class for parallelly workflowd Flows in sourdough projects.
        
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
            'algorithms' Catalog for the sourdough project. Defaults to None.
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
          
    """ Public Methods """

    def apply(self, project: sourdough.Project, **kwargs) -> sourdough.Project:
        """[summary]

        Args:
            project (sourdough.Project): [description]

        Returns:
            sourdough.Project: [description]
            
        """
        if hasattr(project, 'parallelize') and project.parallelize:
            multiprocessing.set_start_method('spawn')
            with multiprocessing.Pool() as pool:
                components = zip(self.contents)
                all_projects = pool.starmap(super().apply, components)
            # queue = multiprocessing.Queue()
            # process = multiprocessing.Process(target = project, args = (queue,))
            # process.start()
            # process.join()
            return all_projects
        else:
            return super().apply(project = project, **kwargs)


@dataclasses.dataclass
class Contest(ParallelFlow):
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
            'algorithms' Catalog for the sourdough project. Defaults to None.
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
class Study(ParallelFlow):
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
            'algorithms' Catalog for the sourdough project. Defaults to None.
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
class Survey(ParallelFlow):
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
            'algorithms' Catalog for the sourdough project. Defaults to None.
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
