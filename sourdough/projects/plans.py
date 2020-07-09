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
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union

import sourdough


@dataclasses.dataclass
class Plan(sourdough.OptionsMixin, sourdough.Progression):
    """Base class for iterables storing Worker instances.

    Args:
        contents (Sequence[sourdough.Worker]]): stored iterable of 
            actions to apply in order. Defaults to an empty list.
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
        options (ClassVar['sourdough.Catalog']): a sourdough dictionary of 
            available Worker instances available to use.
            
    """
    contents: Union[
        Sequence['sourdough.Worker'], 
        str] = dataclasses.field(default_factory = list)
    name: str = None
    options: ClassVar['sourdough.Catalog'] = sourdough.Catalog(
        always_return_list = True)

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        super().__post_init__()
        # Converts str in 'contents' to classes or objects.
        self.contents = [self.add(c) for c in self.contents]

    """ Public Methods """
    
    def apply(self, data: object = None) -> object:
        """Applies stored Worker instances to 'data'.

        Args:
            data (object): an object to be modified and/or analyzed by stored 
                Worker instances. Defaults to None.

        Returns:
            object: data, possibly with modifications made by Operataor 
                instances.
            If data is not passed, no object is returned.
            
        """
        if data is None:
            for operator in self.__iter__():
                operator.apply()
            return self
        else:
            for operator in self.__iter__():
                data = operator.apply(data = data)
            return data
        
        
@dataclasses.dataclass
class PlaceHolder(sourdough.base.Plan):
    """Contains information and objects that are part of sourdough projects.
    
    Args:
        contents (Sequence[Union[PlaceHolder, sourdough.Task, str]]]): stored 
            PlaceHolder or Task instances or strings corresponding to keys in 
            'options'. Defaults to an empty list.  
        name (str): designates the name of the class instance used
            for internal referencing throughout sourdough. For example if a 
            class instance needs settings from the shared Settings instance, 
            'name' should match the appropriate section name in that Settings 
            instance. When subclassing, it is sometimes a good idea to use the 
            same 'name' attribute as the base class for effective coordination 
            between sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Component is called, 'name' is set to a snake 
            case version of the class name ('__class__.__name__').
        design (str): the name of the structural design that should
            be used to create objects in an instance. This should correspond
            to a key in a Manager instance's 'designs' class attribute. 
            Defaults to 'chained'.
        options (ClassVar['sourdough.Catalog']): an instance to store possible
            PlaceHolder and Task classes for use in the Project. Defaults to an
            empty Catalog instance.
            
    """
    contents: Sequence[Union[
        'PlaceHolder', 
        'sourdough.Task', 
        str]] = dataclasses.field(default_factory = list)  
    name: str = None  
    design: str = dataclasses.field(default_factory = lambda: 'chained')
    options: ClassVar['sourdough.Catalog'] = sourdough.Catalog()

    """ Class Methods """
    
    @classmethod
    def add_option(cls, 
            name: str, 
            option: Union['PlaceHolder', 'sourdough.Task']) -> None:
        """Adds a PlaceHolder or Task to 'options'.

        Args:
            name (str): key to use for storing 'option'.
            option (PlaceHolder, sourdough.Task): the subclass to store in the 
                'options' class attribute.

        Raises:
            TypeError: if 'option' is not a PlaceHolder or Task type.
            
        """
        if issubclass(option, (PlaceHolder, sourdough.Task)):
            cls.options[name] = option
        elif isinstance(option, (PlaceHolder, sourdough.Task)):
            cls.options[name] = option.__class__
        else:
            raise TypeError('option must be a PlaceHolder or Task type')
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
    def workers(self) -> Sequence['sourdough.PlaceHolder']:
        """
        """
        return [
            isinstance(i, 'sourdough.PlaceHolder') for i in self._get_flattened()]
    
    """ Private Methods """

    def _get_flattened(self) -> Sequence[Union[
            'sourdough.PlaceHolder', 
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
class Project(PlaceHolder):
    """Basic sourdough project container.
    
    Subclasses can easily expand upon the basic design and functionality of this
    class. Or, if the underlying structure is acceptable, you can simply add to
    the 'options' class attribute. This can be done manually or with the 
    'add_option' method inherited from PlaceHolder.

    Args:
        name (str): designates the name of the class instance used
            for internal referencing throughout sourdough. If the class instance
            needs settings from the shared Settings instance, 'name' should
            match the appropriate section name in that Settings instance. When
            subclassing, it is a good settings to use the same 'name' attribute
            as the base class for effective coordination between sourdough
            classes. Defaults to None or __class__.__name__.lower().
        contents (Sequence[Union[sourdough.PlaceHolder, sourdough.Task, str]]]): 
            stored PlaceHolder or Task instances or strings corresponding to keys in
            'options'. Defaults to an empty list.  
        design (str): the name of the structural design that should
            be used to create objects in an instance. This should correspond
            to a key in a Manager instance's 'designs' class attribute. 
            Defaults to 'chained'.
        identification (str): a unique identification name for a 
            Project instance. The name is used for creating file folders
            related to the 'Project'. If not provided, a string is created from
            'name' and the date and time. This is a notable difference
            between an ordinary PlaceHolder instancce and a Project instance. Other
            PlaceHolders are not given unique identification. Defaults to None.    
        data (Any]): a data object to apply any constructed objects to.
            This need only be provided when the class is instanced for
            automatic execution. Defaults to None. If you are working on a data-
            focused Project, consider using siMpLify instead 
            (https://github.com/WithPrecedent/simplify). It applies sourdough
            in the data science context. sourdough itself treats 'data' as an
            unknown object of any type which offers more flexibility of design.
        options (ClassVar['sourdough.Catalog']): an instance to store possible
            PlaceHolder and Task classes for use in the Project. Defaults to an
            empty Catalog instance.
                             
    """  
    name: str = None
    contents: Sequence[Union[
        'sourdough.PlaceHolder', 
        'sourdough.Task', 
        str]] = dataclasses.field(default_factory = list) 
    design: str = dataclasses.field(default_factory = lambda: 'chained')
    data: Any = None
    identification: str = None
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
