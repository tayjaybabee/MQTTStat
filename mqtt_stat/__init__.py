from mqtt_stat.log_engine import ROOT_LOGGER as LOG_DEVICE
from mqtt_stat.stats.battery import get_battery_info
from mqtt_stat.stats.network import get_network_name

_initialized = False
"""Set a flag  to indicate when MQTTStat is initialized."""

__all__ = ["LOG_DEVICE"]

LOG = LOG_DEVICE.logger
"""Logging device for MQTTStat"""

if not _initialized:
    LOG.info('Started MQTTStat!')
    _initialized = True
