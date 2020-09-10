"""
test_project: tests Project class and created composite objects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)
"""

import dataclasses
import pathlib
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union

import sourdough


@dataclasses.dataclass
class Parser(sourdough.Structure):

    def perform(self):
        return


@dataclasses.dataclass
class Search(sourdough.Task):

    def perform(self):
        return   


@dataclasses.dataclass
class Slice(sourdough.Technique):

    def perform(self):
        return  


@dataclasses.dataclass
class Dice(sourdough.Technique):

    def perform(self):
        return 
    
    
@dataclasses.dataclass
class Find(sourdough.Technique):

    def perform(self):
        return 

    
@dataclasses.dataclass
class Locate(sourdough.Technique):

    def perform(self):
        return 

    
@dataclasses.dataclass
class Explode(sourdough.Technique):

    def perform(self):
        return 

    
@dataclasses.dataclass
class Dynamite(sourdough.Technique):
    
    name: str = 'annihilate'

    def perform(self):
        return 
    

def test_project():
    print('test registry', sourdough.Component.registry)
    assert 'parser' in sourdough.Component.registry
    project = sourdough.Project(
        name = 'cool_project',
        settings = pathlib.Path('tests') / 'composite_settings.py',
        automatic = True)
    print('test project', project.manager)
    return

# @dataclasses.dataclass
# class NewAction(sourdough.core.Action):
    
#     def perform(self, data: object) -> object:
#         data.new_value = 7
#         return data
        

# @dataclasses.dataclass
# class OtherAction(sourdough.core.Action):
    
#     def perform(self, data: object) -> object:
#         data.other_value = 'something'
#         return data


# @dataclasses.dataclass
# class AStructure(sourdough.Structure):
    
#     options: ClassVar[sourdough.core.Catalog] = sourdough.core.Catalog(
#         contents = {'new': NewAction()},
#         always_return_list = True)
  

# @dataclasses.dataclass 
# class SomeData(object):
    
#     new_value: int = 4
#     other_value: str = 'nothing'
    

# def test_Structure():
#     new_operator = NewAction()
#     other_operator = OtherAction()
#     another_operator = OtherAction()
#     some_data = SomeData()
#     more_data = SomeData()
#     # Tests OptionsMixin of a Structure instance.
#     AStructure.options.add(contents = {'other_operator': other_operator})
#     assert len(AStructure.options['all']) == 2
#     assert len(AStructure.options['none']) == 0
#     # Tests the 'add' method of a Structure instance.
#     a_Structure = AStructure()
#     a_Structure.add('other_operator')
#     a_Structure.add('new')
#     a_Structure.add(another_operator)
#     assert a_Structure['new_operator'] == new_operator
#     a_Structure.add([other_operator, another_operator])
#     assert a_Structure.contents == [
#         other_operator, 
#         new_operator, 
#         another_operator,
#         other_operator, 
#         another_operator]
#     # Tests 'perform' function of a Structure instance.
#     some_data = a_Structure.perform(item = some_data)
#     assert some_data.other_value == 'something'
#     # Tests manual iteration of a Structure instance.
#     for element in a_Structure:
#         more_data = element.perform(item = more_data)
#     assert more_data.other_value == 'something'
#     return

if __name__ == '__main__':
    test_project()