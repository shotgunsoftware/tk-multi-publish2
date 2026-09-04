# Copyright 2026 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.

from __future__ import annotations  # needed for Houdini support

import mimetypes
import os
import shutil
import tempfile
import fileseq
from dataclasses import asdict, dataclass

import sgtk

from tank_vendor.flow_data_sdk.base import model as medm_model
from tank_vendor.flow_integration_sdk import (
    dependency,
    globals,
    publish,
    sandbox,
    schema,
    storage,
    utils,
)
from tank_vendor.flow_integration_sdk.exceptions import (
    CreateAssetError,
    FlowError,
    PublishAssetError,
    PublishConflictError,
)
from tank_vendor.flow_integration_sdk.objects import (
    FlowAsset,
    FlowProject,
    FlowRevision,
    FlowVersion,
)
from tank.flowam import create, open, utils as flowam_utils

from .constants import DerivativeType, REP_VARIANT_SET
from .exceptions import GenerateDerivativeError, IllegalDependencyError
from .inputs import (
    CreateDerivativeInputs,
    CreateGenericInputs,
    GenericPublishInputs,
    PublishInputs,
)


@dataclass
class PublishInfo:
    """Container for info about a recently published revision."""

    #: Name of asset that was published.
    asset_name: str
    #: Id of revision that was published.
    revision_id: str
    #: Version of revision that was published.
    version: int
    #: Updated draft id of asset in sandbox.
    #: Not applicable if asset is not in sandbox.
    draft_id: str | None = None


# =============================================================================
# DCC Publish
# =============================================================================


@utils.trace
def publish_dcc_draft(inputs: PublishInputs) -> PublishInfo | None:
    """Publish a draft revision of a new asset or existing asset from current DCC scene.
    See documentation for PublishInputs for expected inputs.

    .. note:: Inputs can be passed in as a PublishInputs object assigned to the keyword
              argument _inputs_ or as a set of individual parameters. (e.g. am_draft_id=<draft id>)

    Returns:
        A PublishInfo object containing information about the asset/revision
        that was published, or None if publish is aborted due to publish conflict.

    Raises:
        PublishAssetError
    """
    inputs.log_intro("Publishing DCC draft")
    inputs.validate()
    logger = utils.get_logger(__name__)

    engine = sgtk.platform.current_engine()
    host = engine.flow_host
    draft_id = inputs.am_draft_id
    thumbnail_path = inputs.thumbnail_path

    # Make sure we're in a DCC context
    if engine.name == "tk-desktop":
        msg = "Cannot publish DCC workfile outside of DCC FlowContext."
        raise PublishAssetError(data=inputs.asdict(), details=msg)

    # Make sure draft can be found locally and has valid source path
    draft_info = sandbox.read_draft_info(draft_id)
    draft_path = draft_info.source_path
    if not os.path.exists(draft_path):
        msg = f'Draft "{draft_id}" has an invalid source path: {draft_path}'
        raise PublishAssetError(data=inputs.asdict(), details=msg)

    # Make sure draft is currently open in dcc
    if engine.context.flow_draft_id != draft_id:
        name = draft_info.name
        msg = f'Draft of asset "{name}" is not currently open in DCC.'
        raise PublishAssetError(data=inputs.asdict(), details=msg)

    # Warn of stale checkout (applicable only if asset is not new)
    # (Users can choose to check out a version that is not the latest
    # and then publish it. At publish time, warn them if this is the case
    # to make sure it is fully intended.)
    is_new_asset = sandbox.is_new_asset(draft_id)
    if not is_new_asset:
        if not _outdated_checkout_warning(host, draft_info):
            return None  # User chose to cancel

    # Ensure thumbnail path is valid
    if thumbnail_path and not os.path.exists(thumbnail_path):
        msg = f"Thumbnail path provided does not exist: {thumbnail_path}"
        raise PublishAssetError(data=inputs.asdict(), details=msg)

    # Save current scene to draft path
    int_deps = _save_scene(host, draft_path, draft_id)

    # Generate components — sandbox (publish_draft) handles comment and
    # type components internally, so only source + thumbnail needed here
    components = flowam_utils.create_components_for_publish(
        source_paths=[draft_path],
        thumbnail_path=thumbnail_path,
        deps=int_deps,
    )

    # Get unique list of versions "used" by current asset - i.e. version ids
    # of all internal dependencies found
    used_versions = list(set([dep.version_id for dep in int_deps]))

    # Ensure draft name is unique under its parent
    if is_new_asset:
        parent_id = draft_info.parent_id
        if FlowAsset.is_asset_id(parent_id):
            draft_parent = FlowAsset(parent_id)
        else:
            draft_parent = FlowProject(parent_id)
        draft_name = create.ensure_unique_name(draft_info.name, draft_parent)
        if draft_name != draft_info.name:
            draft_info.name = draft_name
            draft_info_path = sandbox.get_draft_info_file(draft_id)
            draft_info.write_file(draft_info_path)
    else:
        draft_parent = None

    # Do publish
    try:
        medm_asset = sandbox.publish_draft(
            draft_id=draft_id,
            comment=inputs.comment,
            components=components,
            used_versions=used_versions,
        )
    except PublishConflictError as exc:
        result = _handle_publish_conflict(host, draft_id, exc)
        if result is False:
            # Re-open the draft before exiting
            if engine.context.flow_draft_id != draft_id:
                open.open_draft(draft_id)
            # Abort the publish
            return None
        # Attempt publish again with force flag
        medm_asset = sandbox.publish_draft(
            draft_id=draft_id,
            comment=inputs.comment,
            components=components,
            used_versions=used_versions,
            force=True,
        )

    asset = FlowAsset(medm_asset)
    new_draft_id = sandbox.get_draft_id(asset.id)

    # If the source path has changed, we must open the new source file
    draft_info = sandbox.read_draft_info(new_draft_id)
    source_path = draft_info.source_path
    if source_path != host.current_file():
        logger.info(f"Opening new source file: {source_path}")
        host.open_file(source_path)

    # If this is a new asset, we must update the parent root asset
    # to add a variant set component with this dcc variant.
    # Add to default set which is "representation"
    # Name variant after current engine since we should be in a dcc
    if is_new_asset:
        # NOTE: draft parent should be defined in this case
        set_name = REP_VARIANT_SET
        variant_name = engine.name.rsplit("-", maxsplit=1)[-1]
        display_name = f"{set_name.capitalize()}-{variant_name.capitalize()}"
        logger.info(
            f'Appending "{display_name}" component to parent asset "{draft_parent.name}"...'
        )
        try:
            draft_parent = _add_variant_set_component(
                asset_id=draft_parent.id,
                set_name=set_name,
                variant_name=variant_name,
                target_asset_id=asset.id,
                display_name=display_name,
            )
        except PublishAssetError as exc:
            msg = f"Parent publish failed - variant set component could not be added. {exc}"
            raise PublishAssetError(data=inputs.asdict(), details=msg) from exc

    return PublishInfo(
        asset_name=asset.name,
        revision_id=asset.revision_id,
        version=asset.revision_number,
        draft_id=new_draft_id,
    )


# =============================================================================
# Generic Publish
# =============================================================================


@utils.trace
def publish_new_generic_workfile(inputs: CreateGenericInputs) -> PublishInfo:
    """Create a generic workfile asset on remote based on criteria provided in inputs.
    See documentation for CreateGenericInputs for expected inputs.

    .. note:: Inputs can be passed in as a CreateGenericInputs object assigned to the keyword
              argument _inputs_ or as a set of individual parameters. (e.g. am_project_id=<project id>)
    .. note:: Generic assets do not pass through sandbox!

    Returns:
        A PublishInfo object containing all pertinent information about
        new asset published.

    Raises:
        CreateAssetError
    """
    inputs.log_intro("Creating new generic workfile asset")
    inputs.validate()
    logger = utils.get_logger(__name__)

    if not inputs.parent_id:
        # Create any necessary hierarchy above current asset
        if inputs.sg_entity:
            parent = create.create_federated_hierarchy(inputs)
        else:
            parent = create.create_generic_hierarchy(inputs)
    else:
        # Use override parent
        parent = FlowAsset(inputs.parent_id)

    # Create the workfile asset in sandbox
    # NOTE: The revision_id property of this asset object should be accurate
    #       because we know it was just published.
    asset = _create_generic_workfile_asset(parent, inputs)

    logger.info("Creating generic asset complete!")

    # NOTE: For now continue to return revision info to caller.
    #       This allows toolkit side implementation to remain largely
    #       the same until we are ready to remove PublishedFile proxies.
    #       This is ok because we expect each revision to be a new version.
    return PublishInfo(
        asset_name=asset.name,
        revision_id=asset.revision_id,
        version=asset.revision_number,
    )


@utils.trace
def publish_generic_revision(inputs: GenericPublishInputs) -> PublishInfo:
    """Publish a new revision of an existing generic asset direct to remote.
    See documentation for PublishInputs for expected inputs.

    .. note:: Inputs can be passed in as a PublishInputs object assigned to the keyword
              argument _inputs_ or as a set of individual parameters. (e.g. am_draft_id=<draft id>)
    .. note:: Generic assets do not pass through sandbox!

    Returns:
        A PublishInfo object containing information about the asset/revision
        that was published.

    Raises:
        PublishAssetError
    """
    inputs.log_intro("Publishing generic revision")
    inputs.validate()

    # Ensure asset id is valid
    # If revision/version id was provided, convert to asset id
    asset_id = inputs.am_asset_id
    if FlowRevision.is_revision_id(asset_id) or FlowVersion.is_version_id(asset_id):
        asset_id = FlowAsset.get_asset_id(asset_id)
    try:
        asset = FlowAsset(asset_id)
    except FlowError as exc:
        msg = f"Invalid asset id provided: {asset_id}"
        raise PublishAssetError(data=inputs.asdict(), details=msg) from exc

    # Ensure asset is of generic workfile type
    is_generic_asset, msg = validate_generic_asset(asset_id)
    if not is_generic_asset:
        raise PublishAssetError(data=inputs.asdict(), details=msg)

    # Ensure source path is valid
    # Ensure source path(s) is/are valid
    if isinstance(inputs.source_path, list):
        source_paths = inputs.source_path
    else:
        source_paths = [inputs.source_path]
    for source_path in source_paths:
        if not os.path.exists(source_path):
            msg = f"Source path does not exist: {source_path}"
            raise PublishAssetError(data=inputs.asdict(), details=msg)

    # Ensure thumbnail path is valid
    thumbnail_path = inputs.thumbnail_path
    if thumbnail_path and not os.path.exists(thumbnail_path):
        msg = f"Thumbnail path provided does not exist: {thumbnail_path}"
        raise PublishAssetError(data=inputs.asdict(), details=msg)

    # If no valid thumbnail path is provided, and source path is an image type,
    # use that as the thumbnail
    if not thumbnail_path:
        ext = os.path.splitext(source_paths[0])[1].lstrip(".")
        if (mimetypes.guess_type(f"file.{ext}")[0] or "").startswith("image"):
            thumbnail_path = source_paths[0]

    # Generate components — publish_new_revision preserves type ids internally,
    # only pass comment
    components = flowam_utils.create_components_for_publish(
        source_paths,
        thumbnail_path,
        comment=inputs.comment,
        type_ids=asset.type_ids,
    )
    # If a FOR_PIPELINE_STEP_TYPE component exists on the asset
    # we must carry it over to maintain its SG context
    orig_pipestep_comp = asset.find_component(
        type_id=schema.get_schema_id(globals.FOR_PIPELINE_STEP_TYPE)
    )
    if orig_pipestep_comp:
        deliverable_id = orig_pipestep_comp.properties["targetDeliverable"]
        pipeline_step_id = orig_pipestep_comp.properties["targetStep"]
        components.append(
            publish.ForPipelineStepComponentSpec(
                deliverable_id=deliverable_id,
                pipeline_step_id=pipeline_step_id,
            )
        )

    # Do publish
    medm_asset = publish.publish_new_revision(
        asset_id=asset.id,
        components=components,
    )
    asset = FlowAsset(medm_asset)
    return PublishInfo(
        asset_name=asset.name,
        revision_id=asset.revision_id,
        version=asset.revision_number,
    )


@utils.trace
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


# =============================================================================
# Derivative Publish
# =============================================================================


@utils.trace
def generate_derivative(inputs: CreateDerivativeInputs) -> PublishInfo:
    """Publish a derivative asset that is associated with the provided source revision.
    Create the derivative asset if one does not already exist.
    See documentation for CreateDerivativeInputs for expected inputs.

    .. note:: Inputs can be passed in as a CreateDerivativeInputs object assigned to the keyword
              argument _inputs_ or as a set of individual parameters. (e.g. description="My derivative asset.")

    Returns:
        A PublishInfo object containing information about the asset/revision that was published.

    Raises:
        GenerateDerivativeError
    """
    inputs.log_intro("Generating a derivative asset")
    inputs.validate()
    logger = utils.get_logger(__name__)

    engine = sgtk.platform.current_engine()
    host = engine.flow_host
    if engine.name == "tk-desktop":
        msg = "Cannot generate derivative without being in DCC FlowContext."
        raise GenerateDerivativeError(data=inputs.asdict(), details=msg)

    try:
        src_rev = FlowRevision.get_revision(inputs.source_revision_id)
        src_asset = FlowAsset(src_rev.asset_id)
    except FlowError as exc:
        msg = f"Invalid source revision id provided: {inputs.source_revision_id}"
        raise GenerateDerivativeError(data=inputs.asdict(), details=msg) from exc

    # Ensure thumbnail path is valid
    thumbnail_path = inputs.thumbnail_path
    if thumbnail_path and not os.path.exists(thumbnail_path):
        msg = f"Thumbnail path provided does not exist: {thumbnail_path}"
        raise GenerateDerivativeError(data=asdict(inputs), details=msg)

    der_type = inputs.derivative_type
    der_name = _get_derivative_name(src_rev, der_type)
    der_ext = der_type.file_type()
    der_type_id = der_type.type_id()

    # Export derivative file to temp location
    with tempfile.TemporaryDirectory() as temp_dir:
        der_file = utils.cleanpath(temp_dir, f"{der_name}.{der_ext}")
        logger.info(f"Exporting derivative file to: {der_file}")
        try:
            host.export(der_file)
        except Exception as exc:  # pylint: disable=broad-except
            msg = f"Failed to export derivative file to: {der_file}"
            raise GenerateDerivativeError(data=inputs.asdict(), details=msg) from exc

        # Check for existing derivative asset
        der_asset = src_asset.find_derivative(der_type_id)

        # Generate components
        components = flowam_utils.create_components_for_publish(
            [der_file],
            thumbnail_path,
            type_ids=der_asset.type_ids if der_asset else [der_type_id],
        )

        # Add derivative component to point back to source revision
        components.append(publish.DerivativeSourceComponentSpec(src_rev.version_id))

        if der_asset:
            logger.info(f"Existing derivative asset found: {der_asset.name}")
            logger.info("Publishing new version of derivative asset...")
            # Publish new revision of existing asset
            try:
                medm_asset = publish.publish_new_revision(
                    asset_id=der_asset.id,
                    components=components,
                )
            except PublishAssetError as exc:
                msg = f"Derivative publish failed. {exc}"
                raise GenerateDerivativeError(data=asdict(inputs), details=msg) from exc
            der_asset = FlowAsset(medm_asset)
        else:
            logger.info(f"Creating new derivative asset: {der_name}")
            # Create a brand new asset under same parent as source
            try:
                parent = src_asset.get_parent()
            except FlowError as exc:
                msg = f'Could not retrieve parent of source asset "{src_asset.name}".'
                raise GenerateDerivativeError(data=asdict(inputs), details=msg) from exc
            try:
                medm_asset = publish.publish_new_asset(
                    name=create.ensure_unique_name(der_name, parent),
                    parent_id=parent.id,
                    description=inputs.description,
                    components=components,
                )
            except CreateAssetError as exc:
                msg = f"Derivative asset creation failed. {exc}"
                raise GenerateDerivativeError(data=asdict(inputs), details=msg) from exc

            der_asset = FlowAsset(medm_asset)
            # Add new derivative asset to the "representation" variant set of parent asset
            set_name = REP_VARIANT_SET
            variant_name = der_type.name.lower()
            display_name = f"{set_name.capitalize()}-{variant_name.capitalize()}"
            logger.info(
                f'Appending "{display_name}" component to parent asset "{parent.name}"...'
            )
            try:
                parent = _add_variant_set_component(
                    asset_id=parent.id,
                    set_name=set_name,
                    variant_name=variant_name,
                    target_asset_id=der_asset.id,
                    display_name=display_name,
                )
            except PublishAssetError as exc:
                msg = f"Parent publish failed - variant set component could not be added. {exc}"
                raise GenerateDerivativeError(data=asdict(inputs), details=msg) from exc

        # NOTE: For now continue to return revision info to caller.
        #       This allows toolkit side implementation to remain largely
        #       the same until we are ready to remove PublishedFile proxies.
        #       This is ok because we expect each revision to be a new version.
        publish_info = PublishInfo(
            asset_name=der_asset.name,
            revision_id=der_asset.revision_id,
            version=der_asset.revision_number,
        )

    logger.info(f'Publish of derivative asset "{der_name}" complete!')
    msg = f'Derivative revision "{der_name}" (r{publish_info.version}) '
    msg += f'points to source version "{src_rev.name}" (r{src_rev.version_number}).'
    logger.info(msg)

    return publish_info


# =============================================================================
# Private Helpers
# =============================================================================


@utils.trace
def _create_generic_workfile_asset(
    parent: FlowAsset, inputs: CreateGenericInputs
) -> FlowAsset:
    """Called when creating a new generic workfile asset.
    This function will create the workfile asset in sandbox under the given parent.

    Args:
        parent: Asset to create workfile asset under.
        See CreateInputs documentation.

    Returns:
        Asset created.

    Raises:
        CreateAssetError
    """
    logger = utils.get_logger(__name__)

    # Determine workfile type to be created
    workfile_type = create.GENERIC_WORKFILE_TYPE
    type_id = schema.get_schema_id(workfile_type)

    # Ensure source path(s) is/are valid
    if isinstance(inputs.source_path, list):
        source_paths = inputs.source_path
    else:
        source_paths = [inputs.source_path]
    for source_path in source_paths:
        if not os.path.exists(source_path):
            msg = f"Source path does not exist: {source_path}"
            raise CreateAssetError(data=inputs.asdict(), details=msg)

    # Use the name of the source file for generic assets
    name = _get_generic_name(source_paths)

    # Ensure thumbnail path is valid
    thumbnail_path = inputs.thumbnail_path
    if thumbnail_path and not os.path.exists(thumbnail_path):
        msg = f"Thumbnail path provided does not exist: {thumbnail_path}"
        raise CreateAssetError(data=inputs.asdict(), details=msg)

    # If no thumbnail path is provided, and source path is an image type,
    # use that as the thumbnail (for file sequences, use the first file)
    if not thumbnail_path:
        ext = os.path.splitext(source_paths[0])[1].lstrip(".")
        if (mimetypes.guess_type(f"file.{ext}")[0] or "").startswith("image"):
            thumbnail_path = source_paths[0]

    # Generate components
    components = flowam_utils.create_components_for_publish(
        source_paths,
        thumbnail_path,
        comment=inputs.comment,
        type_ids=[type_id],
    )
    # If we're given an sg context, add a component to designate that
    if inputs.sg_entity and inputs.sg_pipeline_step:
        project_id = inputs.am_project_id
        sg_entity = inputs.sg_entity
        sg_pipeline_step = inputs.sg_pipeline_step
        deliverable = create._find_deliverable(project_id, sg_entity)
        pipeline_step = create._find_pipeline_step(project_id, sg_pipeline_step)
        if not deliverable or not pipeline_step:
            msg = "MEDM proxies for sg context could not be found."
            raise CreateAssetError(data=inputs.asdict(), details=msg)
        components.append(
            publish.ForPipelineStepComponentSpec(
                pipeline_step_id=pipeline_step.id,
                deliverable_id=deliverable.id,
            )
        )

    # Create a new asset on remote
    logger.info(
        f'Creating a workfile asset of type "{workfile_type}" under parent "{parent.name}" in sandbox...'
    )
    medm_asset = publish.publish_new_asset(
        name=create.ensure_unique_name(name, parent),
        parent_id=parent.id,
        description=inputs.description,
        components=components,
    )
    asset = FlowAsset(medm_asset)
    return asset


def _get_generic_name(source_paths: list[str]) -> str:
    """Return name for generic asset based on source file name."""
    # NOTE: we can assume there is at least one source path
    if len(source_paths) > 1:
        # For file sequences, we will determine the basename via api
        seqs = fileseq.findSequencesInList(source_paths)
        # Based on fileseq api, we are guaranteed at least one
        # sequence object here if the input list is not empty
        return seqs[0].basename().rstrip(".")
    else:
        # For single files, we will just use the file's base name
        return os.path.splitext(os.path.basename(source_paths[0]))[0]


@utils.trace
def _save_scene(
    host, draft_path: str, draft_id: str
) -> list[dependency.DependencyData]:
    """Save current scene to given location while handling
    dependencies properly.

    Returns list of top-level asset dependencies found in scene.

    Raises:
        IllegalDependencyError
        PublishAssetError
    """
    # Retrieve all the dependencies within the scene
    dep_tree = host.get_dependency_tree()

    # Local (external) dependencies aren't supported for now
    ext_deps = dep_tree.get_external_dependencies()
    if len(ext_deps) > 0:
        dep_paths = [e.file_path for e in ext_deps]
        msg = "Non-asset dependencies are not supported currently."
        msg += " Please convert the following dependencies into assets before proceeding.\n"
        msg += "\n".join(dep_paths)
        raise IllegalDependencyError(dep_paths=dep_paths, details=msg)

    # Convert all asset dependencies to be storage root agnostic
    # Also check for self references! (Not applicable for new assets)
    if sandbox.is_new_asset(draft_id):
        current_asset_id = None
    else:
        try:
            current_asset_id = storage.storage_key_to_asset_id(draft_id)
        except FlowError:
            # This shouldn't happen, but it's such an edge case that
            # we won't worry about self references here
            current_asset_id = None

    int_deps = dep_tree.get_internal_dependencies()
    for dep in int_deps:
        if dep.asset_id == current_asset_id:
            msg = f"Self reference found: {dep.file_path}"
            raise IllegalDependencyError(dep_paths=[dep.file_path], details=msg)

        remote_path = dep.file_path.replace(
            storage.get_storage_root(),
            host.env_var_marker(storage.FLOW_STORAGE_ROOT),
        )
        if dep.raw_path != remote_path:
            host.update_dependency(dep, remote_path)

    # Save current scene to draft path
    try:
        host.save_file(draft_path)
    except Exception as exc:  # pylint: disable=broad-except
        msg = f"Could not save current scene to draft path: {draft_path}"
        raise PublishAssetError(data={"draft_path": draft_path}, details=msg) from exc

    return int_deps


@utils.trace
def _handle_publish_conflict(host, draft_id: str, exc: PublishConflictError) -> bool:
    """Give user options on how to handle a publish conflict
    that has been detected.

    1. Cancel -> exit publish process
    2. Stash changes and update -> copy current draft folder to a back up location
                                   and create new draft of latest revision
    3. Force publish -> publish a new revision with existing draft
    4. Discard and update -> discard local draft and checkout latest revision
                          -> publish is abandoned


    Returns:
        True to continue publish, and False to abort publish.
    """
    logger = utils.get_logger(__name__)

    asset = FlowAsset(exc.asset)
    options = [
        "Cancel",  # 0
        "Stash changes and update",  # 1
        "Force publish",  # 2
        "Discard and update",  # 3
    ]

    msg = str(exc) + "\n\n How would you like to proceed?"
    action = host.dialog(
        title="Publish conflict detected",
        msg=msg,
        buttons=options,
        cancel=0,
        default=0,  # cancel by default
    )

    if action == 0:
        # Cancel the publish
        logger.warning("Publish operation cancelled.")
        return False
    elif action == 1:
        # Stash changes and update
        if _stash_draft(host, draft_id):
            latest_rev = asset.get_latest_revision()
            logger.info(f"Checking out revision {latest_rev.revision_number}...")
            open.checkout_revision(latest_rev.id, force=True)
        return False
    elif action == 2:
        # Force publish
        logger.warning("Forcing publish...")
        return True
    elif action == 3:
        # Discard and update
        # Provide confirmation dialog
        msg = f'Discard existing draft for asset "{asset.name}"?'
        msg += "\nAny work done on the draft will be lost and unrecoverable."
        result = host.dialog(
            title="Discard changes?",
            msg=msg,
            buttons=["Discard", "Cancel"],
            cancel=1,
            default=1,
        )
        if result == 0:
            # Close current file before checking out new revision
            host.new_scene(force=True)
            latest_rev = asset.get_latest_revision()
            msg = f"Discarding current draft and checking out revision {latest_rev.revision_number}..."
            logger.info(msg)
            open.checkout_revision(latest_rev.id, force=True)
        elif result == 1:
            logger.warning("Publish operation cancelled.")
        else:
            msg = "Invalid option received for discard confirmation: {result}"
            raise RuntimeError(msg)
        return False
    else:
        msg = "Invalid option received for publish conflict resolution: {action}"
        raise RuntimeError(msg)


@utils.trace
def _stash_draft(host, draft_id: str) -> bool:
    """Allow user to stash their current draft to a selected location.

    Returns:
        False if operation is cancelled.
    """
    logger = utils.get_logger(__name__)

    # Trigger confirmation dialog
    msg = "Choosing to stash your current draft will copy your draft folder "
    msg += "to a selected location. Then the latest revision will be checked "
    msg += "out into your sandbox.\n\n Would you like to proceed?"
    result = host.dialog(
        title="Stash current draft?",
        msg=msg,
        buttons=["Yes", "Cancel"],
        cancel=1,
        default=1,
    )
    if result == 1:
        logger.warning("Publish operation cancelled.")
        return False

    # Stash location selection
    selected_paths = host.file_dialog(
        title="Select stash location",
        folder_mode=True,  # select directory
    )
    if not selected_paths:
        # User cancelled
        logger.warning("Publish operation cancelled.")
        return False

    # Clear scene before attempting move
    host.new_scene(force=True)

    # We will move the parent directory of the draft folder which includes the
    # draft id for easier tracking
    stash_dir = selected_paths[0]
    draft_dir = os.path.dirname(sandbox.get_draft_folder(draft_id))
    new_draft_loc = utils.cleanpath(stash_dir, draft_id)
    logger.info(f"Stashing draft in: {new_draft_loc}")
    if os.path.exists(new_draft_loc):
        msg = f'A draft folder for id "{draft_id}" already exists in:\n'
        msg += f"     {stash_dir}\nHow would you like to proceed?"
        result = host.dialog(
            title="Move failed",
            msg=msg,
            buttons=["Overwrite existing stash", "Cancel"],
            cancel=1,
            default=1,
        )
        if result == 1:
            logger.warning("Publish operation cancelled.")
            return False
        shutil.rmtree(new_draft_loc)
    shutil.move(draft_dir, stash_dir)

    # Open file explorer to stash as a courtesy
    flowam_utils.open_explorer(new_draft_loc)

    return True


@utils.trace
def _outdated_checkout_warning(host, draft_info: sandbox.CheckoutDraftInfo) -> bool:
    """If the user, at the time of checkout, had checked out a version
    that was not the latest, give a warning and verify whether to
    proceed with publish.

    NOTE: There is a distinction between this check for a "stale checkout"
          and a publish conflict. The publish conflict arises any time new
          versions have been published since the asset was checked out.
          In the above case, the user may very well have checked out the latest
          version at the time of checkout.

          Meanwhile this check catches the scenario where the user had checked out
          something old to begin with. Therefore, this is simply a courtesy warning
          to inform the user that this is the situation, and verify whether they really
          want to proceed.

    NOTE: We are able to ignore changes in revisions within a single version here
          because we are operating under the assumption that within a version,
          the components and uses relationship of the asset should not change.
          Since our publishes only update these properties of an asset, we do
          not need to be concerned about overwriting any metadata changes that
          may have taken place across revisions of the same version.

    Returns:
        False to cancel the publish operation.
    """
    checkout_version = draft_info.version
    latest_version = draft_info.latest_version
    checkout_revision = draft_info.revision
    latest_revision = draft_info.latest_revision
    if checkout_version < latest_version:
        msg = f"The version {checkout_version} (r{checkout_revision}) checked out "
        msg += "in this draft was not the latest at the time of checkout "
        msg += f"{latest_version} (r{latest_revision}).\n"
        msg += "Are you sure you want to publish from an outdated version?"
        result = host.dialog(
            title="Outdated Checkout",
            msg=msg,
            buttons=["Publish", "Cancel"],
            cancel=1,
            default=1,
        )
        if result == 1:
            return False  # User cancelled
    return True


def _get_derivative_name(revision: FlowRevision, dtype: DerivativeType) -> str:
    """Return conventional name for derivative asset.

    Args:
        revision: Source revision object.
        dtype: Derivative type.

    Returns:
        Name of derivative asset by convention.
    """
    return f"{revision.name} - {dtype.value}"


def _add_variant_set_component(
    asset_id: str,
    set_name: str,
    variant_name: str,
    target_asset_id: str,
    display_name: str = "",
) -> FlowAsset:
    """Create a variant set component and add it to the given asset via a remote publish.

    Args:
        asset_id: Id of asset to be updated.
        set_name: Name of set that the new variant belongs to.
        variant_name: Name of new variant.
        target_asset_id: Id of asset which is the variant.
        display_name: Optional display name for set/variant combo.

    Returns:
        Updated FlowAsset object.

    Raises:
        PublishAssetError
    """
    variant_set_comp = publish.VariantSetComponentSpec(
        set_name=set_name,
        variant_name=variant_name,
        display_name=display_name,
        asset_id=target_asset_id,
    )
    # NOTE: New component is being appended to asset.
    #       All other components will be carried over from previous revision.
    medm_asset = publish.publish_new_revision(
        asset_id=asset_id,
        components=[variant_set_comp],
        components_action=medm_model.ListAction.ADD,
    )
    return FlowAsset(medm_asset)
