# -*- coding: utf-8 -*-
"""
This module provides functionality to play an alarm sound using pygame's mixer.

It allows for the sound to be played at a regular interval, with the volume
increasing incrementally until a maximum volume is reached or the alarm is stopped.

The alarm sound can be started in a separate thread, enabling the main program to
continue execution independently. The user can stop the alarm by pressing <ENTER>.

Functions:

    play_sound(volume):
        Play a sound at a specified volume.

    alarm(interval, volume_increment, volume_start, volume_max):
        Play an alarm sound at set intervals, increasing the volume each time.

    start_alarm(**kwargs):
        Start the alarm in a separate thread.

Example:
    >>> from mqtt_stat.helpers.audio import start_alarm
    >>> start_alarm(interval=2, volume_increment=0.05, volume_start=0.1, volume_max=0.5)

Note:
    Ensure pygame is installed and the sound file path is correctly set before running the module.

Created on Mon Nov 6 16:07:12 2023
@author: Taylor

"""
import io
from pathlib import Path
from threading import Thread, Event
from time import sleep

import pygame

from mqtt_stat.audio.asset_crypt import AssetCrypt

# Initialize pygame's mixer
pygame.mixer.init()

DEFAULTS = {
    'interval': 1,
    'volume': {
        'decrement': 0.01,
        'increment': 0.1,
        'max': 1.0,
        'start': 0.1,
    }
}
"""The default settings for the volume controller"""


class VolumeControl:
    __decrement = None
    __increment = None
    __max_volume = None
    __sound = None
    __volume = None

    def __init__(
            self,
            sound: pygame.mixer.Sound,
            start_volume: (float | int | None) = None,
            max_volume: (float | int | None) = None,
            increment: (float | None) = None
    ):

        self.__sound = sound
        vol_defaults = DEFAULTS['volume']

        # Set max_volume first since increment depends on it
        self.__max_volume = max_volume if max_volume is not None else vol_defaults['max']

        # Now set increment
        self.increment = increment if increment is not None else vol_defaults['increment']

        # Finally, set the initial volume
        self.__volume = start_volume if start_volume is not None else vol_defaults['start']
        self.sound.set_volume(self.volume)

    @property
    def increment(self) -> float:
        return self.__increment

    @increment.setter
    def increment(self, new):

        new = float(new)

        if new <= 0:
            raise ValueError('"increment" must be greater than 0!')
        elif new >= self.max_volume:
            raise ValueError(f'"increment" must be less than {self.max_volume}!')

        self.__increment = new

    @property
    def max_volume(self) -> float:
        """
        The maximum volume level.
        """
        return self.__max_volume

    @max_volume.setter
    def max_volume(self, new):
        new = float(new)

        # Ensure that the max volume does not exceed 1 or fall below 0.
        if new <= 0:
            raise ValueError('"max_volume" must be greater than 0!')
        elif new > 1:
            raise ValueError('"max_volume" cannot exceed 1!')
        elif new <= self.increment:
            raise ValueError(f'"max_volume" must be greater than {self.increment} (the incremental)!')

        # Set the maximum volume
        self.__max_volume = new

    @property
    def sound(self) -> pygame.mixer.Sound:
        """
        The sound object associated with this volume controller.

        .. note::
            This is a read-only property.
        """
        return self.__sound

    @property
    def volume(self) -> float:
        """
        The current volume level of this volume controller.

        """
        return self.sound.get_volume()

    @volume.setter
    def volume(self, new: float) -> None:
        new = float(new)

        # Ensure that the new volume level is within acceptable bounds.
        if new > self.max_volume:
            raise ValueError(f'The volume cannot be set above {self.max_volume}!')

        if new < 0.0:
            raise ValueError('The volume cannot be set below 0.0!')

        self.sound.set_volume(new)

    def decrease_volume(self, decrement) -> None:
        """
        Decrease the volume by a set amount.

        Arguments:
            decrement (float):
                The amount to decrease the volume by.

        Returns:
            None

        .. note::
            This function will not decrease the volume below 0.0.
        """
        self.volume -= decrement

    def get_volume(self):
        return self.volume

    def increase_volume(self, increment: float = None):

        increment = increment or self.increment
        new_vol = min(self.max_volume, self.volume + increment)
        self.volume = min(self.max_volume, self.volume + increment)

    def set_volume(self, volume):
        """
        Sets the volume to the specified level.

        .. note::
            This function will not set the volume below 0.0 or above `self.max_volume`.

        Parameters:
            volume (float|int):
                The volume to set `self.sound` to play at.

        Returns:
            None

        """
        volume = float(volume)
        self.volume = max(0, min(self.max_volume, volume))

    """
    Initializes the `VolumeControl` object with a Pygame sound object.

    Arguments:

        sound (pgame.mixer.Sound):
            The Pygame sound object to manipulate.

        start_volume (float):
            The initial volume level (0.0 - .10).

        max_volume (float):
            The maximum volume level
    """


class AlarmAsset:
    ALARM_EVENT = Event()
    VOL_DEFAULTS = DEFAULTS['volume']

    def __init__(
            self,
            encrypted_audio_path: (str | Path),
            interval: (int | float) = DEFAULTS['interval'],
            volume_increment: float = VOL_DEFAULTS['increment'],
            volume_start: float = VOL_DEFAULTS['start'],
            volume_max: (float | int) = VOL_DEFAULTS['max']
    ):
        self.__encrypted_audio_path = encrypted_audio_path

        self.__sound = self.load_audio_asset()

        self.__alarm_event = self.ALARM_EVENT

        self.__volume_controller = VolumeControl(
            sound=self.sound,
            max_volume=volume_max,
            increment=volume_increment,
            start_volume=volume_start
        )

        self.__thread = None

        self.__encrypted_audio_path = Path(encrypted_audio_path)

        self.__interval = float(interval)

        self.__volume_increment = float(volume_increment)

        self.__volume_start = float(volume_start)

        self.__volume_max = float(volume_max)

    @property
    def alarm_event(self) -> Event:
        """
        The alarm event.
        
        .. note::
            This is a read-only property.
        """
        return self.__alarm_event

    @property
    def encrypted_audio_path(self) -> Path:
        """
        The path to the encrypted audio file.
        """
        return self.__encrypted_audio_path

    @encrypted_audio_path.setter
    def encrypted_audio_path(self, new):
        # Make sure the new value is a valid `Path` object.
        new = Path(new)

        # Make sure the new value is a path that exists.
        if not new.exists():
            raise FileNotFoundError(f'"{new}" does not exist!')

        # Set the property to its new value.

    @property
    def interval(self) -> float:
        """
        The interval in seconds of time between each iteration.
        
        .. note::
            This is a read-only property.
        """
        return self.__interval

    @property
    def sound(self) -> (pygame.mixer.Sound, None):
        return self.__sound

    @property
    def thread(self) -> Thread:
        """"
        The alarm thread.
        
        ., note::
            This is a read-only property.
        """
        return self.__thread

    @property
    def volume_max(self) -> float:
        """

        .. note::
            This is a read-only property.
        """
        return self.__volume_max

    @property
    def volume_increment(self) -> float:
        """
        The number at which the volume is increased with each iteration.

        .. note::
            This is a read-only property.
        """
        return self.__volume_increment

    @property
    def volume_start(self) -> float:
        """
        The volume level (0.0 - 1.0) at which the alarm starts increasing from.

        .. note::
            This is a read-only property.
        """
        return self.__volume_start

    def load_audio_asset(self):
        with AssetCrypt(self.encrypted_audio_path) as ac:
            return pygame.mixer.Sound(file=io.BytesIO(ac.decrypt()))

    def play_sound(self, volume: float):
        pass


# Old version code ------------------------------------


# Event for controlling the alarm state.
alarm_event = Event()


def load_audio_asset(asset_path):
    asset_path = Path(asset_path).expanduser().resolve()

    with AssetCrypt(asset_path) as ac:
        return pygame.mixer.Sound(file=io.BytesIO(ac.decrypt()))


def play_sound(volume):
    """
    Play a sound at a given volume level.

    Arguments:

        volume (float):
            Volume of the sound to play (0.0 - 1.0).

    Returns:
        None

    Example:
        >>> play_sound(0.5)  # Plays the sound at half volume.

    """
    sound.set_volume(volume)
    sound.play()
    pygame.time.wait(int(sound.get_length() * 1000))


def alarm(interval=1, volume_increment=0.1, volume_start=0.1, volume_max=1.0):
    """
    Play an alarm sound at a regular interval, increasing in volume with each iteration.

    Arguments:
        interval (int):
            The time in seconds between each iteration.

        volume_increment (float):
            The amount to increase the volume with each iteration.

        volume_start (float):
            The volume level the alarm starts with.

    Returns:
        None

    Example:
        >>> alarm(1, 0.1)  # Plays the sound every second, increasing volume by 10% with each iteration.

    """
    if interval <= 0:
        raise ValueError('"interval" must be greater than 0!')

    # Iterate through the variables
    for arg in ['volume_increment', 'volume_start', 'volume_max']:
        value = locals()[arg]

        if not (0 <= value <= 1):
            raise ValueError(f'{arg} must be between 0 and 1 inclusive!')

    try:
        # Set initial volume to the set percentage.
        volume = volume_start
        print('Alarm sounding...press <ENTER> to stop it.')

        while not alarm_event.is_set():
            # Announce sound play
            print(f'Playing sound at volume: {volume:.2f}')
            play_sound(volume)
            sleep(interval)

            # Increase the volume level by the set increment.
            volume += volume_increment
            # Ensure volume does not exceed `volume_max`.
            volume = min(volume, volume_max)

    except KeyboardInterrupt:

        pass

    except Exception as e:

        # Announce that an error has occurred
        print(f'An error occurred: {e}')

    finally:

        # Announce finish of alarm
        print('Alarm finished.')


def rearm_alarm(no_delay=False, delay_duration=2):
    global alarm_event

    if not no_delay:
        sleep(delay_duration)

    alarm_event.clear()


def start_alarm(**kwargs):
    """
    Start the alarm in a separate thread.

    This function starts the alarm in a thread, allowing it to run independently of the main program flow.

    Arguments:
        interval (int):
            The time in seconds between each iteration.

        volume_increment (float):
            The amount to increase the volume with each iteration.

        volume_start (float):
            The volume level the alarm starts with.

    Example:
        >>> start_alarm()

    """
    global alarm_event

    alarm_event.clear()
    snd_thread = Thread(target=alarm, kwargs=kwargs)
    snd_thread.start()

    while not alarm_event.is_set():
        try:
            input('Press <ENTER> to stop the alarm...\n')
            alarm_event.set()
        except KeyboardInterrupt:
            print('\nPlease press <Enter> to stop the alarm...')

    snd_thread.join()
    print('Alarm stopped')
