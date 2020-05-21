"""
.. module:: composite project test
:synopsis: tests CompositeProject and CompositeDirector classes
:author: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import pathlib

import sourdough


def test_composite_project():
    settings = pathlib.Path.cwd().joinpath('tests', 'ini_settings.ini')
    project = sourdough.CompositeProject(settings = settings)
    director = sourdough.CompositeDirector(project = project)
    print('test project', director.project)
    return

if __name__ == '__main__':
    test_composite_project()