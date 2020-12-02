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
class Parser(sourdough.workflows.Contest):

    pass


@dataclasses.dataclass
class Search(sourdough.elements.Step):

    pass   


@dataclasses.dataclass
class Divide(sourdough.elements.Step):

    pass   
    
    
@dataclasses.dataclass
class Destroy(sourdough.elements.Step):

    pass   
    

@dataclasses.dataclass
class Slice(sourdough.elements.Technique):

    pass  


@dataclasses.dataclass
class Dice(sourdough.elements.Technique):

    pass 
    
    
@dataclasses.dataclass
class Find(sourdough.elements.Technique):

    pass 

    
@dataclasses.dataclass
class Locate(sourdough.elements.Technique):

    pass 

    
@dataclasses.dataclass
class Explode(sourdough.elements.Technique):

    pass 

    
@dataclasses.dataclass
class Dynamite(sourdough.elements.Technique):
    
    name: str = 'annihilate'

    pass 
    

def test_project():
    assert 'parser' in sourdough.Component.registry
    parser = Parser()
    dynamite = Dynamite()
    assert 'parser' in sourdough.Component.library
    assert 'annihilate' in sourdough.Component.library
    assert 'annihilate' not in sourdough.Component.registry
    project = sourdough.Project(
        name = 'cool_project',
        settings = pathlib.Path('tests') / 'composite_settings.py',
        automatic = True)
    print('test project', project['results'])
    return


if __name__ == '__main__':
    test_project()