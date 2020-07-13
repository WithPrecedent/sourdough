"""
.. module:: iterables
:synopsis: sourdough Progression
:author: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import collections.abc
import dataclasses
import itertools
import more_itertools
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union

import sourdough
        
        
@dataclasses.dataclass
class Progression(sourdough.Component, collections.abc.MutableSequence):
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
        6) Iterating Plan iterates all contained iterables by using the
            'more_itertools.collapse' method. This orders all stored iterables 
            in a depth-first manner.      

    Args:
        contents (Sequence[sourdough.Component]]): stored iterable of 
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

    """
    contents: Sequence['sourdough.Component'] = dataclasses.field(
        default_factory = list)
    name: str = None

    """ Public Methods """
       
    def add(self, 
            component: Union[
                'sourdough.Component',
                Mapping[str, 'sourdough.Component'], 
                Sequence['sourdough.Component']]) -> None:
        """Appends 'component' to 'contents'.
        
        Args:
            component (Union[sourdough.Component, Mapping[str, 
                sourdough.Component], Sequence[sourdough.Component]]): Component 
                instance(s) to add to 'contents'.

        """
        if hasattr(component, 'name'):
            self.append(component = component)
        else:
            self.update(components = component)
        return self    

    def append(self, component: 'sourdough.Component') -> None:
        """Appends 'component' to 'contents'.
        
        Args:
            component (sourdough.Component): Component instance to add to 
                'contents'.

        Raises:
            TypeError: if 'component' does not have a name attribute.
            
        """
        if hasattr(component, 'name'):
            self.contents.append(component)
        else:
            raise TypeError('component must have a name attribute')
        return self    
   
    def extend(self, component: 'sourdough.Component') -> None:
        """Extends 'component' to 'contents'.
        
        Args:
            component (sourdough.Component): Component instance to add to 
                'contents'.

        Raises:
            TypeError: if 'component' does not have a name attribute.
            
        """
        if hasattr(component, 'name'):
            self.contents.extend(component)
        else:
            raise TypeError('component must have a name attribute')
        return self   
    
    def insert(self, index: int, component: 'sourdough.Component') -> None:
        """Inserts 'component' at 'index' in 'contents'.

        Args:
            index (int): index to insert 'component' at.
            component (sourdough.Component): object to be inserted.

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
                Mapping[str, 'sourdough.Component'], 
                Sequence['sourdough.Component']]) -> None:
        """Mimics the dict 'update' method by appending 'contents'.
        
        Args:
            components (Union[Mapping[str, sourdough.Component], Sequence[
                sourdough.Component]]): Component instances to add to 
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

    def __getitem__(self, key: Union[str, int]) -> 'sourdough.Component':
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
            sourdough.Component: value(s) stored in 'contents' that correspond 
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
            value: 'sourdough.Component') -> None:
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
    
    def __add__(self, other: 'Progression') -> None:
        """Adds 'other' to 'contents' with 'add' method.

        Args:
            other (Progression): another Progression instance.

        """
        self.add(component = other)
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
            f'name: {self.name}\n'
            f'contents: {self.contents.__str__()}') 
