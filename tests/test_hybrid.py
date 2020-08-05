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
    a_element = AComponent(name = 'test_name')
    another_element = AnotherComponent()
    some_element = AnotherComponent(name = 'some_element')
    worker.add(a_element)
    worker.add(another_element)
    worker.extend([a_element, another_element])
    worker.insert(3, some_element)
    assert worker.keys() == [
        'test_name', 
        'another_element', 
        'test_name', 
        'some_element',
        'another_element']
    assert worker.values() == [
        a_element,
        another_element,
        a_element,
        some_element,
        another_element]
    for key, value in worker.items():
        pass
    subset_worker = worker.subsetify(subset = ['test_name'])
    assert subset_worker.keys() == [
        'test_name', 
        'test_name']
    assert worker.pop(1) == another_element
    assert worker.pop('test_name') == sourdough.Hybrid(
        contents = [a_element, a_element])
    worker.update({'new_worker': a_element})
    assert worker.keys() == [
        'some_element',
        'another_element',
        'new_worker']
    assert worker.get('nothing') == 'default value'
    worker.setdefault(None)  
    assert worker.get('nothing') == None
    worker['crazy_element'] = AnotherComponent(name = 'crazy')
    worker.append(sourdough.Hybrid(
        name = 'nested', 
        contents = [another_element, some_element]))
    assert worker.keys() == [
        'some_element', 
        'another_element',
        'new_worker', 
        'crazy',
        'nested']
    assert len(worker) == 6
    worker.clear()
    assert len(worker) == 0
    worker += another_element
    assert len(worker) == 1
    worker.remove(0)
    assert len(worker) == 0
    return


if __name__ == '__main__':
    test_hybrid()
    