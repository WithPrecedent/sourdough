"""
.. module:: project test
:synopsis: tests Project class
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
    
    def apply(self, project: 'sourdough.project.Project') -> 'sourdough.project.Project':
        return project
   

@dataclasses.dataclass
class Slice(sourdough.project.Plan):
    pass


@dataclasses.dataclass
class Dice(sourdough.project.Plan):
    pass


@dataclasses.dataclass    
class Divider(sourdough.project.Plan):

    options: [ClassVar[Mapping[str, Any]]] = sourdough.base.Catalog(
        contents = {'slice': Slice, 'dice': Dice})


@dataclasses.dataclass      
class Parser(sourdough.project.Plan):

    options: [ClassVar[Mapping[str, Any]]] = sourdough.base.Catalog(
        contents = {'divider': Divider})


@dataclasses.dataclass
class Munger(sourdough.project.Plan):
    pass


def test_project():
    
    sourdough.project.Project.add_option(name = 'parser', option = Parser)
    sourdough.project.Project.add_option(name = 'munger', option = Munger)
    project = sourdough.project.Project()
    
    settings = pathlib.Path.cwd().joinpath('tests', 'composite_settings.py')
    sourdough.base.Manager.add_stage_option(
        name = 'distribute', 
        option = Distributor)
    director = sourdough.base.Manager(
        settings = settings,
        contents = ['draft', 'publish', 'distribute', 'apply'],
        project = project)
    print('test project overview', director.project.overview)
    # print('test parser contents', director.project['parser'].contents)
    return

if __name__ == '__main__':
    test_project()
    