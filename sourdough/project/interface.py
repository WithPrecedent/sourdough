"""
interface: user interface for sourdough project construction and iteration
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents: 
    Project (Hybrid): access point and interface for creating and implementing
        sourdough projects.

"""
from __future__ import annotations
from _typeshed import NoneType
import dataclasses
import functools
import inspect
import logging
import pathlib
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Set, Tuple, Type, Union)
import warnings

import sourdough 


logger = logging.getLogger()
 

# @dataclasses.dataclass
# class Validator(object):
#     """
#     """
#     project: Project
#     accepts: Tuple[Type]
#     returns: type
#     parameters: Tuple[str] = tuple()
#     additions: Tuple[str] = tuple()
    
#     """ Public Methods """
    
#     @functools.singledispatchmethod
#     def convert(self, item) -> Any:
#         """[summary]

#         Args:
#             item ([type]): [description]
#             instance (object, optional): [description]. Defaults to None.

#         Raises:
#             TypeError: [description]

#         Returns:
#             Any: [description]
            
#         """
#         if isinstance(item, self.returns):
#             converted = item
#             for addition in self.additions:
#                 setattr(converted, addition, getattr(self.project, addition))
#         elif item == self.returns:
#             kwargs = {}
#             for parameter in self.parameters:
#                 kwargs[parameter] = getattr(self.project, parameter)
#             converted = item(**kwargs)
#         else:
#             raise TypeError(
#                 f'Must be these types: {self.accepts}, or {self.returns}')
#         return converted

# settings_validator = Validator(
#     acccepts = [str, pathlib.Path], 
#     returns = sourdough.Settings)          

    
# @functools.singledispatch
# def validate(self, item, returns: Type, project: Project) -> Any:
#     """Validates 'settings' or converts it to a Configuration instance."""
#     raise TypeError(
#             'settings must be a Configuration, Path, str, or None type.')

# @validate.register
# def _(self, item: object) -> sourdough.Settings:
#     return item

# @validate.register
# def _(self, item: Type) -> sourdough.Settings:
#     return item()
    
# @validate.register
# def _(self, settings: str) -> sourdough.Settings:
#     return self.bases.settings(contents = settings)

# @validate.register
# def _(self, settings: pathlib.Path) -> sourdough.Settings:
#     return self.bases.settings(contents = settings)

# @validate.register
# def _(self, settings: None) -> sourdough.Settings:
#     return self.bases.settings(contents = settings)


@dataclasses.dataclass
class Project(sourdough.quirks.Director):
    """Constructs, organizes, and implements a a collection of projects.

    Args:
        contents (Mapping[str, object]): keys are names of objects stored and 
            values are the stored object. Defaults to an empty dict.
        builder (Constructor): related builder which constructs objects to be 
            stored in 'contents'. subclasses 
            stored in 'options'. Defaults to an empty list.
        settings (Union[Type[], str, pathlib.Path]]): a Configuration-compatible class,
            a str or pathlib.Path containing the file path where a file of a 
            supported file type with settings for a Configuration instance is 
            located. Defaults to the default Configuration instance.
        clerk (Union[Type, str, pathlib.Path]]): a Clerk-compatible class or a 
            str or pathlib.Path containing the full path of where the root 
            folder should be located for file input and output. A 'clerk' must 
            contain all file path and import/export methods for use throughout 
            sourdough. Defaults to the default Clerk instance. 
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example if a 
            sourdough instance needs settings from a Configuration instance, 'name' 
            should match the appropriate section name in the Configuration instance. 
            If it is None, the 'name' will be attempted to be inferred from the 
            first section name in 'settings' after 'general' and 'files'. If 
            that fails, 'name' will be the snakecase name of the class. Defaults 
            to None. 
        identification (str): a unique identification name for a Director 
            instance. The name is used for creating file folders related to the 
            project. If it is None, a str will be created from 'name' and the 
            date and time. Defaults to None.   
        automatic (bool): whether to automatically advance 'director' (True) or 
            whether the director must be advanced manually (False). Defaults to 
            True.
        data (object): any data object for the project to be applied. If it is
            None, an instance will still execute its workflow, but it won't
            apply it to any external data. Defaults to None.  
        validations (Sequence[str]): 
        bases (ClassVar[object]): contains information about default base 
            classes used by a Director instance. Defaults to an instance of 
            SimpleBases.

    """
    contents: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    builder: sourdough.quirks.Constructor = None
    settings: Union[sourdough.types.Configuration, str, pathlib.Path] = None
    clerk: Union[sourdough.Clerk, str, pathlib.Path] = None
    bases: object = sourdough.project.bases
    factory: Union[sourdough.base.Factory, str] = None
    builder: Union[sourdough.base.Builder, str] = None
    name: str = None
    identification: str = None
    automatic: bool = True
    data: Any = None
    validations: Sequence[str] = dataclasses.field(default_factory = lambda: [
        'settings', 'name', 'identification', 'clerk', 'directors', 'factory'])
    
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent and/or mixin initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass
        # Removes various python warnings from console output.
        warnings.filterwarnings('ignore')
        # Calls validation methods based on items listed in 'validations'.
        self.validate()
        # Adds 'general' section attributes from 'settings'.
        self.settings.inject(instance = self)
        # Sets index for iteration.
        self.index = 0
        # Advances through 'contents' if 'automatic' is True.
        if self.automatic:
            print('test yes auto')
            self.complete()
            
    """ Public Methods """
    
    def add_director(self, director: Union[str, Type, object]) -> None:
        """

        Args:
            director (Union[str, Type, object]): [description]
        """
        self.directors.append(self._validate_director(director = director))
        return self  
    
    def validate(self, validations: List[str] = None) -> None:
        """Validates or converts stored attributes.
        
        Args:
            validations (List[str]): a list of attributes that need validating.
                Each item in 'validations' should also have a corresponding
                method named f'_validate_{item}'. If not passed, the
                'validations' attribute will be used instead. Defaults to None. 
        
        """
        if validations is None:
            validations = self.validations
        # Calls validation methods based on items listed in 'validations'.
        for item in validations:
            kwargs = {item: getattr(self, item)}
            setattr(self, item, getattr(self, f'_validate_{item}')(**kwargs))
        return self      
                                    
    """ Private Methods """
    
    @functools.singledispatchmethod
    def _validate_settings(self, settings) -> sourdough.Settings:
        """Validates 'settings' or converts it to a Configuration instance."""
        raise TypeError(
                'settings must be a Configuration, Path, str, or None type.')
    
    @_validate_settings.register
    def _(self, settings: sourdough.Settings) -> sourdough.Settings:
        return settings

    @_validate_settings.register
    def _(self, settings: Type[sourdough.Settings]) -> sourdough.Settings:
        return settings()
        
    @_validate_settings.register
    def _(self, settings: str) -> sourdough.Settings:
        return self.bases.settings(contents = settings)

    @_validate_settings.register
    def _(self, settings: pathlib.Path) -> sourdough.Settings:
        return self.bases.settings(contents = settings)
    
    @_validate_settings.register
    def _(self, settings: None) -> sourdough.Settings:
        return self.bases.settings(contents = settings)
       
    @functools.singledispatchmethod
    def _validate_name(self, name) -> str:
        """Creates 'name' if one doesn't exist.
        
        If 'name' was not passed, this method first tries to infer 'name' as the 
        first appropriate section name in 'settings'. If that doesn't work, it 
        uses the snakecase name of the class.
        
        """
        raise TypeError('name must be a str or None type.')

    @_validate_name.register
    def _(self, name: str) -> str:
        return name
    
    @_validate_name.register
    def _validate_name(self, name: None) -> str:
        try:
            node_sections = self.settings.excludify(subset = self.rules.skip)
            return node_sections.keys()[0]
        except IndexError:
            return sourdough.tools.snakify(self.__class__)
    
    @functools.singledispatchmethod
    def _validate_identification(self, identification) -> str:
        """Creates unique 'identification' if one doesn't exist.
        
        By default, 'identification' is set to the 'name' attribute followed by
        an underscore and the date and time.
        
        """
        raise TypeError('identification must be a str or None type.')

    @_validate_identification.register
    def _(self, identification: str) -> str:
        return identification
        
    @_validate_identification.register
    def _(self, identification: None) -> str:
        return sourdough.tools.datetime_string(prefix = self.name)
    
    @functools.singledispathmethod
    def _validate_clerk(self, clerk) -> sourdough.files.Clerk:
        """Validates 'clerk' or converts it to a Clerk instance.
        
        If a file path is passed, that becomes the root folder with the default
        file structure in the default Clerk instance.
        
        If an object is passed, its 'settings' attribute is replaced with this 
        instance's 'settings'.
        
        """
        raise TypeError('clerk must be a Clerk, Path, str, or None type.')
    
    @_validate_clerk.register
    def _(self, clerk: sourdough.files.clerk) -> sourdough.files.Clerk:  
        return clerk  
    
    @_validate_clerk.register
    def _(self, clerk: Type[sourdough.files.clerk]) -> sourdough.files.Clerk:  
        return clerk(settings = self.settings)

    @_validate_clerk.register
    def _(self, clerk: str) -> sourdough.files.Clerk:  
        return self.bases.clerk(root_folder = clerk, settings = self.settings) 
    
    @_validate_clerk.register
    def _(self, clerk: pathlib.Path) -> sourdough.files.Clerk:  
        return self.bases.clerk(root_folder = clerk, settings = self.settings)
    
    @_validate_clerk.register
    def _(self, clerk: NoneType) -> sourdough.files.Clerk:  
        return self.bases.clerk(root_folder = clerk, settings = self.settings)
    
    def _validate_directors(self) -> None:
        """Validates 'contents' or converts it to Director instances.
        
        """
        if not self.contents:
            try:
                self.contents = self.settings[self.name][
                    f'{self.name}_directors']
            except KeyError:
                pass
        new_contents = []
        for item in self.contents:
            new_contents.append(self._validate_director(director = item))
        self.contents = new_contents
        return self

    @functools.singledispathmethod
    def _validate_director(self, director) -> sourdough.Director:
        """
        """
        raise TypeError('director must be a str or Director type')

    @_validate_director.register
    def _(self, director: str) -> sourdough.Director:
        director = self.bases.get_class(name = director, kind = 'director')
        return director(name = director, project = self)'
    
    @_validate_director.register
    def _(self, director: sourdough.Director) -> sourdough.Director:
        director.project = self
        return director
    
    @_validate_director.register
    def _(self, director: Type[sourdough.Director]) -> sourdough.Director:
        return director(project = self)
    
    @functools.singledispathmethod
    def _validate_factory(self, factory) -> sourdough.project.bases.factory:
        """Validates 'factory' or converts it to a Factory instance.'"""
        if isinstance(self.factory, self.bases.factory):
            pass
        elif isinstance(self.factory, str):
            self.factory = self.bases.get_class(
                name = self.factory, 
                kind = 'factory')()
        elif inspect.isclass(self.factory):
            self.factory = self.factory()
        elif self.factory is None:
            self.factory = self.bases.factory()
        else:
            raise TypeError('factory must be a Factory, str, or None type.')
        return self
       
    """ Dunder Methods """     

    def __iter__(self) -> Iterable:
        """Returns iterable of a Project instance.

        Returns:
            Iterable: of the Project instance.

        """
        return iter(self)
 
    def __next__(self) -> object:
        """Returns completed Director instance.

        Returns:
            Any: item project by the 'create' method of a Creator.
            
        """
        if self.index < len(self.directors):
            director = self.directors[self.index]
            if hasattr(self, 'verbose') and self.verbose:
                print(f'Starting {director.__name__}')
            director.complete()
            self.index += 1
            if hasattr(self, 'verbose') and self.verbose:
                print(f'Completed {director.__name__}')
        else:
            raise IndexError()
        return self
           