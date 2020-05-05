"""
.. module:: project test
:synopsis: tests Project class
:author: Corey Rayburn Yung
:copyright: 2019-2020
:license: Apache-2.0
"""

from pathlib import pathlib.Path

import pandas as pd
import pytest

from sourdough.settings import Settings
from sourdough.project import Project


def test_project():
    settings = Settings(
        configuration = pathlib.Path.cwd().joinpath('tests', 'settings_settings.ini'))
    project = Project(settings = settings)
    print('test', project.library)
    return

if __name__ == '__main__':
    test_project()