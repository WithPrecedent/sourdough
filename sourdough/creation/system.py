"""
.. module:: system
:synopsis: project workflow made simple
:author: Corey Rayburn Yung
:copyright: 2019-2020
:license: Apache-2.0
"""

import collections.abc
import dataclasses
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Union

import sourdough


@dataclasses.dataclass
class System(sourdough.Component, collections.abc.Iterator):
    """Base class for sourdough project stages.

    A System maintains a progress state stored in the attribute 'stage'. The
    'stage' corresponds to whether one of the core workflow methods has been
    called. The string stored in 'stage' can then be used by instances to alter
    instance behavior, call methods, or change access method functionality.

    Args:
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. If the class instance
            needs settings from the shared Settings instance, 'name' should
            match the appropriate section name in that Settings instance. When
            subclassing, it is a good settings to use the same 'name' attribute
            as the base class for effective coordination between sourdough
            classes. Defaults to None or __class__.__name__.lower().
        stages (Optional[Union[Dict[str, str], List[str]]]): list of recognized
            states which correspond to methods within a class instance or a dict
            with keys of stage names and values of method names. Defaults to
            ['initialize', 'draft', 'publish', 'apply'].
        auto_advance (Optional[bool]): whether to automatically advance 'stage'
            when one of the stage methods is called (True) or whether 'stage'
            must be changed manually by using the 'advance' method (False).
            Defaults to True.

    """
    name: Optional[str] = None
    stages: Optional[Union[Dict[str, str], List[str]]] = dataclasses.field(
        default_factory = lambda: ['initialize', 'draft', 'publish', 'apply'])
    auto_advance: Optional[bool] = True

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Sets 'name' to the default value if it is not passed.
        super().__post_init__()
        # Validates that corresponding methods exist for each stage after the
        # first stage and converts 'stages' to a list, if necessary.
        self.stages = self._validate_stages(stages = self.stages)
        # Sets initial stage.
        self.stage = self.stages[0]
        # Automatically calls stage methods if attributes named 'auto_{stage}'
        # are set to True. For example, if there is an attribute named
        # 'auto_draft' and it is True, the 'draft' method will be called.
        self._auto_stages()
        return self

    """ Public Methods """

    def advance(self, stage: Optional[str] = None) -> None:
        """Advances to next stage in 'stages' or to 'stage' argument.

        This method only needs to be called manually if 'auto_advance' is False.
        Otherwise, this method is automatically called when individual stage
        methods are called via '__getattribute__'.

        If this method is called at the last stage, it does not raise an
        IndexError. It simply leaves 'stage' at the last item in the list.

        Args:
            stage(Optional[str]): name of stage matching a string in 'stages'.
                Defaults to None. If not passed, the method goes to the next
                'stage' in stages.

        Raises:
            ValueError: if 'stage' is neither None nor in 'stages'.

        """
        self.previous_stage = self.stage
        if stage is None:
            try:
                self.stage = self.stages[self.stages.index(self.stage) + 1]
            except IndexError:
                pass
        elif stage in self.stages:
            self.stage = stage
        else:
            raise ValueError(f'{stage} is not a recognized stage')
        return self

    """ Required ABC Methods """

    def __iter__(self) -> Iterable:
        """Returns iterable of methods corresponding to 'stages'.

        Returns:
            Iterable: methods with names in 'stages'.

        """
        return iter([getattr(
            self, self._mapped_stages[stage]) for stage in self.stages])

    def __next__(self) -> Callable:
        """Returns next method after method matching 'stage'.

        Returns:
            Callable: next method corresponding to those listed in 'stages'.

        """
        try:
            return getattr(self.stages[self.stages.index(self.stage) + 1])
        except IndexError:
            raise StopIteration()

    """ Other Dunder Methods """

    def __getattribute__(self, attribute: str) -> Any:
        """Changes 'stage' if one of the corresponding methods are called.

        For example, if 'publish' is in 'stages' and the 'publish' method is
        called, this method advances the 'stage' attribute to 'publish'.

        This method only differs from the normal '__getattribute__' if
        'auto_advance' is True.

        Args:
            attribute (str): name of attribute sought.

        """
        if super().__getattribute__('auto_advance'):
            try:
                if attribute in super().__getattribute__('stages'):
                    super().__getattribute__('advance')(stage = attribute)
            except AttributeError:
                pass
        return super().__getattribute__(attribute)

    """ Private Methods """

    def _validate_stages(self,
            stages: Optional[Union[
                Dict[str, str],
                List[str]]] = None) -> List[str]:
        """Validates 'stages' and existence of corresponding methods.

        This method ignores the first item in 'stages' which does not require
        a corresponding method.

        Args:
            stages (Optional[Union[Dict[str, str], List[str]]]): a dict with
                keys as stage names and values of names of stage methods.
                Defaults to None. If not passed, the local 'stages' attribute
                is used and returned as a list.

        Raises:
            AttributeError: if a method listed in 'stages' does not exist.

        Returns:
            List[str]: stages as a list of names. These will correspond to the
                keys in the stored private variable '_mapped_stages'.

        """
        if stages is None:
            stages = self.stages
        # Creates '_mapped_stages' to store stage to method relationship and
        # converts 'stages' to a list, if necessary.
        if isinstance(stages, dict):
            self._mapped_stages = stages
            stages = list(stages.keys())
        elif isinstance(stages, list):
            self._mapped_stages = dict(zip(stages, stages))
        # Tests whether stage methods listed in 'stages' exist.
        for stage, stage_method in self._mapped_stages.items():
            if stage_method not in dir(self) and stage not in [stages[0]]:
                raise AttributeError(f'{stage} is not in {self.name}')
        return stages

    def _auto_stages(self) -> None:
        """Calls stage method if corresponding boolean is True."""
        # Automatically calls stage methods if attribute named 'auto_{stage}'
        # is set to True.
        for stage in self.stages[1:]:
            try:
                if getattr(self, f'auto_{stage}'):
                    getattr(self, self._mapped_stages[stage])()
            except AttributeError:
                pass
        return self