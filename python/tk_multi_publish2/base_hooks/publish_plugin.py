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


class PublishPlugin(HookBaseClass):
    """
    This class defines the required interface for a publish plugin. Publish
    plugins are responsible for operating on items collected by the collector
    plugin. Publish plugins define which items they will operate on as well as
    the execution logic for each phase of the publish process.
    """

    ############################################################################
    # Plugin properties

    @property
    def id(self):
        """
        Unique string identifying this plugin.
        """
        return self._id

    @id.setter
    def id(self, new_id):
        """
        Allows to set the unique string identifying this plugin.
        """
        self._id = new_id

    @property
    def icon(self):
        """
        The path to an icon on disk that is representative of this plugin
        (:class:`str`).

        The icon will be displayed on the left side of the task driven by this
        plugin, as shown in the image below.

        .. image:: ./resources/task_icon.png

        |

        Icons can be stored within the same bundle as the plugin itself and
        referenced relative to the disk location of the plugin, accessible via
        :meth:`sgtk.Hook.disk_location`.

        Example implementation:

        .. code-block:: python

            @property
            def icon(self):

                return os.path.join(
                    self.disk_location,
                    "icons",
                    "publish.png"
                )

        .. note:: Publish plugins drive the tasks that operate on publish items.
            It can be helpful to think of items as "things" and tasks as the
            "actions" that operate on those "things". A publish icon that
            represents some type of action can help artists understand the
            distinction between items and tasks in the interface.

        """
        return None

    @property
    def name(self):
        """
        The general name for this plugin (:class:`str`).

        This value is not generally used for display. Instances of the plugin
        are defined within the app's configuration and those instance names are
        what is shown in the interface for the tasks.
        """
        raise NotImplementedError

    @property
    def description(self):
        """
        Verbose, multi-line description of what the plugin does (:class:`str`).

        The string can contain html for formatting for display in the UI (any
        html tags supported by Qt's rich text engine).

        The description is displayed via the plugin's default
        :meth:`create_settings_widget` implementation, as shown in the image
        below:

        .. image:: ./resources/plugin_description.png

        |

        A simple implementation example:

        .. code-block:: python

            @property
            def description(self):

                return '''
                Creates a publish in Shotgun.

                A <b>Publish</b> entry will be created in Shotgun which will
                include a reference to the file's path on disk. Other users will
                be able to access the published file via the
                <b><a href='%s'>Loader</a></b> so long as they have access to
                the file's location on disk.
                ''' % (loader_url,)

        """
        raise NotImplementedError

    @property
    def settings(self):
        """
        A :class:`dict` defining the configuration interface for this plugin.

        The dictionary can include any number of settings required by the
        plugin, and takes the form::

            {
                <setting_name>: {
                    "type": <type>,
                    "default": <default>,
                    "description": <description>
                },
                <setting_name>: {
                    "type": <type>,
                    "default": <default>,
                    "description": <description>
                },
                ...
            }

        The keys in the dictionary represent the names of the settings. The
        values are a dictionary comprised of 3 additional key/value pairs.

        * ``type``: The type of the setting. This should correspond to one of
          the data types that toolkit accepts for app and engine settings such
          as ``hook``, ``template``, ``string``, etc.
        * ``default``: The default value for the settings. This can be ``None``.
        * ``description``: A description of the setting as a string.

        Example implementation:

        .. code-block:: python

            @property
            def settings(self):
                return {
                    "Publish Template": {
                        "type": "template",
                        "default": None,
                        "description": "The output path template for this plugin."
                    },
                    "Resolution": {
                        "type": "str",
                        "default": "1920x1080"
                        "description": "The output resolution to export before publishing."
                    }
                }

        The settings are exposed via the ``settings`` key as the plugins are
        configured via the ``publish_plugins`` setting in the app's
        configuration. Example::

            publish_plugins:
                - name: Export and Publish
                  hook: "{config}/export_and_publish.py"
                  settings:
                      Publish Template: export_template
                      Resolution: 2048x1556

        The values configured for the plugin will be supplied via settings
        parameter in the :meth:`accept`, :meth:`validate`, :meth:`publish`, and
        :meth:`finalize` methods.

        The values also drive the custom UI defined by the plugin which allows
        artists to manipulate the settings at runtime. See the
        :meth:`create_settings_widget`, :meth:`set_ui_settings`, and
        :meth:`get_ui_settings` for additional information.

        .. note:: See the hooks defined in the publisher app's ``hooks/`` folder
           for additional example implementations.
        """
        return {}

    @property
    def item_filters(self):
        """
        A :class:`list` of item type wildcard :class:`str` objects that this
        plugin is interested in.

        As items are collected by the collector hook, they are given an item
        type string (see :meth:`~.api.PublishItem.create_item`). The strings
        provided by this property will be compared to each collected item's
        type.

        Only items with types matching entries in this list will be considered
        by the :meth:`accept` method. As such, this method makes it possible to
        quickly identify which items the plugin may be interested in. Any
        sophisticated acceptance logic is deferred to the :meth:`accept` method.

        Strings can contain glob patters such as ``*``, for example ``["maya.*",
        "file.maya"]``.
        """
        raise NotImplementedError

    ############################################################################
    # Publish processing methods

    def accept(self, settings, item):
        """
        This method is called by the publisher to see if the plugin accepts the
        supplied item for processing.

        Only items matching the filters defined via the :data:`item_filters`
        property will be presented to this method.

        A publish task will be generated for each item accepted here.

        This method returns a :class:`dict` of the following form::

            {
                "accepted": <bool>,
                "enabled": <bool>,
                "visible": <bool>,
                "checked": <bool>,
            }

        The keys correspond to the acceptance state of the supplied item. Not
        all keys are required. The keys are defined as follows:

        * ``accepted``: Indicates if the plugin is interested in this value at all.
          If ``False``, no task will be created for this plugin. Required.
        * ``enabled``: If ``True``, the created task will be enabled in the UI,
          otherwise it will be disabled (no interaction allowed). Optional,
          ``True`` by default.
        * ``visible``: If ``True``, the created task will be visible in the UI,
          otherwise it will be hidden. Optional, ``True`` by default.
        * ``checked``: If ``True``, the created task will be checked in the UI,
          otherwise it will be unchecked. Optional, ``True`` by default.

        In addition to the item, the configured settings for this plugin are
        supplied. The information provided by each of these arguments can be
        used to decide whether to accept the item.

        For example, the item's ``properties`` :class:`dict` may house meta data
        about the item, populated during collection. This data can be used to
        inform the acceptance logic.

        Example implementation:

        .. code-block:: python

            def accept(self, settings, item):

                accept = True

                # get the path for the item as set during collection
                path = item.properties["path"]

                # ensure the file is not too big
                size_in_bytes = os.stat(path).st_stize
                if size_in_bytes > math.pow(10, 9): # 1 GB
                    self.logger.warning("File is too big (> 1 GB)!")
                    accept = False

                return {"accepted": accepted}

        :param dict settings: The keys are strings, matching the keys returned
            in the :data:`settings` property. The values are
            :ref:`publish-api-setting` instances.
        :param item: The :ref:`publish-api-item` instance to process for
            acceptance.

        :returns: dictionary with boolean keys accepted, required and enabled
        """
        raise NotImplementedError

    def validate(self, settings, item):
        """
        Validates the given item, ensuring it is ok to publish.

        Returns a boolean to indicate whether the item is ready to publish.
        Returning ``True`` will indicate that the item is ready to publish. If
        ``False`` is returned, the publisher will disallow publishing of the
        item.

        An exception can also be raised to indicate validation failed.
        When an exception is raised, the error message will be displayed as a
        tooltip on the task as well as in the logging view of the publisher.

        Simple implementation example for a Maya session item validation:

        .. code-block:: python

            def validate(self, settings, item):

                 path = cmds.file(query=True, sn=True)

                 # ensure the file has been saved
                 if not path:
                    raise Exception("The Maya session has not been saved.")

                 return True

        :param dict settings: The keys are strings, matching the keys returned
            in the :data:`settings` property. The values are
            :ref:`publish-api-setting` instances.
        :param item: The :ref:`publish-api-item` instance to validate.

        :returns: True if item is valid, False otherwise.
        """
        raise NotImplementedError

    def publish(self, settings, item):
        """
        Executes the publish logic for the given item and settings.

        Any raised exceptions will indicate that the publish pass has failed and
        the publisher will stop execution.

        Simple implementation example for a Maya session item publish:

        .. code-block:: python

            def publish(self, settings, item):

                path = item.properties["path"]

                # ensure the session is saved
                cmds.file(rename=path)
                cmds.file(save=True, force=True)

                # the hook's parent is the publisher
                publisher = self.parent

                # get the publish info
                publish_version = publisher.util.get_version_number(path)
                publish_name = publisher.util.get_publish_name(path)

                # register the publish and pack the publish info into the item's
                # properties dict
                item.properties["sg_publish_data"] = sgtk.util.register_publish(
                    "tk": publisher.sgtk,
                    "context": item.context,
                    "comment": item.description,
                    "path": path,
                    "name": publish_name,
                    "version_number": publish_version,
                    "thumbnail_path": item.get_thumbnail_as_path(),
                    "published_file_type": "Maya Scene",
                    "dependency_paths": self._maya_get_session_dependencies()
                )

        :param dict settings: The keys are strings, matching the keys returned
            in the :data:`settings` property. The values are
            :ref:`publish-api-setting` instances.
        :param item: The :ref:`publish-api-item` instance to publish.
        """
        raise NotImplementedError

    def finalize(self, settings, item):
        """
        Execute the finalize logic for the given item and settings.

        This method can be used to do any type of cleanup or reporting after
        publishing is complete.

        Any raised exceptions will indicate that the finalize pass has failed
        and the publisher will stop execution.

        Simple implementation example for a Maya session item finalization:

        .. code-block:: python

            def finalize(self, settings, item):

                path = item.properties["path"]

                # get the next version of the path
                next_version_path = publisher.util.get_next_version_path(path)

                # save to the next version path
                cmds.file(rename=next_version_path)
                cmds.file(save=True, force=True)

        :param dict settings: The keys are strings, matching the keys returned
            in the :data:`settings` property. The values are
            :ref:`publish-api-setting` instances.
        :param item: The :ref:`publish-api-item` instance to finalize.
        """
        raise NotImplementedError

    ############################################################################
    # Methods for creating/displaying custom plugin interface

    # NOTE: We provide a default settings widget implementation here to show the
    # plugin's description. This allows for a consistent default look and
    # allows clients to write their own publish plugins while deferring custom
    # UI settings implementations until needed.

    def create_settings_widget(self, parent, items=None):
        """
        Creates a Qt widget, for the supplied parent widget (a container widget
        on the right side of the publish UI).

        :param parent: The parent to use for the widget being created.
        :param items: A list of PublishItems the selected publish tasks are parented to.
        :return: A QtGui.QWidget or subclass that displays information about
            the plugin and/or editable widgets for modifying the plugin's
            settings.
        """

        # defer Qt-related imports
        from sgtk.platform.qt import QtCore, QtGui

        # create a group box to display the description
        description_group_box = QtGui.QGroupBox(parent)
        description_group_box.setTitle("Description:")

        # The publish plugin that subclasses this will implement the
        # `description` property. We'll use that here to display the plugin's
        # description in a label.
        description_label = QtGui.QLabel(self.description)
        description_label.setWordWrap(True)
        description_label.setOpenExternalLinks(True)
        description_label.setTextFormat(QtCore.Qt.TextFormat.RichText)

        # create the layout to use within the group box
        description_layout = QtGui.QVBoxLayout()
        description_layout.addWidget(description_label)
        description_layout.addStretch()
        description_group_box.setLayout(description_layout)

        # return the description group box as the widget to display
        return description_group_box

    def get_ui_settings(self, widget, items=None):
        """
        Invoked by the Publisher when the selection changes. This method gathers the settings
        on the previously selected task, so that they can be later used to repopulate the
        custom UI if the task gets selected again. They will also be passed to the accept, validate,
        publish and finalize methods, so that the settings can be used to drive the publish process.

        The widget argument is the widget that was previously created by
        `create_settings_widget`.

        The method returns a dictionary, where the key is the name of a
        setting that should be updated and the value is the new value of that
        setting. Note that it is up to you how you want to store the UI's state as
        settings and you don't have to necessarily to return all the values from
        the UI. This is to allow the publisher to update a subset of settings
        when multiple tasks have been selected.

        Example::

            {
                 "setting_a": "/path/to/a/file"
            }

        :param widget: The widget that was created by `create_settings_widget`
        """

        # the default implementation does not show any editable widgets, so this
        # is a no-op. this method is required to be defined in order for the
        # custom UI to show up in the app
        return {}

    def set_ui_settings(self, widget, settings, items=None):
        """
        Allows the custom UI to populate its fields with the settings from the
        currently selected tasks.

        The widget is the widget created and returned by
        `create_settings_widget`.

        A list of settings dictionaries are supplied representing the current
        values of the settings for selected tasks. The settings dictionaries
        correspond to the dictionaries returned by the settings property of the
        hook.

        Example::

            settings = [
            {
                 "seeting_a": "/path/to/a/file"
                 "setting_b": False
            },
            {
                 "setting_a": "/path/to/a/file"
                 "setting_b": False
            }]

        The default values for the settings will be the ones specified in the
        environment file. Each task has its own copy of the settings.

        When invoked with multiple settings dictionaries, it is the
        responsibility of the custom UI to decide how to display the
        information. If you do not wish to implement the editing of multiple
        tasks at the same time, you can raise a ``NotImplementedError`` when
        there is more than one item in the list and the publisher will inform
        the user than only one task of that type can be edited at a time.

        :param widget: The widget that was created by `create_settings_widget`.
        :param settings: a list of dictionaries of settings for each selected
            task.
        :param items: A list of PublishItems the selected publish tasks are parented to.
        """

        # the default implementation does not show any editable widgets, so this
        # is a no-op. this method is required to be defined in order for the
        # custom UI to show up in the app
        pass
