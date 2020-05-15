"""
.. module:: worker
:synopsis: Worker and related base classes
:author: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import abc
import dataclasses
from typing import (
    Any, Callable, ClassVar, Dict, Iterable, List, Optional, Tuple, Union)

import sourdough


@dataclasses.dataclass
class Instructions(sourdough.ImporterBase):
    """Instructions for 'Worker' construction and usage.

    Arguments:
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. For example if a 
            class instance needs settings from the shared Settings instance, 
            'name' should match the appropriate section name in that Settings 
            instance. When subclassing, it is sometimes a good idea to use the 
            same 'name' attribute as the base class for effective coordination 
            between sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Component is called, 'name' is set to a snake 
            case version of the class name ('__class__.__name__').
        module (Optional[str]): name of module where object to use is located
            (can either be a sourdough or non-sourdough module). Defaults to
            'sourdough'.
        default_module (Optional[str]): a backup name of module where object to
            use is located (can either be a sourdough or non-sourdough module).
            Defaults to 'sourdough'. In general, subclasses should not override
            this attribute so that the generic base classes can be instanced if
            the specificied worker cannot be found.
        options (Optional[Union[str, Options]]): name of a Options 
            instance with various options available to a particular Worker. 
            Defaults to an empty Options.
        worker_kind (Optional[str]): name of worker kind which should match a
            key in Worker.options. In sourdough, two kinds are supported:
            'comparer' and 'sequencer'. However, further options can be added
            to Worker.options. Defaults to 'sequencer'.

    """
    name: Optional[str] = None
    module: Optional[str] = dataclasses.field(
        default_factory = lambda: 'sourdough')
    default_module: Optional[str] = dataclasses.field(
        default_factory = lambda: 'sourdough')
    author: Optional[str] = dataclasses.field(
        default_factory = lambda: 'Author')
    publisher: Optional[str] = dataclasses.field(
        default_factory = lambda: 'Publisher')
    reader: Optional[str] = dataclasses.field(
        default_factory = lambda: 'Reader')
    worker: Optional[str] = dataclasses.field(
        default_factory = lambda: 'sequencer')
    task: Optional[str] = dataclasses.field(
        default_factory = lambda: 'Task')
    

class Worker(abc.ABC):
    """Creates and instances different WorkerBase kinds.

    Arguments:
        kind (Optional[str]): name of Worker to return. 'kind' must
            correspond to a key in 'kinds'.
        default (ClassVar[str]): the name of the default object to instance. If 
            'kind' is not passed, 'default' is used. 'default' must correspond 
            to a key in 'kinds'. Defaults to None. It should be specified by a 
            subclass or by a user setting the class attribute if it is to be 
            used.
        kinds (ClassVar[MutableMapping]): a dictionary or other mapping of
            available options for object creation. Keys are the names of the
            'kind'. Values are the objects to create. Defaults to an empty
            dictionary.
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. For example if a 
            class instance needs settings from the shared Settings instance, 
            'name' should match the appropriate section name in that Settings 
            instance. When subclassing, it is sometimes a good idea to use the 
            same 'name' attribute as the base class for effective coordination 
            between sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Component is called, 'name' is set to a snake 
            case version of the class name ('__class__.__name__').
        settings (Optional[Settings]): shared project configuration settings.
        instructions (Optional[Instructions]): an instance with information to
            create and apply the essential components of a Worker. Defaults to
            None.

    Returns:
        Component: the factory uses the '__new__' method to return a different
            object instance with kwargs as the parameters.

    """
    settings: Optional[sourdough.Settings] = None
    design: Optional[sourdough.Design] = dataclasses.field(
        default_factory = lambda: sourdough.SerialDesign)
    
    """ Initialization Methods """
    
    def __new__(cls, 
            design: Optional[str] = None,
            instructions: Optional[str] = None,
            **kwargs) -> 'sourdough.Component':
        """Returns an instance from 'kinds'.

        Arguments:
            kind (Optional[str]): name of Component to return. 'kind' must
                correspond to a key in 'kinds'. Defaults to None. If not passed,
                the kind 'default' will be used.
            kwargs (Dict[str, Any]): parameters to pass to the object being 
                created.

        Returns:
            Component: an instance of an object stored in 'kinds'.
        
        """
        instance = super().__new__(design = design, **kwargs)
        for stage in ['author', 'publisher', 'reader']:
            setattr(instance, stage, getattr(instructions, stage)(**kwargs))
        return instance
