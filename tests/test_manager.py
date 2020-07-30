"""
test_manager: tests Manager class and created composite objects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)
"""

import dataclasses
import pathlib

import sourdough


@dataclasses.dataclass
class Parser(sourdough.Worker):

    def perform(self):
        return


@dataclasses.dataclass
class Search(sourdough.Task):

    def perform(self):
        return   


def test_manager():
    sourdough.Manager.options.add(Parser)
    sourdough.Manager.options.add(Search)
    manager = sourdough.Manager(
        name = 'cool_project',
        settings = pathlib.Path('tests') / 'composite_settings.py',
        structure = 'creator',
        automatic = True)
    print('test project', manager.project)
    return


if __name__ == '__main__':
    test_manager()