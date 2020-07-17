"""
.. module:: test iterables
:synopsis: tests core sourdough sequenced iterables and mixins
:author: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import dataclasses
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union

import sourdough


@dataclasses.dataclass
class NewTask(sourdough.base.Task):
    
    def apply(self, data: object) -> object:
        data.new_value = 7
        return data
        

@dataclasses.dataclass
class OtherTask(sourdough.base.Task):
    
    def apply(self, data: object) -> object:
        data.other_value = 'something'
        return data


@dataclasses.dataclass
class AWorker(sourdough.manager.Worker):
    
    options: ClassVar['sourdough.base.Catalog'] = sourdough.base.Catalog(
        contents = {'new': NewTask()},
        always_return_list = True)
  

@dataclasses.dataclass 
class SomeData(object):
    
    new_value: int = 4
    other_value: str = 'nothing'
    

def test_Worker():
    new_operator = NewTask()
    other_operator = OtherTask()
    another_operator = OtherTask()
    some_data = SomeData()
    more_data = SomeData()
    # Tests OptionsMixin of a worker instance.
    AWorker.options.add(component = other_operator)
    assert len(AWorker.options['all']) == 2
    assert len(AWorker.options['none']) == 0
    # Tests the 'add' method of a worker instance.
    a_Worker = AWorker()
    a_Worker.add('other_operator')
    a_Worker.add('new')
    a_Worker.add(another_operator)
    assert a_Worker['new_operator'] == new_operator
    a_Worker.add([other_operator, another_operator])
    assert a_Worker.contents == [
        other_operator, 
        new_operator, 
        another_operator,
        other_operator, 
        another_operator]
    # Tests 'apply' function of a worker instance.
    some_data = a_Worker.apply(data = some_data)
    assert some_data.other_value == 'something'
    # Tests manual iteration of a worker instance.
    for component in a_Worker:
        more_data = component.apply(data = more_data)
    assert more_data.other_value == 'something'
    return


if __name__ == '__main__':
    test_Worker()