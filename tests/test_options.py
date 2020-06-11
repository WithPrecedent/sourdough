"""
.. module:: test Catalog
:synopsis: tests Catalog class
:author: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import sourdough


def test_Catalog():
    Catalog = sourdough.Catalog(contents = {
        'run' : 'tired',
        'sleep': 'rested',
        'walk': 'relax'})
    assert Catalog['all'] == ['tired', 'rested', 'relax']
    assert Catalog['default'] == ['tired', 'rested', 'relax']
    assert Catalog['sleep'] == 'rested'
    assert Catalog['none'] == []
    return


if __name__ == '__main__':
    test_Catalog()