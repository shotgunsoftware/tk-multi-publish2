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

    __slots__ = [
        "_bundle",
        "_logger",
        "_tree",
        "_collector_instance",
        "_processed_contexts",
        "_post_phase_hook",
    ]

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

        :param publish_logger: This is a standard python logger to use during
            publishing. A default logger will be provided if not supplied. This
            can be useful when implementing a custom UI, for example, with a
            specialized log handler (as is the case with the Publisher)
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
            self.CONFIG_POST_PHASE_HOOK_PATH
        )
        self._post_phase_hook = self._bundle.create_hook_instance(
            post_phase_hook_path, base_class=self._bundle.base_hooks.PostPhaseHook
        )

    def collect_files(self, file_paths):
        """
        Run the collection logic to populate the publish tree with items for
        each supplied path.

        Each path supplied to this method will be processed by the configured
        collector hook for the current context. The collector will create
        :ref:`publish-api-item` instances accordingly, each of which will be
        marked as :py:attr:`~.api.PublishItem.persistent`.

        :param list file_paths: A list of file paths to collect as items to
            publish.
        :returns: A list of the created :ref:`publish-api-item` instances.
        """

        new_items = []

        for file_path in file_paths:

            # get a list of all items in the tree prior to collection
            items_before = list(self.tree)

            if self._path_already_collected(file_path):
                logger.debug(
                    "Skipping previously collected file path: '%s'" % (file_path,)
                )
            else:
                logger.debug("Collecting file path: %s" % (file_path,))

                # we supply the root item of the tree for parenting of items
                # that are collected.
                self._collector_instance.run_process_file(
                    self.tree.root_item, file_path
                )

            # get a list of all items in the tree after collection
            items_after = list(self.tree)

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
                file_item.properties[self.PROPERTY_KEY_COLLECTED_FILE_PATH] = file_path

            # attach the appropriate plugins to the new items
            self._attach_plugins(new_file_items)

            new_items.extend(new_file_items)

        return new_items

    def collect_session(self):
        """
        Run the collection logic to populate the tree with items to publish.

        This method will collect all session :ref:`publish-api-item` instances
        as defined by the configured collector hook for the current context.

        This will reestablish the state of the publish tree, recomputing
        everything. Any externally added file path items, or other items, marked
        as :py:attr:`~.api.PublishItem.persistent` will be retained.

        :returns: A list of the created :ref:`publish-api-item` instances.
        """

        # this will clear the tree of all non-persistent items.
        self.tree.clear(clear_persistent=False)

        # get a list of all items in the tree prior to collection (this should
        # be only the persistent items)
        items_before = list(self.tree)

        # we supply the root item of the tree for parenting of items that
        # are collected.
        self._collector_instance.run_process_current_session(self.tree.root_item)

        # get a list of all items in the tree after collection
        items_after = list(self.tree)

        # calculate which items are new
        new_items = list(set(items_after) - set(items_before))

        # attach the appropriate plugins to the new items
        if new_items:
            self._attach_plugins(new_items)

        return new_items

    def load(self, path):
        """
        Load a publish tree that was serialized and saved to disk.

        This is a convenience method that replaces the manager's underlying
        :ref:`publish-api-tree` with the deserialized contents stored in the
        supplied file.
        """
        self._tree = PublishTree.load_file(path)

    def save(self, path):
        """
        Saves a publish tree to disk.
        """
        self._tree.save_file(path)

    def _process_tasks(self, task_generator, task_cb):
        """
        Processes tasks returned by the generator and invokes the passed in
        callback on each. The result of the task callback will be forwarded back
        to the generator.

        :param task_genrator: Iterator on task to process.
        :param task_cb: Callable that will process a task.
            The signature is
            def task_cb(task):
                ...
        """
        # calling code can supply its own generator for tasks to process. if not
        # supplied, we'll use our own generator.
        if not task_generator:
            task_generator = self._task_generator()

        # get the first task
        task = None
        try:
            task = next(task_generator)
        except StopIteration:
            pass

        # now begin iterating over tasks supplied by the generator
        while task:

            return_value = task_cb(task)

            # send the return_value and get the next task. this is a bit annoying
            # since send() returns the next value of the generator. which is why
            # we're using `while` instead of a for loop with the generator.
            try:
                task = task_generator.send(return_value)
            except StopIteration:
                break

    def validate(self, task_generator=None):
        """
        Validate items to be published.

        This is done by running the :meth:`~.base_hooks.PublishPlugin.validate`
        method on each task in the publish tree. A list of
        :class:`~PublishTask` instances that failed validation will be returned.
        An exception will be associated with every task that failed validation
        if one was raised. If no exception was raised, the second member of the
        tuple will be ``None``.

        By default, the method will iterate over the manager's publish tree,
        validating all active tasks on all active items. To process tasks in a
        different way (different order or different criteria) you can provide
        a custom ``task_generator`` that yields :class:`~PublishTask` instances.

        For example, to validate all items in the tree, without worrying about
        their active state:

        .. code-block:: python

            def all_tasks_generator(publish_tree):

                for item in publish_tree:
                    for task in item.tasks:
                        yield task

            publish_manager.validate(task_generator=all_tasks_generator)

        :param task_generator: A generator of :class:`~PublishTask` instances.

        :returns: A list of tuples of (:class:`~PublishTask`,
            optional :class:`Exception`) that failed to validate.
        """

        # we'll use this to build a list of tasks that failed to validate
        failed_to_validate = []

        def task_cb(task):
            error = None
            # do the actual validation and send the status back to the generator
            # so that it can react to the results. This is used, for example, by
            # the UI's generator to update the display of the task as it is
            # being processed.
            try:
                is_valid = task.validate()
            except Exception as e:
                is_valid = False
                error = e

            # if the task didn't validate, add it to the list of tasks that
            # failed.
            if not is_valid:
                failed_to_validate.append((task, error))

            return (is_valid, error)

        self._process_tasks(task_generator, task_cb)

        # execute the post validate method of the phase phase hook
        self._post_phase_hook.post_validate(
            self.tree,
        )

        return failed_to_validate

    def publish(self, task_generator=None):
        """
        Publish items in the tree.

        This is done by running the :meth:`~.base_hooks.PublishPlugin.publish`
        method on each task in the publish tree.

        By default, the method will iterate over the manager's publish tree,
        publishing all active tasks on all active items. To process tasks in a
        different way (different order or different criteria) you can provide
        a custom ``task_generator`` that yields :class:`~PublishTask` instances.

        For example, to publish all items in the tree that have a
        ``local_publish`` flag set in their properties dictionary, you could do
        the following:

        .. code-block:: python

            def local_tasks_generator(publish_tree):

                for item in publish_tree:
                    if item.properties.get("local_publish"):
                        for task in item.tasks:
                            yield task

            publish_manager.publish(task_generator=local_tasks_generator)

        If an exception is raised by one of the published task, the publishing
        is aborted and the exception is raised back to the caller.

        :param task_generator: A generator of :class:`~PublishTask` instances.
        """
        self._process_tasks(task_generator, lambda task: task.publish())

        # execute the post publish method of the phase phase hook
        self._post_phase_hook.post_publish(self.tree)

    def finalize(self, task_generator=None):
        """
        Finalize items in the tree.

        This is done by running the :meth:`~.base_hooks.PublishPlugin.finalize`
        method on each task in the publish tree.

        By default, the method will iterate over the manager's publish tree,
        finalizing all active tasks on all active items. To process tasks in a
        different way (different order or different criteria) you can provide
        a custom ``task_generator`` that yields :class:`~PublishTask` instances.

        For example, to finalize all items in the tree that have a
        ``generate_report`` flag set in their properties dictionary, you could
        do the following:

        .. code-block:: python

            def report_tasks_generator(publish_tree):

                for item in publish_tree:
                    if item.properties.get("generate_report"):
                        for task in item.tasks:
                            yield task

            publish_manager.finalize(task_generator=report_tasks_generator)

        If an exception is raised by one of the finalized task, the finalization
        is aborted and the exception is raised back to the caller.

        :param task_generator: A generator of :class:`~PublishTask` instances.
        """
        self._process_tasks(task_generator, lambda task: task.finalize())

        # execute the post finalize method of the phase phase hook
        self._post_phase_hook.post_finalize(self.tree)

    @property
    def context(self):
        """Returns the execution context of the manager."""
        return self._bundle.context

    @property
    def logger(self):
        """
        Returns the manager's logger which is used during publish execution.
        """
        return self._logger

    @property
    def collected_files(self):
        """
        Returns a list of file paths for all items collected via the
        :meth:`~collect_files` method.
        """
        collected_paths = []
        for item in self.tree.persistent_items:
            if self.PROPERTY_KEY_COLLECTED_FILE_PATH in item.properties:
                collected_paths.append(
                    item.properties[self.PROPERTY_KEY_COLLECTED_FILE_PATH]
                )

        return collected_paths

    @property
    def tree(self):
        """
        Returns the underlying :ref:`publish-api-tree` instance.
        :return:
        """
        return self._tree

    ############################################################################
    # protected methods

    def _attach_plugins(self, items):
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
                "Offering %s plugins for context: %s"
                % (len(context_plugins), item_context)
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
                    "Item %s with spec '%s' matches plugin filters: '%s'"
                    % (item, item.type_spec, item_filter)
                )
                return True

        # no filters match the item's type
        logger.debug(
            "Item %s with spec '%s' does not match any plugin filters: '%s'"
            % (item, item.type_spec, publish_plugin.item_filters)
        )
        return False

    def _load_collector(self):
        """
        Load the collector plugin for the current bundle configuration/context.
        """

        collector_hook_path = self._bundle.get_setting(self.CONFIG_COLLECTOR_HOOK_PATH)
        collector_settings = self._bundle.get_setting(self.CONFIG_COLLECTOR_SETTINGS)

        self._collector_instance = CollectorPluginInstance(
            collector_hook_path, collector_settings, self.logger
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

        if context == self._bundle.context:
            # if the context matches the bundle, we don't need to do any extra
            # work since the settings are already accessible
            logger.debug("Finding publish plugin settings for context: %s" % (context,))
            plugin_settings = self._bundle.get_setting(self.CONFIG_PLUGIN_DEFINITIONS)
        else:
            # load the plugins from the supplied context. this means executing
            # the pick environment hook and reading from disk. this is why we
            # cache the plugins.
            logger.debug(
                "Finding publish plugin settings via pick_environment for context: %s"
                % (context,)
            )
            context_settings = sgtk.platform.engine.find_app_settings(
                engine.name,
                self._bundle.name,
                self._bundle.sgtk,
                context,
                engine_instance_name=engine.instance_name,
            )

            app_settings = None
            if len(context_settings) > 1:
                # There's more than one instance of that app for the engine
                # instance, so we'll need to deterministically pick one. We'll
                # pick the one with the same application instance name as the
                # current app instance.
                for settings in context_settings:
                    if settings.get("app_instance") == self._bundle.instance_name:
                        app_settings = settings.get("settings")
            elif len(context_settings) == 1:
                app_settings = context_settings[0].get("settings")

            if app_settings:
                plugin_settings = app_settings[self.CONFIG_PLUGIN_DEFINITIONS]
            else:
                logger.debug(
                    "Could not find publish plugin settings for context: %s"
                    % (context,)
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
                self.logger,
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
                collected_path = item.properties[self.PROPERTY_KEY_COLLECTED_FILE_PATH]
                if collected_path == file_path:
                    return True

        # no existing, persistent item was collected with this path
        return False

    def _task_generator(self):
        """
        This method generates all active tasks for all active items in the
        publish tree and yields them to the caller.

        This is the default task generator used by validate, publish, and
        finalize if no custom task generator is supplied.
        """

        self.logger.debug("Iterating over tasks...")
        for item in self.tree:

            if not item.active:
                logger.debug("Skipping item '%s' because it is inactive" % (item,))
                continue

            if not item.tasks:
                logger.debug(
                    "Skipping item '%s' because it has no tasks attached." % (item,)
                )
                continue

            logger.debug("Processing item: %s" % (item,))
            for task in item.tasks:

                if not task.active:
                    logger.debug("Skipping inactive task: %s" % (task,))
                    continue

                status = yield task
                logger.debug("Task %s status: %s" % (task, status))
