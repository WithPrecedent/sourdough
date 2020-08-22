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
class Parser(sourdough.Worker):

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
# class AWorker(sourdough.Worker):
    
#     options: ClassVar[sourdough.core.Catalog] = sourdough.core.Catalog(
#         contents = {'new': NewAction()},
#         always_return_list = True)
  

# @dataclasses.dataclass 
# class SomeData(object):
    
#     new_value: int = 4
#     other_value: str = 'nothing'
    

# def test_Worker():
#     new_operator = NewAction()
#     other_operator = OtherAction()
#     another_operator = OtherAction()
#     some_data = SomeData()
#     more_data = SomeData()
#     # Tests OptionsMixin of a Worker instance.
#     AWorker.options.add(contents = {'other_operator': other_operator})
#     assert len(AWorker.options['all']) == 2
#     assert len(AWorker.options['none']) == 0
#     # Tests the 'add' method of a Worker instance.
#     a_Worker = AWorker()
#     a_Worker.add('other_operator')
#     a_Worker.add('new')
#     a_Worker.add(another_operator)
#     assert a_Worker['new_operator'] == new_operator
#     a_Worker.add([other_operator, another_operator])
#     assert a_Worker.contents == [
#         other_operator, 
#         new_operator, 
#         another_operator,
#         other_operator, 
#         another_operator]
#     # Tests 'perform' function of a Worker instance.
#     some_data = a_Worker.perform(item = some_data)
#     assert some_data.other_value == 'something'
#     # Tests manual iteration of a Worker instance.
#     for element in a_Worker:
#         more_data = element.perform(item = more_data)
#     assert more_data.other_value == 'something'
#     return

if __name__ == '__main__':
    test_project()