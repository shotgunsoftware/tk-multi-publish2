# Copyright (c) 2018 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import fnmatch

import sgtk

from .tree import PublishTree
from .plugins import CollectorPluginInstance, PublishPluginInstance

logger = sgtk.platform.get_logger(__name__)


class PublishManager(object):
    """
    This class is used for managing and executing publishes.
    """

    ############################################################################
    # setting names

    CONFIG_COLLECTOR_HOOK_PATH = "collector"
    CONFIG_COLLECTOR_SETTINGS = "collector_settings"
    CONFIG_PLUGIN_DEFINITIONS = "publish_plugins"

    ############################################################################
    # special item property keys

    # this is the key we'll use to store a special property on items that
    # are collected via a file path. we can use this later on to determine which
    # items were added to the tree via path collection and what that original
    # path was (client code could add multiple items for a single path).
    PROPERTY_KEY_COLLECTED_FILE_PATH = "__collected_file_path__"

    ############################################################################
    # instance methods

    def __init__(self, publish_logger=None):
        """
        Initialize the manager.
        """

        # the current bundle (the publisher instance)
        self._bundle = sgtk.platform.current_bundle()

        # a logger to be used by the various collector/publish plugins
        self._logger = publish_logger or logger

        # the underlying tree representation of the items to publish
        self._tree = PublishTree()

        # collector instance for this context
        self._collector_instance = None

        # a lookup of context to publish plugins.
        self._processed_contexts = {}

        # initialize the collector plugin
        self.logger.debug("Loading collector configuration...")
        self._load_collector()

        # go ahead and load the plugins for the current context for efficiency
        self.logger.debug("Loading plugins for the current context...")
        self._load_publish_plugins(self._bundle.context)

    def attach_plugins(self, items):
        """
        For each item supplied, given it's context, load the appropriate plugins
        and add any matching tasks. If any tasks exist on the supplied items,
        they will be removed.
        """
        for item in items:

            # clear existing tasks for this item
            item.clear_tasks()

            self.logger.debug("Processing item: %s" % (item,))

            item_context = item.context

            context_plugins = self._load_publish_plugins(item_context)
            self.logger.debug(
                "Offering %s plugins for context: %s" %
                (len(context_plugins), item_context)
            )

            for context_plugin in context_plugins:

                self.logger.debug(
                    "Checking plugin: %s" % (context_plugin,))

                if not self._item_filters_match(item, context_plugin):
                    continue

                self.logger.debug("Running plugin acceptance method...")

                # item/filters matched. now see if the plugin accepts
                accept_data = context_plugin.run_accept(item)

                if accept_data.get("accepted"):
                    self.logger.debug("Plugin accepted the item.")
                    task = item.add_task(context_plugin)
                    task.visible = accept_data.get("visible", True)
                    task.active = accept_data.get("checked", True)
                    task.enabled = accept_data.get("enabled", True)
                else:
                    self.logger.debug("Plugin did not accept the item.")

    def clear(self):
        """
        Clear all items to be published.
        :return:
        """
        self._tree.clear(clear_persistent=True)

    def collect_files(self, file_paths):
        """
        Run the collection logic to populate the publish tree with items for
        each supplied path.

        :param file_paths: A list of file paths to collect as items to publish.
        :returns: A list of the items created.
        """

        new_items = []

        for file_path in file_paths:

            # get a list of all items in the tree prior to collection
            items_before = list(self._tree.items)

            if self._path_already_collected(file_path):
                self.logger.debug(
                    "Skipping previously collected file path: '%s'" %
                    (file_path,)
                )
            else:
                self.logger.debug(
                    "Collecting file path: %s" % (file_path,))

                # we supply the root item of the tree for parenting of items
                # that are collected.
                self._collector_instance.run_process_file(
                    self._tree.root_item,
                    file_path
                )

            # get a list of all items in the tree after collection
            items_after = list(self._tree.items)

            # calculate which items are new
            new_file_items = list(set(items_after) - set(items_before))

            if not new_file_items:
                self.logger.debug(
                    "No items collected for path: %s" % (file_path,))
                continue

            # Mark new items as persistent and include the file path that was
            # used for collection as part of the item properties
            for file_item in new_file_items:
                if file_item.parent == self._tree.root_item:
                    # only top-level items can be marked as persistent
                    file_item.persistent = True
                file_item.properties[self.PROPERTY_KEY_COLLECTED_FILE_PATH] = \
                    file_path

            # attach the appropriate plugins to the new items
            self.attach_plugins(new_file_items)

            new_items.extend(new_file_items)

        return new_items

    def collect_session(self):
        """
        Run the collection logic to populate the tree with items to publish.

        This will reestablish the state of the publish tree, recomputing
        everything. Any externally added file paths will be retained.

        :returns: A list of the items created.
        """

        # this will clear the tree of all non-persistent items.
        self._tree.clear()

        # get a list of all items in the tree prior to collection (this should
        # be only the persistent items)
        items_before = list(self._tree.items)

        # we supply the root item of the tree for parenting of items that
        # are collected.
        self._collector_instance.run_process_current_session(
            self._tree.root_item)

        # get a list of all items in the tree after collection
        items_after = list(self._tree.items)

        # calculate which items are new
        new_items = list(set(items_after) - set(items_before))

        # attach the appropriate plugins to the new items
        if new_items:
            self.attach_plugins(new_items)

        return new_items

    def load(self, path):
        """
        Load a publish tree that was saved to disk.
        """
        self._tree = PublishTree.load_file(path)

    def remove_item(self, item):
        """
        Remove the supplied item from the items to be published.
        """
        self._tree.remove_item(item)

    def save(self, path):
        """Serialize and save the underlying publish tree to disk."""
        self._tree.save_file(path)

    def validate(self):
        """
        Validate the items in the publish tree.

        Each collected item with attached publish plugins will validate the
        state of the item in preparation for publishing.
        """

        all_valid = True

        self.logger.info("Running validation pass...")
        for item in self._tree:
            if not item.active:
                self.logger.debug(
                    "Skipping item '%s' because it is inactive" % (item,))
                continue

            if not item.tasks:
                self.logger.debug(
                    "Skipping item '%s' because it has no tasks attached." %
                    (item,)
                )
                continue

            self.logger.debug("Validating: %s" % (item,))

            for task in item.tasks:

                if not task.active:
                    self.logger.debug(
                        "Skipping inactive task: %s" % (task,))
                    continue

                self.logger.debug(
                    "Running validation for task: %s" % (task,))
                if not task.validate():
                    all_valid = False

        return all_valid

    def publish(self):
        """
        Publish the collected items.

        The ``validate()`` method should be called first

        Each task assigned to collected items will execute their publish
        payload. Items are processed in depth first order.
        """

        self.logger.info("Executing publish pass...")

        for item in self._tree:
            if not item.active:
                self.logger.debug(
                    "Skipping item '%s' because it is inactive" % (item,))
                continue

            if not item.tasks:
                self.logger.debug(
                    "Skipping item '%s' because it has no tasks attached." %
                    (item,)
                )
                continue

            self.logger.debug("Publishing: %s" % (item,))

            for task in item.tasks:

                if not task.active:
                    self.logger.debug(
                        "Skipping inactive task: %s" % (task,))
                    continue

                self.logger.debug(
                    "Executing publish for task: %s" % (task,))
                task.publish()

    @property
    def context(self):
        """Returns the execution context of the manager."""
        return self._bundle.context

    @property
    def items(self):
        """A depth-first generator of all items to be published."""
        for item in self._tree.items:
            yield item

    @property
    def logger(self):
        """Returns the logger used during publish execution."""
        return self._logger

    @logger.setter
    def logger(self, logger):
        """Set the logger to be used during publish execution."""
        self._logger = logger

    @property
    def root_item(self):
        """
        Returns the special root item of the tree. This is the parent item to
        all items to be published.
        :return:
        """
        return self._tree.root_item

    @property
    def top_level_items(self):
        """
        Returns a list of top-level items to be published. These are the
        immediate children of the root item.
        """
        return self._tree.root_item.children

    @property
    def persistent_items(self):
        """Returns a list of """
        return self._tree.persistent_items

    @property
    def collected_files(self):
        """
        Returns a list of file paths for all items collected via the
        collect_files method.
        """
        collected_paths = []
        for item in self.persistent_items:
            if self.PROPERTY_KEY_COLLECTED_FILE_PATH in item.properties:
                collected_paths.append(
                    item.properties[self.PROPERTY_KEY_COLLECTED_FILE_PATH])

        return collected_paths

    ############################################################################
    # protected methods

    def _item_filters_match(self, item, publish_plugin):
        """
        Returns ``True`` if the supplied item's type specification matches
        the publish plugin's item filters.

        :param item: The item to compare
        :param publish_plugin: The publish plugin instance to compare
        """

        for item_filter in publish_plugin.item_filters:
            if fnmatch.fnmatch(item.type_spec, item_filter):
                # there is a match!
                self.logger.debug(
                    "Item %s with spec '%s' matches plugin filters: '%s'" %
                    (item, item.type_spec, item_filter)
                )
                return True

        # no filters match the item's type
        self.logger.debug(
            "Item %s with spec '%s' does not match any plugin filters: '%s'" %
            (item, item.type_spec, publish_plugin.item_filters)
        )
        return False

    def _load_collector(self):
        """
        Load the collector plugin for the current bundle configuration/context.
        """

        collector_hook_path = self._bundle.get_setting(
            self.CONFIG_COLLECTOR_HOOK_PATH)
        collector_settings = self._bundle.get_setting(
            self.CONFIG_COLLECTOR_SETTINGS)

        self._collector_instance = CollectorPluginInstance(
            collector_hook_path,
            collector_settings,
            self.logger
        )

    def _load_publish_plugins(self, context):
        """
        Given a context, this method load the corresponding, configured publish
        plugins.
        """

        # return the cached plugins if the context has already been processed
        if context in self._processed_contexts:
            return self._processed_contexts[context]

        engine = self._bundle.engine

        self.logger.debug(
            "Finding publish plugin settings for context: %s" % (context,))

        if context == self._bundle.context:
            # if the context matches the bundle, we don't need to do any extra
            # work since the settings are already accessible
            plugin_settings = self._bundle.get_setting(
                self.CONFIG_PLUGIN_DEFINITIONS)
        else:
            # load the plugins from the supplied context. this means executing
            # the pick environment hook and reading from disk. this is why we
            # cache the plugins.
            context_settings = sgtk.platform.engine.find_app_settings(
                engine.name,
                self._bundle.name,
                self._bundle.sgtk,
                context,
                engine_instance_name=engine.instance_name
            )

            app_settings = None
            if len(context_settings) > 1:
                # There's more than one instance of that app for the engine
                # instance, so we'll need to deterministically pick one. We'll
                # pick the one with the same application instance name as the
                # current app instance.
                for settings in context_settings:
                    if settings.get("app_instance") == self._bundle.instance_name:
                        app_settings = settings
            elif len(context_settings) == 1:
                app_settings = context_settings[0]["settings"]


            if app_settings:
                plugin_settings = app_settings[self.CONFIG_PLUGIN_DEFINITIONS]
            else:
                self.logger.debug(
                    "Could not find publish plugin settings for context: %s" %
                    (context,)
                )
                plugin_settings = []

        # build up a list of all configured publish plugins here
        plugins = []

        # create plugin instances for configured plugins
        for plugin_def in plugin_settings:

            self.logger.debug(
                "Found publish plugin config: %s" % (plugin_def,))

            publish_plugin_instance_name = plugin_def["name"]
            publish_plugin_hook_path = plugin_def["hook"]
            publish_plugin_settings = plugin_def["settings"]

            plugin_instance = PublishPluginInstance(
                publish_plugin_instance_name,
                publish_plugin_hook_path,
                publish_plugin_settings,
                self.logger
            )
            plugins.append(plugin_instance)
            self.logger.debug(
                "Created publish plugin: %s" % (plugin_instance,))

        # ensure the plugins are cached
        self._processed_contexts[context] = plugins

        return plugins

    def _path_already_collected(self, file_path):
        """
        Returns ``True`` if the supplied file path has been collected into the
        tree already. ``False`` otherwise.
        """

        # check each persistent item for a collected file path. if it matches
        # the supplied path, then the path has already been collected.
        for item in self.persistent_items:
            if self.PROPERTY_KEY_COLLECTED_FILE_PATH in item.properties:
                collected_path = \
                    item.properties[self.PROPERTY_KEY_COLLECTED_FILE_PATH]
                if collected_path == file_path:
                    return True

        # no existing, persistent item was collected with this path
        return False
