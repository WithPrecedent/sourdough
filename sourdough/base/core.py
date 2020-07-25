"""
core: sourdough core base classes
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Component: abstract base class for composite objects.
    Action (Component): abstract base class for storing action methods. 
        Subclasses must have a 'perform' method.
    Plan (Component): iterable containing Action and Component instances 
        with dict and list interfaces and methods.
    Creator: abstract base class for constructing Action, Component, and
        Plan instances. Subclasses must have a 'create' method.
    Lexicon: sourdough drop-in replacement for dict with additional 
        functionality.
    Catalog (Lexicon): list and wildcard accepting dict replacement.

"""

import abc
import collections.abc
import dataclasses
import inspect
import more_itertools
import textwrap
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union

import sourdough


@dataclasses.dataclass
class Component(abc.ABC):
    """Base class for composite sourdough objects.

    A Component has a 'name' attribute for internal referencing and to allow 
    sourdough iterables to function propertly. Component instances can be used 
    to create a variety of tree data structures such as trees and graphs. 

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
        if hasattr(cls, 'name') and cls.name is not None:
            return cls.name
        elif inspect.isclass(cls):
            return sourdough.utilities.snakify(cls.__name__)
        elif isinstance(cls, sourdough.Component):
            return cls.name
        else:
            return sourdough.utilities.snakify(cls.__class__.__name__)

    """ Dunder Methods """

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
        new_line = '\n'
        representation = [f'sourdough {self.__class__.__name__}']
        for dataclass_field in dataclasses.fields(self):
            name = dataclass_field.name
            attribute = getattr(self, name)
            if (isinstance(attribute, (Sequence, Mapping))
                    and not isinstance(attribute, str)):
                representation.append(
                    f'''{name}:{new_line}{textwrap.indent(
                        str(attribute), '    ')}''')
            else:
                representation.append(f'{name}: {str(attribute)}')
        return new_line.join(representation)        


@dataclasses.dataclass
class Action(Component, abc.ABC):
    """Base class for applying stored methods to passed data.
    
    All Action subclasses must have 'perform' methods. Acceptance and return of 
    a data argument by the 'perform' method is optional.
    
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
    def perform(self, data: object = None, **kwargs) -> object:
        """Subclasses must provide their own methods."""
        pass

        
@dataclasses.dataclass
class Plan(Component, collections.abc.MutableSequence):
    """Base class for sourdough sequenced iterables.
    
    A Plan differs from a python list in 6 significant ways:
        1) It includes a 'name' attribute which is used for internal referencing
            in sourdough. This is inherited from Component.
        2) It includes an 'add' method which allows different datatypes to
            be passed and added to the 'contents' of a Plan instance.
        3) It only stores items that have a 'name' attribute or are str type.
        4) It includes a 'subsetify' method which will return a Plan or
            Plan subclass instance with only the items with 'name'
            attributes matching items in the 'subset' argument.
        5) Plan has an interface of both a dict and a list, but stores a 
            list. Plan does this by taking advantage of the 'name' 
            attribute in Component instances (although any instance with a 
            'name' attribute is compatiable with a Plan). A 'name' acts 
            as a key to create the facade of a dictionary with the items in the 
            stored list serving as values. This allows for duplicate keys for 
            storing class instances, easier iteration, and returning multiple 
            matching items. This design comes at the expense of lookup speed. As 
            a result, Plan should only be used if a high volumne of 
            access calls is not anticipated. Ordinarily, the loss of lookup 
            speed should have negligible effect on overall performance. 
        6) Iterating Plan iterates all contained iterables by using the
            'more_itertools.collapse' method. This orders all stored iterables 
            in a depth-first manner.      

    Args:
        contents (Sequence[Component]]): stored list of Component instances.
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

    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent initialization method(s).
        super().__post_init__()        
        # Validates 'contents' or converts it to appropriate iterable.
        self.contents = self.validate(contents = self.contents)  

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
            and (all(isinstance(c, Component) for c in contents)
                or all(issubclass(c, Component) for c in contents))):
            return contents
        elif (isinstance(contents, Mapping)
            and (all(isinstance(c, Component) for c in contents.values())
                or all(issubclass(c, Component) for c in contents.values()))):
            return list(contents.values())
        elif isinstance(contents, Component):
            return [contents]
        else:
            raise TypeError(
                'contents must be a list of Components, dict with' 
                'Component values, or Component type')

    def add(self, 
            contents: Union[
                'Component',
                Mapping[str, 'Component'], 
                Sequence['Component']]) -> None:
        """Appends 'contents' argument to 'contents' attribute.
        
        Args:
            contents (Union[Component, Mapping[str, Component], 
                Sequence[Component]]): Component instance(s) to add to the
                'contents' attribute.

        """
        contents = self.validate(contents = contents)
        self.append(contents)
        return self    

    def append(self, component: 'Component') -> None:
        """Appends 'component' to 'contents'.
        
        Args:
            component (Component): Component instance to add to 
                'contents'.

        Raises:
            TypeError: if 'component' does not have a name attribute.
            
        """
        if isinstance(component, Component):
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
        if isinstance(component, Component):
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
        if isinstance(component, Component):
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
            Worker: with only items with 'name' attributes in 'subset'.

        """
        subset = sourdough.utilities.listify(subset)
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
        more are found, a Plan or Plan subclass with the matching
        'name' attributes is returned.

        Args:
            key (Union[str, int]): name or index to search for in 'contents'.

        Returns:
            Component: value(s) stored in 'contents' that correspond 
                to 'key'. If there is more than one match, the return is a
                Plan or Plan subclass with that matching stored
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

    def __add__(self, other: Any) -> None:
        """Combines argument with 'contents'.

        Args:
            other (Any): item to add to 'contents' using the 'add' method.

        """
        self.add(other)
        return self
        
 
@dataclasses.dataclass
class Creator(Component, abc.ABC):
    """Base class for stages of creation of sourdough objects.
    
    All subclasses must have 'create' methods. 
    
    Creators often have a 'settings' parameter to acquire information about
    object construction. However, that parameter is not required.
    
    """
    
    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def create(self, component: 'Component' = None, **kwargs) -> 'Component':
        """Constructs or modifies a Component instance.
        
        Subclasses must provide their own methods.
        
        """
        pass


@dataclasses.dataclass
class Lexicon(Component, collections.abc.MutableMapping):
    """Basic sourdough dict replacement.

    Lexicon subclasses can serve as drop in replacements for dicts with added
    features.
    
    A Lexicon differs from a python dict in 4 significant ways:
        1) It includes an 'add' method which allows different datatypes to
            be passed and added to a Lexicon instance. All of the normal dict 
            methods are also available. 'add' should be used to set default or 
            more complex methods of adding elements to the stored dict.
        2) It uses a 'validate' method to validate or convert the passed 
            'contents' argument. It will convert all supported datatypes to 
            a dict. The 'validate' method is automatically called when a
            Lexicon is instanced and when the 'add' method is called.
        3) It includes a 'subsetify' method which will return a Lexicon or
            Lexicon subclass instance with only the key/value pairs matching
            keys in the 'subset' argument.
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
      
    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent initialization method(s).
        super().__post_init__()    
        # Validates 'contents' or converts it to appropriate iterable.
        self.contents = self.validate(contents = self.contents)  
        
    """ Public Methods """
    
    def validate(self, contents: Any) -> Mapping[Any, Any]:
        """Validates 'contents' or converts 'contents' to a dict.
        
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
        if isinstance(contents, Mapping):
            return contents
        else:
            raise TypeError('contents must be a dict type')
     
    def add(self, contents: Mapping[Any, Any], **kwargs) -> None:
        """Adds 'contents' to the 'contents' attribute.
        
        Args:
            contents (Mapping[Any, Any]): items to add to 'contents' attribute.
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
        subset = sourdough.utilities.listify(subset)
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
        """Combines argument with 'contents' using the 'add' method.

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


@dataclasses.dataclass
class Catalog(Creator, Lexicon):
    """Base class for a wildcard and list-accepting dictionary.

    A Catalog inherits the differences between a Lexicon and an ordinary python
    dict.

    A Catalog differs from a Lexicon in 5 significant ways:
        1) It recognizes an 'all' key which will return a list of all values
            stored in a Catalog instance.
        2) It recognizes a 'default' key which will return all values matching
            keys listed in the 'defaults' attribute. 'default' can also be set
            using the 'catalog['default'] = new_default' assignment. If 
            'defaults' is not passed when the instance is initialized, the 
            initial value of 'defaults' is 'all'
        3) It recognizes a 'none' key which will return an empty list.
        4) It supports a list of keys being accessed with the matching
            values returned. For example, 'catalog[['first_key', 'second_key']]' 
            will return the values for those keys in a list ['first_value',
            'second_value'].
        5) If a single key is sought, a Catalog can either return the stored
            value or a stored value in a list (if 'always_return_list' is
            True). The latter option is available to make iteration easier
            when the iterator assumes a single datatype will be returned.
        6) It includes a 'create' method which will either instance a stored
            class or return a stored instance.

    Args:
        contents (Union[sourdough.Component, Sequence[sourdough.Component], 
            Mapping[str, sourdough.Component]]): Component(s) to validate or
            convert to a dict. If 'contents' is a Sequence or a Component, 
            the key for storing 'contents' is the 'name' attribute of each 
            Component.
        defaults (Sequence[str]]): a list of keys in 'contents' which will be 
            used to return items when 'default' is sought. If not passed, 
            'default' will be set to all keys.
        always_return_list (bool]): whether to return a list even when
            the key passed is not a list or special access key (True) or to 
            return a list only when a list or special acces key is used (False). 
            Defaults to False.
            
    """
    contents: Union[
        'sourdough.Component',
        Sequence['sourdough.Component'],
        Mapping[str, 'sourdough.Component']] = dataclasses.field(
            default_factory = dict)    
    defaults: Sequence[str] = dataclasses.field(default_factory = list)
    always_return_list: bool = False

    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent initialization method(s).
        super().__post_init__()
        # Sets 'default' to all keys of 'contents', if not passed.
        self.defaults = self.defaults or 'all'
        
    """ Public Methods """

    def validate(self, 
            contents: Union[
                'sourdough.Component',
                Sequence['sourdough.Component'],
                Mapping[str, 'sourdough.Component']]) -> Mapping[
                    str, 'sourdough.Component']:
        """Validates 'contents' or converts 'contents' to a dict.
        
        Args:
            contents (Union[sourdough.Component, Sequence[sourdough.Component], 
                Mapping[str, sourdough.Component]]): Component(s) to validate or
                convert to a dict. If 'contents' is a Sequence or a Component, 
                the key for storing 'contents' is the 'name' attribute of each 
                Component.
                
        Raises:
            TypeError: if 'contents' is neither a Component subclass, Sequence
                of Component subclasses, or Mapping with Components subclasses
                as values.
                
        Returns:
            Mapping (str, sourdough.Component): a properly typed dict derived
                from passed 'contents'.
            
        """
        if (isinstance(contents, sourdough.Component) 
            or (inspect.isclass(contents) 
                and issubclass(contents, sourdough.Component))):
            return {contents.get_name(): contents}
        elif (isinstance(contents, Mapping)
            and (all(isinstance(v, Component) for v in contents.values())
                or all(issubclass(v, Component) for v in contents.values()))):
            return contents
        elif (isinstance(contents, Sequence)
            and (all(isinstance(c, Component) for c in contents)
                or all(issubclass(c, Component) for c in contents))):
            new_contents = {}
            for component in contents:
                new_contents[component.get_name()] = component
            return new_contents
        else:
            raise TypeError(
                'contents must a Component or Mapping or Sequence storing '
                'Components') 

    def subsetify(self, subset: Union[str, Sequence[str]]) -> 'Catalog':
        """Returns a subset of 'contents'.

        Args:
            subset (Union[str, Sequence[str]]): key(s) to get key/value pairs 
                from 'contents'.

        Returns:
            Catalog: with only keys in 'subset'.

        """
        new_defaults = [i for i in self.defaults if i in subset] 
        return super().subsetify(
            contents = self.contents,
            defaults = new_defaults,
            always_return_list = self.always_return_list)

    def create(self, key: str, **kwargs) -> 'sourdough.Component':
        """Returns an instance of a stored subclass or instance.
        
        This method acts as a factory for instancing stored classes or returning
        instances.
        
        Args:
            key (str): key to desired Component in 'contents'.
            kwargs: arguments to pass to the selected Component when it is
                instanced.
                    
        Returns:
            sourdough.Component: that has been instanced with kwargs as 
                arguments if it was a stored class. Otherwise, the instance
                is returned as it was stored.
            
        """
        try:
            return self.contents[key](**kwargs)
        except TypeError:
            return self.contents[key] 

    """ Dunder Methods """

    def __getitem__(self, 
            key: Union[Sequence[str], str]) -> Union[Sequence[Any], Any]:
        """Returns value(s) for 'key' in 'contents'.

        The method searches for 'all', 'default', and 'none' matching wildcard
        options before searching for direct matches in 'contents'.

        Args:
            key (Union[Sequence[str], str]): name(s) of key(s) in 'contents'.

        Returns:
            Union[Sequence[Any], Any]: value(s) stored in 'contents'.

        """
        # Returns a list of all values if the 'all' key is sought.
        if key in ['all', ['all']]:
            return list(self.contents.values())
        # Returns a list of values for keys listed in 'defaults' attribute.
        elif key in ['default', ['default'], 'defaults', ['defaults']]:
            try:
                return self[self.defaults]
            except KeyError:
                return list(
                    {k: self.contents[k] for k in self.defaults}.values())
        # Returns an empty list if a null value is sought.
        elif key in ['none', ['none'], 'None', ['None']]:
            return []
        # Returns list of matching values if 'key' is list-like.        
        elif isinstance(key, Sequence) and not isinstance(key, str):
            return [self.contents[k] for k in key if k in self.contents]
        # Returns matching value if key is a str.
        else:
            try:
                if self.always_return_list:
                    return [self.contents[key]]
                else:
                    return self.contents[key]
            except KeyError:
                raise KeyError(f'{key} is not in {self.__class__.__name__}')

    def __setitem__(self,
            key: Union[Sequence[str], str],
            value: Union[Sequence[Any], Any]) -> None:
        """Sets 'key' in 'contents' to 'value'.

        Args:
            key (Union[Sequence[str], str]): name of key(s) to set in 
                'contents'.
            value (Union[Sequence[Any], Any]): value(s) to be paired with 'key' 
                in 'contents'.

        """
        if key in ['default', ['default']]:
            self.defaults = sourdough.tools.listify(value)
        else:
            try:
                self.contents[key] = value
            except TypeError:
                self.contents.update(dict(zip(key, value)))
        return self

    def __delitem__(self, key: Union[Sequence[str], str]) -> None:
        """Deletes 'key' in 'contents'.

        Args:
            key (Union[Sequence[str], str]): name(s) of key(s) in 'contents' to
                delete the key/value pair.

        """
        self.contents = {
            i: self.contents[i]
            for i in self.contents if i not in sourdough.tools.listify(key)}
        return self


""" 
Reflector is currently omitted from the sourdough build because I'm unsure
if it has a significant use case. The code below should still work, but it
isn't included in the uploaded package build. 
"""

# @dataclasses.dataclass
# class Reflector(Lexicon):
#     """Base class for a mirrored dictionary.

#     Reflector access methods search keys and values for corresponding
#     matched values and keys, respectively.

#     Args:
#         contents (Mapping[str, Any]]): stored dictionary. Defaults to 
#             en empty dict.
              
#     """
#     contents: Mapping[str, Any] = dataclasses.field(default_factory = dict)

#     def __post_init__(self) -> None:
#         """Creates 'reversed_contents' from passed 'contents'."""
#         self._create_reversed()
#         return self

#     """ Dunder Methods """

#     def __getitem__(self, key: str) -> Any:
#         """Returns match for 'key' in 'contents' or 'reversed_contents'.

#         Args:
#             key (str): name of key to find.

#         Returns:
#             Any: value stored in 'contents' or 'reversed_contents'.

#         Raises:
#             KeyError: if 'key' is neither found in 'contents' nor 
#                 'reversed_contents'.

#         """
#         try:
#             return self.contents[key]
#         except KeyError:
#             try:
#                 return self.reversed_contents[key]
#             except KeyError:
#                 raise KeyError(f'{key} is not in {self.__class__.__name__}')

#     def __setitem__(self, key: str, value: Any) -> None:
#         """Stores arguments in 'contents' and 'reversed_contents'.

#         Args:
#             key (str): name of key to set.
#             value (Any): value to be paired with key.

#         """
#         self.contents[key] = value
#         self.reversed_contents[value] = key
#         return self

#     def __delitem__(self, key: str) -> None:
#         """Deletes key in the 'contents' and 'reversed_contents' dictionaries.

#         Args:
#             key (str): name of key to delete.

#         """
#         try:
#             value = self.contents[key]
#             del self.contents[key]
#             del self.reversed_contents[value]
#         except KeyError:
#             try:
#                 value = self.reversed_contents[key]
#                 del self.reversed_contents[key]
#                 del self.contents[value]
#             except KeyError:
#                 pass
#         return self

#     """ Private Methods """

#     def _create_reversed(self) -> None:
#         """Creates 'reversed_contents' from 'contents'."""
#         self.reversed_contents = {
#             value: key for key, value in self.contents.items()}
#         return self

""" 
Factory is currently omitted from the sourdough build because its design doesn't
presently fit with the sourdough workflow. However, the code should still work.
"""

# @dataclasses.dataclass
# class Factory(abc.ABC):
#     """The Factory interface instances a class from available options.

#     Args:
#         product (Union[str, Sequence[str]]): name(s) of sourdough object(s) to 
#             return. 'product' must correspond to a key(s) in 'options'. 
#             Defaults to None.
#         default (ClassVar[Union[str, Sequence[str]]]): the name(s) of the 
#             default object(s) to instance. If 'product' is not passed, 'default' 
#             is used. 'default' must correspond to key(s) in 'options'. Defaults 
#             to None.
#         options (ClassVar[sourdough.Catalog]): a dictionary of available options 
#             for object creation. Keys are the names of the 'product'. Values are 
#             the objects to create. Defaults to an empty dictionary.

#     Returns:
#         Any: the factory uses the '__new__' method to return a different object 
#             instance with kwargs as the parameters.

#     """
#     product: Union[str, Sequence[str]] = None
#     default: ClassVar[Union[str, Sequence[str]]] = None
#     options: ClassVar['sourdough.Catalog'] = sourdough.Catalog(
#         always_return_list = True)

#     """ Initialization Methods """
    
#     def __new__(cls, product: str = None, **kwargs) -> Any:
#         """Returns an instance from 'options'.

#         Args:
#             product (str): name of sourdough object(s) to return. 
#                 'product' must correspond to key(s) in 'options'. Defaults to 
#                 None. If not passed, the product listed in 'default' will be 
#                 used.
#             kwargs (MutableMapping[str, Any]): parameters to pass to the object 
#                 being created.

#         Returns:
#             Any: an instance of an object stored in 'options'.
        
#         """
#         if not product:
#             product = cls.default
#         if isinstance(product, str):
#             return cls.options[product](**kwargs)
#         else:
#             instances = []
#             for match in cls.options[product]:
#                 instances.append(match(**kwargs))
#             return instances
    
#     """ Class Methods """
    
#     @classmethod
#     def add(cls, key: str, option: 'sourdough.Component') -> None:
#         """Adds 'option' to 'options' at 'key'.
        
#         Args:
#             key (str): name of key to link to 'option'.
#             option (sourdough.Component): object to store in 'options'.
            
#         """
#         cls.options[key] = option
#         return cls
        
#     """ Dunder Methods """
    
#     def __repr__(self) -> str:
#         """Returns '__str__' representation.

#         Returns:
#             str: default representation of a class instance.

#         """
#         return self.__str__()

#     def __str__(self) -> str:
#         """Returns default representation of a class instance.

#         Returns:
#             str: default representation of a class instance.

#         """
#         return textwrap.dedent(f'''
#             sourdough {self.__class__.__name__}
#             product: {self.product}
#             default: {self.default}
#             options: {str(self.options)}''')        