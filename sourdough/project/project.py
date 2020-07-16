"""
.. module: project
:synopsis: sourdough Project and related classes
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
class Technique(sourdough.base.Task):
    """Base class for creating or modifying data objects.

    Args:
        algorithm (object): core object used by the 'apply' method. Defaults to 
            None.
        parameters (Mapping[str, Any]]): parameters to be attached to
            'algorithm' when the 'apply' method is called. Defaults to an empty
            dict.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough.base. For example if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Component is called, 'name' is set based upon
            the 'get_name' method in Component. If that method is not 
            overridden by a subclass instance, 'name' will be assigned to the 
            snake case version of the class name ('__class__.__name__').
            
    """
    algorithm: object = None
    parameters: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    name: str = None
    
    """ Public Methods """
    
    def apply(self, data: object = None, **kwargs) -> object:
        """Applies stored 'algorithm' with 'parameters'.
        
        Args:
            data (object): optional object to apply 'algorithm' to. Defaults to
                None.
                
        Returns:
            object: with any modifications made by 'algorithm'. If data is not
                passed, nothing is returned.        
        
        
        """
        if data is None:
            self.algorithm(**parameters, **kwargs)
            return self
        else:
            return self.algorithm(data, **parameters, **kwargs)
        
    """ Dunder Methods """

    def __repr__(self) -> str:
        """Returns string representation of a class instance."""
        return self.__str__()

    def __str__(self) -> str:
        """Returns string representation of a class instance."""
        return (
            f'sourdough {self.__class__.__name__} {self.name}\n'
            f'algorithm: {str(self.algorithm)}\n'
            f'parameters: {str(self.parameters)}\n')
        
            
@dataclasses.dataclass
class Step(sourdough.base.Task):
    """Base class for wrapping a Technique.

    A Step is a basic wrapper for a Technique that adds a 'name' for the
    'plan' that a stored technique instance is associated with. Subclasses of
    Step can store additional methods and attributes to apply to all possible
    technique instances that could be used. This is often useful when creating
    'comparative' Plan instances which test a variety of strategies with
    similar or identical parameters and/or methods.

    A Plan instance will try to return attributes from 'technique' if the
    attribute is not found in the Plan instance. 

    Args:
        plan (str): the name of the plan in a Plan instance that 
            the algorithm is being performed. This attribute is generally 
            optional but can be useful for tracking and/or displaying the status 
            of iteration. It is automatically created when using a chained or 
            comparative Plan. Defaults to None.
        technique (technique): technique object for this plan in a sourdough
            sequence. Defaults to None.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough.base. For example if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Component is called, 'name' is set based upon
            the 'get_name' method in Component. If that method is not 
            overridden by a subclass instance, 'name' will be assigned to the 
            snake case version of the class name ('__class__.__name__').
            
    """
    # plan: str = dataclasses.field(default_factory = lambda: '')
    technique: Union[Technique, str] = None
    name: str = None

    """ Public Methods """
    
    def apply(self, data: object = None, **kwargs) -> object:
        """Applies stored 'algorithm' with 'parameters'.
        
        Args:
            data (object): optional object to apply 'algorithm' to. Defaults to
                None.
                
        Returns:
            object: with any modifications made by 'algorithm'. If data is not
                passed, nothing is returned.        
        
        
        """
        if data is None:
            self.technique(data = data, **kwargs)
            return self
        else:
            return self.technique(data = data, **kwargs)

    """ Dunder Methods """

    def __getattr__(self, attribute: str) -> Any:
        """Looks for 'attribute' in 'technique'.

        Args:
            attribute (str): name of attribute to return.

        Returns:
            Any: matching attribute.

        Raises:
            AttributeError: if 'attribute' is not found in 'technique'.

        """
        try:
            return getattr(self.technique, attribute)
        except AttributeError:
            raise AttributeError(
                f'{attribute} neither found in {self.name} nor \
                    {self.technique}')

    def __repr__(self) -> str:
        """Returns string representation of a class instance."""
        return self.__str__()

    def __str__(self) -> str:
        """Returns string representation of a class instance."""
        return (
            f'sourdough {self.__class__.__name__} {self.name}\n'
            # f'plan: {self.plan.name}\n'
            f'technique: {str(self.technique)}\n')


@dataclasses.dataclass
class Plan(sourdough.base.Task, sourdough.base.Progression):
    """Base class for iterables storing Task and other Plan subclass instances.

    Plan inherits all of the differences between a Progression and a python 
    list.
    
    A Plan differs from a Progression in 3 significant ways:
        1) It has a 'design' attribute which indicates how the contained 
            iterable should be ordered. 
        2)
        
    Args:
        contents (Sequence[Task]]): stored iterable of actions to apply in 
            order. Defaults to an empty list.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough.base. For example if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Component is called, 'name' is set based upon
            the 'get_name' method in Component. If that method is not 
            overridden by a subclass instance, 'name' will be assigned to the 
            snake case version of the class name ('__class__.__name__').
        options (ClassVar['sourdough.base.Catalog']): a sourdough dictionary of 
            available Task instances available to use.
        design (str): the name of the structural design that should be used to 
            create objects in an instance. This should correspond to a key in a 
            Manager instance's 'designs' class attribute. Defaults to 'chained'.
            
    """
    contents: Union[
        Sequence['Task'], 
        str] = dataclasses.field(default_factory = list)
    name: str = None
    options: ClassVar['sourdough.base.Catalog'] = sourdough.base.Catalog(
        always_return_list = True)
    design: str = dataclasses.field(default_factory = lambda: 'chained')

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        super().__post_init__()
        # Converts str in 'contents' to objects.
        self.contents = self.validate(contents = self.contents)

    """ Public Methods """
    
    def validate(self, 
            contents: Union[Sequence['Task'], str] ) -> Sequence[
                'Task']:
        """[summary]

        Returns:
            [type]: [description]
            
        """
        new_contents = []
        for step in contents:
            if isinstance(step, str):
                try:
                    new_contents.append[self.options[step]]
                except KeyError:
                    new_contents.append[step]
            else:
                new_contents.append[step]
        return new_contents
        
    def apply(self, data: object = None) -> object:
        """Applies stored Task instances to 'data'.

        Args:
            data (object): an object to be modified and/or analyzed by stored 
                Task instances. Defaults to None.

        Returns:
            object: data, possibly with modifications made by Operataor 
                instances. If data is not passed, no object is returned.
            
        """
        if data is None:
            for operator in self.__iter__():
                operator.apply()
            return self
        else:
            for operator in self.__iter__():
                data = operator.apply(data = data)
            return data
             
    """ Properties """
    
    @property
    def overview(self) -> 'Overview':
        """Returns a string snapshot of a Plan subclass instance.
        
        Returns:
            Overview: configured according to the '_get_overview' method.
        
        """
        return self._get_overview() 

    @property    
    def plans(self) -> Sequence['Plan']:
        """
        """
        return [isinstance(i, Plan) for i in self._get_flattened()]
 
    @property
    def steps(self) -> Sequence['Step']:
        """[summary]

        Returns:
            [type]: [description]
        """
        return [isinstance(i, Step) for i in self._get_flattened()]
    
    @property    
    def techniques(self) -> Sequence['Technique']:
        """[summary]

        Returns:
            [type]: [description]
        """
        return [isinstance(i, Technique) for i in self._get_flattened()]
    
    """ Private Methods """
    
    def _get_flattened(self) -> Sequence[Union[
            'sourdough.project.Plan', 
            'sourdough.base.Step', 
            'sourdough.base.Technique']]:
        return more_itertools.collapse(self.contents)
        
    def _get_overview(self) -> Mapping[str, Sequence[str]]:
        """
        """
        overview = {}
        overview['plans'] = [p.name for p in self.plans]
        overivew['steps'] = [t.name for t in self.steps]
        overview['techniques'] = [t.name for t in self.techniques]
        return overview

    
@dataclasses.dataclass
class Project(Plan):
    """Top-level sourdough project iterable.
    
    Subclasses can easily expand upon the basic design and functionality of this
    class. Or, if the underlying structure is acceptable, you can simply add to
    the 'options' class attribute. This can be done manually or with the 
    'add_option' method inherited from Plan.

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough.base. For example if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Component is called, 'name' is set based upon
            the 'get_name' method in Component. If that method is not 
            overridden by a subclass instance, 'name' will be assigned to the 
            snake case version of the class name ('__class__.__name__').
        contents (Sequence[Union[sourdough.project.Plan, sourdough.base.Step, str]]]): 
            stored Plan or Step instances or strings corresponding to keys in
            'options'. Defaults to an empty list.  
        design (str): the name of the structural design that should
            be used to create objects in an instance. This should correspond
            to a key in a Manager instance's 'designs' class attribute. 
            Defaults to 'chained'.
        identification (str): a unique identification name for a 
            Project instance. The name is used for creating file folders
            related to the 'Project'. If not provided, a string is created from
            'name' and the date and time. This is a notable difference
            between an ordinary Plan instancce and a Project instance. Other
            Plans are not given unique identification. Defaults to None.    
        data (Any]): a data object to apply any constructed objects to.
            This need only be provided when the class is instanced for
            automatic execution. Defaults to None. If you are working on a data-
            focused Project, consider using siMpLify instead 
            (https://github.com/WithPrecedent/simplify). It applies sourdough
            in the data science context. sourdough itself treats 'data' as an
            unknown object of any type which offers more flexibility of design.
        options (ClassVar['sourdough.base.Catalog']): an instance to store possible
            Plan and Step classes for use in the Project. Defaults to an
            empty Catalog instance.
                             
    """  
    name: str = None
    contents: Sequence[Union[
        'sourdough.project.Plan', 
        'sourdough.base.Step', 
        str]] = dataclasses.field(default_factory = list) 
    design: str = dataclasses.field(default_factory = lambda: 'chained')
    data: Any = None
    identification: str = None
    options: ClassVar['sourdough.base.Catalog'] = sourdough.base.Catalog()

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls inherited initialization method.
        super().__post_init__()
        # Creates unique 'identification' based upon date and time if none 
        # exists.
        self.identification = (
            self.identification or sourdough.utilities.datetime_string(
                prefix = self.name))
