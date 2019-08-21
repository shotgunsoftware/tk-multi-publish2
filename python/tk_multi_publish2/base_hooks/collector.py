# Copyright (c) 2018 Shotgun Software Inc.
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


class CollectorPlugin(HookBaseClass):
    """
    This class defines the required interface for a collector plugin.
    Collectors are used to gather individual files that are loaded via the
    file browser or dragged and dropped into the Publish2 UI. It is also used
    to gather items to be published within the current DCC session.
    """

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

    ############################################################################
    # Collector properties
    @property
    def settings(self):
        """
        A :class:`dict` defining the configuration interface for this collector.

        The values configured for the collector will be supplied via settings
        parameter in the :func:`process_current_session` and
        :func:`process_file` methods.

        The dictionary can include any number of settings required by the
        collector, and takes the form::

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
                    "Work Template": {
                        "type": "template",
                        "default": None,
                        "description": "A work file template required by this collector."
                    },
                    "Exclude Objects": {
                        "type": "list",
                        "default": ["obj1", "obj2", "obj3"],
                        "description": "A list of objects to ignore."
                    }
                }

        The settings are exposed via the ``collector_settings`` setting in the
        app's configuration. Example::

            collector_settings:
                Work Template: my_work_template
                Exclude Objects: [obj1, obj4]

        .. note:: See the hooks defined in the publisher app's ``hooks/`` folder
           for additional example implementations.
        """
        return {}

    ############################################################################
    # Collection methods

    def process_current_session(self, settings, parent_item):
        """
        This method analyzes the current engine session and creates a hierarchy
        of items for publishing.

        A typical implementation of this method would create an item that
        represents the current session (e.g. the current Maya file) or all open
        documents in a multi-document scenario (such as Photoshop). Top level
        items area created as children of the supplied ``parent_item``
        (a :ref:`publish-api-item` instance).

        Any additional items, specific to the current session, can then be
        created as children of the session item. This is not a requirement
        however. You could, for example, create a flat list of items, all
        sharing the same parent.

        The image below shows a Maya scene item with a child item that
        represents a playblast to be published. Each of these items has one or
        more publish tasks attached to them.

        .. image:: ./resources/collected_session_item.png

        |

        The ``settings`` argument is a dictionary where the keys are the names
        of the settings defined by the :func:`settings` property and the values
        are :ref:`publish-api-setting` instances as configured for this
        instance of the publish app.

        To create items within this method, use the
        :meth:`~.api.PublishItem.create_item` method available on the supplied
        ``parent_item``.

        Example Maya implementation:

        .. code-block:: python

            def process_current_session(settings, parent_item):

                path = cmds.file(query=True, sn=True)

                session_item = parent_item.create_item(
                    "maya.session",
                    "Maya Session",
                    os.path.basename(path)
                )

                # additional work here to prep the session item such as defining
                # an icon, populating the properties dictionary, etc.
                session_item.properties["path"] = path

                # collect additional file types, parented under the session
                self._collect_geometry(settings, session_item)

        .. note:: See the hooks defined in the publisher app's ``hooks/`` folder
           for additional example implementations.

        :param dict settings: A dictionary of configured
            :ref:`publish-api-setting` objects for this collector.
        :param parent_item: The root :ref:`publish-api-item` instance to
            collect child items for.
        """
        raise NotImplementedError

    def process_file(self, settings, parent_item, path):
        """
        This method creates one or more items to publish for the supplied file
        path.

        The image below shows a collected text file item to be published.

        .. image:: ./resources/collected_file.png

        |

        A typical implementation of this method involves processing the supplied
        path to determine what type of file it is and how to display it before
        creating the item to publish.

        The ``settings`` argument is a dictionary where the keys are the names
        of the settings defined by the :func:`settings` property and the values
        are :ref:`publish-api-setting` instances as
        configured for this instance of the publish app.

        To create items within this method, use the
        :meth:`~.api.PublishItem.create_item` method available on the supplied
        ``parent_item``.

        Example implementation:

        .. code-block:: python

            def process_file(settings, parent_item):

                # make sure the path is normalized. no trailing separator,
                # separators are appropriate for the current os, no double
                # separators, etc.
                path = sgtk.util.ShotgunPath.normalize(path)

                # do some processing of the file to determine its type, and how
                # to display it.
                ...

                # create and populate the item
                file_item = parent_item.create_item(
                    item_type,
                    type_display,
                    os.path.basename(path)
                )

                # additional work here to prep the session item such as defining
                # an icon, populating the properties dictionary, etc.
                session_item.properties["path"] = path

        .. note:: See the hooks defined in the publisher app's ``hooks/`` folder
           for additional example implementations.

        :param dict settings: A dictionary of configured
            :ref:`publish-api-setting` objects for this collector.
        :param parent_item: The root :ref:`publish-api-item` instance to
            collect child items for.
        """
        raise NotImplementedError
