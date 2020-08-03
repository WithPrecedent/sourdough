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
class NewAction(sourdough.Action):
    
    def perform(self, data: object) -> object:
        data.new_value = 7
        return data
        

@dataclasses.dataclass
class OtherComponent(sourdough.Component):
    
    def perform(self, data: object) -> object:
        data.other_value = 'something'
        return data
    

def test_component():
    new_operator = NewAction()
    other_component= OtherComponent(name = 'something')
    another_operator = OtherComponent
    assert new_operator.name == 'new_action'
    assert other_component.name == 'something'
    assert another_operator.get_name() == 'other_component'
    assert str(new_operator) == '\n'.join(
        ['sourdough NewAction', 'name: new_action'])
    return


if __name__ == '__main__':
    test_component()