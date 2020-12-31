"""
test_settings: unit tests for Configuration
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)
"""

import pathlib

import sourdough


class Divide(sourdough.Component):
    pass


def test_settings():
    actual_settings = {
        'general': {'verbose': True, 'seed': 43},
        'files': {
            'source_format': 'csv',
            'interim_format': 'csv',
            'final_format': 'csv',
            'analysis_format': 'csv',
            'file_encoding': 'windows-1252'},
        'manager': {
            'manager_tasks': ['parser', 'munger']},
        'parser': {
            'parser_tasks': 'divide',
            'divide_techniques': ['slice', 'dice']},
        'divide_parameters': {'replace_strings': True}}
    ini_settings = sourdough.types.Configuration(
        contents = pathlib.Path('tests') / 'ini_settings.ini')
    assert ini_settings.contents == actual_settings
    py_settings = sourdough.types.Configuration(
        contents = pathlib.Path('tests') / 'py_settings.py')
    assert py_settings.contents == actual_settings
    json_settings = sourdough.types.Configuration(
        contents = pathlib.Path('tests') / 'json_settings.json')
    assert json_settings.contents == actual_settings
    assert ini_settings['general']['seed'] == 43
    ini_settings['new_section'] = {}
    ini_settings.contents['new_section']['new_setting'] = 'value'
    assert ini_settings['new_section']['new_setting'] == 'value'
    ini_settings.add('new_section', {'newer_setting': 'value'})
    assert ini_settings['new_section']['newer_setting'] == 'value'
    divide = Divide()
    divide = ini_settings.inject(
        instance = divide,
        additional = ['divide_parameters'])
    assert divide.seed == 43
    assert divide.replace_strings
    return


if __name__ == '__main__':
    test_settings()