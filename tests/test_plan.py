"""
.. module:: test plan
:synopsis: tests Plan class
:author: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import sourdough


class NewComponent(sourdough.Component):
    pass

class OtherComponent(sourdough.Component):
    pass

def test_plan():
    new_component = NewComponent()
    other_component = OtherComponent()
    another_component = OtherComponent()
    new_plan = sourdough.Plan()
    new_plan.add(new_component)
    new_plan.add(other_component)
    new_plan.add(another_component)
    assert new_plan['new_component'] == new_component
    new_plan.add([other_component, another_component])
    assert new_plan.items == [
        new_component, 
        other_component, 
        another_component,
        [other_component, another_component]]
    return


if __name__ == '__main__':
    test_plan()