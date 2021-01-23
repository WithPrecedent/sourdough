"""
test_project: tests Project class and created composite objects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)
"""

import dataclasses
import pathlib
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import sourdough


@dataclasses.dataclass
class Parser(sourdough.project.Manager):

    pass


@dataclasses.dataclass
class Search(sourdough.project.Step):

    pass   


@dataclasses.dataclass
class Divide(sourdough.project.Step):

    pass   
    
    
@dataclasses.dataclass
class Destroy(sourdough.project.Step):

    pass   
    

@dataclasses.dataclass
class Slice(sourdough.project.Technique):

    pass  


@dataclasses.dataclass
class Dice(sourdough.project.Technique):

    pass 
    
    
@dataclasses.dataclass
class Find(sourdough.project.Technique):

    pass 

    
@dataclasses.dataclass
class Locate(sourdough.project.Technique):

    pass 

    
@dataclasses.dataclass
class Explode(sourdough.project.Technique):

    pass 

    
@dataclasses.dataclass
class Dynamite(sourdough.project.Technique):
    
    name: str = 'annihilate'
# 
    pass 
    

def test_project():
    assert 'parser' in sourdough.project.Manager.library
    find = Find()
    dynamite = Dynamite()
    assert 'find' in sourdough.project.Component.library
    assert 'annihilate' not in sourdough.project.Component.library
    project = sourdough.Project(
        name = 'cool_project',
        settings = pathlib.Path('tests') / 'composite_settings.py',
        automatic = True)
    print('test parser contents', project['parser'].contents)
    print('test parser', project['parser'].keys())
    return


if __name__ == '__main__':
    test_project()
    