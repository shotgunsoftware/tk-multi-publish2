# Copyright 2026 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.

from __future__ import annotations  # needed for Houdini 19.5 support

from enum import Enum

from tank_vendor.flow_integration_sdk import schema

# File extensions that must be published from within their DCC application,
# not from the Desktop publisher.
FLOWAM_DCC_EXTENSIONS = [
    "aep",
    "aet",
    "hip",
    "hipnc",
    "hiplc",
    "hrox",
    "ma",
    "max",
    "mb",
    "nk",
    "nkple",
    "osb",
    "psb",
    "psd",
    "vpb",
    "vpe",
    "wire",
]


class DerivativeType(Enum):
    """Enum of supported derivative asset types."""

    ALEMBIC = "ABC"  #: Alembic export.

    def file_type(self) -> str:
        """Return the file extension associated with derivative type."""
        if self == DerivativeType.ALEMBIC:
            return "abc"
        return ""  # type: ignore[unreachable]

    def type_id(self) -> str:
        """Return the type id associated with derivative type."""
        if self == DerivativeType.ALEMBIC:
            return schema.get_schema_id("type.derivative.abc")
        return ""  # type: ignore[unreachable]
