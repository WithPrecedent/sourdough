"""
plugins: sourdough plugins architecture
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:


    Repository (Library): abstract base class for automatically storing subclass
        instances in a 'contents' class attribute.
    Validator (Registry): abstract base class for type validators and 
        converters. The class provides a universal 'verify' method for type
        validation. All subclasses must have a 'convert' method for type 
        conversion.
    Loader (ABC): lazy loader which uses a 'load' method to import python
        classes, functions, and other items at runtime on demand. 
 
"""
from __future__ import annotations
import abc
import dataclasses
import inspect
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union

import sourdough


@dataclasses.dataclass
class Plugin(abc.ABC):
    """Base class for plugins
    
    Plugin automatically stores all non-abstract subclasses in the 'contents' 
    class attribute.

    Args:
        register_from_disk (bool): whether to look in the current working
            folder and subfolders for Plugin subclasses. Defaults to False.
        contents (ClassVar[sourdough.base.Catalog]): the instance which stores 
            subclasses in a sourdough.base.Catalog instance.
            
    """
    # register_from_disk: bool = False
    library: ClassVar[sourdough.base.Library] = sourdough.base.Library()
    _abstracts: ClassVar[Mapping[str, abc.ABC]] = {}
    
    """ Initialization Methods """
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        try:
            name = cls.get_name()
        except AttributeError:
            name = sourdough.tools.snakify(cls.__name__)
        if abc.ABC in cls.__bases__:
            Plugin._abstracts[name] = {}
        else:
            item = {name: cls}
            for key, abstract in reversed(Plugin._abstracts.items()):
                if abstract in cls.__mro__:
                    item = {key: {name: cls}}
                    break
            Plugin.library.update(item)
                       
    # """ Initialization Methods """
    
    # def __post_init__(self) -> None:
    #     """Initializes class instance attributes."""
    #     super().__post_init__()
    #     # Adds subclasses from disk to 'contents' if 'register_from_disk'.
    #     if self.register_from_disk:
    #         self.find_subclasses(folder = pathlib.Path.cwd())
    
    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def execute(self) -> Any:
        pass

    # """ Public Methods """

    # def find_subclasses(self, 
    #         folder: Union[str, pathlib.Path], 
    #         recursive: bool = True) -> None:
    #     """Adds Element subclasses for python files in 'folder'.
        
    #     If 'recursive' is True, subfolders are searched as well.
        
    #     Args:
    #         folder (Union[str, pathlib.Path]): folder to initiate search for 
    #             Element subclasses.
    #         recursive (bool]): whether to also search subfolders (True)
    #             or not (False). Defaults to True.
                
    #     """
    #     if recursive:
    #         glob_method = 'rglob'
    #     else:
    #         glob_method = 'glob'
    #     for file_path in getattr(pathlib.Path(folder), glob_method)('*.py'):
    #         if not file_path.name.startswith('__'):
    #             module = self._import_from_path(file_path = file_path)
    #             subclasses = self._get_subclasses(module = module)
    #             for subclass in subclasses:
    #                 self.add({
    #                     sourdough.tools.snakify(subclass.__name__): subclass})    
    #     return self
       
    # """ Private Methods """
    
    # def _import_from_path(self, file_path: Union[pathlib.Path, str]) -> object:
    #     """Returns an imported module from a file path.
        
    #     Args:
    #         file_path (Union[pathlib.Path, str]): path of a python module.
        
    #     Returns:
    #         object: an imported python module. 
        
    #     """
    #     # file_path = str(file_path)
    #     # file_path = pathlib.Path(file_path)
    #     print('test file path', file_path)
    #     module_spec = importlib.util.spec_from_file_location(file_path)
    #     print('test module_spec', module_spec)
    #     module = importlib.util.module_from_spec(module_spec)
    #     return module_spec.loader.exec_module(module)
    
    # def _get_subclasses(self, 
    #         module: object) -> Sequence[sourdough.base.Element]:
    #     """Returns a list of subclasses in 'module'.
        
    #     Args:
    #         module (object): an import python module.
        
    #     Returns:
    #         Sequence[Element]: list of subclasses of Element. If none are 
    #             found, an empty list is returned.
                
    #     """
    #     matches = []
    #     for item in pyclbr.readmodule(module):
    #         # Adds direct subclasses.
    #         if inspect.issubclass(item, sourdough.base.Element):
    #             matches.append[item]
    #         else:
    #             # Adds subclasses of other subclasses.
    #             for subclass in self.contents.values():
    #                 if subclass(item, subclass):
    #                     matches.append[item]
    #     return matches
    
    
@dataclasses.dataclass
class Validator(Plugin, abc.ABC):
    """Base class for type validation and/or conversion.
    
    Args:
        accepts (Union[Sequence[Any], Any]): type(s) accepted by the parent 
            class either as an individual item, in a Mapping, or in a Sequence.
        stores (Any): a single type stored by the parent class. Defaults to 
            None.
                        
    """
    accepts: Union[Sequence[Any], Any] = dataclasses.field(
        default_factory = list)
    stores: Any = None

    """ Initialization Methods """
    
    def __post_init__(self):
        """Registers an instance with 'contents'."""
        # Calls initialization method of other inherited classes.
        try:
            super().__post_init__()
        except AttributeError:
            pass
        # Initializes 'contents' attribute.
        self._initial_validation()
        
    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def convert(self, contents: Any) -> Any:
        """Submodules must provide their own methods.
        
        This method should convert every one of the types in 'accepts' to the
        type in 'stores'.
        
        """
        pass   

    """ Public Methods """
    
    def verify(self, contents: Any) -> Any:
        """Verifies that 'contents' is one of the types in 'accepts'.
        
        Args:
            contents (Any): item(s) to be type validated.
            
        Raises:
            TypeError: if 'contents' is not one of the types in 'accepts'.
            
        Returns:
            Any: original contents if there is no TypeError.
        
        """
        accepts = sourdough.tools.tuplify(self.accepts)
        if all(isinstance(c, accepts) for c in contents):
            return contents
        else:
            raise TypeError(
                f'contents must be or contain one of the following types: ' 
                f'{self.accepts}')
       
    """ Private Methods """
    
    def _initial_validation(self) -> None:
        """Validates passed 'contents' on class initialization."""
        self.contents = self.convert(contents = self.contents)
        return self 
    

@dataclasses.dataclass
class Loader(abc.ABC):
    """ for lazy loading of python modules and objects.

    Args:
        modules Union[str, Sequence[str]]: name(s) of module(s) where object to 
            load is/are located. Defaults to an empty list.
        _loaded (ClassVar[Mapping[Any, Any]]): dict of str keys and previously
            loaded objects. This is checked first by the 'load' method to avoid
            unnecessary re-importation. Defaults to an empty dict.

    """
    modules: Union[str, Sequence[str]] = dataclasses.field(
        default_factory = list)
    _loaded: ClassVar[Mapping[Any, Any]] = {}
    
    """ Public Methods """

    def load(self, 
            key: str, 
            check_attributes: bool = False, 
            **kwargs) -> object:
        """Returns object named by 'key'.

        Args:
            key (str): name of class, function, or variable to try to import 
                from modules listed in 'modules'.

        Returns:
            object: imported from a python module.

        """
        imported = None
        if key in self._loaded:
            imported = self._loaded[key]
        else:
            if check_attributes:
                try:
                    key = getattr(self, key)
                except AttributeError:
                    pass
            for module in sourdough.tools.listify(self.modules):
                try:
                    imported = sourdough.tools.importify(
                        module = module, 
                        key = key)
                    break
                except (AttributeError, ImportError):
                    pass
        if imported is None:
            raise ImportError(f'{key} was not found in {self.modules}')
        elif kwargs:
            self._loaded[key] = imported(**kwargs)
            return self._loaded[key]
        else:
            self._loaded[key] = imported
            return self._loaded[key]
             