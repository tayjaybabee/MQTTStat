# -*- coding: utf-8 -*-
"""
Created on Mon Nov  6 18:40:54 2023

@author: tayja
"""

import PySimpleGUI as psg

from mqtt_stat.GUI.errors import *


class AlarmWindow:
    """A class to represent an alarm window using PySimpleGUI.

    This class provides a simple GUI window with a button to stop an alarm.

    Attributes:
        built (bool):
            Indicates whether the window has been built (read-only).

        layout (list):
            Stores the layout of the window (read-only).

            .. important::
                Accessing this before the window is built raises a :class:`WindowNotBuiltError`.

    Note:
        The window must be built using the `build` method before it can be used.
    """

    def __init__(
            self,
            auto_build=False,
            auto_run=False,
    ):
        self.__built = False
        self.__layout = None
        self.__auto_build = auto_build
        self.__auto_run = auto_run

    @property
    def auto_build(self) -> bool:
        """
        Is this window instance set to automatically build its layout?

        .. note::
            This is a read-only property.
        """
        return self.__auto_build

    @property
    def auto_run(self) -> bool:
        """
        Is this window instance set to automatically run?

        .. note::
            This is a read-only property.

        """
        return self.__auto_run

    @property
    def built(self) -> bool:
        """ Has this window been built? """
        return self.__built

    @property
    def layout(self):
        """ The window's layout """
        if self.built:
            return self.__layout
        else:
            raise WindowNotBuiltError(
                'The window\'s layout must be built before it can be returned! Try `self.build()`')

    def build(self):
        """
        Build the window.

        Calling this function causes the following changes:
            - `self.built` is set to `True`.
            - `self.layout` is given a PySimpleGUI layout-list object.
            - `self.run` will be runnable.

        Returns:
            None

        Raises:
            WindowAlreadyBuiltError:
                Raised when this method is called while `self.layout` is a value other than `None` or `self.built` is `True`

        Example:
            Without `self.build`:
                >>> window = AlarmWindow()
                >>> print(window.built)
                False  # The output indicates that the window has not yet been built.

            With `self.build`:
                >>> window = AlarmWindow()
                >>> window.build()
                >>> window.built
                True  # This output indicates that the window was built

            Passing `True` for
        """
        if self.built:
            raise WindowAlreadyBuiltError('The window has already been built!')

        self.__layout = [
            # A text field
            [psg.Text('Alarm Controller', justification='center')],

            [
                # A button to stop the active alarm.
                psg.Button(
                    'Stop Alarm',
                    tooltip='Stop the associated alarm.',
                    bind_return_key=True,
                    focus=True,
                    key='STOP_BUTTON'
                )
            ]

        ]

        # Set the `built` attribute.
        self.__built = True
