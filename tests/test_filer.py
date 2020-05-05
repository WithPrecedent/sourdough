"""
.. module:: filer test
:synopsis: tests Settings class
:author: Corey Rayburn Yung
:copyright: 2019-2020
:license: Apache-2.0
"""

import os
import pathlib
import sys

print(pathlib.Path.cwd())

import sourdough

def test_filer():
    settings = sourdough.Settings(contents = 'tests\ini_settings.ini')
    filer = sourdough.Filer(settings = settings)
    # Tests default folders.
    assert str(filer.root_folder) == '..\..'
    assert str(filer.input_folder) == '..\..\data'
    # Tests injection from settings.
    assert filer.file_encoding == 'windows-1252'
    return


if __name__ == '__main__':
    test_filer()