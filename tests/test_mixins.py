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
    sourdough.base.Repository,
    sourdough.quirks.Registry,
    sourdough.base.Element):
    pass


@dataclasses.dataclass
class OtherComponent(AComponent):
    pass


@dataclasses.dataclass
class AnotherComponent(sourdough.base.Options, OtherComponent):
    
    options = sourdough.base.Catalog(contents = {
        'base': AComponent(),
        'other': OtherComponent()})
 

@dataclasses.dataclass
class ProxiedComponent(sourdough.base.Proxy, OtherComponent):
    
    def __post_init__(self):
        super().__post_init__()
        self._hidden_attribute = 'value'
        self.proxify(proxy = 'new_property', attribute = '_hidden_attribute')


def test_mixins():
    # Tests Component, Registry, and Repository
    a_component = AComponent()
    other_component = OtherComponent()
    assert 'other_component' in AComponent.library
    assert 'other_component' in a_component.library
    assert 'other_component' in AComponent.library
    assert 'other_component' in a_component.library
    an_instance = a_component.instance(key = 'other_component', name = 'test')
    assert an_instance.name == 'test'
    another_instance = a_component.borrow(key = 'other_component')
    assert another_instance.name == 'other_component'
    
    # Tests Options
    another_component = AnotherComponent()
    base_instance = another_component.select(key = 'base')
    other_instance = another_component.select(key = 'other')
    assert other_instance.name == 'other_component'
    
    # Tests Proxy
    # proxied_component = ProxiedComponent()
    # print('test property', proxied_component.new_property)
    # assert proxied_component.new_property == 'value'
    return

if __name__ == '__main__':
    test_mixins()