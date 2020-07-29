"""
test_catalog: unit tests for Catalog
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


def test_catalog():
    test_component = AComponent(name = 'first_test')
    another_component = AnotherComponent()
    test_mapping = {'a_key': AComponent(), 'another_key': AnotherComponent()}
    test_sequence = [AComponent(), AnotherComponent(name = 'test_name')]
    
    # Tests Catalog
    catalog = sourdough.Catalog(contents = {
        'test' : test_component,
        'another': another_component})
    assert catalog['all'] == [test_component, another_component]
    assert catalog['default'] == [test_component, another_component]
    assert catalog['another'] == another_component
    assert catalog['none'] == []
    catalog += {'third': another_component}
    catalog.add(test_mapping)
    catalog.add(test_sequence)
    assert len(catalog) == 7
    assert catalog[['test', 'another']] == [test_component, another_component]
    catalog.always_return_list = True
    assert catalog['test'] == [test_component]
    assert catalog.perform('another') == another_component
    subset_catalog = catalog.subsetify(subset = ['third', 'a_key'])
    assert subset_catalog.always_return_list
    return


if __name__ == '__main__':
    test_catalog()
    