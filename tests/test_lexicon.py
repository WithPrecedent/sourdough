"""
test_lexicon: unit tests for Lexicon
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


def test_lexicon():
    test_element = AComponent(name = 'first_test')
    another_element = AnotherComponent()
    test_mapping = {'a_key': AComponent(), 'another_key': AnotherComponent()}
    test_sequence = [AComponent(), AnotherComponent(name = 'test_name')]
    
    # Tests Lexicon
    lexicon = sourdough.core.Lexicon()
    try:
        lexicon.add(test_element)
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
    assert len(lexicon) == 2
    del lexicon['a_key']
    assert len(lexicon) == 1
    for key, value in lexicon.items():
        pass
    lexicon += {'another_element': another_element}
    assert len(lexicon) == 2
    return


if __name__ == '__main__':
    test_lexicon()
    