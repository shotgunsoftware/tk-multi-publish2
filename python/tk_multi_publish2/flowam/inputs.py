# Copyright 2026 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.

from __future__ import annotations  # needed for Houdini 19.5 support

from dataclasses import dataclass

from tank_vendor.flow_integration_sdk.exceptions import (
    CreateAssetError,
    PublishAssetError,
)
from tank.flowam import create, utils as flowam_utils

from .constants import (
    DerivativeType,
)  # noqa: F401 (re-exported for callers)


@dataclass
class CreateGenericInputs(flowam_utils.BaseInputs):
    """Inputs for creating a new generic workfile asset via the Desktop publish hook.

    Generic assets are files that are not tied to a specific DCC (e.g. reference
    images, documents, Alembic caches).  They can be published to two locations:

    - **Project level** - leave all ``sg_entity_*`` fields as ``None``.
      The asset lands under a flat ``GENERIC FOLDER`` at the project root.
    - **Entity level** (Shot, Asset, etc.) - populate ``sg_entity``,
      and ``sg_pipeline_step``.
      The asset lands under the matching entity -> pipeline step -> task
      hierarchy in AM.

    ``parent_id`` is an escape hatch: when provided, hierarchy resolution is
    skipped entirely and the asset is created directly under that AM parent.
    """

    #: The AM project under which the asset should be added.
    am_project_id: str = ""
    # Create mode determines the source of the initial asset file(s).
    create_mode: create.CreateMode = create.CreateMode.GENERIC
    #: Path(s) to the source file(s) to copy directly to the asset.
    source_path: str | list[str] = ""
    #: SG entity object (returned as a dict from SG API)
    #: Should minimally contain keys: type, name, id
    sg_entity: dict | None = None
    #: SG step object (returned as a dict from SG API)
    #: Should minimally contain keys: name, entity_type
    sg_pipeline_step: dict | None = None
    #: Description stored with the AM asset.
    description: str = ""
    #: Path to the thumbnail file stored with the AM asset.
    thumbnail_path: str = ""
    #: Comment stored with the new revision.
    comment: str = ""
    #: Optional parent asset id.  When provided, hierarchy creation is skipped.
    parent_id: str = ""

    def validate(self):
        """Check that inputs are valid.

        Raises:
            CreateAssetError
        """
        if not self.am_project_id:
            raise CreateAssetError(
                data=self.asdict(), details="No project id provided."
            )
        if not self.source_path:
            raise CreateAssetError(
                data=self.asdict(), details="No source path provided."
            )
        # Ensure sg_entity contains required keys and pipeline step is provided
        if self.sg_entity:
            msg = "Incomplete sg_entity dict provided. '%s' key is required."
            if "name" not in self.sg_entity:
                msg = msg % "name"
                raise CreateAssetError(data=self.asdict(), details=msg)
            elif "id" not in self.sg_entity:
                msg = msg % "id"
                raise CreateAssetError(data=self.asdict(), details=msg)
            elif "type" not in self.sg_entity:
                msg = msg % "type"
                raise CreateAssetError(data=self.asdict(), details=msg)

            if not self.sg_pipeline_step:
                msg = "Incomplete sg context provided. Must provide sg_pipeline_step."
                raise CreateAssetError(data=self.asdict(), details=msg)
        # Ensure sg_pipeline_step contains required keys and entity is provided
        if self.sg_pipeline_step:
            msg = "Incomplete sg_pipeline_step dict provided. '%s' key is required."
            if "name" not in self.sg_pipeline_step:
                msg = msg % "name"
                raise CreateAssetError(data=self.asdict(), details=msg)
            if "entity_type" not in self.sg_pipeline_step:
                msg = msg % "name"
                raise CreateAssetError(data=self.asdict(), details=msg)

            if not self.sg_entity:
                msg = "Incomplete sg context provided. Must provide sg_entity."
                raise CreateAssetError(data=self.asdict(), details=msg)


@dataclass
class CreateDerivativeInputs(flowam_utils.BaseInputs):
    """Inputs for the derivative generation step."""

    #: Id of the asset revision that the derivative will be attributed to.
    source_revision_id: str = ""
    #: Type of derivative to be created.  See :class:`~flowam.constants.DerivativeType`.
    derivative_type: DerivativeType | None = None
    #: Description of derivative asset.
    description: str = ""
    #: Optional thumbnail path.
    thumbnail_path: str = ""


@dataclass
class PublishInputs(flowam_utils.BaseInputs):
    """Inputs for a DCC draft publish."""

    #: Path to the thumbnail file stored with the AM asset.
    thumbnail_path: str = ""
    #: Comment stored with the new revision.
    comment: str = ""
    #: Unique draft id associated with the sandbox revision to be published.
    am_draft_id: str | None = None

    def validate(self):
        """Check that inputs are valid.

        Raises:
            PublishAssetError
        """
        if not self.am_draft_id:
            raise PublishAssetError(data=self.asdict(), details="No draft id provided.")


@dataclass
class GenericPublishInputs(PublishInputs):
    """Inputs for publishing an existing generic revision."""

    #: Asset or revision id of the generic asset to be published.  Mandatory.
    am_asset_id: str = ""
    #: File(s) to be published to a new revision.  Mandatory.
    source_path: str | list[str] = ""

    def validate(self):
        """Check that inputs are valid.

        Raises:
            PublishAssetError
        """
        if not self.am_asset_id:
            raise PublishAssetError(data=self.asdict(), details="No asset id provided.")
        if not self.source_path:
            raise PublishAssetError(
                data=self.asdict(), details="No source path provided."
            )
