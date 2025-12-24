"""
This module provides errors/exceptions and warnings of general use.

Exceptions that are specific to a given package should **not** be here,
but rather in the particular package.

This code is based on that provided by SunPy see
    licenses/SUNPY.rst
"""

import warnings

__all__ = [
    "CCSDSWarning",
    "CCSDSUserWarning",
    "CCSDSDeprecationWarning",
    "CCSDSPendingDeprecationWarning",
    "warn_user",
    "warn_deprecated",
]


class CCSDSWarning(Warning):
    """
    The base warning class from which all SWX warnings should inherit.

    Any warning inheriting from this class is handled by the SWX
    logger. This warning should not be issued in normal code. Use
    "SWXUserWarning" instead or a specific sub-class.
    """


class CCSDSUserWarning(UserWarning, CCSDSWarning):
    """
    The primary warning class for CCSDS.

    Use this if you do not need a specific type of warning.
    """


class CCSDSDeprecationWarning(FutureWarning, CCSDSWarning):
    """
    A warning class to indicate a deprecated feature.
    """


class CCSDSPendingDeprecationWarning(PendingDeprecationWarning, CCSDSWarning):
    """
    A warning class to indicate a soon-to-be deprecated feature.
    """


def warn_user(msg, stacklevel=1):
    """
    Raise a `CCSDSUserWarning`.

    Parameters
    ----------
    msg : str
        Warning message.
    stacklevel : int
        This is interpreted relative to the call to this function,
        e.g. ``stacklevel=1`` (the default) sets the stack level in the
        code that calls this function.
    """
    warnings.warn(msg, CCSDSUserWarning, stacklevel + 1)


def warn_deprecated(msg, stacklevel=1):
    """
    Raise a `CCSDSDeprecationWarning`.

    Parameters
    ----------
    msg : str
        Warning message.
    stacklevel : int
        This is interpreted relative to the call to this function,
        e.g. ``stacklevel=1`` (the default) sets the stack level in the
        code that calls this function.
    """
    warnings.warn(msg, CCSDSDeprecationWarning, stacklevel + 1)
