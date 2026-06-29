# Copyright 2026 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.

import sgtk

logger = sgtk.platform.get_logger(__name__)

try:
    from . import constants  # noqa: F401 — exposes full constants module
    from .exceptions import (  # noqa: F401
        GenerateDerivativeError,
        IllegalDependencyError,
        PublishCanceledException,
    )
    from .inputs import (  # noqa: F401
        CreateDerivativeInputs,
        CreateGenericInputs,
        GenericPublishInputs,
        PublishInputs,
    )
    from .publish import (  # noqa: F401
        generate_derivative,
        publish_dcc_draft,
        publish_generic_revision,
        publish_new_generic_workfile,
        PublishInfo,
    )
    from .validate import has_asset_conflict, validate_generic_asset  # noqa: F401
except ImportError as _e:
    logger.debug(
        "tk-multi-publish2: Flow AM features are unavailable because the current "
        "version of tk-core does not include the Flow Integration SDK "
        "('tank_vendor.flow_integration_sdk' / 'tank.flowam'). "
        "This is safe to ignore if you are not working on a Flow AM project. "
        "Upgrade tk-core to enable Flow AM publishing. (ImportError: %s)",
        _e,
    )
