"""
hybrids: Hybrid subclasses used in sourdough projects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Worker (Hybrid): iterator of stored Components.

The sourdough hybrid composite design emphasizes:
    1) Independence: components of the tree do not require knowledge of parent
        objects to function. The primitive Technique objects can be completely
        detached from the tree and still function. Any segment of the tree can
        be removed from the rest and operate and be serialized.
    2) Flexibility: tree objects can contain Worker, Task, and/or Technique 
        instances. There are no limits on the number of children that the tree 
        objects can have. The trees can be constructed for different iteration 
        patterns (using the 'design') attribute or manually built by users.
    3) Accessibility: because sourdough tree objects inherit from Hybrid,
        users can access the trees with list and dictionary methods. Further,
        'workers', 'tasks', and 'techniques' properties all for instance access
        to the various types of contained objects.
    4) Familiarity: for people without a computer science background, the varied
        language of trees can be confusing: nodes, leafs, root, edges, etc. 
        Instead, sourdough follows an employment hierarchy with a Manager, 
        Workers, Tasks (optional), and Techniques. The hope is that these labels
        better indicate the functionality of the objects within the tree 
        design.

"""

import dataclasses
import textwrap
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union

import sourdough


@dataclasses.dataclass
class Worker(sourdough.Hybrid):
    """Iterator in sourdough composite projects.

    Worker inherits all of the differences between a Hybrid and a python list.
    
    A Worker differs from a Hybrid in 3 significant ways:
        1) It has a 'structure' attribute which indicates how the contained 
            iterator should be ordered. 
        2) An 'overview' property is added which returns a dict of the names
            of the various parts of the tree objects. It doesn't include the
            hierarchy itself. Rather, it includes lists of all the types of
            sourdough.Component objects.
        
    Args:
        contents (Sequence[sourdough.Component]]): stored iterable of Action
            subclasses. Defaults to an empty list.
        name (str): creates the name of a class instance that is used for 
            internal referencing throughout sourdough. For example if a 
            sourdough instance needs settings from a Settings instance, 'name' 
            should match the appropriate section name in the Settings instance. 
            When subclassing, it is sometimes a good idea to use the same 'name' 
            attribute as the base class for effective coordination between 
            sourdough classes. Defaults to None. If 'name' is None and 
            '__post_init__' of Component is called, 'name' is set based upon
            the 'get_name' method in sourdough.Component. If that method is not 
            overridden by a subclass instance, 'name' will be assigned to the 
            snake case version of the class name ('__class__.__name__').
        structure (sourdough.Structure): design for the organization, iteration,
            and composition of 'contents'.
        _default (Any): default value to use when there is a KeyError using the
            'get' method.

    Attributes:
        contents (Sequence[sourdough.Component]): all objects in 'contents' must 
            be sourdough Component subclass instances and are stored in a list.

    ToDo:
        draw: a method for producting a diagram of a Worker instance's 
            'contents' to the console or a file.
            
    """
    contents: Union[
        'sourdough.Component',
        Mapping[str, 'sourdough.Component'], 
        Sequence['sourdough.Component']] = dataclasses.field(
            default_factory = list)
    name: str = None
    structure: 'sourdough.Structure' = None
    _default: Any = None

    """ Properties """
    
    @property
    def overview(self) -> Mapping[str, Sequence[str]]:
        """Returns a dict snapshot of a Worker subclass instance.
        
        Returns:
            Mapping[str, Sequence[str]]: configured according to the 
                '_get_overview' method.
        
        """
        return self._get_overview()

    """ Public Methods """ 
        
    # def perform(self, data: object = None) -> object:
    #     """Applies stored Action instances to 'data'.

    #     Args:
    #         data (object): an object to be modified and/or analyzed by stored 
    #             Action instances. Defaults to None.

    #     Returns:
    #         object: data, possibly with modifications made by Operataor 
    #             instances. If data is not passed, no object is returned.
            
    #     """
    #     if data is None:
    #         for action in iter(self):
    #             action.perform()
    #         return self
    #     else:
    #         for action in iter(self):
    #             data = action.perform(item = data)
    #         return data
    
    """ Dunder Methods """

    # def __str__(self) -> str:
    #     """Returns default string representation of an instance.

    #     Returns:
    #         str: default string representation of an instance.

    #     """
    #     if hasattr(self.structure, 'name'):
    #         return '\n'.join([textwrap.dedent(f'''
    #             sourdough {self.__class__.__name__}
    #             name: {self.name}
    #             structure: {self.structure.name}
    #             contents:'''),
    #             f'''{textwrap.indent(str(self.contents), '    ')}'''])
    #     else:
    #         return '\n'.join([textwrap.dedent(f'''
    #             sourdough {self.__class__.__name__}
    #             name: {self.name}
    #             structure: {self.structure}
    #             contents:'''),
    #             f'''{textwrap.indent(str(self.contents), '    ')}'''])
            
    """ Private Methods """

    def _get_type(self, 
            item: 'sourdough.Component', 
            component: 'sourdough.Component') -> Sequence[
                'sourdough.Component']: 
        """[summary]

        Args:
            item (sourdough.Component): [description]
            sourdough.Component (sourdough.Component): [description]

        Returns:
            Sequence[sourdough.Component]:
            
        """
        if isinstance(item, sourdough.Component):
            return [item]
        else:
            return []
          
    def _get_overview(self) -> Mapping[str, Sequence[str]]:
        """Returns outline of the overal project tree.
        
        Returns:  
            Mapping[str, Sequence[str]]: the names of the contained Component
                subclasses arranged by supported types.
                
        """
        if self.structure is not None:
            overview = {
                'name': self.name, 
                'structure': self.structure.name}
            for key, value in self.structure.options.items():
                overview[f'{key}s'] = self.find(
                    self._get_type, 
                    component = value)
        else:
            raise ValueError(
                'structure must be a Structure for an overview to be created.')
        return overview
