import subprocess
from mqtt_stat.stats.network import NetworkInfo


class WindowsNetworkInfo(NetworkInfo):
    """Class to fetch network information on Windows."""

    def get_network_name(self):
        """Get the SSID of the currently connected network on Windows."""
        command = "netsh wlan show interfaces"
        try:
            result = subprocess.check_output(command, shell=True).decode()
            # Look for the SSID in the command output
            for line in result.split('\n'):
                if "SSID" in line:
                    return line.split(":")[1].strip()
        except subprocess.CalledProcessError:
            return "Not connected to a network."
