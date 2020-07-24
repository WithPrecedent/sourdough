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
class AComponent(
    sourdough.RegistryMixin,
    sourdough.LibraryMixin,
    sourdough.Component):
    pass


@dataclasses.dataclass
class OtherComponent(AComponent):
    pass


@dataclasses.dataclass
class AnotherComponent(sourdough.OptionsMixin, sourdough.Component):
    
    options = sourdough.Catalog(contents = {
        'base': AComponent(),
        'other': OtherComponent()})


def test_tree():
    project = sourdough.Project(
        name = 'awesome_project',
        settings = pathlib.Path('tests') / 'composite_settings.py',
        structure = 'comparative',
        automatic = False)
    return


if __name__ == '__main__':
    test_tree()