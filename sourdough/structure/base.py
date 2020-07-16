"""
.. module:: base
:synopsis: sourdough base classes
:author: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import abc
import collections.abc
import dataclasses
import inspect
import more_itertools
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union

import sourdough


@dataclasses.dataclass
class Component(abc.ABC):
    """Base class for core sourdough objects.

    A Component has a 'name' attribute for internal referencing and to allow 
    sourdough iterables to function propertly. Component instances can be used 
    to create a variety of composite data structures such as trees and graphs. 

    The mixins included with sourdough are all compatible, individually and
    collectively, with Component.

    Args:
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
    
    """
    name: str = None

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Sets 'name' to the default value if it is not passed.
        self.name: str = self.name or self.get_name()

    """ Class Methods """

    @classmethod
    def get_name(cls) -> str:
        """Returns 'name' of class for use throughout sourdough.
        
        The method is a classmethod so that a 'name' can properly derived even
        before a class is instanced. It can also be called after a subclass is
        instanced (as is the case in '__post_init__').
        
        This method converts the class name from CapitalCase to snake_case.
        
        If a user wishes to use an alternate naming system, a subclass should
        simply override this method. 
        
        Returns:
            str: name of class for internal referencing and some access methods.
        
        """
        try:
            return cls.name
        except AttributeError:
            if inspect.isclass(cls):
                return sourdough.tools.snakify(cls.__name__)
            else:
                return sourdough.tools.snakify(cls.__class__.__name__)


@dataclasses.dataclass
class Task(Component, abc.ABC):
    """Base class for applying stored methods to passed data.
    
    Task subclass instances are often arranged in an ordered sequence such as a
    Progression instance. All Task subclasses must have 'apply' methods for 
    handling data. 
    
    Args:
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
    
    """
    name: str = None
    
    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def apply(self, data: object = None, **kwargs) -> object:
        """Subclasses must provide their own methods."""
        pass

 
@dataclasses.dataclass
class Creator(Component, abc.ABC):
    """Base class for stages of creation of sourdough objects.
    
    All subclasses must have 'create' methods. 
    
    Args:
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
    
    """
    name: str = None
    
    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def create(self, component: 'Component' = None, **kwargs) -> 'Component':
        """Constructs or modifies a Component instance.
        
        Subclasses must provide their own methods.
        
        """
        pass
    

@dataclasses.dataclass
class Anthology(abc.ABC):
    """Base class for sourdough iterables.
    
    All Anthology subclasses must include 'validate' and 'add' methods. 
    Requirements for those methods are described in the respective 
    abstractmethods.
    
    Args:
        contents (Iterable): stored iterable. Defaults to None.
              
    """
    contents: Iterable = None 

    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Validates 'contents' or converts it to appropriate iterable.
        self.contents = self.validate(contents = self.contents)
        
    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def validate(self, contents: Any, **kwargs) -> Iterable:
        """Validates 'contents' or converts 'contents' to proper type.
        
        Subclasses must provide their own methods.
        
        The 'contents' argument should accept any supported datatype and either
        validate its type or convert it to an iterable. This method is used to 
        validate or convert both the passed 'contents' and by the 'add' method
        to add new keys and values to the 'contents' attribute.
        
        """
        pass
    
    @abc.abstractmethod
    def add(self, contents: Any, **kwargs) -> None:
        """Adds 'contents' to the 'contents' attribute.
        
        Subclasses must provide their own methods.
        
        This method should first call 'validate' to convert or 'validate' the
        passed argument. It should then use the appropraite default mechanism
        for adding 'contents' argument to the 'contents' attribute.
        
        """
        contents = self.validate(contents = contents)
        # Subclasses should add code for incorporating 'contents' argument here.
        return self  
    
    """ Dunder Methods """
    
    def __iter__(self) -> Iterable:
        """Returns iterable of 'contents'.

        Returns:
            Iterable: of 'contents'.

        """
        return iter(self.contents)

    def __len__(self) -> int:
        """Returns length of 'contents'.

        Returns:
            int: length of 'contents'.

        """
        return len(self.contents)

    def __add__(self, other: Any) -> None:
        """Combines argument with 'contents'.

        Args:
            other (Any): item to add to 'contents' using the 'add' method.

        """
        self.add(other)
        return self

    def __repr__(self) -> str:
        """Returns '__str__' representation.

        Returns:
            str: default string representation of an instance.

        """
        return self.__str__()
    
    def __str__(self) -> str:
        """Returns default string representation of an instance.

        Returns:
            str: default string representation of an instance.

        """
        return (
            f'sourdough {self.__class__.__name__}\n'
            f'contents: {self.contents.__str__()}')     


@dataclasses.dataclass
class Lexicon(collections.abc.MutableMapping, Anthology):
    """Basic sourdough dict replacement.

    Lexicon subclasses can serve as drop in replacements for dicts with added
    features.
    
    A Lexicon differs from a python dict in 4 significant ways:
        1) It includes an 'add' method which allows different datatypes to
            be passed and added to a Lexicon instance. All of the normal dict 
            methods are also available. 'add' should be used to set default or 
            more complex methods of adding elements to the stored dict.
        2) It uses a 'validate' method to validate or convert all passed 
            'contents' arguments. It will convert all supported datatypes to 
            a dict. The 'validate' method is automatically called when a
            Lexicon is instanced and when the 'add' method is called.
        3) It includes a 'subsetify' method which will return a Lexicon or
            Lexicon subclass instance with only the key/value pairs matching
            keys in the 'subset' parameter.
        4) It allows the '+' operator to be used to join a Lexicon instance
            with another Lexicon instance, a dict, or a Component. The '+' 
            operator calls the Lexicon 'add' method to implement how the added 
            item(s) is/are added to the Lexicon instance.
    
    All Lexicon subclasses must include a 'validate' method. Requirements for
    that method are described in the abstractmethod itself.
    
    Args:
        contents (Mapping[str, Any]]): stored dictionary. Defaults to an empty 
            dict.
              
    """
    contents: Mapping[str, Any] = dataclasses.field(default_factory = dict)
        
    """ Public Methods """
    
    def validate(self, contents: Any) -> Mapping[Any, Any]:
        """Validates 'contents' or converts 'contents' to proper type.
        
        This method simply confirms that 'contents' is a Mapping. Subclasses
        should overwrite this method to support more datatypes and implement
        any type conversion techniques that are necessary.
        
        Args:
            contents (Any): variable to validate as compatible with an instance.
            
        Raises:
            TypeError: if 'contents' argument is not of a supported datatype.
            
        Returns:
            Mapping[Any, Any]: validated or converted argument that is 
                compatible with an instance.
        
        """
        if not isinstance(contents, Mapping):
            raise TypeError('contents must be a dict type')
        else:
            return contents
     
    def add(self, contents: Any) -> None:
        """Adds 'contents' to the 'contents' attribute.
        
        Args:
            component (Union[Component, 
                Sequence[Component], Mapping[str, 
                Component]]): Component(s) to add to
                'contents'. If 'component' is a Sequence or a Component, the 
                key for storing 'component' is the 'name' attribute of each 
                Component.

        """
        contents = self.validate(contents = contents)
        self.contents.update(contents)
        return self
                
    def subsetify(self, 
            subset: Union[str, Sequence[str]], 
            **kwargs) -> 'Lexicon':
        """Returns a new instance with a subset of 'contents'.

        Args:
            subset (Union[str, Sequence[str]]): key(s) for which key/value pairs 
                from 'contents' should be returned.
            kwargs: allows subclasses to send additional parameters to this 
                method.

        Returns:
            Lexicon: with only keys in 'subset'.

        """
        subset = sourdough.tools.listify(subset)
        return self.__class__(
            contents = {k: self.contents[k] for k in subset},
            **kwargs)

    """ Dunder Methods """

    def __getitem__(self, key: str) -> Any:
        """Returns value for 'key' in 'contents'.

        Args:
            key (str): name of key in 'contents' for which a value is sought.

        Returns:
            Any: value stored in 'contents'.

        """
        return self.contents[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Sets 'key' in 'contents' to 'value'.

        Args:
            key (str): name of key to set in 'contents'.
            value (Any): value to be paired with 'key' in 'contents'.

        """
        self.contents[key] = value
        return self

    def __delitem__(self, key: str) -> None:
        """Deletes 'key' in 'contents'.

        Args:
            key (str): name of key in 'contents' to delete the key/value pair.

        """
        del self.contents[key]
        return self


@dataclasses.dataclass
class Corpus(sourdough.Lexicon):
    """sourdough two-level nested dict replacement.
    
    Corpus inherits all of the differences between a Lexicon and a python dict.

    A Corpus differs from a Lexicon in 3 significant ways:
        1) Its 'add' method requirements 2 arguments ('section' and 'contents') 
            due to the 2-level nature of the stored dict.
        2) It does not return an error if you attempt to delete a key that is
            not stored within 'contents'.
        3) If you try to find a key that does not correspond to a section in 
            'contents', a Corpus subclass instance will return the first 
            matching key within a section (iterated in stored order), if a
            match exists.
    
    The Corups 'add' method accounts for whether the 'section' passed already
    exists and adds the passed 'contents' appropriately.
    
    Args:
        contents (Mapping[str, Any]]): stored dictionary. Defaults to an empty 
            dict.
              
    """
    contents: Mapping[str, Mapping[str, Any]] = dataclasses.field(
        default_factory = dict)

    """ Public Methods """

    def add(self, 
            section: str, 
            contents: Mapping[str, Any]) -> None:
        """Adds 'settings' to 'contents'.

        Args:
            section (str): name of section to add 'contents' to.
            contents (Mapping[str, Any]): a dict to store in 'section'.

        """
        try:
            self[section].update(self._validate(contents = contents))
        except KeyError:
            self[section] = self._validate(contents = contents)
        return self
    
    """ Dunder Methods """

    def __getitem__(self, key: str) -> Union[Mapping[str, Any], Any]:
        """Returns a section of the active dictionary or key within a section.

        Args:
            key (str): the name of the dictionary key for which the value is
                sought.

        Returns:
            Union[Mapping[str, Any], Any]: dict if 'key' matches a section in
                the active dictionary. If 'key' matches a key within a section,
                the value, which can be any of the supported datatypes is
                returned.

        """
        try:
            return self.contents[key]
        except KeyError:
            for section in list(self.contents.keys()):
                try:
                    return self.contents[section][key]
                except KeyError:
                    pass
            raise KeyError(f'{key} is not found in {self.__class__.__name__}')

    def __setitem__(self, key: str, value: Mapping[str, Any]) -> None:
        """Creates new key/value pair(s) in a section of the active dictionary.

        Args:
            key (str): name of a section in the active dictionary.
            value (MutableMapping): the dictionary to be placed in that section.

        Raises:
            TypeError if 'key' isn't a str or 'value' isn't a dict.

        """
        try:
            self.contents[key].update(value)
        except KeyError:
            try:
                self.contents[key] = value
            except TypeError:
                raise TypeError(
                    'key must be a str and value must be a dict type')
        return self

    def __delitem__(self, key: str) -> None:
        """Deletes 'key' entry in 'contents'.

        Args:
            key (str): name of key in 'contents'.

        """
        try:
            del self.contents[key]
        except KeyError:
            pass
        return self

        
@dataclasses.dataclass
class Progression(collections.abc.MutableSequence, Component, Anthology):
    """Base class for sourdough sequenced iterables.
    
    A Progression differs from a python list in 6 significant ways:
        1) It includes a 'name' attribute which is used for internal referencing
            in sourdough. This is inherited from Component.
        2) It includes an 'add' method which allows different datatypes to
            be passed and added to the 'contents' of a Progression instance.
        3) It only stores items that have a 'name' attribute or are str type.
        4) It includes a 'subsetify' method which will return a Progression or
            Progression subclass instance with only the items with 'name'
            attributes matching items in the 'subset' argument.
        5) Progression has an interface of both a dict and a list, but stores a 
            list. Progression does this by taking advantage of the 'name' 
            attribute in Component instances (although any instance with a 
            'name' attribute is compatiable with a Progression). A 'name' acts 
            as a key to create the facade of a dictionary with the items in the 
            stored list serving as values. This allows for duplicate keys for 
            storing class instances, easier iteration, and returning multiple 
            matching items. This design comes at the expense of lookup speed. As 
            a result, Progression should only be used if a high volumne of 
            access calls is not anticipated. Ordinarily, the loss of lookup 
            speed should have negligible effect on overall performance. 
        6) Iterating Progression iterates all contained iterables by using the
            'more_itertools.collapse' method. This orders all stored iterables 
            in a depth-first manner.      

    Args:
        contents (Sequence[Component]]): stored iterable of Component instances.
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

    """
    contents: Sequence['Component'] = dataclasses.field(default_factory = list)
    name: str = None

    """ Public Methods """
    
    def validate(self, 
            contents: Union[
                'Component',
                Mapping[str, 'Component'], 
                Sequence['Component']]) -> Sequence['Component']:
        """Validates 'contents' or converts 'contents' to proper type.
        
        Args:
            contents (Union[Component, Mapping[str, Component], 
                Sequence[Component]]): items to validate or convert to a list of
                Component instances.
            
        Raises:
            TypeError: if 'contents' argument is not of a supported datatype.
            
        Returns:
            Sequence[Component]: validated or converted argument that is 
                compatible with an instance.
        
        """
        if (isinstance(contents, Sequence) 
                and all(isinstance(c, Component) for c in contents)):
            return contents
        elif (isinstance(contents, Mapping)
                and all(isinstance(c, Component) for c in contents.values())):
            return list(contents.values())
        elif isinstance(contents, Component):
            return [contents]
        else:
            raise TypeError('contents must be a list of Components, dict with' 
                            'Component values, or Component type')

    def add(self, 
            contents: Union[
                'Component',
                Mapping[str, 'Component'], 
                Sequence['Component']]) -> None:
        """Appends 'contents' argument to 'contents' attribute.
        
        Args:
            contents (Union[Component, Mapping[str, Component], 
                Sequence[Component]]): Component instance(s) to add to 
                'contents'.

        """
        contents = self.validate(contents = contents)
        self.append(contents = contents)
        return self    

    def append(self, component: 'Component') -> None:
        """Appends 'component' to 'contents'.
        
        Args:
            component (Component): Component instance to add to 
                'contents'.

        Raises:
            TypeError: if 'component' does not have a name attribute.
            
        """
        if hasattr(component, 'name'):
            self.contents.append(component)
        else:
            raise TypeError('component must have a name attribute')
        return self    
   
    def extend(self, component: 'Component') -> None:
        """Extends 'component' to 'contents'.
        
        Args:
            component (Component): Component instance to add to 
                'contents'.

        Raises:
            TypeError: if 'component' does not have a name attribute.
            
        """
        if hasattr(component, 'name'):
            self.contents.extend(component)
        else:
            raise TypeError('component must have a name attribute')
        return self   
    
    def insert(self, index: int, component: 'Component') -> None:
        """Inserts 'component' at 'index' in 'contents'.

        Args:
            index (int): index to insert 'component' at.
            component (Component): object to be inserted.

        Raises:
            TypeError: if 'component' does not have a name attribute.
            
        """
        if hasattr(component, 'name'):
            self.contents.insert[index] = component
        else:
            raise TypeError('component must have a name attribute')
        return self
 
    def subsetify(self, subset: Union[str, Sequence[str]]) -> 'Plan':
        """Returns a subset of 'contents'.

        Args:
            subset (Union[str, Sequence[str]]): key(s) to get Component 
                instances with matching 'name' attributes from 'contents'.

        Returns:
            Plan: with only items with 'name' attributes in 'subset'.

        """
        subset = sourdough.tools.listify(subset)
        return self.__class__(
            name = self.name,
            contents = [c for c in self.contents if c.name in subset])    
     
    def update(self, 
            components: Union[
                Mapping[str, 'Component'], 
                Sequence['Component']]) -> None:
        """Mimics the dict 'update' method by appending 'contents'.
        
        Args:
            components (Union[Mapping[str, Component], Sequence[
                Component]]): Component instances to add to 
                'contents'. If a Mapping is passed, the keys are ignored and
                the values are added to 'contents'. To mimic 'update', the
                passed 'components' are added to 'contents' by the 'extend'
                method.
 
        Raises:
            TypeError: if any of 'components' do not have a name attribute or
                if 'components is not a dict.               
        
        """
        if isinstance(components, Mapping):
            for key, value in components.items():
                if hasattr(value, 'name'):
                    self.append(component = value)
                else:
                    new_component = value
                    new_component.name = key
                    self.extend(component = new_component)
        elif all(hasattr(c, 'name') for c in components):
            for component in components:
                self.append(component = component)
        else:
            raise TypeError(
                'components must be a dict or all have a name attribute')
        return self
          
    """ Dunder Methods """

    def __getitem__(self, key: Union[str, int]) -> 'Component':
        """Returns value(s) for 'key' in 'contents'.
        
        If 'key' is a str type, this method looks for a matching 'name'
        attribute in the stored instances.
        
        If 'key' is an int type, this method returns the stored component at the
        corresponding index.
        
        If only one match is found, a single Component instance is returned. If
        more are found, a Progression or Progression subclass with the matching
        'name' attributes is returned.

        Args:
            key (Union[str, int]): name or index to search for in 'contents'.

        Returns:
            Component: value(s) stored in 'contents' that correspond 
                to 'key'. If there is more than one match, the return is a
                Progression or Progression subclass with that matching stored
                components.

        """
        if isinstance(key, int):
            return self.contents[key]
        else:
            matches = [c for c in self.contents if c.name == key]
            if len(matches) == 1:
                return matches[0]
            else:
                return self.__class__(name = self.name, contents = matches)

    def __setitem__(self, 
            key: Union[str, int], 
            value: 'Component') -> None:
        """Sets 'key' in 'contents' to 'value'.

        Args:
            key (Union[str, int]): if key is a string, it is ignored (since the
                'name' attribute of the value will be acting as the key). In
                such a case, the 'value' is added to the end of 'contents'. If
                key is an int, 'value' is assigned at the that index number in
                'contents'.
            value (Any): value to be paired with 'key' in 'contents'.

        """
        if isinstance(key, int):
            self.contents[key] = value
        else:
            self.contents.add(value)
        return self

    def __delitem__(self, key: Union[str, int]) -> None:
        """Deletes item matching 'key' in 'contents'.

        If 'key' is a str type, this method looks for a matching 'name'
        attribute in the stored instances and deletes all such items. If 'key'
        is an int type, only the item at that index is deleted.

        Args:
            key (Union[str, int]): name or index in 'contents' to delete.

        """
        if isinstance(key, int):
            del self.contents[key]
        else:
            self.contents = [c for c in self.contents if c.name != key]
        return self

    def __iter__(self) -> Iterable:
        """Returns collapsed iterable of 'contents'.
     
        Returns:
            Iterable: using the itertools method which automatically iterates
                all stored iterables within 'contents'.Any
               
        """
        return iter(more_itertools.collapse(self.contents))

    def __len__(self) -> int:
        """Returns length of collapsed 'contents'.

        Returns:
            int: length of collapsed 'contents'.

        """
        return len(more_itertools.collapse(self.contents))

    def __str__(self) -> str:
        """Returns default string representation of an instance.

        Returns:
            str: default string representation of an instance.

        """
        return (
            f'sourdough {self.__class__.__name__}\n'
            f'name: {self.name}\n'
            f'contents: {self.contents.__str__()}') 
