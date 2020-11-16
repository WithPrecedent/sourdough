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
class Parser(sourdough.workflows.Contest):

    def apply(self):
        return


@dataclasses.dataclass
class Search(sourdough.elements.Step):

    def apply(self):
        return   


@dataclasses.dataclass
class Divide(sourdough.elements.Step):

    def apply(self):
        return   
    
    
@dataclasses.dataclass
class Destroy(sourdough.elements.Step):

    def apply(self):
        return   
    

@dataclasses.dataclass
class Slice(sourdough.elements.Technique):

    def apply(self):
        return  


@dataclasses.dataclass
class Dice(sourdough.elements.Technique):

    def apply(self):
        return 
    
    
@dataclasses.dataclass
class Find(sourdough.elements.Technique):

    def apply(self):
        return 

    
@dataclasses.dataclass
class Locate(sourdough.elements.Technique):

    def apply(self):
        return 

    
@dataclasses.dataclass
class Explode(sourdough.elements.Technique):

    def apply(self):
        return 

    
@dataclasses.dataclass
class Dynamite(sourdough.elements.Technique):
    
    name: str = 'annihilate'

    def apply(self):
        return 
    

def test_project():
    assert 'parser' in sourdough.project.resources.components
    project = sourdough.Project(
        name = 'cool_project',
        settings = pathlib.Path('tests') / 'composite_settings.py',
        automatic = True)
    print('test project', project['results'])
    return


if __name__ == '__main__':
    test_project()