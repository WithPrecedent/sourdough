"""
test_tree: tests for a Project to construct and use a tree object
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

def test_tree():
    sourdough.Project.components.add(Parser)
    sourdough.Project.components.add(Search)
    project = sourdough.Project(
        name = 'cool_project',
        settings = pathlib.Path('tests') / 'composite_settings.py',
        structure = 'study',
        automatic = True)
    print('test project', project)
    return


if __name__ == '__main__':
    test_tree()