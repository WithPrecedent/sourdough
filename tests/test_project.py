"""
.. module:: project test
:synopsis: tests Project class
:author: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import pathlib

import pandas as pd

import sourdough


class Author(sourdough.Stage):
    
    def apply(self, project: 'sourdough.Project') -> 'sourdough.Project':
        return project


class Publisher(sourdough.Stage):
    
    def apply(self, project: 'sourdough.Project') -> 'sourdough.Project':
        return project


class Reader(sourdough.Stage):
    
    def apply(self, project: 'sourdough.Project') -> 'sourdough.Project':
        return project


def test_project():
    settings = sourdough.Settings(
        contents = pathlib.Path.cwd().joinpath(
            'tests', 
            'ini_settings.ini'))
    project = sourdough.Project(settings = settings)
    sourdough.Manager.add_stage('author', Author)
    sourdough.Manager.add_stage('publisher', Publisher)
    sourdough.Manager.add_stage('reader', Reader)
    manager = sourdough.Manager(
        stages = ['author', 'publisher', 'reader'], 
        project = project)
    return

if __name__ == '__main__':
    test_project()