# Copyright (c) 2018 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import os

from publish_api_test_base import PublishApiTestBase
from tank_test.tank_test_base import setUpModule # noqa

import sgtk

# When this file is being loaded by the the unit test framework, there is no hook base
# class, so we'll skip the hook declaration in that case.
# When we call create_hook_instance during the test however, this file will be parsed
# again and this time get_hook_baseclass will return something.
try:
    base_class = sgtk.get_hook_baseclass()
except:
    pass
else:
    class TestHook(base_class):

        def test_get_user_settings(self, test, settings, item):

            # Make sure get_publish_user returns nothing by default.
            test.assertIsNone(self.get_publish_user({}, item))

            # If the publish_user is set, get_publish_user should return it.
            user_in_property = {"type": "HumanUser", "id": 1}
            item.properties.publish_user = user_in_property
            test.assertEqual(self.get_publish_user({}, item), user_in_property)

            # If the publish_user local property is set, get_publish_user should return that
            # instead of the global property.
            user_in_local_property = {"type": "HumanUser", "id": 2}
            item.local_properties.publish_user = user_in_local_property
            test.assertEqual(self.get_publish_user({}, item), user_in_local_property)


class TestBasicPublishPlugin(PublishApiTestBase):

    def test_get_user_settings(self):
        """
        Ensures get_user_settings reads publish_user from the properties.
        """
        hook_instance = self.engine.create_hook_instance(
            os.path.pathsep.join([
                os.path.join(os.environ["REPO_ROOT"], "hooks", "publish_file"),
                os.path.splitext(__file__)[0]
            ]),
            base_class=self.app.base_hooks.PublishPlugin
        )
        hook_instance.id = __file__

        hook_instance.test_get_user_settings(self, {}, self.PublishItem("user", "user", "user"))
