# Copyright 2026 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.

from __future__ import annotations  # needed for Houdini 19.5 support

from tank_vendor.flow_integration_sdk import sandbox, schema
from tank_vendor.flow_integration_sdk.objects import FlowAsset
from tank_vendor.flow_integration_sdk.utils import trace
from tank.flowam import create


@trace
def has_asset_conflict(draft_id: str) -> tuple[bool, str]:
    """When publishing a new asset, check whether the parent already has a
    workfile of the same DCC type (only applies to new assets).

    Generic and template assets are exempt - multiple are allowed under the
    same parent.

    Args:
        draft_id: The draft id of the asset being published.

    Returns:
        Tuple of (conflict_found, reason_message).
    """
    if not sandbox.is_new_asset(draft_id):
        return False, ""

    draft_info = sandbox.read_draft_info(draft_id)
    type_ids = draft_info.type_ids

    generic_type_id = schema.get_schema_id(create.GENERIC_WORKFILE_TYPE)
    if generic_type_id in type_ids:
        return False, ""

    parent = FlowAsset(draft_info.parent_id)
    type_id = type_ids[0]
    if _has_workfile_type(parent, type_id):
        msg = f'A workfile of type "{type_id}" has already been created '
        msg += f'under pipeline step "{parent.name}". Please open the asset '
        msg += "from the Loader app to publish another revision of this asset."
        return True, msg

    return False, ""


@trace
def validate_generic_asset(asset_id: str) -> tuple[bool, str]:
    """Validate that the given asset id corresponds to a generic workfile asset.

    Args:
        asset_id: Asset id to be checked.

    Returns:
        Tuple of (valid, reason_message).
    """
    asset = FlowAsset(asset_id)
    if schema.get_schema_id(create.GENERIC_WORKFILE_TYPE) not in asset.type_ids:
        msg = f"Invalid asset type provided. Asset {asset.name} is not of generic workfile type."
        return False, msg
    return True, ""


@trace
def _has_workfile_type(parent: FlowAsset, type_id: str) -> bool:
    """Return True if parent asset contains a child of given type."""
    return bool(parent.find_children(type_id=type_id))
