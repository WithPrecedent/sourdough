"""
.. module:: dictionaries
:synopsis: sourdough dictionaries
:author: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import collections.abc
import dataclasses
import importlib
import inspect
import pathlib
import pyclbr
from typing import Any, ClassVar, Iterable, Mapping, Sequence, Tuple, Union

import sourdough


@dataclasses.dataclass
class Lexicon(collections.abc.MutableMapping):
    """Base class for sourdough dictionaries.

    Lexicon and its subclasses can serve as drop in replacements for dicts with 
    added features.
    
    A Lexicon differs from a python dict in 3 ways:
        1) It includes an 'add' method which allows different datacontents to
            be passed and added to a Lexicon instance. All of the normal 
            dictionary methods are also available. 'add' is available to set
            default or more complex methods of adding elements to the stored
            dict.
        2) It includes a 'subsetify' method which will return a Lexicon or
            Lexicon subclass instance with only the key/value pairs matching
            keys in the 'subset' parameter.
        3) It allows the '+' operator to be used to join a Lexicon instance
            with another Lexicon instance, a python dictionary, or a
            sourdough Component. The '+' operator calls the Lexicon 'add'
            method to implement how the added item(s) is/are added to the
            Lexicon instance.
    
    Args:
        contents (Optional[Mapping[str, Any]]): stored dictionary. Defaults to 
            en empty dict.
              
    """
    contents: Optional[Mapping[str, Any]] = dataclasses.field(
        default_factory = dict)

    """ Public Methods """

    def add(self, 
            contents: Union[Mapping[str, Any], 'sourdough.Component']) -> None:
        """Combines arguments with 'contents'.

        Args:
            contents (Union[Mapping[str, Any], sourdough.Component]): a
                Mapping or sourdough Component to add to the 'contents' 
                attribute.
                
        Raises:
            TypeError: if 'contents' is not a Mapping, Component, or class.

        """
        if hasattr(contents, 'name'):
            self.contents[contents.name] = contents
        elif isinstance(contents, collections.abc.Mapping):
            self.contents.update(contents)
        elif inspect.isclass(contents):
            self.contents[
                sourdough.tools.snakify(contents.__name__)] = contents
        else:
            raise TypeError('contents must be dict or Component type')
        return self
    
    def subsetify(self, 
            subset: Union[str, Sequence[str]], **kwargs) -> 'Lexicon':
        """Returns a subset of 'contents'.

        Args:
            subset (Union[str, Sequence[str]]): key(s) for which key/value pairs 
                from 'contents' should be returned.
            kwargs: allows subclasses to send additional parameters to this 
                method.

        Returns:
            Lexicon: with only keys in 'subset'.

        """
        return self.__class__(
            contents = sourdough.tools.subsetify(
                dictionary = self.contents,
                subset = subset),
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

    def __add__(self, 
            other: Union[Mapping[str, Any], 'sourdough.Component']) -> None:
        """Combines argument with 'contents'.

        Args:
            contents (Union[Mapping[str, Any], sourdough.Component]): a
                Mapping or sourdough Component to add to the 'contents' 
                attribute.

        """
        self.add(contents = other)
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
class Catalog(Lexicon):
    """Base class for a wildcard and list-accepting dictionary.

    A Catalog inherits the differences between a Lexicon and an ordinary python
    dict.

    A Catalog differs from a Lexicon in 5 ways:
        1) It recognizes an 'all' key which will return a list of all values
            stored in a Catalog instance.
        2) It recognizes a 'default' key which will return all values matching
            keys listed in the 'defaults' attribute. 'default' can also be set
            using the 'catalog['default'] = new_default' assignment. If 
            'defaults' is not passed when the instance is initialized, the 
            initial value of 'defaults' is a list of all the stored keys at
            that time.
        3) It recognizes a 'none' key which will return an empty list.
        4) It supports a list of keys being accessed with the matching
            values returned. For example, 'catalog[['first_key', 'second_key']]' 
            will return the values for those keys in a list.
        5) If a single key is sought, a Catalog can either return the stored
            value or a stored value in a list (if 'always_return_list' is
            True). The latter option is available to make iteration easier
            when the iterator assumes a single datatype will be returned.

    Args:
        contents (Optional[Mapping[str, Any]]): stored dictionary. Defaults to 
            an empty dict.
        defaults (Optional[Sequence[str]]): a list of keys in 'contents' which
            will be used to return items when 'default' is sought. If not
            passed, 'default' will be set to all keys.
        always_return_list (Optional[bool]): whether to return a list even when
            the key passed is not a list or special access key (True) or to 
            return a list in all cases (False). Defaults to False.

    """
    contents: Optional[Mapping[str, Any]] = dataclasses.field(
        default_factory = dict)    
    defaults: Optional[Sequence[str]] = dataclasses.field(
        default_factory = list)
    always_return_list: Optional[bool] = False

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Sets 'default' to all keys of 'contents', if not passed.
        self.defaults = self.defaults or list(self.contents.keys())
        return self

    """ Public Methods """

    def subsetify(self, subset: Union[str, Sequence[str]]) -> 'Catalog':
        """Returns a subset of 'contents'.

        Args:
            subset (Union[str, Sequence[str]]): key(s) to get key/value pairs 
                from 'contents'.

        Returns:
            Catalog: with only keys in 'subset'.

        """
        return super().subsetify(
            contents = self.contents,
            name = self.name,
            defaults = self.defaults,
            always_return_list = self.always_return_list)

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
        elif key in ['default', ['default']]:
            return list({k: self.contents[k] for k in self.defaults}.values())
        # Returns an empty list if a null value is sought.
        elif key in ['none', ['none'], 'None', ['None'], '', ['']]:
            return []
        else:
            if isinstance(key, list):
                return [self.contents[k] for k in key if k in self.contents]
            else:
                try:
                    if self.always_return_list:
                        return [self.contents[key]]
                    else:
                        return self.contents[key]
                except KeyError:
                    raise KeyError(f'{key} is not in {self.name}')

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

    def __str__(self) -> str:
        """Returns default dictionary string representation of an instance.

        Returns:
            str: default dictionary string representation of an instance.

        """
        return (
            f'sourdough {self.__class__.__name__}\n'
            f'contents: {self.contents.__str__()}\n'
            f'defaults: {self.defaults.__str__()}')



@dataclasses.dataclass
class Library(sourdough.Catalog): 
    """Dictionary for storing subclass instances.

    Library adds 'base' to an ordinary Catalog implementation. 'base' is the
    object where the Library instance is stored as a class variable. This allows
    each subclass, with a registration method to automatically store instances
    in the base class Library instance.
    
    Args:
        contents (Optional[Mapping[str, Component]]): stored dictionary. 
            Defaults to en empty dict.
        defaults (Optional[Sequence[str]]): a list of keys in 'contents' which
            will be used to return items when 'default' is sought. If not
            passed, 'default' will be set to all keys.
        always_return_list (Optional[bool]): whether to return a list even when
            the key passed is not a list (True) or to return a list in all cases
            (False). Defaults to True.
        base (object): related class where Component subclass instances should 
            be stored.

    """
    contents: Optional[Mapping[str, 'sourdough.Component']] = dataclasses.field(
        default_factory = dict)
    defaults: Optional[Sequence[str]] = dataclasses.field(
        default_factory = list)
    always_return_list: Optional[bool] = True
    base: Optional[object] = None
    
    """ Public Methods """

    def add(self, component: 'sourdough.Component') -> None:
        """Adds 'sourdough.Component' to 'contents'.
        
        Args:
            component (sourdough.Component) -> a Component instance to add to
                'contents'.

        Raises:
            TypeError: if 'sourdough.Component' is not a Component instance.
            
        """
        if isinstance(component, sourdough.Component):
            self.contents[component.name] = component
        else:
            raise TypeError('component must be a Component instance')
        return self
    
    """ Dunder Methods """

    def __str__(self) -> str:
        """Returns default string representation of an instance.

        Returns:
            str: default string representation of an instance.

        """
        return (
            f'sourdough {self.__class__.__name__}\n'
            f'base: {self.base.__name__}\n'
            f'contents: {self.contents.__str__()}')  

    
@dataclasses.dataclass
class Registry(sourdough.Catalog): 
    """Dictionary for  storing subclasses.

    Args:
        contents (Optional[Mapping[str, Component]]): stored dictionary. 
            Defaults to en empty dict.
        defaults (Optional[Sequence[str]]): a list of keys in 'contents' which
            will be used to return items when 'default' is sought. If not
            passed, 'default' will be set to all keys.
        always_return_list (Optional[bool]): whether to return a list even when
            the key passed is not a list (True) or to return a list in all cases
            (False). Defaults to False.
        base (object): related class where subclasses should be stored.
        auto_register (Optional[bool]): whether to walk through the current
            working directory and subfolders to search for classes to add to
            the Library (True). Defaults to True.
    
    """ 
    contents: Optional[Mapping[str, 'sourdough.Component']] = dataclasses.field(
        default_factory = dict)
    defaults: Optional[Sequence[str]] = dataclasses.field(
        default_factory = list)
    always_return_list: Optional[bool] = False
    base: Optional[object] = None
    auto_register: Optional[bool] = False
        
    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Sets base class to this instance's class if 'base' is not passed.
        self.base = self.base or self.__class__
        # Finds Component subclasses in the present working folder or 
        # subfolders if 'auto_register' is True.
        if self.auto_register:
            self.walk(folder = pathlib.Path.cwd())
        return self
     
    """ Class Methods """
    
    @classmethod
    def create(cls, name: str, **kwargs) -> 'sourdough.Component':
        """Returns an instance of a stored subclass.
        
        This method acts as a factory for instancing stored Component 
        subclasses.
        
        Args:
            name (str): key to desired Component in 'contents'.
            kwargs: arguments to pass to the selected Component when it is
                instanced.
                    
        Returns:
            sourdough.Component: that has been instanced with kwargs as 
                arguments.
            
        """
        return cls.contents[name](**kwargs) 
        
    """ Public Methods """

    def add(self, component: 'sourdough.Component') -> None:
        """Adds 'sourdough.Component' to 'contents'.
        
        Args:
            component (sourdough.Component) -> a Component subclass to add to
                'contents'.

        Raises:
            TypeError: if 'sourdough.Component' is not a Component subclass
            
        """
        try:
            key = sourdough.tools.snakify(component.__name__)
            self.contents[key] = component
        except AttributeError:
            try:
                key = sourdough.tools.snakify(component.__class__.__name__)
                self.contents[key] = component.__class__
            except AttributeError:
                raise TypeError('component must be a Component subclass')
        return self

    def walk(self, 
            folder: Union[str, pathlib.Path], 
            recursive: Optional[bool] = True) -> None:
        """Adds Component subclasses for python files in 'folder'.
        
        If 'recursive' is True, subfolders are searched as well.
        
        Args:
            folder (Union[str, pathlib.Path]): folder to initiate search for 
                Component subclasses.
            recursive (Optional[bool]): whether to also search subfolders (True)
                or not (False). Defaults to True.
                
        """
        if recursive:
            glob_method = 'rglob'
        else:
            glob_method = 'glob'
        for file_path in getattr(pathlib.Path(folder), glob_method)('*.py'):
            module = self._import_from_path(file_path = file_path)
            subclasses = self._get_subclasses(module = module)
            for subclass in subclasses:
                self.add({
                    sourdough.tools.snakify(subclass.__name__): subclass})    
        return self
       
    """ Private Methods """
    
    def _import_from_path(self, file_path: Union[pathlib.Path, str]) -> object:
        """Returns an imported module from a file path.
        
        Args:
            file_path (Union[pathlib.Path, str]): path of a python module.
        
        Returns:
            object: an imported python module. 
        
        """
        file_path = pathlib.Path(file_path)
        module_spec = importlib.util.spec_from_file_location(file_path)
        module = importlib.util.module_from_spec(module_spec)
        return module_spec.loader.exec_module(module)
    
    def _get_subclasses(self, 
            module: object) -> Sequence['sourdough.Component']:
        """Returns a list of Component subclasses.
        
        Args:
            module (object): an import python module.
        
        Returns:
            Sequence[Component]: list of subclasses of Component. If none are 
                found, an empty list is returned.
                
        """
        matches = []
        for item in pyclbr.readmodule(module):
            # Adds direct subclasses.
            if inspect.issubclass(item, sourdough.Component):
                matches.append[item]
            else:
                # Adds subclasses of other subclasses.
                for subclass in self.contents.values():
                    if subclass(item, subclass):
                        matches.append[item]
        return matches

    # @classmethod
    # def create(cls,
    #         component: Union[str, 'sourdough.Component'],
    #         **kwargs) -> 'sourdough.Component':
    #     """Returns a Component subclass for 'sourdough.Component'.

    #     Args:
    #         component (Union[str, Component]): either a key in 'catalog' or a
    #             Component subclass. If a Component subclass is passed, it is
    #             automatically added to 'catalog' and instanced.
    #         kwArgs: arguments to be passed to instanced Component subclass.

    #     Raises:
    #         ValueError: if 'sourdough.Component' is a string but does not exist in
    #             'catalog'.
    #         TypeError: if 'sourdough.Component' is neither a string nor Component.

    #     Returns:
    #         Component: instanced subclass with kwargs as initialization
    #             parameters.

    #     """
    #     if isinstance(component, cls):
    #         if cls.name not in cls.catalog:
    #             cls.register(component = component)
    #         return component(**kwargs)
    #     elif isinstance(component, str):
    #         if component in cls.catalog:
    #             return cls.catalog[component](**kwargs)
    #         else:
    #             raise ValueError(
    #                 f'{component} is not a recognized {cls.__name__} type')
    #     elif inspect.isclass(component):
    #         instance = component(**kwargs)
    #         if instance.name not in cls.catalog:
    #             cls.register(component = instance)
    #         return instance          
    #     else:
    #         raise TypeError(
    #             f'component must be a str or {cls.__name__} type or instance')

    # @classmethod
    # def register(cls,
    #         component: 'sourdough.Component',
    #         name: str = None) -> None:
    #     """Adds 'sourdough.Component' to 'library'.

    #     If 'name' is passed, that is the key used in 'library'.

    #     If not and 'sourdough.Component' is an instance, the 'name' attribute of that
    #     instance is used. If 'sourdough.Component' has not been instanced, the snake case
    #     of the class name (lower case and underscored appropriately) is used.

    #     Args:
    #         component (Component): subclass of Component to add to 'library'.
    #         name (Optional[str]): optional key name to use in 'library'.

    #     """
    #     if name is None:
    #         if inspect.isclass(component) or component.name is None:
    #             name = self._get_name()
    #         else:
    #             name = component.name
    #     if base is None:
    #         base = Component 
    #     cls._register_class(component = component, name = name)
    #     cls._register_instance(component = component, name = name)
    #     return cls  


@dataclasses.dataclass
class MirrorDictionary(collections.abc.MutableMapping):
    """Base class for a mirrored dictionary.

    MirrorDictionary access methods search keys and values for corresponding
    matched values and keys, respectively.

    Args:
        contents (Mapping[str, Any]): an ordinary dictionary that will have its
            keys and values searched by the access methods. For that reason,
            all values should be useable as keys in a python dict.

    """
    contents: Mapping[str, Any]

    def __post_init__(self) -> None:
        """Creates 'reversed_contents' from passed 'contents'."""
        self._create_reversed()
        return self

    """ Dunder Methods """

    def __getitem__(self, key: str) -> Any:
        """Returns match for 'key' in 'contents' or 'reversed_contents'.

        Args:
            key (str): name of key to find.

        Returns:
            Any: value stored in 'contents' or 'reversed_contents'.

        Raises:
            KeyError: if 'key' is neither found in 'contents' nor 
                'reversed_contents'.

        """
        try:
            return self.contents[key]
        except KeyError:
            try:
                return self.reversed_contents[key]
            except KeyError:
                raise KeyError(f'{key} is not in {self.__class__.__name__}')

    def __setitem__(self, key: str, value: Any) -> None:
        """Stores arguments in 'contents' and 'reversed_contents'.

        Args:
            key (str): name of key to set.
            value (Any): value to be paired with key.

        """
        self.contents[key] = value
        self.reversed_contents[value] = key
        return self

    def __delitem__(self, key: str) -> None:
        """Deletes key in the 'contents' and 'reversed_contents' dictionaries.

        Args:
            key (str): name of key to delete.

        """
        try:
            value = self.contents[key]
            del self.contents[key]
            del self.reversed_contents[value]
        except KeyError:
            try:
                value = self.reversed_contents[key]
                del self.reversed_contents[key]
                del self.contents[value]
            except KeyError:
                pass
        return self

    def __iter__(self) -> Iterable:
        """Returns iterable of 'contents'.

        Returns:
            Iterable stored in 'contents'.

        """
        return iter(self.contents)

    def __len__(self) -> int:
        """Returns length of the 'contents' dict.

        Returns:
            int of length of 'contents' dict.

        """
        return len(self.contents)

    """ Private Methods """

    def _create_reversed(self) -> None:
        """Creates 'reversed_contents'."""
        self.reversed_contents = {
            value: key for key, value in self.contents.items()}
        return self
