# Copyright (c) 2018 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from publish_api_test_base import PublishApiTestBase
from tank_test.tank_test_base import setUpModule  # noqa

import logging
from unittest.mock import Mock, MagicMock, patch
from functools import wraps

# We're going to make sure the plugin logs the proper messages, since those
# are important as they as destined for the UI.
logger = logging.getLogger(__name__)


def mock_publish_plugin_instance_hook_creation(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        with patch.object(self.PublishPluginInstance, "_create_hook_instance") as mock:
            return func(self, mock, *args, **kwargs)

    return wrapper


# We're going to put a logging handler that listens for a particular string.
# When the string is detected during the emit, the found flag will be raised.
# It's very important to derive from object here, because Python 2.6's
# implementation of the handler class doesn't, which breaks property setters.
class Handler(logging.Handler, object):
    def __init__(self):
        logging.Handler.__init__(self)
        self.found = False
        self._keyword = None

    @property
    def keyword(self):
        return self._keyword

    @keyword.setter
    def keyword(self, keyword):
        self.found = False
        self._keyword = keyword

    def emit(self, record):
        if self.keyword:
            self.found |= self.keyword in record.msg


# Set up the testing logger.
handler = Handler()
logger.addHandler(handler)


class TestPublishPluginInstance(PublishApiTestBase):
    @mock_publish_plugin_instance_hook_creation
    def test_plugin_attributes(self, create_hook_instance):
        """
        Ensures hook attributes and their omission are handled property by the
        plugin instance object.
        """
        mock_plugin = MagicMock(
            name="test name",
            description="test description",
            item_filters=["item.filter"],
            create_settings_widget=lambda: None,
            get_ui_settings=lambda: None,
            set_ui_settings=lambda: None,
            icon=self.image_path,
        )
        create_hook_instance.return_value = mock_plugin

        ppi = self.PublishPluginInstance("test hook", None, {})

        self.assertEqual(ppi.plugin_name, mock_plugin.name)
        del mock_plugin.name
        self.assertEqual(ppi.plugin_name, "Untitled Integration.")

        self.assertEqual(ppi.description, mock_plugin.description)
        del mock_plugin.description
        self.assertEqual(ppi.description, "No detailed description provided.")

        self.assertEqual(ppi.item_filters, mock_plugin.item_filters)
        del mock_plugin.item_filters
        self.assertEqual(ppi.item_filters, [])

        self.assertTrue(ppi.has_custom_ui)
        del mock_plugin.create_settings_widget
        self.assertFalse(ppi.has_custom_ui)

        # Ensure the icon that was loaded by the plugin is the one specified
        # via the file path.
        self.assertEqual(ppi.icon.cacheKey(), self.image.cacheKey())
        # Clear the pixmap cache.
        ppi._icon_pixmap = None
        del mock_plugin.icon
        self.assertEqual(
            ppi.icon.cacheKey(),
            self.QtGui.QPixmap(":/tk_multi_publish2/task.png").cacheKey(),
        )

    @mock_publish_plugin_instance_hook_creation
    def test_accept_with_exception(self, create_hook_instance):
        """
        Ensure raised exceptions are caught.
        """
        create_hook_instance.return_value = MagicMock(
            accept=Mock(side_effect=Exception("Test error!"))
        )
        ppi = self.PublishPluginInstance("test hook", None, {}, logger)
        handler.keyword = "Error running accept for"
        self.assertEqual(ppi.run_accept(None), {"accepted": False})
        self.assertTrue(handler.found)

    @mock_publish_plugin_instance_hook_creation
    def test_accept_with_rejected_item(self, create_hook_instance):
        """
        Ensure rejected nodes are not accepted.
        """
        create_hook_instance.return_value = MagicMock(
            accept=Mock(return_value={"accepted": False})
        )
        ppi = self.PublishPluginInstance("test hook", None, {}, logger)

        handler.keyword = "Error running accept for"
        self.assertEqual(ppi.run_accept(None), {"accepted": False})
        self.assertFalse(handler.found)

    @mock_publish_plugin_instance_hook_creation
    def test_accept_with_accepted_item(self, create_hook_instance):
        """
        Ensure accepted nodes are accepted.
        """
        create_hook_instance.return_value = MagicMock(
            accept=Mock(return_value={"accepted": True})
        )
        ppi = self.PublishPluginInstance("test hook", None, {}, logger)

        handler.keyword = "Error running accept for"
        self.assertEqual(ppi.run_accept(None), {"accepted": True})
        self.assertFalse(handler.found)

    # The following four methods are mock methods for the three UI customization methods.
    # get_ui_settings
    # set_ui_settings
    # create_settings_widget
    # We're not using proper return values, as we are only testing that the API handles
    # passing the correct amount of arguments.

    # Both create and get methods accept the same args, so we don't need
    # separate testing methods.
    def _mock_get_create_w_items(self, parent, items):
        return "passed"

    def _mock_get_create_wo_items(self, parent):
        return "passed"

    def _mock_set_settings_w_items(self, parent, settings, items):
        pass

    def _mock_set_settings_wo_items(self, parent, settings):
        pass

    @mock_publish_plugin_instance_hook_creation
    def test_plugin_ui_methods(self, create_hook_instance):
        """
        Ensure that the custom UI methods receive the correct number of arguments.
        Previously the custom ui Methods didn't get passed items, so this test makes sure
        that the API can handle calling the hooks when they either implement or don't
        implement the items.
        """

        # Create hook instances for the UI methods that accept the items arg
        # We are not using lambdas for these, since the API checks for the
        # number of arguments on the method, and there wouldn't be a `self`
        # arg with a lambda.
        create_hook_instance.return_value = MagicMock(
            create_settings_widget=self._mock_get_create_w_items,
            get_ui_settings=self._mock_get_create_w_items,
            set_ui_settings=self._mock_set_settings_w_items,
        )
        ppi_w_items = self.PublishPluginInstance("test hook", None, {}, logger)

        create_hook_instance.return_value = MagicMock(
            create_settings_widget=self._mock_get_create_wo_items,
            get_ui_settings=self._mock_get_create_wo_items,
            set_ui_settings=self._mock_set_settings_wo_items,
        )
        ppi_wo_items = self.PublishPluginInstance("test hook", None, {}, logger)

        for ppi in [ppi_w_items, ppi_wo_items]:

            widget = ppi.run_create_settings_widget(None, [])
            self.assertEqual(widget, "passed")

            settings = ppi.run_get_ui_settings(None, [])
            self.assertEqual(settings, "passed")

            # we're just checking this doesn't error, as it doesn't return anything
            ppi.run_set_ui_settings(None, [], [])
