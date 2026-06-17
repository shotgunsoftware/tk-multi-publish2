# Copyright 2026 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.

from __future__ import annotations

from enum import Enum

from tank_vendor.flow_integration_sdk.schema import get_schema_id

# Flow AM schema type names (used with get_schema_id to resolve full type IDs).
GENERIC_WORKFILE_TYPE = "type.workfile.generic"
FILE_SEQ_COMP = "File Sequence"
FILE_SEQ_TYPE = "type.fileSequence"

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


class CreateMode(Enum):
    """Determines which initial source file to use when creating an asset."""

    CURRENT = "CURRENT"  #: Use the currently open scene.
    NEW = "NEW"  #: Start from an empty scene.
    TEMPLATE = "TEMPLATE"  #: Copy from a template file.
    GENERIC = "GENERIC"  #: Copy source file(s) directly (no DCC scene).


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
            return get_schema_id("type.derivative.abc")
        return ""  # type: ignore[unreachable]
