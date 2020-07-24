"""
test_tree: tests for a Project to construct and use a tree object
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)
"""

import dataclasses
import pathlib

import sourdough
import sourdough.project.actions
import sourdough.project.workers


@dataclasses.dataclass
class Parser(sourdough.project.workers.Worker):

    def perform(self):
        return


@dataclasses.dataclass
class Search(sourdough.project.actions.Task):

    def perform(self):
        return   


def test_tree():
    sourdough.Project.options.add(Parser)
    sourdough.Project.options.add(Search)
    project = sourdough.Project(
        name = 'cool_project',
        settings = pathlib.Path('tests') / 'composite_settings.py',
        structure = 'comparative',
        automatic = True)
    print('test project', project)
    return


if __name__ == '__main__':
    test_tree()