"""
.. module:: filer test
:synopsis: tests Configuration class
:author: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import pathlib

import sourdough


def test_filer():
    settings = sourdough.resources.Configuration(
        contents = pathlib.Path('tests') / 'ini_settings.ini')
    filer = sourdough.Clerk(settings = settings)
    # Tests injection from settings.
    assert str(filer.root_folder) == '..'
    assert str(filer.input_folder) == '../input'
    assert filer.file_encoding == 'windows-1252'
    return

if __name__ == '__main__':
    test_filer()