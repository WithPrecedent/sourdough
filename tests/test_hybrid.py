"""
test_hybrid: unit tests for Hybrid
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
    worker = sourdough.Hybrid()
    worker.setdefault('default value')
    a_component = AComponent(name = 'test_name')
    another_component = AnotherComponent()
    some_component = AnotherComponent(name = 'some_component')
    worker.add(a_component)
    worker.add(another_component)
    worker.extend([a_component, another_component])
    worker.insert(3, some_component)
    assert worker.keys() == [
        'test_name', 
        'another_component', 
        'test_name', 
        'some_component',
        'another_component']
    assert worker.values() == [
        a_component,
        another_component,
        a_component,
        some_component,
        another_component]
    for key, value in worker.items():
        pass
    subset_worker = worker.subsetify(subset = ['test_name'])
    assert subset_worker.keys() == [
        'test_name', 
        'test_name']
    assert worker.pop(1) == another_component
    assert worker.pop('test_name') == sourdough.Hybrid(
        contents = [a_component, a_component])
    worker.update({'new_worker': a_component})
    assert worker.keys() == [
        'some_component',
        'another_component',
        'new_worker']
    assert worker.get('nothing') == 'default value'
    worker.setdefault(None)  
    assert worker.get('nothing') == None
    worker['crazy_component'] = AnotherComponent(name = 'crazy')
    worker.append(sourdough.Hybrid(
        name = 'nested', 
        contents = [another_component, some_component]))
    assert worker.keys() == [
        'some_component', 
        'another_component',
        'new_worker', 
        'crazy',
        'nested']
    assert len(worker) == 6
    worker.clear()
    assert len(worker) == 0
    worker += another_component
    assert len(worker) == 1
    worker.remove(0)
    assert len(worker) == 0
    return


if __name__ == '__main__':
    test_hybrid()
    