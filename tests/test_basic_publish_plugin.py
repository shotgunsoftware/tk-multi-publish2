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
from unittest import mock

from publish_api_test_base import PublishApiTestBase
from tank_test.tank_test_base import setUpModule  # noqa

import sgtk

# When this file is being loaded by the the unit test framework, there is no hook base
# class, so we'll skip the hook declaration in that case.
# When we call create_hook_instance during the test however, this file will be parsed
# again and this time get_hook_baseclass will return something.
try:
    base_class = sgtk.get_hook_baseclass()
except Exception:
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
    def _create_hook(self):
        # Use a relative path for the repo root, since __resolve_hook_expression splits on `:`,
        # and this will break on Windows where absolute paths include `:`
        # We'll be coming from the fixtures' hooks dir, `REPO_ROOT/tests/fixtures/config/hooks`,
        # so we'll need to go up 4 levels.
        rel_repo_root = os.path.join(*("..",) * 4)
        hook_instance = self.engine.create_hook_instance(
            ":".join(
                [
                    os.path.join(rel_repo_root, "hooks", "publish_file"),
                    os.path.join(
                        rel_repo_root,
                        "tests",
                        os.path.splitext(os.path.basename(__file__))[0],
                    ),
                ]
            ),
            base_class=self.app.base_hooks.PublishPlugin,
        )
        hook_instance.id = __file__
        return hook_instance

    def test_get_user_settings(self):
        """
        Ensures get_user_settings reads publish_user from the properties.
        """
        hook_instance = self._create_hook()
        hook_instance.test_get_user_settings(
            self, {}, self.PublishItem("user", "user", "user")
        )

    def test_publish(self):
        """
        Ensure that the publish method passes the correct kwargs to
        register_publish.
        """
        # test hook instance
        hook_instance = self._create_hook()
        # mock parent object
        parent = mock.MagicMock()
        parent.sgtk = sgtk
        # mock publish item with specific data we expect to see
        global_props_dict = {
            "publish_type": "publish_type value",
            "publish_name": "publish_name value",
            "publish_version": "publish_version value",
            "publish_path": "publish_path value",
            "publish_dependencies": "publish_dependencies value",
            "publish_user": "publish_user value",
            "publish_fields": {"publish_fields key": "publish_fields value"},
            "publish_kwargs": {"publish_kwargs_key": "publish_kwargs value"},
        }
        item_dict = {
            "description": "description value",
            "thumbnail_path": "thumbnail_path value",
        }
        parent = self.PublishItem("blah", "blah", "blah")
        parent.properties.sg_publish_data = {"type": "PublishedFile", "id": 32}
        publish_item = self.PublishItem("baz", "baz", "baz")
        publish_item._parent = parent
        publish_item._global_properties = self.PublishData.from_dict(global_props_dict)
        publish_item._description = item_dict["description"]
        publish_item._thumbnail_path = item_dict["thumbnail_path"]

        # ensure that register_publish is called with the expected data
        with mock.patch("sgtk.util.register_publish") as register_publish_mock:
            hook_instance.publish({}, publish_item)
            expected_kwargs = {
                "tk": hook_instance.parent.sgtk,
                "context": parent.context,
                "comment": item_dict["description"],
                "path": global_props_dict["publish_path"],
                "name": global_props_dict["publish_name"],
                "created_by": global_props_dict["publish_user"],
                "version_number": global_props_dict["publish_version"],
                "thumbnail_path": item_dict["thumbnail_path"],
                "published_file_type": global_props_dict["publish_type"],
                "dependency_paths": global_props_dict["publish_dependencies"],
                "dependency_ids": [32],
                "sg_fields": global_props_dict["publish_fields"],
            }
            expected_kwargs.update(global_props_dict["publish_kwargs"])
            register_publish_mock.assert_called_once_with(**expected_kwargs)
