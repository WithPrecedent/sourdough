"""
test_mixins: unit tests for Component mixins
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)
"""

import dataclasses

import sourdough


@dataclasses.dataclass
class AComponent(
    sourdough.LibraryMixin,
    sourdough.mixins.RegistryMixin,
    sourdough.core.Element):
    pass


@dataclasses.dataclass
class OtherComponent(AComponent):
    pass


@dataclasses.dataclass
class AnotherComponent(sourdough.OptionsMixin, OtherComponent):
    
    options = sourdough.core.Catalog(contents = {
        'base': AComponent(),
        'other': OtherComponent()})
 

@dataclasses.dataclass
class ProxiedComponent(sourdough.ProxyMixin, OtherComponent):
    
    def __post_init__(self):
        super().__post_init__()
        self._hidden_attribute = 'value'
        self.proxify(proxy = 'new_property', attribute = '_hidden_attribute')


def test_mixins():
    # Tests Component, RegistryMixin, and LibraryMixin
    a_component = AComponent()
    other_component = OtherComponent()
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
    base_instance = another_component.select(key = 'base')
    other_instance = another_component.select(key = 'other')
    assert other_instance.name == 'other_component'
    
    # Tests ProxyMixin
    # proxied_component = ProxiedComponent()
    # print('test property', proxied_component.new_property)
    # assert proxied_component.new_property == 'value'
    return

if __name__ == '__main__':
    test_mixins()