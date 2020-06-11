"""
.. module:: worker
:synopsis: sourdough project workers
:publisher: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import abc
import dataclasses
import copy
import inspect
import itertools
import more_itertools
from typing import Any, ClassVar, Iterable, Mapping, Sequence, Tuple, Union

import sourdough


@dataclasses.dataclass
class Worker(sourdough.base.Plan):
    """Contains information and objects that are part of sourdough projects.
    
    Args:
        contents (Optional[Sequence[Union[Worker, sourdough.Task, str]]]): stored 
            Worker or Task instances or strings corresponding to keys in 
            'options'. Defaults to an empty list.  
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. For example if a 
            class instance needs settings from the shared Settings instance, 
            'name' should match the appropriate section name in that Settings 
            instance. When subclassing, it is sometimes a good idea to use the 
            same 'name' attribute as the base class for effective coordination 
            between sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Component is called, 'name' is set to a snake 
            case version of the class name ('__class__.__name__').
        design (Optional[str]): the name of the structural design that should
            be used to create objects in an instance. This should correspond
            to a key in a Manager instance's 'designs' class attribute. 
            Defaults to 'chained'.
        options (ClassVar['sourdough.Catalog']): an instance to store possible
            Worker and Task classes for use in the Project. Defaults to an
            empty Catalog instance.
            
    """
    contents: Optional[Sequence[Union[
        'Worker', 
        'sourdough.Task', 
        str]]] = dataclasses.field(default_factory = list)  
    name: str = None  
    design: Optional[str] = dataclasses.field(
        default_factory = lambda: 'chained')
    options: ClassVar['sourdough.Catalog'] = sourdough.Catalog()

    """ Class Methods """
    
    @classmethod
    def add_option(cls, 
            name: str, 
            option: Union['Worker', 'sourdough.Task']) -> None:
        """Adds a Worker or Task to 'options'.

        Args:
            name (str): key to use for storing 'option'.
            option (Worker, sourdough.Task): the subclass to store in the 
                'options' class attribute.

        Raises:
            TypeError: if 'option' is not a Worker or Task type.
            
        """
        if issubclass(option, (Worker, sourdough.Task)):
            cls.options[name] = option
        elif isinstance(option, (Worker, sourdough.Task)):
            cls.options[name] = option.__class__
        else:
            raise TypeError('option must be a Worker or Task type')
        return cls  
             
    """ Properties """
    
    @property
    def overview(self) -> 'Overview':
        """Returns string snapshot of a Plan subclass instance.
        
        Returns:
            Overview: configured according to the '_get_overview' method.
        
        """
        return self._get_overview() 
    
    @property
    def tasks(self) -> Sequence['sourdough.Task']:
        """[summary]

        Returns:
            [type]: [description]
        """
        return [isinstance(i, 'sourdough.Task') for i in self._get_flattened()]
    
    @property    
    def techniques(self) -> Sequence['sourdough.Technique']:
        """[summary]

        Returns:
            [type]: [description]
        """
        return [
            isinstance(i, 'sourdough.Technique') for i in self._get_flattened()]
    
    @property    
    def workers(self) -> Sequence['sourdough.Worker']:
        """
        """
        return [
            isinstance(i, 'sourdough.Worker') for i in self._get_flattened()]
    
    """ Private Methods """

    def _get_flattened(self) -> Sequence[Union[
            'sourdough.Worker', 
            'sourdough.Task', 
            'sourdough.Technique']]:
        return more_itertools.collapse(self.contents)
        
    def _get_overview(self) -> Mapping[str, Sequence[str]]:
        """
        """
        overview = {}
        overview['workers'] = [w.name for w in self.workers]
        overivew['tasks'] = [t.name for t in self.tasks]
        overview['techniques'] = [t.name for t in self.techniques]
        return overview

    
@dataclasses.dataclass
class Project(Worker):
    """Basic sourdough project container.
    
    Subclasses can easily expand upon the basic design and functionality of this
    class. Or, if the underlying structure is acceptable, you can simply add to
    the 'options' class attribute. This can be done manually or with the 
    'add_option' method inherited from Worker.

    Args:
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. If the class instance
            needs settings from the shared Settings instance, 'name' should
            match the appropriate section name in that Settings instance. When
            subclassing, it is a good settings to use the same 'name' attribute
            as the base class for effective coordination between sourdough
            classes. Defaults to None or __class__.__name__.lower().
        contents (Optional[Sequence[Union[sourdough.Worker, sourdough.Task, str]]]): 
            stored Worker or Task instances or strings corresponding to keys in
            'options'. Defaults to an empty list.  
        design (Optional[str]): the name of the structural design that should
            be used to create objects in an instance. This should correspond
            to a key in a Manager instance's 'designs' class attribute. 
            Defaults to 'chained'.
        identification (Optional[str]): a unique identification name for a 
            Project instance. The name is used for creating file folders
            related to the 'Project'. If not provided, a string is created from
            'name' and the date and time. This is a notable difference
            between an ordinary Worker instancce and a Project instance. Other
            Workers are not given unique identification. Defaults to None.    
        data (Optional[Any]): a data object to apply any constructed objects to.
            This need only be provided when the class is instanced for
            automatic execution. Defaults to None. If you are working on a data-
            focused Project, consider using siMpLify instead 
            (https://github.com/WithPrecedent/simplify). It applies sourdough
            in the data science context. sourdough itself treats 'data' as an
            unknown object of any type which offers more flexibility of design.
        options (ClassVar['sourdough.Catalog']): an instance to store possible
            Worker and Task classes for use in the Project. Defaults to an
            empty Catalog instance.
                             
    """  
    name: str = None
    contents: Optional[Sequence[Union[
        'sourdough.Worker', 
        'sourdough.Task', 
        str]]] = dataclasses.field(default_factory = list) 
    design: Optional[str] = dataclasses.field(
        default_factory = lambda: 'chained')
    data: Optional[Any] = None
    identification: Optional[str] = None
    options: ClassVar['sourdough.Catalog'] = sourdough.Catalog()

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls inherited initialization method.
        super().__post_init__()
        # Creates unique 'identification' based upon date and time if none 
        # exists.
        self.identification = (
            self.identification or sourdough.tools.datetime_string(
                prefix = self.name))
