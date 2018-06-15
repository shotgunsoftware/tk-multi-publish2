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

from .graph import PublishGraph
from .plugins import CollectorPluginInstance, PublishPluginInstance

logger = sgtk.platform.get_logger(__name__)

# TODO:
#  collector plugin api must be identical
#  publish plugin api must be identical
#  item api must be identical
    # consider how to handle Qt stuff in api

class PublishManager(object):
    """
    This class is used for managing and executing a publish graph.

    TODO: more description here...
    """

    ############################################################################
    # setting names

    CONFIG_COLLECTOR_HOOK_PATH = "collector"
    CONFIG_COLLECTOR_SETTINGS = "collector_settings"
    CONFIG_PLUGIN_DEFINITIONS = "publish_plugins"

    ############################################################################
    # special item property keys

    PROPERTY_KEY_COLLECTED_FILE_PATH = "__collected_file_path__"

    ############################################################################
    # instance methods

    def __init__(self, publish_logger=None):
        """
        Initialize the manager.

        :param publish_logger: A logger object that the collector and publish
            plugins can send logging information to. If not supplied, the app's
            logger will be used.
        """

        # the current bundle (the publisher instance)
        self._bundle = sgtk.platform.current_bundle()

        if not publish_logger:
            publish_logger = logger

        # a logger to be used by the various collector/publish plugins
        self.publish_logger = publish_logger

        # the graph representation
        self._graph = PublishGraph()

        # collector and publish plugins
        self._collector_instance = None
        self._processed_contexts = {}

        # initialize the collector plugin
        self.publish_logger.debug("Loading collector configuration...")
        self._load_collector()

        # go ahead and load the plugins for the current context for efficiency
        self.publish_logger.debug("Loading plugins for the current context...")
        self._load_publish_plugins(self._bundle.context)

    def collect_files(self, file_paths):
        """
        Run the collection logic to populate the graph with items for each
        supplied path.

        :param file_paths: A list of file paths to collect as items to publish.
        :returns: A list of the items created.
        """

        new_items = []

        for file_path in file_paths:

            # get a list of all items in the graph prior to collection
            item_ids_before = [i.id for i in self._graph.items]

            if self._path_already_collected(file_path):
                self.publish_logger.debug(
                    "Skipping previously collected file path: '%s'" %
                    (file_path,)
                )
            else:
                self.publish_logger.debug(
                    "Collecting file path: %s" % (file_path,))

                # we supply the root item of the graph for parenting of items
                # that are collected.
                self._collector_instance.run_process_file(
                    self._graph.root_item,
                    file_path
                )

            # get a list of all items in the graph after collection
            item_ids_after = [i.id for i in self._graph.items]

            # calculate which items are new
            new_file_item_ids = list(set(item_ids_after) - set(item_ids_before))
            new_file_items = self._graph.get_items_for_ids(new_file_item_ids)

            if not new_file_items:
                self.publish_logger.debug(
                    "No items collected for path: %s" % (file_path,))
                continue

            # Mark new items as persistent and include the file path that was
            # used for collection as part of the item properties
            for file_item in new_file_items:
                if file_item.parent == self._graph.root_item:
                    # only top-level items can be marked as persistent
                    file_item.persistent = True
                file_item.properties[self.PROPERTY_KEY_COLLECTED_FILE_PATH] = \
                    file_path

            # attach the appropriate plugins to the new items
            self._attach_plugins(new_file_items)

            new_items.extend(new_file_items)

        return new_items

    def collect_session(self):
        """
        Run the collection logic to populate the graph with items to publish.

        This will reestablish the state of the graph, recomputing everything.
        Any externally added file paths will be retained.

        :returns: A list of the items created.
        """

        # this will clear the graph of all non-persistent items.
        self._graph.clear()

        # get a list of all items in the graph prior to collection (this should
        # be only the persistent items)
        item_ids_before = [i.id for i in self._graph.items]

        # we supply the root item of the graph for parenting of items that
        # are collected.
        self._collector_instance.run_process_current_session(
            self._graph.root_item)

        # get a list of all items in the graph after collection
        item_ids_after = [i.id for i in self._graph.items]

        # calculate which items are new
        new_item_ids = list(set(item_ids_after) - set(item_ids_before))
        new_items = self._graph.get_items_for_ids(new_item_ids)

        # attach the appropriate plugins to the new items
        if new_items:
            self._attach_plugins(new_items)

        return new_items

    def load_graph(self, path):
        """Deserialize and load a graph that was previously to disk.

        NOTE: the manager's current graph will be lost.
        """
        self._graph = PublishGraph.load(path)

    def save_graph(self, path):
        """Serialize and save the underlying publish graph to disk."""
        self._graph.save(path)

    def validate(self):

        all_valid = True

        self.publish_logger.info("Running validation pass...")
        for item in self._graph:
            if not item.active:
                self.publish_logger.debug(
                    "Skipping item '%s' because it is inactive" % (item,))
                continue

            if not item.tasks:
                self.publish_logger.debug(
                    "Skipping item '%s' because it has no tasks attached." %
                    (item,)
                )
                continue

            self.publish_logger.debug("Validating: %s" % (item,))

            for task in item.tasks:

                if not task.active:
                    self.publish_logger.debug(
                        "Skipping inactive task: %s" % (task,))
                    continue

                self.publish_logger.debug(
                    "Running validation for task: %s" % (task,))
                if not task.validate():
                    all_valid = False

        return all_valid

    def publish(self):

        self.publish_logger.info("Executing publish pass...")

        # TODO: re-validate?

        for item in self._graph:
            if not item.active:
                self.publish_logger.debug(
                    "Skipping item '%s' because it is inactive" % (item,))
                continue

            if not item.tasks:
                self.publish_logger.debug(
                    "Skipping item '%s' because it has no tasks attached." %
                    (item,)
                )
                continue

            self.publish_logger.debug("Publishing: %s" % (item,))

            for task in item.tasks:

                if not task.active:
                    self.publish_logger.debug(
                        "Skipping inactive task: %s" % (task,))
                    continue

                self.publish_logger.debug(
                    "Executing publish for task: %s" % (task,))
                task.publish()

    @property
    def context(self):
        """Returns the execution context of the manager."""
        return self._bundle.context

    @property
    def graph(self):
        """Returns the graph object this manager is operating on."""
        return self._graph

    @property
    def publish_logger(self):
        """Returns the logger used during publish execution."""
        return self._logger

    @publish_logger.setter
    def publish_logger(self, publish_logger):
        """Set the logger to be used during publish execution."""
        self._logger = publish_logger

    ############################################################################
    # protected methods

    def _attach_plugins(self, items):
        """
        For each item supplied, load the appropriate plugins and add matching
        tasks.
        """

        # TODO: clear existing plugins/tasks to allow rerunning attach logic?

        for item in items:

            self.publish_logger.debug("Processing item: %s" % (item,))

            item_context = item.context

            context_plugins = self._load_publish_plugins(item_context)
            self.publish_logger.debug(
                "Offering %s plugins for context: %s" %
                (len(context_plugins), item_context)
            )

            for context_plugin in context_plugins:

                self.publish_logger.debug(
                    "Checking plugin: %s" % (context_plugin,))

                if not self._item_filters_match(item, context_plugin):
                    continue

                self.publish_logger.debug("Running plugin acceptance method...")

                # item/filters matched. now see if the plugin accepts
                accept_data = context_plugin.run_accept(item)

                if accept_data.get("accepted"):
                    self.publish_logger.debug("Plugin accepted the item.")
                    task = item.add_task(context_plugin)
                    task.visible = accept_data.get("visible", True)
                    task.active = accept_data.get("checked", True)
                    task.enabled = accept_data.get("enabled", True)
                else:
                    self.publish_logger.debug("Plugin did not accept the item.")

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
                self.publish_logger.debug(
                    "Item %s with spec '%s' matches plugin filters: '%s'" %
                    (item, item.type_spec, item_filter)
                )
                return True

        # no filters match the item's type
        self.publish_logger.debug(
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
            self.publish_logger
        )

    def _load_publish_plugins(self, context):

        # return the cached plugins if the context has already been processed
        if context in self._processed_contexts:
            return self._processed_contexts[context]

        engine = self._bundle.engine

        self.publish_logger.debug(
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

            # since we've supplied an instance name, we should get a list with a
            # single dictionary returned. if not, return an empty list of
            # plugins.
            if len(context_settings) != 1:
                self.publish_logger.debug(
                    "Could not find publish plugin settings for context: %s" %
                    (context,)
                )

            # retrieve the settings from the returned list of dictionaries
            app_settings = context_settings[0]["settings"]
            plugin_settings = app_settings[self.CONFIG_PLUGIN_DEFINITIONS]

        # build up a list of all configured publish plugins here
        plugins = []

        # create plugin instances for configured plugins
        for plugin_def in plugin_settings:

            self.publish_logger.debug(
                "Found publish plugin config: %s" % (plugin_def,))

            publish_plugin_instance_name = plugin_def["name"]
            publish_plugin_hook_path = plugin_def["hook"]
            publish_plugin_settings = plugin_def["settings"]

            plugin_instance = PublishPluginInstance(
                publish_plugin_instance_name,
                publish_plugin_hook_path,
                publish_plugin_settings,
                self.publish_logger
            )
            plugins.append(plugin_instance)
            self.publish_logger.debug(
                "Created publish plugin: %s" % (plugin_instance,))

        # ensure the plugins are cached
        self._processed_contexts[context] = plugins

        return plugins

    def _path_already_collected(self, file_path):
        """
        Returns ``True`` if the supplied file path has been collected into the
        graph already. ``False`` otherwise.
        """

        # check each persistent item for a collected file path. if it matches
        # the supplied path, then the path has already been collected.
        for item in self._graph.persistent_items:
            if self.PROPERTY_KEY_COLLECTED_FILE_PATH in item.properties:
                collected_path = \
                    item.properties[self.PROPERTY_KEY_COLLECTED_FILE_PATH]
                if collected_path == file_path:
                    return True

        # no existing, persistent item was collected with this path
        return False
