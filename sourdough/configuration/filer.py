"""
filer: sourdough file management classes
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Filer: interface for sourdough file management classes and methods.

"""

import abc
import csv
import dataclasses
import datetime
import pathlib
from typing import Any, Callable, ClassVar, Iterable, Mapping, Sequence, Union

import sourdough


@dataclasses.dataclass
class Filer(object):
    """File and folder management for sourdough.

    Creates and stores dynamic and static file paths, properly formats files
    for import and export, and provides methods for loading and saving
    sourdough, pandas, and numpy objects.

    Args:
        settings (sourdough.Settings): a Settings instance, preferably with a 
            section named 'filer' or 'files' with file-management related 
            settings. If 'settings' does not have file configuration options or
            if 'settings' is None, internal defaults will be used. Defaults to
            None.
        root_folder (Union[str, pathlib.Path]): the complete path from which the 
            other paths and folders used by Filer are ordinarily derived 
            (unless you decide to use full paths for all other options). 
            Defaults to None. If not passed, the parent folder of the current 
            working directory is used.
        input_folder (Union[str, pathlib.Path]]): the input_folder subfolder 
            name or a complete path if the 'input_folder' is not off of
            'root_folder'. Defaults to 'input'.
        output_folder (Union[str, pathlib.Path]]): the output_folder subfolder
            name or a complete path if the 'output_folder' is not off of
            'root_folder'. Defaults to 'output'.

    """
    settings: 'sourdough.Settings' = None
    root_folder: Union[str, pathlib.Path] = None
    input_folder: Union[str, pathlib.Path] = 'input'
    output_folder: Union[str, pathlib.Path] = 'output'
    
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Attempots to Inject attributes from 'settings'.
        try:
            self.settings.inject(
                instance = self, 
                additional = ['files', 'filer'])
        except (AttributeError, TypeError):
            pass
        # Validates core folder paths and writes them to disk.
        self.root_folder = self.root_folder or pathlib.Path('..')
        self.root_folder = self.validate(path = self.root_folder)
        self.input_folder = self._validate_io_folder(path = self.input_folder)
        self.output_folder = self._validate_io_folder(path = self.output_folder)
        # Sets default file formats in a dictionary of FileFormat instances.
        self.file_formats = self._get_default_file_formats()
        # Gets default parameters for file transfers from 'settings'.
        self.default_parameters = self._get_default_parameters(
            settings = self.settings)
        # Creates FileLoader and FileSaver instances for loading and saving
        # files.
        self.loader = FileLoader(filer = self)
        self.saver = FileSaver(filer = self)
        return self

    """ Public Methods """
    
    def validate(self, 
            path: Union[str, pathlib.Path],
            test: bool = True,
            create: bool = True) -> pathlib.Path:
        """Turns 'file_path' into a pathlib.Path.

        Args:
            path (Union[str, pathlib.Path]): str or Path to be validated. If
                a str is passed, the method will see if an attribute matching
                'path' exists and if that attribute contains a Path.
            test (bool): whether to test if the path exists. Defaults to True.
            create (bool): whether to create the folder path if 'test' is True,
                but the folder does not exist. Defaults to True.

        Raises:
            TypeError: if 'path' is neither a str nor Path.
            FileNotFoundError: if the validated path does not exist and 'perform'
                is False.

        Returns:
            pathlib.Path: derived from 'path'.

        """
        if isinstance(path, str):
            if (hasattr(self, path) 
                    and isinstance(getattr(self, path), pathlib.Path)):
                validated = getattr(self, path)
            else:
                validated = pathlib.Path(path)
        elif isinstance(path, pathlib.Path):
            validated = path
        else:
            raise TypeError(f'path must be a str or Path type')
        if test and not validated.exists():
            if create:
                self._write_folder(folder = validated)
            else:
                raise FileNotFoundError(f'{validated} does not exist')
        return validated
        
    def load(self,
            file_path: Union[str, pathlib.Path] = None,
            folder: Union[str, pathlib.Path] = None,
            file_name: str = None,
            file_format: Union[str, 'FileFormat'] = None,
            **kwargs) -> Any:
        """Imports file by calling appropriate method based on file_format.

        If needed arguments are not passed, default values are used. If
        'file_path' is passed, 'folder' and 'file_name' are ignored.

        Args:
            file_path (Union[str, Path]]): a complete file path.
                Defaults to None.
            folder (Union[str, Path]]): a complete folder path or the
                name of a folder stored in 'filer'. Defaults to None.
            file_name (str): file name without extension. Defaults to
                None.
            file_format (Union[str, FileFormat]]): object with
                information about how the file should be loaded or the key to
                such an object stored in 'filer'. Defaults to None
            **kwargs: can be passed if additional options are desired specific
                to the pandas or python method used internally.

        Returns:
            Any: depending upon method used for appropriate file format, a new
                variable of a supported type is returned.

        """
        return self.loader.transfer(
            file_path = file_path,
            folder = folder,
            file_name = file_name,
            file_format = file_format,
            **kwargs)

    def save(self,
            variable: Any,
            file_path: Union[str, pathlib.Path] = None,
            folder: Union[str, pathlib.Path] = None,
            file_name: str = None,
            file_format: Union[str, 'FileFormat'] = None,
            **kwargs) -> None:
        """Exports file by calling appropriate method based on file_format.

        If needed arguments are not passed, default values are used. If
        file_path is passed, folder and file_name are ignored.

        Args:
            variable (Any): object to be save to disk.
            file_path (Union[str, pathlib.Path]]): a complete file path.
                Defaults to None.
            folder (Union[str, pathlib.Path]]): a complete folder path or the
                name of a folder stored in 'filer'. Defaults to None.
            file_name (str): file name without extension. Defaults to
                None.
            file_format (Union[str, 'FileFormat']]): object with
                information about how the file should be loaded or the key to
                such an object stored in 'filer'. Defaults to None
            **kwargs: can be passed if additional options are desired specific
                to the pandas or python method used internally.

        """
        self.saver.transfer(
            variable = variable,
            file_path = file_path,
            folder = folder,
            file_name = file_name,
            file_format = file_format,
            **kwargs)
        return self

    def pathlibify(self,
            folder: str,
            file_name: str = None,
            extension: str = None) -> pathlib.Path:
        """Converts strings to pathlib Path object.

        If 'folder' matches an attribute, the value stored in that attribute
        is substituted for 'folder'.

        If 'name' and 'extension' are passed, a file path is created. Otherwise,
        a folder path is created.

        Args:
            folder (str): folder for file location.
            name (str): the name of the file.
            extension (str): the extension of the file.

        Returns:
            Path: formed from string arguments.

        """
        try:
            folder = getattr(self, folder)
        except (AttributeError, TypeError):
            pass
        if file_name and extension:
            return pathlib.Path(folder).joinpath(f'{file_name}.{extension}')
        else:
            return pathlib.Path(folder)

    """ Private Methods """

    def _validate_io_folder(self, 
            path: Union[str, pathlib.Path]) -> pathlib.Path:
        """[summary]

        Args:
            path (Union[str, pathlib.Path]): [description]

        Returns:
            [type]: [description]
            
        """
        try:
            return self.validate(path = path, create = False)
        except FileNotFoundError:
            return self.validate(path = self.root_folder / path)
                
    def _get_default_file_formats(self) -> Mapping[Any, 'FileFormat']:
        """Returns supported file formats.

        Returns:
            Mapping: with string keys and FileFormat instances as values.

        """
        return {
            'csv': FileFormat(
                name = 'csv',
                modules =  'pandas',
                extension = '.csv',
                load_method = 'read_csv',
                save_method = 'to_csv',
                shared_parameters = {
                    'encoding': 'file_encoding',
                    'index_col': 'index_column',
                    'header': 'include_header',
                    'usecols': 'included_columns',
                    'low_memory': 'conserve_memory',
                    'nrows': 'test_size'}),
            'excel': FileFormat(
                name = 'excel',
                modules =  'pandas',
                extension = '.xlsx',
                load_method = 'read_excel',
                save_method = 'to_excel',
                shared_parameters = {
                    'index_col': 'index_column',
                    'header': 'include_header',
                    'usecols': 'included_columns',
                    'nrows': 'test_size'}),
            'feather': FileFormat(
                name = 'feather',
                modules =  'pandas',
                extension = '.feather',
                load_method = 'read_feather',
                save_method = 'to_feather',
                required_parameters = {'nthreads': -1}),
            'hdf': FileFormat(
                name = 'hdf',
                modules =  'pandas',
                extension = '.hdf',
                load_method = 'read_hdf',
                save_method = 'to_hdf',
                shared_parameters = {
                    'columns': 'included_columns',
                    'chunksize': 'test_size'}),
            'json': FileFormat(
                name = 'json',
                modules =  'pandas',
                extension = '.json',
                load_method = 'read_json',
                save_method = 'to_json',
                shared_parameters = {
                    'encoding': 'file_encoding',
                    'columns': 'included_columns',
                    'chunksize': 'test_size'}),
            'stata': FileFormat(
                name = 'stata',
                modules =  'pandas',
                extension = '.dta',
                load_method = 'read_stata',
                save_method = 'to_stata',
                shared_parameters = {'chunksize': 'test_size'}),
            'text': FileFormat(
                name = 'text',
                modules =  None,
                extension = '.txt',
                load_method = '_import_text',
                save_method = '_export_text'),
            'png': FileFormat(
                name = 'png',
                modules =  'seaborn',
                extension = '.png',
                save_method = 'save_fig',
                required_parameters = {
                    'bbox_inches': 'tight', 
                    'format': 'png'}),
            'pickle': FileFormat(
                name = 'pickle',
                modules =  None,
                extension = '.pickle',
                load_method = '_pickle_object',
                save_method = '_unpickle_object')}

    def _get_default_parameters(self,
            settings: sourdough.Settings) -> Mapping[Any, Any]:
        """Returns default parameters for file transfers from 'settings'.

        Args:
            settings (Settings): an instance with a section named 'files' which
                contains default parameters for file transfers.

        Returns:
            Mapping: with default parameters from settings.

        """
        return self.settings['files']

    def _write_folder(self, folder: Union[str, pathlib.Path]) -> None:
        """Writes folder to disk.

        Parent folders are created as needed.

        Args:
            folder (Union[str, Path]): intended folder to write to disk.

        """
        pathlib.Path.mkdir(folder, parents = True, exist_ok = True)
        return self

    def _make_unique_path(self,
            folder: Union[pathlib.Path, str],
            name: str) -> pathlib.Path:
        """Creates a unique path to avoid overwriting a file or folder.

        Thanks to RealPython for this bit of code:
        https://realpython.com/python-pathlib/.

        Args:
            folder (Path): the folder where the file or folder will be located.
            name (str): the basic name that should be used.

        Returns:
            Path: with a unique name. If the original name conflicts with an
                existing file/folder, a counter is used to find a unique name
                with the counter appended as a suffix to the original name.

        """
        counter = 0
        while True:
            counter += 1
            path = pathlib.Path(folder) / name.format(counter)
            if not path.exists():
                return path


@dataclasses.dataclass
class Distributor(abc.ABC):
    """Base class for sourdough FileLoader and FileSaver.

    Args:
        filer (Filer): a related Filer instance.

    """

    filer: Filer

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""

        return self

    """ Private Methods """

    def _check_required_parameters(self,
            file_format: 'FileFormat',
            passed_kwargs: Mapping[Any, Any]) -> Mapping[Any, Any]:
        """Adds requited parameters if not passed.

        Args:
            file_format (FileFormat): an instance with information about
                additional kwargs to search for.
            passed_kwargs (MutableMapping[Any, Any]): kwargs passed to method.

        Returns:
            Mapping[Any, Any]: kwargs with only relevant parameters.

        """
        new_kwargs = passed_kwargs
        if file_format.required_parameters:
            for key, value in file_format.required_parameters:
                if value not in new_kwargs:
                    new_kwargs[key] = value
        return new_kwargs

    def _check_shared_parameters(self,
            file_format: 'FileFormat',
            passed_kwargs: Mapping[Any, Any]) -> Mapping[Any, Any]:
        """Selects kwargs for particular methods.

        If a needed argument was not passed, default values are used.

        Args:
            file_format (FileFormat): an instance with information about
                additional kwargs to search for.
            passed_kwargs (MutableMapping[Any, Any]): kwargs passed to method.

        Returns:
            Mapping[Any, Any]: kwargs with only relevant parameters.

        """
        new_kwargs = passed_kwargs
        if file_format.shared_parameters:
            for key, value in file_format.shared_parameters:
                if (value not in new_kwargs
                        and value in self.filer.default_parameters):
                    new_kwargs[key] = self.filer.default_parameters[value]
        return new_kwargs

    def _check_file_format(self,
            file_format: Union[str, 'FileFormat']) -> 'FileFormat':
        """Selects 'file_format' or returns FileFormat instance intact.

        Args:
            file_format (Union[str, FileFormat]): name of file format or a
                FileFormat instance.

        Raises:
            TypeError: if 'file_format' is neither a str nor FileFormat type.

        Returns:
            FileFormat: appropriate instance.

        """
        if isinstance(file_format, FileFormat):
            return file_format
        elif isinstance(file_format, str):
            return self.filer.file_formats[file_format]
        else:
            raise TypeError('file_format must be a str or FileFormat type')

    def _get_parameters(self,
            file_format: 'FileFormat',
            **kwargs) -> Mapping[Any, Any]:
        """Creates complete parameters for a file input/output method.

        Args:
            file_format (FileFormat): an instance with information about the
                needed and optional parameters.
            kwargs: additional parameters to pass to an input/output method.

        Returns:
            Mapping[Any, Any]: parameters to be passed to an input/output method.

        """
        parameters = self._check_required_parameters(
            file_format = file_format,
            passed_kwargs = kwargs)
        parameters = self._check_shared_parameters(
            file_format = file_format,
            passed_kwargs = kwargs)
        return parameters

    def _prepare_transfer(self,
            file_path: Union[str, pathlib.Path],
            folder: Union[str, pathlib.Path],
            file_name: str,
            file_format: Union[str, 'FileFormat']) -> Sequence[Union[
                pathlib.Path,
                'FileFormat']]:
        """Prepares file path related arguments for loading or saving a file.

        Args:
            file_path (Union[str, Path]): a complete file path.
            folder (Union[str, Path]): a complete folder path or the name of a
                folder stored in 'filer'.
            file_name (str): file name without extension.
            file_format (Union[str, FileFormat]): object with information about
                how the file should be loaded or the key to such an object
                stored in 'filer'.
            **kwargs: can be passed if additional options are desired specific
                to the pandas or python method used internally.

        Returns:
            Sequence: of a completed Path instance and FileFormat instance.

        """
        if file_path:
            file_path = pathlib.Path(file_path)
            if not file_format:
                file_format = [
                    f for f in self.filer.file_formats.values()
                    if f.extension == file_path.suffix[1:]][0]
        file_format = self._check_file_format(file_format = file_format)
        extension = file_format.extension
        if not file_path:
            file_path = self.filer.pathlibify(
                folder = folder,
                file_name = file_name,
                extension = extension)
        return file_path, file_format


@dataclasses.dataclass
class FileLoader(Distributor):
    """Manages file importing for sourdough.

    Args:
        filer (Filer): related Filer instance.

    """
    filer: Filer

    """ Public Methods """

    def load(self, **kwargs):
        """Calls 'transfer' method with **kwergs."""
        return self.transfer(**kwargs)

    def transfer(self,
            file_path: Union[str, pathlib.Path] = None,
            folder: Union[str, pathlib.Path] = None,
            file_name: str = None,
            file_format: Union[str, 'FileFormat'] = None,
            **kwargs) -> Any:
        """Imports file by calling appropriate method based on file_format.

        If needed arguments are not passed, default values are used. If
        file_path is passed, folder and file_name are ignored.

        Args:
            file_path (Union[str, Path]]): a complete file path.
                Defaults to None.
            folder (Union[str, Path]]): a complete folder path or the
                name of a folder stored in 'filer'. Defaults to None.
            file_name (str): file name without extension. Defaults to
                None.
            file_format (Union[str, FileFormat]]): object with
                information about how the file should be loaded or the key to
                such an object stored in 'filer'. Defaults to None
            **kwargs: can be passed if additional options are desired specific
                to the pandas or python method used internally.

        Returns:
            Any: depending upon method used for appropriate file format, a new
                variable of a supported type is returned.

        """
        file_path, file_format = self._prepare_transfer(
            file_path = file_path,
            folder = folder,
            file_name = file_name,
            file_format = file_format)
        parameters = self._get_parameters(file_format = file_format, **kwargs)
        if file_format.module:
            tool = file_format.load('import_method')
        else:
            tool = getattr(self, file_format.import_method)
        return tool(file_path, **parameters)


@dataclasses.dataclass
class FileSaver(Distributor):
    """Manages file exporting for sourdough.

    Args:
        filer (Filer): related Filer instance.

    """
    filer: Filer

    """ Public Methods """

    def save(self, **kwargs):
        """Calls 'transfer' method with **kwargs."""
        return self.transfer(**kwargs)

    """ Core sourdough Methods """

    def transfer(self,
            variable: Any,
            file_path: Union[str, pathlib.Path] = None,
            folder: Union[str, pathlib.Path] = None,
            file_name: str = None,
            file_format: Union[str, 'FileFormat'] = None,
            **kwargs) -> None:
        """Exports file by calling appropriate method based on file_format.

        If needed arguments are not passed, default values are used. If
        file_path is passed, folder and file_name are ignored.

        Args:
            variable (Any): object to be save to disk.
            file_path (Union[str, Path]]): a complete file path.
                Defaults to None.
            folder (Union[str, Path]]): a complete folder path or the
                name of a folder stored in 'filer'. Defaults to None.
            file_name (str): file name without extension. Defaults to
                None.
            file_format (Union[str, FileFormat]]): object with
                information about how the file should be loaded or the key to
                such an object stored in 'filer'. Defaults to None
            **kwargs: can be passed if additional options are desired specific
                to the pandas or python method used internally.

        """
        file_path, file_format = self._prepare_transfer(
            file_path = file_path,
            folder = folder,
            file_name = file_name,
            file_format = file_format)
        parameters = self._get_parameters(file_format = file_format, **kwargs)
        if file_format.module:
            getattr(variable, file_format.export_method)(variable, **parameters)
        else:
            getattr(self, file_format.export_method)(variable, **parameters)
        return self


@dataclasses.dataclass
class FileFormat(sourdough.LoaderMixin, sourdough.Component):
    """File format information.

    Args:
        name (str): designates the name of the class instance used
            for internal referencing throughout sourdough. If the class instance
            needs settings from the shared Settings instance, 'name' should
            match the appropriate section name in that Settings instance. When
            subclassing, it is a good settings to use the same 'name' attribute
            as the base class for effective coordination between sourdough
            classes. Defaults to None or __class__.__name__.lower().
        module (str): name of module where object to incorporate is located
            (can either be a sourdough or non-sourdough module).
        extension (str): actual file extension to use. Defaults to
            None.
        load_method (str): name of import method in 'module' to
            use. If module is None, the Distributor looks for the method
            as a local attribute. Defaults to None.
        save_method (str): name of export method in 'module' to
            use. If module is None, the Distributor looks for the method
            as a local attribute. Defaults to None.
        shared_parameters (Sequence[str]]): names of commonly used kwargs
            for either the import or export method. Defaults to None.
        required_parameters (Mapping[Any, Any]]): any required parameters
            that should be passed to the import or export methods. Defaults to
            None.

    """

    name: str = None
    modules: str = 'sourdough'
    _loaded: Mapping[Any, Any] = dataclasses.field(
        default_factory = dict)
    extension: str = None
    load_method: str = None
    save_method: str = None
    shared_parameters: Sequence[str] = None
    required_parameters: Mapping[Any, Any] = None
    