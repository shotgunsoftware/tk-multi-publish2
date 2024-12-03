# Copyright (c) 2019 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import os
import datetime

import sgtk

HookBaseClass = sgtk.get_hook_baseclass()


class GenericLocalPlugin(HookBaseClass):
    """
    This should process the item locally...
    """

    @property
    def name(self):
        return "Publish Plugin with extra fields"

    @property
    def description(self):
        return "This plugin should add/modify 'created_at', 'comment' and 'sg_field_test' fields \
            to the Published File.  Note that the 'sg_field_test' field must exist, or this will \
            generate an error."

    @property
    def settings(self):
        return super().settings

    @property
    def item_filters(self):
        return ["generic.item"]

    def accept(self, settings, item):
        item.local_properties.publish_kwargs = {
            "created_at": datetime.datetime.now() - datetime.timedelta(days=(3 * 365)),
            "comment": "A different description",
        }
        item.local_properties.publish_fields = {"sg_field_test": "some value"}
        item.local_properties.plugin_name = "extra_fields"
        item.properties.path = __file__
        return {"accepted": True}

    def validate(self, settings, item):
        if "TEST_LOCAL_PROPERTIES" in os.environ:
            # local properties was properly set, so make sure it raises an error.
            # see test_item:test_local_properties_persistance for more info.
            if item.local_properties.plugin_name == "extra_fields":
                raise Exception("local_properties was serialized properly.")
        self.logger.debug("Executing extra_fields plugin validate.")
        return super().validate(settings, item)

    def publish(self, settings, item):
        self.logger.debug("Executing extra_fields plugin publish.")
        super().publish(settings, item)
        # Mockgun doesn't properly set the link_type field, so we'll do it ourselves
        # so later calls to resolve_publish_path do not fail.
        item.properties.sg_publish_data["path"]["link_type"] = "web"

    def finalize(self, settings, item):
        self.logger.debug("Executing extra_fields plugin finalize.")
        super().finalize(settings, item)
