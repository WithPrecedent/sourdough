"""
.. module:: test iterables
:synopsis: tests core sourdough sequenced iterables
:author: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import dataclasses

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
class SomeData(object):
    
    new_value: int = 4
    other_value: str = 'nothing'
    

def test_worker():
    new_operator = NewOperator()
    other_operator = OtherOperator()
    another_operator = OtherOperator()
    some_data = SomeData()
    new_worker = sourdough.Plan()
    new_worker.add(new_operator)
    new_worker.add(other_operator)
    new_worker.add(another_operator)
    assert new_worker['new_operator'] == new_operator
    new_worker.add([other_operator, another_operator])
    assert new_worker.items == [
        new_operator, 
        other_operator, 
        another_operator,
        [other_operator, another_operator]]
    return


if __name__ == '__main__':
    test_worker()