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
class APlan(sourdough.base.Plan):
    
    options: ClassVar['sourdough.base.Catalog'] = sourdough.base.Catalog(
        contents = {'new': NewTask()},
        always_return_list = True)
  

@dataclasses.dataclass 
class SomeData(object):
    
    new_value: int = 4
    other_value: str = 'nothing'
    

def test_plan():
    new_operator = NewTask()
    other_operator = OtherTask()
    another_operator = OtherTask()
    some_data = SomeData()
    more_data = SomeData()
    # Tests OptionsMixin of a Plan instance.
    APlan.options.add(component = other_operator)
    assert len(APlan.options['all']) == 2
    assert len(APlan.options['none']) == 0
    # Tests the 'add' method of a Plan instance.
    a_plan = APlan()
    a_plan.add('other_operator')
    a_plan.add('new')
    a_plan.add(another_operator)
    assert a_plan['new_operator'] == new_operator
    a_plan.add([other_operator, another_operator])
    assert a_plan.contents == [
        other_operator, 
        new_operator, 
        another_operator,
        other_operator, 
        another_operator]
    # Tests 'apply' function of a Plan instance.
    some_data = a_plan.apply(data = some_data)
    assert some_data.other_value == 'something'
    # Tests manual iteration of a Plan instance.
    for component in a_plan:
        more_data = component.apply(data = more_data)
    assert more_data.other_value == 'something'
    return


if __name__ == '__main__':
    test_plan()