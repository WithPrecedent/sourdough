"""
test_hybrid: unit tests for Hybrid
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)
"""

import dataclasses

import sourdough


@dataclasses.dataclass
class AElement(sourdough.Element):
    pass


@dataclasses.dataclass
class AnotherElement(sourdough.Element):
    pass


def test_hybrid():
    structure = sourdough.iterables.Hybrid()
    structure.setdefault('default value')
    a_element = AElement(name = 'test_name')
    another_element = AnotherElement()
    some_element = AnotherElement(name = 'some_element')
    structure.add(a_element)
    structure.add(another_element)
    structure.extend([a_element, another_element])
    structure.insert(3, some_element)
    assert structure.keys() == [
        'test_name', 
        'another_element', 
        'test_name', 
        'some_element',
        'another_element']
    assert structure.values() == [
        a_element,
        another_element,
        a_element,
        some_element,
        another_element]
    for key, value in structure.items():
        pass
    subset_structure = structure.subsetify(subset = ['test_name'])
    assert subset_structure.keys() == [
        'test_name', 
        'test_name']
    assert structure.pop(1) == another_element
    assert structure.pop('test_name') == sourdough.iterables.Hybrid(
        contents = [a_element, a_element])
    structure.update({'new_structure': a_element})
    assert structure.keys() == [
        'some_element',
        'another_element',
        'new_structure']
    assert structure.get('nothing') == 'default value'
    structure.setdefault(None)  
    assert structure.get('nothing') == None
    structure['crazy_element'] = AnotherElement(name = 'crazy')
    structure.append(sourdough.iterables.Hybrid(
        name = 'nested', 
        contents = [another_element, some_element]))
    assert structure.keys() == [
        'some_element', 
        'another_element',
        'new_structure', 
        'crazy',
        'nested']
    assert len(structure) == 6
    structure.clear()
    assert len(structure) == 0
    structure += another_element
    assert len(structure) == 1
    structure.remove(0)
    assert len(structure) == 0
    return


if __name__ == '__main__':
    test_hybrid()
    