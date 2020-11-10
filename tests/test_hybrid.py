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
    workflow = sourdough.types.Hybrid()
    workflow.setdefault('default value')
    a_element = AElement(name = 'test_name')
    another_element = AnotherElement()
    some_element = AnotherElement(name = 'some_element')
    workflow.add(a_element)
    workflow.add(another_element)
    workflow.extend([a_element, another_element])
    workflow.insert(3, some_element)
    assert workflow.keys() == [
        'test_name', 
        'another_element', 
        'test_name', 
        'some_element',
        'another_element']
    assert workflow.values() == [
        a_element,
        another_element,
        a_element,
        some_element,
        another_element]
    for key, value in workflow.items():
        pass
    subset_workflow = workflow.subsetify(subset = ['test_name'])
    assert subset_workflow.keys() == [
        'test_name', 
        'test_name']
    assert workflow.pop(1) == another_element
    assert workflow.pop('test_name') == sourdough.types.Hybrid(
        contents = [a_element, a_element])
    workflow.update({'new_workflow': a_element})
    assert workflow.keys() == [
        'some_element',
        'another_element',
        'new_workflow']
    assert workflow.get('nothing') == 'default value'
    workflow.setdefault(None)  
    assert workflow.get('nothing') == None
    workflow['crazy_element'] = AnotherElement(name = 'crazy')
    workflow.append(sourdough.types.Hybrid(
        name = 'nested', 
        contents = [another_element, some_element]))
    assert workflow.keys() == [
        'some_element', 
        'another_element',
        'new_workflow', 
        'crazy',
        'nested']
    assert len(workflow) == 6
    workflow.clear()
    assert len(workflow) == 0
    workflow += another_element
    assert len(workflow) == 1
    workflow.remove(0)
    assert len(workflow) == 0
    return


if __name__ == '__main__':
    test_hybrid()
    