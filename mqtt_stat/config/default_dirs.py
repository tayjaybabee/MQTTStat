import platformdirs

from mqtt_stat.__about__ import __PROG__ as PROG_NAME, __AUTHOR__ as AUTHOR

DEFAULT_CONFIG_DIR = platformdirs.user_config_dir(PROG_NAME, AUTHOR)
"""The default directory where configuration files will be stored."""

DEFAULT_DATA_DIR = platformdirs.user_data_dir(PROG_NAME, AUTHOR)
"""The default directory where app data files will be stored."""

CACHE_DIR = platformdirs.user_cache_dir(PROG_NAME, AUTHOR)
"""The directory where cache files will be stored."""
