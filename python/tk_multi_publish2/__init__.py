# Copyright (c) 2017 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk

from .api import PublishManager  # noqa
from . import base_hooks  # noqa
from . import flowam  # noqa
from . import publish_tree_widget  # noqa
from .utils import publish as util  # noqa


def show_dialog(  # pragma: no cover
    app,
    single_file_mode=False,
    context=None,
    root_item_properties=None,
):
    """
    Show the main dialog ui

    :param app: The parent App
    :param context: Optional sgtk.Context for this dialog. When it matches
        the engine context, it is snapshotted onto the root item to isolate
        the dialog from concurrent engine.change_context() calls. When it
        differs (e.g. Loader passing a Task context into a project-level
        engine), it is applied as a pre-fill suggestion after collection and
        remains editable by the user.
    :param root_item_properties: Optional dict of properties to pre-seed on
        the root publish item before collection runs (e.g.
        ``{"am_revision_id": "123"}``).
    :param single_file_mode: If True, restrict publisher to accepting only a single file.
    """
    # defer imports so that the app works gracefully in batch modes
    from .dialog import AppDialog

    display_name = sgtk.platform.current_bundle().get_setting("display_name")

    if app.pre_publish_hook.validate():
        # pass context and root_item_properties as kwargs so they reach
        # AppDialog.__init__ without colliding with the parent QWidget arg
        # that the engine manages separately via _get_dialog_parent()
        if app.modal:
            app.engine.show_modal(
                display_name,
                app,
                AppDialog,
                context=context,
                root_item_properties=root_item_properties,
                single_file_mode=single_file_mode,
            )
        else:
            app.engine.show_dialog(
                display_name,
                app,
                AppDialog,
                context=context,
                root_item_properties=root_item_properties,
                single_file_mode=single_file_mode,
            )
    else:
        app.logger.debug(
            "%s validate returned False -- abort publish."
            % app.pre_publish_hook.__class__.__name__
        )
