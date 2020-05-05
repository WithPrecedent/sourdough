"""
.. module:: project
:synopsis: data science projects made simple
:publisher: Corey Rayburn Yung
:copyright: 2019-2020
:license: Apache-2.0
"""

import dataclasses
import importlib
import pathlib
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Union
import warnings

import numpy as np
import pandas as pd

import sourdough



@dataclasses.dataclass
class Project(sourdough.System):
    """Top-level iterator class for sourdough projects.

    Args:
        settings (Optional[Union[Settings, str]]): an instance of Settings or a string
            containing the file path or file name (in the current working
            directory) where a file of a supported file type with settings for
            an Settings instance is located. Defaults to None.
        filer (Optional[Union['Filer', str]]): an instance of Filer or a string
            containing the full path of where the root folder should be located
            for file output. A filer instance contains all file path and
            import/export methods for use throughout sourdough. Defaults to None.
        dataset (Optional[Union['Dataset', pd.DataFrame, np.ndarray, str]]): an
            instance of Dataset, an instance of Data, a string containing the
            full file path where a data file for a pandas DataFrame is located,
            a string containing a file name in the default data folder (as
            defined in the shared Filer instance), a full folder path where raw
            files for data to be extracted from, a string
            containing a folder name which is an attribute in the shared Filer
            instance, a DataFrame, or numpy ndarray. If a DataFrame, Data
            instance, ndarray, or string is
            passed, the resultant data object is stored in the 'data' attribute
            in a new Dataset instance as a DataFrame. Defaults to None.
        workers (Optional[Union[List[str], Dict[str, 'Package'], Dict[str,
            'Worker'], sourdough.sourdough.Repository, 'Manager']]): mapping of 'Package'
            instances or the information needed to create one and store it in
            a 'Manager' instance. Defaults to an empty 'sourdough.Repository'
            instance.
        name (Optional[str]): designates the name of the class used for internal
            referencing throughout sourdough. If the class needs settings from
            the shared 'Settings' instance, 'name' should match the appropriate
            section name in 'Settings'. When subclassing, it is a good settings to use
            the same 'name' attribute as the base class for effective
            coordination between sourdough classes. 'name' is used instead of
            __class__.__name__ to make such subclassing easier. Defaults to
            'project'.
        identification (Optional[str]): a unique identification name for this
            'Project' instance. The name is used for creating file folders
            related to the 'Project'. If not provided, a string is created from
            the date and time.
        auto_draft (Optional[bool]): whether to call the 'draft' method when
            instanced. Defaults to True.
        auto_publish (Optional[bool]): whether to call the 'publish' method when
            instanced. Defaults to True.
        auto_apply (Optional[bool]): whether to call the 'apply' method when
            instanced. For auto_apply to have an effect, 'dataset' must also
            be passed. Defaults to False.

    """
    settings: Optional[sourdough.Settings] = None
    filer: Optional[sourdough.Filer] = None
    dataset: Optional[Union[
        sourdough.Dataset,
        pd.DataFrame,
        np.ndarray,
        str,
        Dict[str, Union[
            pd.DataFrame,
            np.ndarray,
            str]]]] = None
    workers: Optional[Union[
        List[str],
        Dict[str, sourdough.Worker],
        Dict[str, Package],
        sourdough.Repository]] = dataclasses.field(
            default_factory = sourdough.Repository)
    name: Optional[str] = dataclasses.field(default_factory = lambda: 'project')
    identification: Optional[str] = dataclasses.field(
        default_factory = sourdough.utilities.datetime_string)
    auto_draft: Optional[bool] = True
    auto_publish: Optional[bool] = True
    auto_apply: Optional[bool] = False

    def __post_init__(self) -> None:
        """Initializes class attributes and calls selected methods."""
        # Removes various python warnings from console output.
        warnings.filterwarnings('ignore')
        # Validates 'Settings' instance.
        self.settings = sourdough.Settings(contents = self.settings)
        # Adds general attributes from 'settings'.
        self.settings.inject(instance = self)
        # Validates 'Filer' instance.
        self.filer = sourdough.Filer(root_folder = self.filer, settings = self.settings)
        # Validates 'Dataset' instance.
        self.dataset = sourdough.Dataset(data = self.dataset, settings = self.settings)
        # Validates and initializes 'options' and 'workers'.
        self.options = self._validate_options(workers = self.workers)
        self.workers = self._validate_workers(
            options = self.options,
            workers = self.workers)
        # Initializes 'outline', 'library', and 'results' which store the
        # products of the 'draft', 'publish', and 'apply' methods, respectively.
        self.outline = sourdough.Repository(
            name = f'{self.name}_outline_{self.identification}')
        self.library = sourdough.Repository(
            name = f'{self.name}_library_{self.identification}')
        self.results = sourdough.Repository(
            name = f'{self.name}_results_{self.identification}')
        # Initializes 'stage' and validates core sourdough objects.
        super().__post_init__()
        # Calls 'draft' method if 'auto_draft' is True.
        if self.auto_draft:
            self.draft()
        # Calls 'publish' method if 'auto_publish' is True.
        if self.auto_publish:
            self.publish()
        # Calls 'apply' method if 'auto_apply' is True.
        if self.auto_apply:
            self.apply()
        return self

    """ Overview Property """

    @property
    def overview(self) -> Dict[str, Dict[str, List[str]]]:
        """Returns snapshot of current state of project.

        Returns:
            Dict[str, Dict[str, List[str]]]: keys match keys in 'workers' and
                values are overviews for each 'Worker' instance.

        """
        return {key: value.overview for key, value in self.workers.items()}

    @overview.setter
    def overview(self, overview: Dict[str, Dict[str, List[str]]]) -> None:
        """Sets the 'overview' for each selected 'Worker' instance.

        Args:
            overview (Dict[str, Dict[str, List[str]]]): keys match keys in
                'workers' and values are overviews for each 'Worker' instance.

        """
        for key, value in overview.items():
            self.workers[key].overview = value
        return self

    @overview.deleter
    def overview(self) -> NotImplemented:
        """Sets snapshot of selected options to empty dictionaries.

        There are few, if any reasons, to use the 'overview' deleter. It is
        included in case a user wants the option to clear out current selections
        and add more manually.

        """
        for key, value in self.workers.items():
            value.overview = {}
        return self

    """ Public Methods """

    def add(self,
            item: Union[
                Package,
                sourdough.Worker,
                str,
                sourdough.Book],
            name: Optional[str] = None,
            overwrite: Optional[bool] = False) -> None:
        """Adds 'worker' to 'manager' or 'book' to 'library'.

        Args:
            item (Union[sourdough.Worker, str, sourdough.Book): a sourdough object
                to add or a string corresponding to a default worker.
            name (Optional[str]): key to use for the passed item in either
                'library' or 'manager'. Defaults to None. If not passed, the
                'name' attribute of item will be used as the key for item.
           overwrite (Optional[bool]): whether to overwrite an existing
                attribute with the imported object (True) or to update the
                existing attribute with the imported object, if possible
                (False). Defaults to True.

        Raises:
            ValueError: if 'name' is None and 'item' has no 'name' attribute.
            TypeError: if 'item' is neither a 'Worker', 'Book', or str.

        """
        if name is None:
            try:
                name = item.name
            except (AttributeError, TypeError):
                raise ValueError(
                    f'name must be a string or item must have a name attribute')
        if isinstance(item, str):
            self.workers.add(contents = {
                name: self.options[item].load('worker')})
        elif isinstance(item, Worker):
            self.workers.add(contents = {name: item})
        elif isinstance(item, Book):
            self.library.add(contents = {name: item})
        else:
            raise TypeError(f'add method requires a Worker, Book, or str type')
        return self

    def draft(self) -> None:
        """Populates an 'outline' for the project."""
        for name, worker in self.workers.items():
            self.outline[name] = worker.draft(settings = self.settings)
        return self

    def publish(self) -> None:
        """Populates a 'Library' instance with 'Book' instances."""
        for name, worker in self.workers.items():
            self.library[name] = worker.publish(library = self.library)
        return self

    def apply(self, data: Optional['Dataset'] = None, **kwargs) -> None:
        """Applies 'library' to passed 'data'.

        Args:
            data (Optional['Dataset']): data object for methods to be
                applied. If not passed, data stored in the 'dataset' is
                used.
            kwargs: any other parameters to pass to the 'apply' method of a
                'Scholar' instance.

        """
        # Assigns 'data' to 'dataset' attribute and validates it.
        if data:
            self.dataset = sourdough.Dataset(data = data, settings = self.settings)
        for name, worker in self.workers.items():
            self.results[name] = worker.apply(
                data = self.dataset,
                library = self.library,
                **kwargs)
        return self

    def load(self,
            file_path: Union[str, pathlib.Path],
            overwrite: Optional[bool] = True) -> None:
        """Loads a sourdough object and stores it in the appropriate attribute.

        Args:
            file_path (Union[str, pathlib.Path]): path to saved 'Library'
                instance.
            overwrite (Optional[bool]): whether to overwrite an existing
                attribute with the imported object (True) or to update the
                existing attribute with the imported object, if possible
                (False). Defaults to True.

        """
        loaded = self.filer(file_path = file_path)
        if isinstance(loaded, Project):
            self = loaded
        elif isinstance(loaded, Library):
            if overwrite:
                self.library = loaded
            else:
                self.library.update(loaded)
        elif isinstance(loaded, Book):
            self.library.add(book = loaded)
        elif isinstance(loaded, Manager):
            if overwrite:
                self.manager = loaded
            else:
                self.manager.update(loaded)
        elif isinstance(loaded, Worker):
            self.manager.add(worker = loaded)
        elif isinstance(loaded, Dataset):
            if overwrite:
                self.dataset = loaded
            else:
                self.dataset.add(data = loaded)
        else:
            raise TypeError(
                'loaded object must be Projecct, Library, Book, Dataset, \
                     Manager, or Worker type')
        return self

    def save(self,
            attribute: Union[str, object],
            file_path: Optional[Union[str, pathlib.Path]]) -> None:
        """Saves a sourdough object.

        Args:
            attribute (Union[str, object]): either the name of the attribute or
                sourdough object to save.
            file_path (Optional[Union[str, pathlib.Path]]): path to save
                'attribute'.

        Raises:
            AttributeError: if 'attribute' is a string and cannot be found in
                the 'Project' subclass or its 'manager' and 'library'
                attributes.

        """
        if isinstance(attribute, str):
            try:
                attribute = getattr(self, attribute)
            except AttributeError:
                try:
                    attribute = getattr(self.manager, attribute)
                except AttributeError:
                    try:
                        attribute = getattr(self.library, attribute)
                    except AttributeError:
                        AttributeError(f'attribute not found in {self.name}')
        else:
            self.filer.save(attribute)
        return self

    """ Dunder Methods """

    def __call__(self) -> Callable:
        """Drafts, publishes, and applies Project.

        Calling Project as a function is compatible with and used by the
        command line interface.

        """
        self.auto_apply = True
        self.__post__init()
        return self

    def __iter__(self) -> Iterable:
        """Returns iterable for class instance, depending upon 'stage'.

        Returns:
            Iterable: different depending upon stage.

        """
        return iter(self.workers)

    def __repr__(self) -> str:
        """Returns string representation of a class instance."""
        return self.__str__()

    def __str__(self) -> str:
        """Returns string representation of a class instance."""
        return f'{self.name} {self.identification}: {str(self.overview)}, \
            workers: {str(self.workers)}, library: {str(self.library)}'

    """ Private Methods """

    def _validate_options(self,
                workers: Optional[List[str]]) -> sourdough.Repository:
        """Creates 'options' either from 'workers' or default options.

        Args:
            workers (Optional[List[str]]): a list

        Returns:
            sourdough.Repository: with workers initialized.

        """
        if (isinstance(workers, (dict, sourdough.Repository))
                and all(isinstance(w, Package) for w in workers.values())):
            return sourdough.Repository(contents = workers)
        else:
            return DEFAULT_PACKAGES

    def _validate_workers(self,
                options: sourdough.sourdough.Repository,
                workers: Optional[List[str]]) -> sourdough.Repository:
        """Validates 'workers' or converts them to the appropriate type.

        Args:
            workers (Optional[List[cxstr]]): a list

        Returns:
            sourdough.Repository: with workers initialized.

        """
        if (isinstance(workers, (dict, sourdough.Repository))
                and all(isinstance(w, Worker) for w in workers.values())):
            return sourdough.Repository(contents = workers)
        else:
            if not workers:
                workers = self.settings.get_workers(name = self.project)
            elif isinstance(workers, (dict, sourdough.Repository)):
                workers = list(workers.keys())
            if isinstance(workers, list):
                new_workers = sourdough.Repository()
                for package in workers:
                    instructions = options[package].load(
                        attribute = 'instructions')
                    new_workers[package] = sourdough.Worker(
                        instructions = instructions)
                return new_workers
            else:
                raise TypeError(
                    f'workers must be dict, sourdough.Repository, or list type')


@dataclasses.dataclass
class Package(sourdough.Loader):
    """Lazy loader for sourdough-compatible packages.

    Args:
        name (Optional[str]): designates the name of the class instance used
            for internal referencing throughout sourdough. If the class
            instance needs settings from the shared 'Settings' instance, 'name'
            should match the appropriate section name in that 'Settings' instance.
            When subclassing, it is a good settings to use the same 'name' attribute
            as the base class for effective coordination between sourdough
            classes. Defaults to None or __class__.__name__.lower().
        module (Optional[str]): name of module where object to use is located
            (can either be a sourdough or non-sourdough module). Defaults to
            'sourdough'.
        instructions (Optional[str]): name of

    """
    name: Optional[str] = None
    module: Optional[str] = dataclasses.field(
        default_factory = lambda: 'sourdough')
    instructions: Optional[str] = 'Instructions'

    def load(self, attribute: Optional[str] = None) -> object:
        """Returns object named in 'attribute' or 'instructions'.

        Args:
            attribute (Optional[str]): name of local attribute to load from
                'module'. Defaults to None. If not passed, the object named in
                'instructions' is loaded.

        Returns:
            object: from 'module'.

        """
        if attribute:
            return super().load(attribute = attribute)
        else:
            return super().load(attribute = 'instructions')


DEFAULT_PACKAGES = sourdough.Repository(
    name = 'default_packages',
    contents = {
        'wrangler': sourdough.Worker(
            name = 'wrangler',
            module = 'sourdough.wrangler.wrangler',
            instructions = 'WranglerInstructions'),
        'explorer': sourdough.Worker(
            name = 'explorer',
            module = 'sourdough.explorer.explorer',
            instructions = 'ExplorerInstructions'),
        'analyst': sourdough.Worker(
            name = 'analyst',
            module = 'sourdough.analyst.analyst',
            instructions = 'AnalystInstructions'),
        'critic': sourdough.Worker(
            name = 'critic',
            module = 'sourdough.critic.critic',
            instructions = 'CriticInstructions'),
        'artist': sourdough.Worker(
            name = 'artist',
            module = 'sourdough.artist.artist',
            instructions = 'ArtistInstructions')})
