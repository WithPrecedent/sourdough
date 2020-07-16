"""
.. module:: test settings
:synopsis: tests Settings class
:author: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import os
import pathlib
import sys

sys.path.insert(0, os.path.join('..', 'src', 'sourdough'))

import sourdough


class Divide(sourdough.base.Component):
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
        'project': {
            'project_steps': ['parser', 'munger']},
        'parser': {
            'parser_steps': 'divide',
            'divide_techniques': ['slice', 'dice']},
        'divide_parameters': {'replace_strings': True}}
    ini_settings = sourdough.base.Settings(contents = 'tests\ini_settings.ini')
    assert ini_settings.contents == actual_settings
    py_settings = sourdough.base.Settings(contents = 'tests\py_settings.py')
    assert py_settings.contents == actual_settings
    json_settings = sourdough.base.Settings(contents = 'tests\json_settings.json')
    assert json_settings.contents == actual_settings
    assert ini_settings.get_steps(section = 'project') == ['parser', 'munger']
    assert ini_settings.get_steps(step = 'parser') == ['divide']
    assert ini_settings.get_techniques(
        step = 'parser',
        step = 'divide') == ['slice', 'dice']
    assert ini_settings.get_parameters(
        step = 'divide',
        technique = 'slice') == {'replace_strings': True}
    assert ini_settings['general']['seed'] == 43
    ini_settings['new_section'] = {}
    ini_settings.contents['new_section']['new_setting'] = 'value'
    assert ini_settings['new_section']['new_setting'] == 'value'
    ini_settings.add('new_section', {'newer_setting': 'value'})
    assert ini_settings['new_section']['newer_setting'] == 'value'
    divide = Divide()
    divide = ini_settings.inject(
        instance = divide,
        other_sections = ['divide_parameters'])
    assert divide.seed == 43
    assert divide.replace_strings
    return


if __name__ == '__main__':
    test_settings()