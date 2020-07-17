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
class Distributor(sourdough.base.Stage):
    
    def apply(self, manager: 'sourdough.manager.Manager') -> 'sourdough.manager.Manager':
        return manager
   

@dataclasses.dataclass
class Slice(sourdough.manager.Worker):
    pass


@dataclasses.dataclass
class Dice(sourdough.manager.Worker):
    pass


@dataclasses.dataclass    
class Divider(sourdough.manager.Worker):

    options: [ClassVar[Mapping[str, Any]]] = sourdough.base.Catalog(
        contents = {'slice': Slice, 'dice': Dice})


@dataclasses.dataclass      
class Parser(sourdough.manager.Worker):

    options: [ClassVar[Mapping[str, Any]]] = sourdough.base.Catalog(
        contents = {'divider': Divider})


@dataclasses.dataclass
class Munger(sourdough.manager.Worker):
    pass


def test_manager():
    
    sourdough.manager.Manager.add_option(name = 'parser', option = Parser)
    sourdough.manager.Manager.add_option(name = 'munger', option = Munger)
    manager = sourdough.manager.Manager()
    
    settings = pathlib.Path.cwd().joinpath('tests', 'composite_settings.py')
    sourdough.base.Project.add_stage_option(
        name = 'distribute', 
        option = Distributor)
    director = sourdough.base.Project(
        settings = settings,
        contents = ['draft', 'publish', 'distribute', 'apply'],
        manager = manager)
    print('test manager overview', director.manager.overview)
    # print('test parser contents', director.manager['parser'].contents)
    return

if __name__ == '__main__':
    test_manager()
    