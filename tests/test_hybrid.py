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
    Structure = sourdough.core.Hybrid()
    Structure.setdefault('default value')
    a_element = AComponent(name = 'test_name')
    another_element = AnotherComponent()
    some_element = AnotherComponent(name = 'some_element')
    Structure.add(a_element)
    Structure.add(another_element)
    Structure.extend([a_element, another_element])
    Structure.insert(3, some_element)
    assert Structure.keys() == [
        'test_name', 
        'another_element', 
        'test_name', 
        'some_element',
        'another_element']
    assert Structure.values() == [
        a_element,
        another_element,
        a_element,
        some_element,
        another_element]
    for key, value in Structure.items():
        pass
    subset_Structure = Structure.subsetify(subset = ['test_name'])
    assert subset_Structure.keys() == [
        'test_name', 
        'test_name']
    assert Structure.pop(1) == another_element
    assert Structure.pop('test_name') == sourdough.core.Hybrid(
        contents = [a_element, a_element])
    Structure.update({'new_Structure': a_element})
    assert Structure.keys() == [
        'some_element',
        'another_element',
        'new_Structure']
    assert Structure.get('nothing') == 'default value'
    Structure.setdefault(None)  
    assert Structure.get('nothing') == None
    Structure['crazy_element'] = AnotherComponent(name = 'crazy')
    Structure.append(sourdough.core.Hybrid(
        name = 'nested', 
        contents = [another_element, some_element]))
    assert Structure.keys() == [
        'some_element', 
        'another_element',
        'new_Structure', 
        'crazy',
        'nested']
    assert len(Structure) == 6
    Structure.clear()
    assert len(Structure) == 0
    Structure += another_element
    assert len(Structure) == 1
    Structure.remove(0)
    assert len(Structure) == 0
    return


if __name__ == '__main__':
    test_hybrid()
    