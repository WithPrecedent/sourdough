"""
.. module:: test Options
:synopsis: tests Options class
:author: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import sourdough


def test_Options():
    Options = sourdough.Options(contents = {
        'run' : 'tired',
        'sleep': 'rested',
        'walk': 'relax'})
    assert Options['all'] == ['tired', 'rested', 'relax']
    assert Options['default'] == ['tired', 'rested', 'relax']
    assert Options['sleep'] == 'rested'
    assert Options['none'] == []
    return


if __name__ == '__main__':
    test_Options()