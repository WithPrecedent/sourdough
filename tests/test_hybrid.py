"""
test_hybrids: unit tests for Hybrid
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)
"""

import dataclasses

import sourdough


@dataclasses.dataclass
class AComponent(sourdough.Component):
    pass


@dataclasses.dataclass
class AnotherComponent(sourdough.Component):
    pass


def test_hybrid():
    plan = sourdough.Hybrid(_default = 'default value')
    a_component = AComponent(name = 'test_name')
    another_component = AnotherComponent()
    some_component = AnotherComponent(name = 'some_component')
    plan.add(a_component)
    plan.add(another_component)
    plan.extend([a_component, another_component])
    plan.insert(3, some_component)
    assert plan.keys() == [
        'test_name', 
        'another_component', 
        'test_name', 
        'some_component',
        'another_component']
    assert plan.values() == [
        a_component,
        another_component,
        a_component,
        some_component,
        another_component]
    for key, value in plan.items():
        pass
    subset_plan = plan.subsetify(subset = ['test_name'])
    assert subset_plan.keys() == [
        'test_name', 
        'test_name']
    assert plan.pop(1) == another_component
    assert plan.pop('test_name') == sourdough.Hybrid(
        contents = [a_component, a_component])
    plan.update({'new_plan': a_component})
    assert plan.keys() == [
        'some_component',
        'another_component',
        'new_plan']
    assert plan.get('nothing') == 'default value'
    plan.setdefault(None)  
    assert plan.get('nothing') == None
    plan['crazy_component'] = AnotherComponent(name = 'crazy')
    return


if __name__ == '__main__':
    test_hybrid()
    