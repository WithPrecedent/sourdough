"""
.. module:: test iterables
:synopsis: tests core sourdough sequenced iterables
:author: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import dataclasses
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union

import sourdough


@dataclasses.dataclass
class NewOperator(sourdough.Operator):
    
    def apply(self, data: object) -> object:
        data.new_value = 7
        return data
        

@dataclasses.dataclass
class OtherOperator(sourdough.Operator):
    
    def apply(self, data: object) -> object:
        data.other_value = 'something'
        return data

@dataclasses.dataclass
class APlan(sourdough.Plan):
    
    options: ClassVar['sourdough.Catalog'] = sourdough.Catalog(
        contents = {'new': NewOperator()},
        always_return_list = True)
  

@dataclasses.dataclass 
class SomeData(object):
    
    new_value: int = 4
    other_value: str = 'nothing'
    

def test_plan():
    new_operator = NewOperator()
    other_operator = OtherOperator()
    another_operator = OtherOperator()
    some_data = SomeData()
    APlan.options.add(component = other_operator)
    a_plan = APlan()
    a_plan.add('other_operator')
    a_plan.add('new')
    a_plan.add(another_operator)
    assert a_plan['new_operator'] == new_operator
    a_plan.add([other_operator, another_operator])
    print('test contents', a_plan.contents)
    assert a_plan.contents == [
        other_operator, 
        new_operator, 
        another_operator,
        [other_operator, another_operator]]
    return


if __name__ == '__main__':
    test_plan()