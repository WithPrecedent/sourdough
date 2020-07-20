"""
.. module:: test system
:synopsis: tests Project class
:author: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import os
import pathlib
import sys

sys.path.insert(0, os.path.join('..', 'sourdough'))

import sourdough


class SomeProject(sourdough):

    def some_action(self):
        pass

    def another_action(self):
        pass

    def final_action(self):
        pass


def test_system():
    a_system = SomeProject(
        stages = ['some_action', 'another_action', 'final_action'])
    assert a_system.name == 'some_system'
    assert a_system.stages == ['some_action', 'another_action', 'final_action']
    for method in a_system:
        result = method()
    return


if __name__ == '__main__':
    test_system()