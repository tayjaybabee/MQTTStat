from logging import INFO

from inspy_logger import Logger

from mqtt_stat.__about__ import __PROG__ as PROG_NAME

ROOT_LOGGER = Logger(PROG_NAME, console_level=INFO, file_level=INFO)

log = ROOT_LOGGER.logger

log.debug(f'Started logging for {PROG_NAME}')
