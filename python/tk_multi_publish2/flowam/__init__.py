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
        validate_generic_asset,
    )
except ImportError as exc:
    logger.error(
        "tk-desktop: There was an error importing the 'flowam' module.\n"
        "This is likely due to Flow AM features being unavailable in the "
        "current version of tk-core - i.e. it is missing the Flow Integration SDK "
        "('tank_vendor.flow_integration_sdk' / 'tank.flowam').\n"
        "This is safe to ignore if you are not working on a Flow AM project. "
        f"Upgrade tk-core to enable Flow AM publishing.\n(ImportError: {exc})"
    )
