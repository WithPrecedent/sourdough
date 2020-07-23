"""
test_dictionaries: unit tests for Lexicon and its subclasses
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


def test_dictionaries():
    test_component = AComponent(name = 'first_test')
    another_component = AnotherComponent()
    test_mapping = {'a_key': AComponent(), 'another_key': AnotherComponent()}
    test_sequence = [AComponent(), AnotherComponent(name = 'test_name')]
    
    # Tests Lexicon
    lexicon = sourdough.Lexicon()
    try:
        lexicon.add(test_component)
        raise TypeError('TypeError message not properly triggered')
    except TypeError:
        pass
    lexicon.add(test_mapping)
    try:
        lexicon.add(test_sequence)
        raise TypeError('TypeError message not properly triggered')
    except TypeError:
        pass
    test_keys = list(lexicon.contents.keys())
    subset_lexicon = lexicon.subsetify(subset = ['a_key'])
    assert test_keys == ['a_key', 'another_key']
    assert list(subset_lexicon.keys()) == ['a_key']
    
    # Tests Catalog
    catalog = sourdough.Catalog(contents = {
        'test' : test_component,
        'another': another_component})
    assert catalog['all'] == [test_component, another_component]
    assert catalog['default'] == [test_component, another_component]
    assert catalog['another'] == another_component
    assert catalog['none'] == []
    
    # # Tests Reflector
    # mirror_dict = sourdough.Reflector(contents = {
    #     'run' : 'tired',
    #     'sleep': 'rested',
    #     'walk': 'relax'})
    # assert mirror_dict['run'] == 'tired'
    # assert mirror_dict['relax'] == 'walk'
    return


if __name__ == '__main__':
    test_dictionaries()
    