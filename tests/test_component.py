"""
.. module:: test component
:synopsis: tests Component class
:author: Corey Rayburn Yung
:copyright: 2019-2020
:license: Apache-2.0
"""

import os
import sys

sys.path.insert(0, os.path.join('..', 'sourdough'))

import sourdough


class NewComponent(sourdough.Component):

    def __post_init__(self) -> None:
        super().__post_init__()
        assert self.name == 'new_component'
        return self

class NewNewComponent(NewComponent):

    def __post_init__(self) -> None:
        sourdough.Component.__post_init__(self)
        assert self.name == 'new_new_component'
        return self

class OtherComponent(sourdough.Component):
    pass

def test_component():
    new_component = NewComponent()
    new_new_component = NewNewComponent()
    assert new_component.name in sourdough.Component.library
    assert new_new_component.name in sourdough.Component.library
    sourdough.Component.register(OtherComponent)
    assert 'other_component' in sourdough.Component.library
    return

if __name__ == '__main__':
    test_component()