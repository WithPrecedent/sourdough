"""
.. module:: test dictionaries
:synopsis: tests Lexicon and its subclasses
:author: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import sourdough

class AComponent(sourdough.Component):
    pass

class AnotherComponent(sourdough.Component):
    pass

def test_dictionaries():
    test_component = AComponent(name = 'first_test')
    test_mapping = {'a_key': 'a_value'}
    test_sequence = [AComponent(), AnotherComponent(name = 'test_name')]
    
    # Tests Lexicon
    lexicon = sourdough.Lexicon()
    lexicon.add(test_component)
    lexicon.add(test_mapping)
    lexicon.add(test_sequence)
    test_keys = list(lexicon.contents.keys())
    subset_lexicon = lexicon.subsetify(subset = ['a_key', 'test_name'])
    assert test_keys == ['first_test', 'a_key', 'a_component', 'test_name']
    assert lexicon['a_key'] == 'a_value'
    
    # Tests Catalog
    catalog = sourdough.Catalog(contents = {
        'run' : 'tired',
        'sleep': 'rested',
        'walk': 'relax'})
    assert catalog['all'] == ['tired', 'rested', 'relax']
    assert catalog['default'] == ['tired', 'rested', 'relax']
    assert catalog['sleep'] == 'rested'
    assert catalog['none'] == []
    
    # Tests MirrorDictionary
    mirror_dict = sourdough.MirrorDictionary(contents = {
        'run' : 'tired',
        'sleep': 'rested',
        'walk': 'relax'})
    assert mirror_dict['run'] == 'tired'
    assert mirror_dict['relax'] == 'walk'
    return


if __name__ == '__main__':
    test_dictionaries()
    