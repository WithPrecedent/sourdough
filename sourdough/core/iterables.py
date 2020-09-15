"""
iterables: sourdough base classes for iterable composite objects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Slate (Element, MutableSequence): sourdough drop-in replacement for list
        with additional functionality.
    Hybrid (Slate): iterable containing Element subclass instances with both 
        dict and list interfaces and methods.

"""
from __future__ import annotations
import collections.abc
import copy
import dataclasses
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union

import sourdough

     
@dataclasses.dataclass
class Slate(sourdough.Element, collections.abc.MutableSequence):
    """Basic sourdough list replacement.
    
    A Slate differs from a python list in 3 significant ways:
        1) It includes a 'name' attribute which is used for internal referencing
            in sourdough. This is inherited from sourdough.Element.
        2) It includes an 'add' method which allows different datatypes to be 
            passed and added to the 'contents' of a Slate instance. 
        3) It uses a 'validate' method to validate or convert the passed 
            'contents' argument. It will convert all supported datatypes to 
            a list. The 'validate' method is automatically called when a
            Slate is instanced and when the 'add' method is called.

    Args:
        contents (Sequence[Any]): items to store in a list. Defaults to an empty 
            list.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of sourdough.Element is called, 'name' is set based 
            upon the '_get_name' method in sourdough.Element. If that method is 
            not overridden by a subclass instance, 'name' will be assigned to 
            the snake case version of the class name ('__class__.__name__').
        
    """
    contents: Sequence[Any] = dataclasses.field(default_factory = list)
    name: str = None
    validator: sourdough.validators.Validator = sourdough.validators.Validator(
        products = 'sequence',                                                                               
        accepts = list) 
        
    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent initialization method(s).
        super().__post_init__()        
        # Validates 'contents' or converts it to appropriate iterable.
        self._initial_validation()  
    
    """ Public Methods """
    
    def validate(self, contents: Sequence[Any]) -> Sequence[Any]:
        """Validates 'contents' or converts 'contents' to proper type.
        
        Args:
            contents (Sequence[Any]): item(s) to validate or convert to a list.
            
        Raises:
            TypeError: if 'contents' argument is not of a supported datatype.
            
        Returns:
            Sequence[Any]: validated or converted argument that is compatible 
                with an instance.
        
        """
        contents = self.validator.verify(contents = contents)
        return self.validator.convert(element = contents)

    def add(self, contents: Sequence[Any]) -> None:
        """Extends 'contents' argument to 'contents' attribute.
        
        Args:
            contents (Sequence[Any]): items to add to the 'contents' attribute.

        """
        contents = self.validate(contents = contents)
        self.contents.extend(contents)
        return self  
        
    """ Dunder Methods """

    def __getitem__(self, key: int) -> Any:
        """Returns value(s) for 'key' in 'contents'.

        Args:
            key (int): index to search for in 'contents'.

        Returns:
            Any: item stored in 'contents' at key.

        """
        return self.contents[key]
            
    def __setitem__(self, key: int, value: Any) -> None:
        """Sets 'key' in 'contents' to 'value'.

        Args:
            key (int): index to set 'value' to in 'contents'.
            value (Any): value to be set at 'key' in 'contents'.

        """
        self.contents[key] = value

    def __delitem__(self, key: Union[str, int]) -> None:
        """Deletes item at 'key' index in 'contents'.

        Args:
            key (int): index in 'contents' to delete.

        """
        del self.contents[key]

    def __iter__(self) -> Iterable:
        """Returns iterable of 'contents'.

        Returns:
            Iterable: generic ordered iterable of 'contents'.
               
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

    """ Private Methods """
    
    def _initial_validation(self) -> None:
        """Validates passed 'contents' on class initialization."""
        new_contents = copy.deepcopy(self.contents)
        new_contents = self.validate(contents = new_contents)
        self.contents = []
        self.add(contents = new_contents)
        return self
    
    
@dataclasses.dataclass
class Hybrid(Slate):
    """Base class for ordered iterables in sourdough composite objects.
    
    Hybrid combines the functionality and interfaces of python dicts and lists.
    It allows duplicate keys and list-like iteration while supporting the easier
    access methods of dictionaries. In order to support this hybrid approach to
    iterables, Hybrid can only store sourdough.Element subclasses.
    
    Hybrid is the primary iterable base class used in sourdough composite 
    objects.
    
    A Hybrid inherits the differences between a Slate and an ordinary python 
    list.
    
    A Hybrid differs from a Slate in 4 significant ways:
        1) It only stores Element subclasses or subclass instances.
        2) It includes a 'subsetify' method which will return a Hybrid or Hybrid 
            subclass instance with only the items with 'name' attributes 
            matching items in the 'subset' argument.
        3) Hybrid has an interface of both a dict and a list, but stores a list. 
            Hybrid does this by taking advantage of the 'name' attribute of 
            Element instances. A 'name' acts as a key to create the facade of 
            a dictionary with the items in the stored list serving as values. 
            This allows for duplicate keys for storing class instances, easier 
            iteration, and returning multiple matching items. This design comes 
            at the expense of lookup speed. As a result, Hybrid should only be 
            used if a high volume of access calls is not anticipated. 
            Ordinarily, the loss of lookup speed should have negligible effect 
            on overall performance.
        4) It includes 'apply' and 'find' methods which traverse items in
            'contents' (recursively, if the 'recursive' argument is True), to
            either 'apply' a callable or 'find' items matching criteria in a
            callable. 

    Args:
        contents (sourdough.Elemental): Element subclasses or Element subclass 
            instances to store in a list. If a dict is passed, the keys will 
            be ignored and only the values will be added to 'contents'. If a
            single Element is passed, it will be placed in a list. Defaults to 
            an empty list.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of sourdough.Element is called, 'name' is set based 
            upon the '_get_name' method in sourdough.Element. If that method is 
            not overridden by a subclass instance, 'name' will be assigned to 
            the snake case version of the class name ('__class__.__name__').
        
    Attributes:
        contents (Sequence[sourdough.Element]): stored Element subclasses or 
            subclass instances.
            
    """
    contents: sourdough.Elemental = dataclasses.field(default_factory = list)
    name: str = None
    validator: sourdough.validators.Validator = sourdough.validators.Validator(
        products = 'sequence',                                                                               
        accepts = sourdough.Elemental)    
    
    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent initialization method(s).
        super().__post_init__()        
        # Sets initial default value for the 'get' method.
        self._default = None
        
    """ Public Methods """
    
    # def validate(self, 
    #         contents: sourdough.Elemental) -> Sequence[sourdough.Element]:
    #     """Validates 'contents' or converts 'contents' to proper type.
        
    #     Args:
    #         contents (sourdough.Elemental): item(s) to validate or convert to a 
    #             list of Element instances.
            
    #     Raises:
    #         TypeError: if 'contents' argument is not of a supported datatype.
            
    #     Returns:
    #         Sequence[sourdough.Element]: validated or converted argument that is 
    #             compatible with an instance.
        
    #     """
    #     contents = self.validator.verify(contents = contents)
    #     return self.validator.convert(element = contents)

    def add(self, contents: sourdough.Elemental) -> None:
        """Extends 'contents' argument to 'contents' attribute.
        
        Args:
            contents (sourdough.Elemental): sourdough.Elemental instance(s) to add to the 'contents' 
                attribute.

        """
        contents = self.validate(contents = contents)
        self.contents.extend(contents)
        return self    

    def append(self, contents: sourdough.Elemental) -> None:
        """Appends 'element' to 'contents'.
        
        Args:
            contents (Union[sourdough.Element, Mapping[Any, sourdough.Element], 
                Sequence[sourdough.Element]]): sourdough.Element instance(s) to add to the
                'contents' attribute.

        Raises:
            TypeError: if 'element' does not have a name attribute.
            
        """
        contents = self.validate(contents = contents)
        if (isinstance(contents, Sequence)
                and not isinstance(contents, sourdough.Element)):
            contents = self.__class__(contents)
        self.contents.append(contents)
        return self    
    
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
        for item in iter(self.contents):
            if isinstance(item, sourdough.base.Hybrid):
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

    def clear(self) -> None:
        """Removes all items from 'contents'."""
        self.contents = []
        return self
   
    def extend(self, contents: sourdough.Elemental) -> None:
        """Extends 'element' to 'contents'.
        
        Args:
            contents (sourdough.Elemental): sourdough.Elemental instance(s) to add to the 'contents' 
                attribute.

        Raises:
            TypeError: if 'element' does not have a name attribute.
            
        """
        contents = self.validate(contents = contents)
        self.contents.extend(contents)
        return self  

    def find(self, 
            tool: Callable, 
            recursive: bool = True, 
            matches: Sequence[sourdough.Element] = None,
            **kwargs) -> Sequence[sourdough.Element]:
        """Finds items in 'contents' that match criteria in 'tool'.
        
        Args:
            tool (Callable): callable which accepts an object in 'contents' as
                its first argument and any other arguments in kwargs.
            recursive (bool): whether to apply 'tool' to nested items in
                'contents'. Defaults to True.
            matches (Sequence[sourdough.Element]): items matching the criteria
                in 'tool'. This should not be passed by an external call to
                'find'. It is included to allow recursive searching.
            kwargs: additional arguments to pass when 'tool' is used.
            
        Returns:
            Sequence[sourdough.Element]: stored items matching the criteria
                in 'tool'. 
        
        """
        if matches is None:
            matches = []
        for item in iter(self.contents):
            matches.extend(sourdough.tools.listify(tool(item, **kwargs)))
            if isinstance(item, sourdough.base.Hybrid):
                if recursive:
                    matches.extend(item.find(
                        tool = tool, 
                        recursive = True,
                        matches = matches, 
                        **kwargs))
        return matches
    
    def get(self, key: Union[str, int]) -> Union[sourdough.Element, Sequence[sourdough.Element]]:
        """Returns value(s) in 'contents' or value in '_default' attribute.
        
        Args:
            key (Union[str, int]): index or stored sourdough.Element name to get from
                'contents'.
                
        Returns:
            Union[sourdough.Element, Sequence[sourdough.Element]]: items in 'contents' or value in 
                '_default' attribute. 
        """
        try:
            return self[key]
        except KeyError:
            return self._default
            
    def insert(self, index: int, element: sourdough.Element) -> None:
        """Inserts 'element' at 'index' in 'contents'.

        Args:
            index (int): index to insert 'element' at.
            element (sourdough.Element): object to be inserted.

        Raises:
            TypeError: if 'element' is not a sourdough.Element type.
            
        """
        if isinstance(element, sourdough.Element):
            self.contents.insert(index, element)
        else:
            raise TypeError('element must be a sourdough.Element type')
        return self

    def items(self) -> Iterable:
        """Emulates python dict 'items' method.
        
        Returns:
            Iterable: tuple of sourdough.Element names and sourdough.Elements.
            
        """
        return tuple(zip(self.keys(), self.values()))

    def keys(self) -> Sequence[str]:
        """Emulates python dict 'keys' method.
        
        Returns:
            Sequence[sourdough.Element]: list of names of sourdough.Elements stored in 
                'contents'
            
        """
        try:
            return [c.name for c in self.contents]
        except AttributeError:
            return [c.get_name() for c in self.contents]

    def pop(self, key: Union[str, int]) -> Union[sourdough.Element, Sequence[sourdough.Element]]:
        """Pops item(s) from 'contents'.

        Args:
            key (Union[str, int]): index or stored sourdough.Element name to pop from
                'contents'.
                
        Returns:
            Union[sourdough.Element, Sequence[sourdough.Element]]: items popped from 
                'contents'.
            
        """
        popped = self[key]
        del self[key]
        return popped
        
    def remove(self, key: Union[str, int]) -> None:
        """Removes item(s) from 'contents'.

        Args:
            key (Union[str, int]): index or stored sourdough.Element name to remove from
                'contents'.
            
        """
        del self[key]
        return self
     
    def setdefault(self, value: Any) -> None:
        """Sets default value to return when 'get' method is used.
        
        Args:
            value (Any): default value to return.
            
        """
        self._default = value 
     
    def subsetify(self, subset: Union[str, Sequence[str]]) -> Hybrid:
        """Returns a subset of 'contents'.

        Args:
            subset (Union[str, Sequence[str]]): key(s) to get sourdough.Element 
                instances with matching 'name' attributes from 'contents'.

        Returns:
            Hybrid: with only items with 'name' attributes in 'subset'.

        """
        subset = sourdough.tools.listify(subset)
        try:
            return self.__class__(
                name = self.name,
                contents = [c for c in self.contents if c.name in subset])  
        except AttributeError:            
            return self.__class__(
                name = self.name,
                contents = [c for c in self.contents if c.get_name() in subset])    
     
    def update(self, contents: sourdough.Elemental) -> None:
        """Mimics the dict 'update' method by appending 'contents'.
        
        Args:
            contents (sourdough.Elemental): sourdough.Elemental instances to add to the 'contents' 
                attribute. If a Mapping is passed, the values are added to 
                'contents' and the keys become the 'name' attributes of those 
                values. To mimic 'update', the passed 'elements' are added to 
                'contents' by the 'extend' method.
 
        Raises:
            TypeError: if any of 'elements' do not have a name attribute or
                if 'elements is not a dict.               
        
        """
        contents = verify(element = contents)
        if isinstance(contents, Mapping):
            for key, value in contents.items():
                new_element = value
                new_element.name = key
                self.extend(contents = new_element)
        else:
            self.extend(contents = contents)
        return self

    def values(self) -> Sequence[sourdough.Element]:
        """Emulates python dict 'values' method.
        
        Returns:
            Sequence[sourdough.Element]: list of sourdough.Elements stored in 'contents'
            
        """
        return self.contents
          
    """ Dunder Methods """

    def __getitem__(self, key: Union[str, int]) -> sourdough.Element:
        """Returns value(s) for 'key' in 'contents'.
        
        If 'key' is a str type, this method looks for a matching 'name'
        attribute in the stored instances.
        
        If 'key' is an int type, this method returns the stored element at the
        corresponding index.
        
        If only one match is found, a single sourdough.Element instance is returned. If
        more are found, a Hybrid or Hybrid subclass with the matching
        'name' attributes is returned.

        Args:
            key (Union[str, int]): name or index to search for in 'contents'.

        Returns:
            sourdough.Element: value(s) stored in 'contents' that correspond 
                to 'key'. If there is more than one match, the return is a
                Hybrid or Hybrid subclass with that matching stored
                elements.

        """
        if isinstance(key, int):
            return self.contents[key]
        else:
            try:
                matches = [c for c in self.contents if c.name == key]
            except AttributeError:
                matches = [c for c in self.contents if c.get_name() == key]
            if len(matches) == 0:
                raise KeyError(f'{key} is not in {self.name}')
            elif len(matches) == 1:
                return matches[0]
            else:
                return self.__class__(name = self.name, contents = matches)
            
    def __setitem__(self, 
            key: Union[str, int], 
            value: sourdough.Element) -> None:
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
            self.add(value)
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
            try:
                self.contents = [c for c in self.contents if c.name != key]
            except AttributeError:
                self.contents = [
                    c for c in self.contents if c.get_name() != key]
        return self

    def __len__(self) -> int:
        """Returns length of collapsed 'contents'.

        Returns:
            int: length of collapsed 'contents'.

        """
        return len(list(more_itertools.collapse(self.contents)))
        

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
#         contents (Mapping[Any, Any]]): stored dictionary. Defaults to 
#             en empty dict.
              
#     """
#     contents: Mapping[Any, Any] = dataclasses.field(default_factory = dict)

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


   