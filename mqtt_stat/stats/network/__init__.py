import subprocess
import platform


class NetworkInfo:
    """Base class for fetching network information."""

    def get_network_name(self):
        """Method to get the network name. Needs to be overridden by subclasses."""
        raise NotImplementedError("Subclasses should implement this method")


def get_network_info_class():
    """Factory function to get the appropriate network info class based on the OS."""
    os_name = platform.system()

    if os_name == 'Windows':
        from mqtt_stat.stats.network.win import WindowsNetworkInfo
        return WindowsNetworkInfo()

    elif os_name == 'Darwin':
        from mqtt_stat.stats.network.mac_os import MacOSNetworkInfo
        return MacOSNetworkInfo()

    elif os_name == 'Linux':
        from mqtt_stat.stats.network.linux import LinuxNetworkInfo
        return LinuxNetworkInfo()
    else:
        raise ValueError(f"Unsupported operating system: {os_name}")


NETWORK_INFO = get_network_info_class()


def get_network_name():
    """Get the network name."""
    return NETWORK_INFO.get_network_name()


# Instantiate the appropriate class and get the network name.
# network_info = get_network_info_class()
# network_name = network_info.get_network_name()
# network_name
