"""
test_catalog: unit tests for Catalog
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)
"""

import dataclasses

import sourdough


@dataclasses.dataclass
class AComponent(sourdough.project.Component):
    pass


@dataclasses.dataclass
class AnotherComponent(sourdough.project.Component):
    pass


def test_catalog():
    test_element = AComponent(name = 'first_test')
    another_element = AnotherComponent()
    test_mapping = {'a_key': AComponent(), 'another_key': AnotherComponent()}
    test_sequence = [AComponent(), AnotherComponent(name = 'test_name')]
    catalog = sourdough.Catalog(contents = {
        'test' : test_element,
        'another': another_element})
    assert catalog['all'] == [test_element, another_element]
    assert catalog['default'] == [test_element, another_element]
    assert catalog['another'] == another_element
    assert catalog['none'] == []
    catalog += {'third': another_element}
    catalog.add(test_mapping)
    try:
        catalog.add(test_sequence)
        raise TypeError('test failed to raise TypeError')
    except TypeError:
        pass
    assert len(catalog) == 5
    assert catalog[['test', 'another']] == [test_element, another_element]
    catalog.always_return_list = True
    assert catalog['test'] == [test_element]
    assert catalog.create('another') == another_element
    subset_catalog = catalog.subsetify(subset = ['third', 'a_key'])
    assert subset_catalog.always_return_list
    return


if __name__ == '__main__':
    test_catalog()
    