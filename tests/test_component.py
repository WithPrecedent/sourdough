"""
.. module:: test component
:synopsis: tests Component class
:author: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import dataclasses

import sourdough


@dataclasses.dataclass
class NewComponent(sourdough.Component):

    pass


@dataclasses.dataclass
class NewNewComponent(NewComponent):

    pass


@dataclasses.dataclass
class OtherComponent(sourdough.Component):
    
    pass


def test_component():
    new_component = NewComponent()
    new_new_component = NewNewComponent()
    assert new_component.name in sourdough.Component.catalog
    assert new_component.name in sourdough.Component.library
    assert new_new_component.name in sourdough.Component.catalog
    assert new_new_component.name in sourdough.Component.library
    # sourdough.Component.register(OtherComponent)
    # assert 'other_component' in sourdough.Component.catalog
    return

if __name__ == '__main__':
    test_component()