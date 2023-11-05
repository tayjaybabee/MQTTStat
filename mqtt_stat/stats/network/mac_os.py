import subprocess
from mqtt_stat.stats.network import NetworkInfo


class MacOSNetworkInfo(NetworkInfo):
    """Class to fetch network information on macOS."""

    def get_network_name(self):
        """Get the SSID of the currently connected network on macOS."""
        command = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -I"
        try:
            result = subprocess.check_output(command, shell=True).decode()
            # Look for the SSID in the command output
            for line in result.split('\n'):
                if " SSID" in line:
                    return line.split(":")[1].strip()
        except subprocess.CalledProcessError:
            return "Not connected to a network."
