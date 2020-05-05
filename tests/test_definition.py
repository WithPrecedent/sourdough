"""
.. module:: test definition
:synopsis: tests MirrorType class
:author: Corey Rayburn Yung
:copyright: 2019-2020
:license: Apache-2.0
"""

import os
import sys

sys.path.insert(0, os.path.join('..', 'sourdough'))

import sourdough


def test_system():
    some_type = sourdough.MirrorType(types = {'integer': 'int'})
    assert some_type['integer'] == 'int'
    assert some_type['int'] == 'integer'
    some_type['floating_point'] = 'float'
    assert some_type['floating_point'] == 'float'
    assert some_type['float'] == 'floating_point'
    return


if __name__ == '__main__':
    test_system()