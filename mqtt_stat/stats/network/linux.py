import subprocess
from mqtt_stat.stats.network import NetworkInfo


class LinuxNetworkInfo(NetworkInfo):
    """Class to fetch network information on Linux."""

    def get_network_name(self):
        """Get the SSID of the currently connected network on Linux."""
        command = "nmcli -t -f active,ssid dev wifi | egrep '^yes' | cut -d\: -f2"
        try:
            result = subprocess.check_output(command, shell=True).decode().strip()
            return result if result else "Not connected to a network."
        except subprocess.CalledProcessError:
            return "Not connected to a network."
