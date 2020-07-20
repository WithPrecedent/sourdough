"""
.. module:: manager test
:synopsis: tests Manager class
:author: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import dataclasses
import pathlib
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union

import sourdough


@dataclasses.dataclass
class Distributor(sourdough.Stage):
    
    def apply(self, manager: 'sourdough.Manager') -> 'sourdough.Manager':
        return manager
   

@dataclasses.dataclass
class Slice(sourdough.Worker):
    pass


@dataclasses.dataclass
class Dice(sourdough.Worker):
    pass


@dataclasses.dataclass    
class Divider(sourdough.Worker):

    options: [ClassVar[Mapping[str, Any]]] = sourdough.Catalog(
        contents = {'slice': Slice, 'dice': Dice})


@dataclasses.dataclass      
class Parser(sourdough.Worker):

    options: [ClassVar[Mapping[str, Any]]] = sourdough.Catalog(
        contents = {'divider': Divider})


@dataclasses.dataclass
class Munger(sourdough.Worker):
    pass


def test_manager():
    
    sourdough.Manager.add_option(name = 'parser', option = Parser)
    sourdough.Manager.add_option(name = 'munger', option = Munger)
    manager = sourdough.Manager()
    
    settings = pathlib.Path.cwd().joinpath('tests', 'tree_settings.py')
    sourdough.add_stage_option(
        name = 'distribute', 
        option = Distributor)
    director = sourdough(
        settings = settings,
        contents = ['draft', 'publish', 'distribute', 'apply'],
        manager = manager)
    print('test manager overview', director.manager.overview)
    # print('test parser contents', director.manager['parser'].contents)
    return

if __name__ == '__main__':
    test_manager()
    