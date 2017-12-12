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

    def post_finalize(self, items):
        """
        This method is called after all items have been finalized.

        The method will run even if the finalize phase fails. The method will
        not run if the publish is manually stopped via the UI's cancel button.

        A list of the top-level items is supplied. Items can be traversed via
        the `children` property.

        :param list items: All enabled, top-level publish items.

        This hook might implement logic like this::

            # iterate over all top-level items
            for item in items:

                # check the state of the items...
                # setting information in the item properties during the
                # publish phase method of publish plugins is a common
                # pattern and can be used to introspect the state of the
                # items in this method.
                if item.properties.get("errors"):
                    # process the items that had trouble during publish
                    ...

        NOTE: The items passed in are the top-level items only. To access the
        children of an item, use `item.children`.
        """
        pass
