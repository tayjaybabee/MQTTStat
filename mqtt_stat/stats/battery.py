import psutil


# Function to get battery information
def get_battery_info():
    """Get the battery status.

    Returns:
        battery_info (dict): A dictionary containing battery percentage and whether it's charging or not.
    """
    battery = psutil.sensors_battery()
    if battery is not None:
        battery_info = {
            'percent': battery.percent,
            'power_plugged': battery.power_plugged
        }
        return battery_info
    else:
        return "No battery information available."


# Get the current battery status
# battery_status = get_battery_info()
# battery_status
