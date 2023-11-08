# -*- coding: utf-8 -*-
"""
This module defines custom exception classes for handling GUI-related errors.

The `GUIError` class is a generic exception class for GUI-related issues, providing a standard prefix for all error messages. `WindowNotBuiltError` is a specific exception class that indicates an attempt to perform an operation on a GUI window that has not been constructed yet.

Classes:
    GUIError: Base class for exceptions that occur within the GUI.
    WindowNotBuiltError: Specific exception for errors related to accessing properties or methods of a GUI window that has not been built.

Example:
    >>> raise WindowNotBuiltError("Custom message")
    Traceback (most recent call last):
        ...
    WindowNotBuiltError: A GUI error has occurred: Custom message

    >>> raise WindowNotBuiltError()
    Traceback (most recent call last):
        ...
    WindowNotBuiltError: A GUI error has occurred: The window has not yet been built.

Created on Mon Nov 6 19:25:40 2023
@author: Taylor
"""


class GUIError(Exception):
    """Base class for exceptions originating from the GUI."""

    # Default error-message prefix for all GUI related errors.
    _prefix_message = 'A GUI error has occurred:'

    def __init__(self, message=None):
        """
        Initialize the error with an optional custom message.

        Arguments:
            message (str, optional):
                Custom message for the error. Defaults to `None`.
        """

        # If a custom message is provided, prepend the prefix.
        if message:
            full_msg = f'{self._prefix_message} {message}'
        else:
            full_msg = self._prefix_message

        super().__init__(full_msg)


class WindowNotBuiltError(GUIError):
    """Exception raised when an operation is attempted on an unbuilt window."""

    # Specific error message
    _default_message = 'The window has not yet been built.'

    def __init__(self, message=None):
        """
        Initialize the error with an optional custom message.

        Arguments:
            message (str, optional):
                Custom message for the error Defaults to `None`.
        """
        if message is None:
            message = self._default_message

        super().__init__(message)


class WindowAlreadyBuiltError(GUIError):
    """Exception raised for errors related to a GUI window being built more than once.

    This exception is raised when there is an attempt to construct or initialize a GUI window that has already been built.

    Inherits from:
        GUIError: Base class for GUI-related exceptions.

    Methods:
        __init__: Constructs the WindowAlreadyBuiltError instance.
    """

    _default_message = 'The window has already been built.'

    def __init__(self, message=None):
        """
        Initializes the WindowAlreadyBuiltError with an optional custom message.

        Args:
            message (str, optional): Custom message for the error. Defaults to a standard message indicating the window has already been built.

        Examples:
            >>> raise WindowAlreadyBuiltError("Tried to initialize the main window twice.")
            WindowAlreadyBuiltError: A GUI error has occurred: Tried to initialize the main window twice.
        """
        message = message if message is not None else self._default_message
        super().__init__(message)
