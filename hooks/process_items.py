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

HookBaseClass = sgtk.get_hook_baseclass()

class ProcessItems(HookBaseClass):
    """
    This hook defines methods that operates on top-level publish items during
    the publishing process.
    """

    def prepare(self, items):
        """
        This method is called after all items to be published have been
        validated, just before the publishing begins. This method will not run
        if validation fails.

        This method can be used to do any type of pre-publish preparation
        required once it is known that all items have been validated. This may
        include custom data base, filesystem, or cache prep.

        A list of the top-level items is supplied. Items can be traversed via
        the `children` property.

        :param items: All enabled, top-level publish items.
        """
        pass


    def cleanup(self, items):
        """
        This method is called after all items have been published and finalized.
        This method will run even if the publish or finalize phases fail.

        This method can be used to do any type of post-publish cleanup
        required once all items have been through the publish and finalize
        phases. This may include custom data base, filesystem, or cache cleanup.

        A list of the top-level items is supplied. Items can be traversed via
        the `children` property.

        The suggested workflow is to populate the `item.properties` dictionary
        in the publish plugins' `publish()` and `validate()` methods. In this
        method you can analyze the state of the supplied items to determine
        if the expected properties are populated and act accordingly.

        :param items: All enabled, top-level publish items.
        """
        pass
