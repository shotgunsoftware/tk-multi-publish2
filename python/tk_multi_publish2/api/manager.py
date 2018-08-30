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
    CONFIG_POST_PHASE_HOOK_PATH = "post_phase"

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
        logger.debug("Loading collector plugin...")
        self._load_collector()

        # go ahead and load the plugins for the current context for efficiency
        logger.debug("Loading plugins for the current context...")
        self._load_publish_plugins(self._bundle.context)

        # load the phose phase hook
        logger.debug("Loading post phase hook...")
        post_phase_hook_path = self._bundle.get_setting(
            self.CONFIG_POST_PHASE_HOOK_PATH)
        self._post_phase_hook = self._bundle.create_hook_instance(
            post_phase_hook_path,
            base_class=self._bundle.base_hooks.PostPhaseHook
        )

    def attach_plugins(self, items):
        """
        For each item supplied, given it's context, load the appropriate plugins
        and add any matching tasks. If any tasks exist on the supplied items,
        they will be removed.
        """
        for item in items:

            # clear existing tasks for this item
            item.clear_tasks()

            logger.debug("Processing item: %s" % (item,))

            item_context = item.context

            context_plugins = self._load_publish_plugins(item_context)
            logger.debug(
                "Offering %s plugins for context: %s" %
                (len(context_plugins), item_context)
            )

            for context_plugin in context_plugins:

                logger.debug("Checking plugin: %s" % (context_plugin,))

                if not self._item_filters_match(item, context_plugin):
                    continue

                logger.debug("Running plugin acceptance method...")

                # item/filters matched. now see if the plugin accepts
                accept_data = context_plugin.run_accept(item)

                if accept_data.get("accepted"):
                    logger.debug("Plugin accepted the item.")
                    task = item.add_task(context_plugin)
                    task.visible = accept_data.get("visible", True)
                    task.active = accept_data.get("checked", True)
                    task.enabled = accept_data.get("enabled", True)
                else:
                    logger.debug("Plugin did not accept the item.")

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
            items_before = list(self.tree.items)

            if self._path_already_collected(file_path):
                logger.debug(
                    "Skipping previously collected file path: '%s'" %
                    (file_path,)
                )
            else:
                logger.debug("Collecting file path: %s" % (file_path,))

                # we supply the root item of the tree for parenting of items
                # that are collected.
                self._collector_instance.run_process_file(
                    self.tree.root_item,
                    file_path
                )

            # get a list of all items in the tree after collection
            items_after = list(self.tree.items)

            # calculate which items are new
            new_file_items = list(set(items_after) - set(items_before))

            if not new_file_items:
                logger.debug("No items collected for path: %s" % (file_path,))
                continue

            # Mark new items as persistent and include the file path that was
            # used for collection as part of the item properties
            for file_item in new_file_items:
                if file_item.parent == self.tree.root_item:
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
        self.tree.clear()

        # get a list of all items in the tree prior to collection (this should
        # be only the persistent items)
        items_before = list(self.tree.items)

        # we supply the root item of the tree for parenting of items that
        # are collected.
        self._collector_instance.run_process_current_session(
            self.tree.root_item)

        # get a list of all items in the tree after collection
        items_after = list(self.tree.items)

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

    def validate(self):
        """
        Validate the items in the publish tree.

        Each collected item with attached publish plugins will validate the
        state of the item in preparation for publishing.
        """

        failed_to_validate = []

        # method to keep a list of tasks that failed to validate
        def validate_action(task):
            if not task.validate():

                # store this task's parent item in the list of items that failed
                # to validate (if it's not already there).
                if task.item not in failed_to_validate:
                    failed_to_validate.append(task.item)

        self._execute_tasks("validate", validate_action)

        # execute the post validate method of the phose phase hook
        return self._post_phase_hook.post_validate(
            self.tree,
            failed_to_validate
        )

    def publish(self):
        """
        Publish the collected items.

        The ``validate()`` method should be called first

        Each task assigned to collected items will execute their publish
        payload. Items are processed in depth first order.
        """

        publish_action = lambda task: task.publish()
        self._execute_tasks("publish", publish_action)

        # execute the post validate method of the phose phase hook
        self._post_phase_hook.post_validate(self.tree)

        finalize_action = lambda task: task.finalize()
        self._execute_tasks("finalize", finalize_action)

        # execute the post validate method of the phose phase hook
        self._post_phase_hook.post_finalize(self.tree)

    @property
    def context(self):
        """Returns the execution context of the manager."""
        return self._bundle.context

    @property
    def logger(self):
        """Returns the logger used during publish execution."""
        return self._logger

    @property
    def collected_files(self):
        """
        Returns a list of file paths for all items collected via the
        collect_files method.
        """
        collected_paths = []
        for item in self.tree.persistent_items:
            if self.PROPERTY_KEY_COLLECTED_FILE_PATH in item.properties:
                collected_paths.append(
                    item.properties[self.PROPERTY_KEY_COLLECTED_FILE_PATH])

        return collected_paths

    @property
    def tree(self):
        """
        Returns the underlying tree instance.
        :return:
        """
        return self._tree

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
                logger.debug(
                    "Item %s with spec '%s' matches plugin filters: '%s'" %
                    (item, item.type_spec, item_filter)
                )
                return True

        # no filters match the item's type
        logger.debug(
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

        logger.debug(
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
                logger.debug(
                    "Could not find publish plugin settings for context: %s" %
                    (context,)
                )
                plugin_settings = []

        # build up a list of all configured publish plugins here
        plugins = []

        # create plugin instances for configured plugins
        for plugin_def in plugin_settings:

            logger.debug("Found publish plugin config: %s" % (plugin_def,))

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
            logger.debug("Created publish plugin: %s" % (plugin_instance,))

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
        for item in self.tree.persistent_items:
            if self.PROPERTY_KEY_COLLECTED_FILE_PATH in item.properties:
                collected_path = \
                    item.properties[self.PROPERTY_KEY_COLLECTED_FILE_PATH]
                if collected_path == file_path:
                    return True

        # no existing, persistent item was collected with this path
        return False

    def _execute_tasks(self, action_name, action):
        """
        This method iterates over all active items in the publish tree and
        executes the supplied callable on each of the item's active tasks.

        :param action_name: The name of the action being performed.
        :param action: A callable with a single argument of the task to execute

        :returns: A ``list`` of results for each task executed, in the order
            they were executed.
        """

        results = []

        self.logger.info("Executing %s..." % (action_name,))
        for item in self.tree:

            if not item.active:
                logger.debug(
                    "Skipping item '%s' because it is inactive" % (item,))
                continue

            if not item.tasks:
                logger.debug(
                    "Skipping item '%s' because it has no tasks attached." %
                    (item,)
                )
                continue

            logger.debug("Executing %s for item: %s" % (action_name, item))

            for task in item.tasks:

                if not task.active:
                    logger.debug("Skipping inactive task: %s" % (task,))
                    continue

                logger.debug("Executing %s for task: %s" % (action_name, task))

                results.append(callable(task))

        return results
