"""
.. module:: project test
:synopsis: tests Project class
:author: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import dataclasses
import pathlib
from typing import (
    Any, Callable, ClassVar, Dict, Iterable, List, Optional, Tuple, Union)

import sourdough


@dataclasses.dataclass
class Distributor(sourdough.Stage):
    
    def apply(self, project: 'sourdough.Project') -> 'sourdough.Project':
        return project
   

@dataclasses.dataclass
class Slice(sourdough.Worker):
    pass


@dataclasses.dataclass
class Dice(sourdough.Worker):
    pass


@dataclasses.dataclass    
class Divider(sourdough.Worker):

    options: [ClassVar[Dict[str, Any]]] = sourdough.Options(
        contents = {'slice': Slice, 'dice': Dice})


@dataclasses.dataclass      
class Parser(sourdough.Worker):

    options: [ClassVar[Dict[str, Any]]] = sourdough.Options(
        contents = {'divider': Divider})


@dataclasses.dataclass
class Munger(sourdough.Worker):
    pass


def test_project():
    
    sourdough.Project.add_option(name = 'parser', option = Parser)
    sourdough.Project.add_option(name = 'munger', option = Munger)
    project = sourdough.Project()
    
    settings = pathlib.Path.cwd().joinpath('tests', 'composite_settings.py')
    sourdough.Director.add_stage_option(
        name = 'distribute', 
        option = Distributor)
    director = sourdough.Director(
        settings = settings,
        contents = ['draft', 'edit', 'publish', 'distribute', 'apply'],
        project = project)
    print('test project overview', director.project.overview)
    # print('test parser contents', director.project['parser'].contents)
    return

if __name__ == '__main__':
    test_project()
    