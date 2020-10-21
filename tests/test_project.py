"""
test_project: tests Project class and created composite objects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)
"""

import dataclasses
import pathlib
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Union)

import sourdough


@dataclasses.dataclass
class Parser(sourdough.project.workers.Contest):

    def perform(self):
        return


@dataclasses.dataclass
class Search(sourdough.components.Step):

    def perform(self):
        return   


@dataclasses.dataclass
class Divide(sourdough.components.Step):

    def perform(self):
        return   
    
    
@dataclasses.dataclass
class Destroy(sourdough.components.Step):

    def perform(self):
        return   
    

@dataclasses.dataclass
class Slice(sourdough.components.Technique):

    def perform(self):
        return  


@dataclasses.dataclass
class Dice(sourdough.components.Technique):

    def perform(self):
        return 
    
    
@dataclasses.dataclass
class Find(sourdough.components.Technique):

    def perform(self):
        return 

    
@dataclasses.dataclass
class Locate(sourdough.components.Technique):

    def perform(self):
        return 

    
@dataclasses.dataclass
class Explode(sourdough.components.Technique):

    def perform(self):
        return 

    
@dataclasses.dataclass
class Dynamite(sourdough.components.Technique):
    
    label: str = 'annihilate'

    def perform(self):
        return 
    

def test_project():
    assert 'parser' in sourdough.inventory.components
    project = sourdough.Project(
        name = 'cool_project',
        settings = pathlib.Path('tests') / 'composite_settings.py',
        automatic = True)
    print('test project', project.results.plan)
    return


if __name__ == '__main__':
    test_project()