"""
.. module:: test components
:synopsis: tests Component, its subclasses, and its mixins
:author: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import dataclasses
import os
import pathlib

os.chdir(pathlib.Path(pathlib.Path.cwd() / 'sourdough'))

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
        'other': OtherComponent})
 

@dataclasses.dataclass   
class ProxiedComponent(sourdough.ProxyMixin, sourdough.Component):
    
    def __post_init__(self):
        super().__post_init__()
        self._hidden_attribute = 'value'
        self.proxify(proxy = 'new_property', attribute = '_hidden_attribute')


def test_components():
    # Tests Component, RegistryMixin, and LibraryMixin
    a_component = AComponent()
    other_component = OtherComponent(register_from_disk = True)
    assert 'other_component' in AComponent.registry
    assert 'other_component' in a_component.registry
    assert 'other_component' in AComponent.library
    assert 'other_component' in a_component.library
    an_instance = a_component.build(key = 'other_component', name = 'test')
    assert an_instance.name == 'test'
    another_instance = a_component.borrow(key = 'other_component')
    assert another_instance.name == 'other_component'
    
    # Tests OptionsMixin
    another_component = AnotherComponent()
    base_instance = another_component.create(key = 'base')
    other_instance = another_component.create(key = 'other', name = 'a_test')
    assert other_instance.name == 'a_test'
    
    # Tests ProxyMixin
    # proxied_component = ProxiedComponent()
    # print('test property', proxied_component.new_property)
    # assert proxied_component.new_property == 'value'
    return

if __name__ == '__main__':
    test_components()