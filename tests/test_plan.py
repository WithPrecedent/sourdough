"""
.. module:: test worker
:synopsis: tests SequenceBase class
:author: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import sourdough


class NewComponent(sourdough.Component):
    pass

class OtherComponent(sourdough.Component):
    pass

def test_worker():
    new_component = NewComponent()
    other_component = OtherComponent()
    another_component = OtherComponent()
    new_worker = sourdough.base.SequenceBase()
    new_worker.add(new_component)
    new_worker.add(other_component)
    new_worker.add(another_component)
    assert new_worker['new_component'] == new_component
    new_worker.add([other_component, another_component])
    assert new_worker.items == [
        new_component, 
        other_component, 
        another_component,
        [other_component, another_component]]
    return


if __name__ == '__main__':
    test_worker()