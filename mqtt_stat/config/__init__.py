import json
import os
from pathlib import Path

from mqtt_stat.config.default_dirs import DEFAULT_CONFIG_DIR
from mqtt_stat.log_engine import ROOT_LOGGER, MQTTLoggable

LOGGER = ROOT_LOGGER.get_child('log_engine')

CONFIG_FILENAME = 'config.json'

DEFAULT_CONFIG_FILEPATH = Path(DEFAULT_CONFIG_DIR).joinpath()


def create_missing_directories(filepath: str) -> (Path | None):
    """
    Create the missing parent directories leading to a filepath.

    Parameters:

        filepath (str):
            The path to create missing parent directories for.

    Returns:
        (Path|None):
            This function has two possible return values;
                - None:
                    The target directory already exists.

                - Path:
                    If the target directory was created, the path is returned.


    """
    # Create an object representing target directory.
    fp = Path(filepath).expanduser().absolute()

    # Get the parent directory
    parent = str(fp.parent)
    parent_fp = Path(parent)

    # Create missing directories.
    if not parent_fp.exists():
        os.makedirs(parent_fp)
        return parent_fp
    else:
        return None


class ConfigManager(MQTTLoggable):
    """
    A class for managing the application configuration.

    Attributes:

        auto_load(bool):
            Should the configuration be automatically loaded at runtime.
            Defaults to False.

        config_file(str):
            The path at which the configuration will be stored. Defaults to
            `user_config_dir(PROG_NAME, AUTHOR)\\config.json`

    """
    DEFAULT_FILEPATH = DEFAULT_CONFIG_FILEPATH

    def __init__(
            self,
            parent_log_device=None,
            config_dir=None,
            config_file='config.json',
            auto_load=False,
            create_missing_dirs=True,
            default_config_file='config.json.example'
    ):
        """
        Initializes the ConfigManager.

        Args:
            parent_log_device (InspyLogger):
                The parent log device for the module.

            config_dir (str):
                The path at which the configuration will be stored.

            config_file (str):
                Path to the configuration file.

            auto_load (bool):
                Should the configuration be loaded automatically at instantiation.(Default: False).

            create_missing_dirs (bool):
                Should missing directories be created at instantiation.(Default: True)

            default_config_file (str):
                Path to the example configuration file with default settings.

        Usage example:
            config_manager = ConfigManager()
            settings = config_manager.load_config()
        """
        # Set up the logger through the logging parent class.
        super().__init__(parent_log_device=parent_log_device or LOGGER)

        # Determine the directory this file is located in to find
        # the sample configuration file.
        file_dir = os.path.dirname(os.path.abspath(__file__))

        log = self.log_device.logger

        self.__config_fp = os.path.join(config_dir or DEFAULT_CONFIG_DIR, config_file)

        log.debug(f'Config file: {self.config_filepathpath}')

        self.default_config_file = os.path.join(file_dir, default_config_file)

        # Create a dunder variable to hold the value of the `auto_load` class property.
        self.__auto_load = auto_load

        log.debug(f'Auto-load enabled: {self.auto_load}')

        # Create a dunder variable to hold the value of the `create_missing_dirs` class property.
        self.__create_missing_dirs = create_missing_dirs
        log.debug(f'create_missing_dirs enabled: {self.create_missing_dirs}')

        # Create a dunder variable to hold the configuration state.
        self.__config = None

        # If `auto_load` is `True` let's load the configuration file.
        if self.auto_load:
            log.debug(f'Loading file automatically due to settings.')
            self.load_config()

    @property
    def auto_load(self) -> bool:
        """
        Retrieves the value of the `auto_load` property.

        Returns:
            (bool):
                The value of the `auto_load` property.
        """
        return self.__auto_load

    @auto_load.setter
    def auto_load(self, new):
        """
        Setter method for the `auto_load` attribute.

        Parameters:
            new (bool):
                The new value for the `auto_load` attribute.

        Raises:
            ValueError:
                If `new` is not a boolean.

        Returns:
            None
        """
        if not isinstance(new, bool):
            raise ValueError("`auto_load` must be a boolean!")

        self.__auto_load = True

    @property
    def config(self):
        """
        The current configuration state.
        """
        if self.__config is None:
            self.load_config()

        return self.__config

    @config.deleter
    def config(self):
        """
        Delete the current configuration state.
        """
        log_device = self.log_device.get_child()
        log = log_device.logger
        log.debug('`config` property value is being deleted.')

    @property
    def config_filepath(self):
        """
        The path to the config file.

        Returns:
            Path:
                The path to the config file.
        """
        return Path(self.__config_fp).expanduser().resolve()

    @config_filepath.setter
    def config_filepath(self, new: Path):
        """
        Setter method for the `config_filepath` property.
        """
        # Validate the `new` path parameter before setting it.
        #     - The `new` parameter value must be  either:
        #         - A pathlib.Path object, or;
        #         - A string that can be converted to a pathlib.Path object
        if isinstance(new, (Path, str)):
            if isinstance(new, str):
                new = Path(new).expanduser().resolve().absolute()
            else:
                new = new.resolve().absolute()
        else:
            raise TypeError('The `config_filepath` property must be a string or a Path object!')

        self.__config_fp = new

    @property
    def config_filepath_string(self):
        """
        The path to the config file as a string.

        Returns:
            str:
                The path to the config file.

        """
        return str(self.config_filepath)

    @property
    def create_missing_dirs(self) -> bool:
        """
        Retrieves the value of the `create_missing_dirs` property.

        Returns:

        """
        return self.__create_missing_dirs

    @create_missing_dirs.setter
    def create_missing_dirs(self, new: bool):
        """
        Setter method for the `create_missing_dirs` property.

        Parameters:
            new: (bool):
                The new value for the `create_missing_dirs` property.

        Returns:
            None

        Raises:
            TypeError:
                If `new` is not a boolean

        """
        # Check the type of `new` to ensure it's a boolean, raise
        # `TypeError` otherwise.
        if not isinstance(new, bool):
            raise TypeError("`create_missing_dirs` must be a boolean value!")

        # No error? Let's set the value.
        self.__create_missing_dirs = new

    def assess_config(self):
        conf_fp = self.config_filepath

        if not conf_fp.exists():
            self.create_blank_config()

    def load_config(self):
        """
        Loads the configuration from the config file, creating one from the defaults if necessary.

        Returns:
            dict: A dictionary containing the configuration parameters.
        """
        log_device = self.log_device.get_child()

        log = log_device.logger

        default_config = self.load_default_config()
        log.debug(f'Default config filepath: {Path(self.default_config_file).absolute()}')

        config_file = Path(self.config_filepath).absolute()

        if not config_file.exists():
            log.warning(f'Found no configuration file at {Path(self.config_filepath).absolute()}')

            log.debug(f'Creating new  configuration file at ')

            self.save_config(default_config)

            return default_config

        log.debug('Requesting configuration merge...')

        self.merge_configs(config_file)

        with open(self.config_filepath, 'r') as f:
            user_config = json.load(f)

        merged_config = {**default_config, **user_config}

        if merged_config != user_config:
            self.save_config(merged_config)

        # Set the class variable for the configuration state.
        self.__config = merged_config

        return merged_config

    @staticmethod
    def load_file(filepath):
        """
        Returns a dictionary of configuration options from a file at the given path.

        Parameters:
            filepath (str|Path):
                The path to the file you want to load.

        Returns:

        """
        with open(filepath, 'r') as file:
            return json.load(file)

    def create_blank_config(self):
        # Set up method logger
        log_device = self.log_device.get_child()
        log = log_device.logger

        parent_fp = self.config_filepath.parent
        parent_fp_str = str(parent_fp)
        config_fp = self.config_filepath
        config_fp_str = str(config_fp)

        # Raise an exception if the config file already exists at the set filepath.
        if self.config_filepath.exists():
            raise FileExistsError(
                f'Found existing config file: {self.config_filepath}. You must explicitly delete this file before proceeding!')

        # Does the directory path in which  the config file is located exist?
        if not parent_fp.exists():

            log.warning(f'Parent directory {parent_fp} nonexistent.')

            if self.create_missing_dirs:
                missing = create_missing_directories(parent_fp_str)
            else:
                log.error(f'Cannot create new config file at {parent_fp_str}!')
                log.info(
                    'Either allow the application to create missing directories or create a new config file and provide the path to the new file to this class in a new instance.')

            self.save_config(self.load_default_config())

    def merge_configs(self, user_config):
        """
        Merges the given configuration with the default configuration to integrate any new config options.

        Parameters:
            user_config(dict):
                The configuration to merge with the default configuration.
        """
        default_config = self.load_file(user_config)

    def save_config(self, config):
        """
        Saves the given configuration to the config file.

        Arguments:
            config (dict): Configuration to save.
        """
        # Start logging for method.
        log = self.log_device.logger

        # Inform
        log.debug(f'Received request to save configuration file to {self.config_filepath}')

        # Save configuration to file
        with open(self.config_filepath, 'w') as f:
            json.dump(config, f, indent=4)

        # Inform success
        log.debug(f'Saved configuration file to {self.config_filepath}')

    def create_default_config(self):
        """
        Creates the actual configuration file from the default values if it doesn't exist.
        """
        config = self.load_default_config()
        if not Path(self.config_filepath).exists():
            os.makedirs(Path(self.config_filepath).parent)
        with open(self.config_filepath, 'w') as f:
            json.dump(config, f, indent=4)
        print(f"Created the default configuration file: {self.config_filepath}")

    def create_user_config(self):
        conf_fp = self.config_filepath

    def load_default_config(self):
        """
        Loads the default configuration from the example file.

        Returns:
            dict: A dictionary containing the default configuration parameters.
        """
        with open(self.default_config_file, 'r') as f:
            return json.load(f)

    def get(self, key):
        return self.config.get(key)

    def set(self, key, new):
        pass

    def reload_config(self):
        log_device = self.log_device.get_child()
        log = log_device.logger

        log.debug('Reloading configuration...')

        log.debug('Deleting current configuration from member...')

        # Delete the current configuration state from memory.
        del self.config

        log.debug(f'Loading configuration state from configuration file {self.config_filepath}...')
        self.load_config()

    def prepare_config_path(self):
        """
        Prepares the path to the config file, while respecting the parameters/attributes of the class.

        Returns:
            None

        """
        # Prepare the log device
        log_device = self.log_device.get_child()
        log = log_device.logger

        parent_fp = self.config_filepath.parent
        parent_fp_str = str(parent_fp)

        config__fp = self.config_filepath

        config_fp_str = str(config__fp)

        # Raise an exception if the config file already exists at the set filepath.
        if self.config_filepath.exists():
            raise FileExistsError(
                f'Found existing config file: {self.config_filepath}. You must explicitly delete this file before '
                f'proceeding!'
            )

        # Does the directory path in which  the config file is located exist?
        if not parent_fp.exists():

            log.warning(f'Parent directory {parent_fp} nonexistent.')

            if self.create_missing_dirs:
                missing = create_missing_directories(config_fp_str)
            else:
                log.error(f'Cannot create new config file at {parent_fp_str}!')
                log.info(
                    'Either;\n '
                    '      - Allow the application to create missing directories, or;\n'
                    '      - Manually:\n'
                    '          - Create a new config file, and;\n'
                    '              - Provide the path to the new file to this class in a new instance, or;\n'
                    '              - Provide the path to the new config file to `config'
                    'provide the path to the new file to this class in a new instance.'
                )


# Instantiate the config manager.
CONFIG_MAN = ConfigManager()
"""An instance of ConfigManager."""

# Load the configuration
config = CONFIG_MAN.load_config()
"""The configuration dictionary."""
