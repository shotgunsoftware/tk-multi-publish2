# Copyright (c) 2017 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
All custom exceptions that this app emits are defined here.
"""

from sgtk import TankError

class PublishError(TankError):
    """
    Base class for all publish related errors
    """
    pass

class ValidationFailure(PublishError):
    """
    Indicates that validation has failed inside a hook
    """
    pass

class PublishFailure(PublishError):
    """
    Indicates that validation has failed inside a hook
    """
    pass

class PluginError(PublishError):
    """
    Base class for all plugin related errors
    """
    pass


class PluginValidationError(PluginError):
    """
    A plugin could not be found
    """
    pass


class PluginNotFoundError(PluginError):
    """
    A plugin could not be found
    """
    pass
