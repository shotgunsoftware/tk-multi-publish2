# Copyright 2026 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.

from __future__ import annotations  # needed for Houdini 19.5 support

from tank_vendor.flow_integration_sdk.exceptions import FlowError


class GenerateDerivativeError(FlowError):
    """Raised when a derivative asset (e.g. Alembic export) could not be generated."""

    def __init__(self, *args, **kwargs):
        message = "Could not generate derivative."
        super().__init__(message, *args, **kwargs)


class IllegalDependencyError(FlowError):
    """Raised when a dependency update is rejected because one or more dependency
    file paths fall outside the allowed locations for the current pipeline context.

    Attributes:
        dep_paths: The list of offending dependency paths.
    """

    def __init__(self, *args, dep_paths: list[str], **kwargs):
        message = "Illegal dependencies encountered."
        super().__init__(message, *args, **kwargs)
        self.dep_paths = dep_paths


class PublishCanceledException(FlowError):
    """
    Exception raised when user cancels publish operation.
    This can happen in various scenarios:
    - User clicks Cancel in conflict dialog
    - User chooses Stash and Update in conflict dialog
    - User chooses Discard and Update in conflict dialog
    - User manually stops the publish process
    When this exception is raised, the publisher will display a
    "Publish Cancelled" message instead of "Publish Failed" or "Publish Complete".
    """

    def __init__(self, *args, **kwargs):
        message = "User cancelled the publish to Flow AM."
        super().__init__(message, *args, **kwargs)
