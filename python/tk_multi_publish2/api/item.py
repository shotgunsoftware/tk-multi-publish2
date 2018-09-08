# Copyright (c) 2018 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from collections import defaultdict

import inspect
import os
import tempfile

import sgtk

from .data import PublishData
from .task import PublishTask

logger = sgtk.platform.get_logger(__name__)


class PublishItem(object):
    """
    The ``PublishItem`` class is used to represent something to be published.
    """

    @classmethod
    def from_dict(cls, item_dict, serialization_version, parent=None):
        """
        Create a publish item instance given the supplied dictionary. The
        supplied dictionary is typically the result of calling ``to_dict`` on
        a publish item instance during serialization.

        :param dict item_dict: A dictionary with the deserialized contents of
            a publish item.
        :param int serialization_version: The version of publish item
            serialization used for this item.
        :param parent: An optional parent to assign to this deserialized item.
        """

        # import here to avoid cyclic imports
        from .tree import PublishTree

        # This check is valid until we need to alter the way serialization is
        # handled after initial release. Once that happens, this should be
        # altered to handle the various versions separately with this as the
        # fallback when the serialization version is not recognized.
        if serialization_version != PublishTree.SERIALIZATION_VERSION:
            raise(
                "Unrecognized serialization version for serlialized publish "
                "item. It is unclear how this could have happened. Perhaps the "
                "serialized file was hand edited? Please consult your pipeline "
                "TD/developer/admin."
            )

        # create the instance
        new_item = PublishItem(
            item_dict["name"],
            item_dict["type_spec"],
            item_dict["type_display"]
        )

        # populate all the instance data from the dictionary
        new_item._active = item_dict["active"]
        new_item._allows_context_change = item_dict["allows_context_change"]
        new_item._description = item_dict["description"]
        new_item._enabled = item_dict["enabled"]
        new_item._expanded = item_dict["expanded"]
        new_item._icon_path = item_dict["icon_path"]
        new_item._thumbnail_enabled = item_dict["thumbnail_enabled"]
        new_item._thumbnail_explict = item_dict["thumbnail_explicit"]
        new_item._thumbnail_path = item_dict["thumbnail_path"]

        # create the children of this item
        for child_dict in item_dict["children"]:
            new_item._children.append(
                PublishItem.from_dict(
                    child_dict,
                    serialization_version,
                    parent=new_item
                )
            )

        # ---- handle the properties

        # global
        new_item._global_properties = PublishData.from_dict(
            item_dict["global_properties"])

        # local
        for (k, prop_dict) in item_dict["local_properties"].iteritems():
            new_item._local_properties[k] = PublishData.from_dict(prop_dict)

        new_item._parent = parent
        new_item._persistent = item_dict["persistent"]

        # set the context
        # TODO: would be nice to have a method in core to get a context from
        # see internal ticket: SG-7690
        # a dictionary.
        if item_dict["context"]:
            new_item._context = sgtk.Context(
                sgtk.platform.current_bundle().sgtk,
                **item_dict["context"]
            )

        # finally, create any tasks for this item
        for task_dict in item_dict["tasks"]:
            new_item._tasks.append(
                PublishTask.from_dict(
                    task_dict,
                    serialization_version,
                    item=new_item
                )
            )

        return new_item

    def __init__(self, name, type_spec, type_display, parent=None):
        """
        .. warning:: You should not create item instances directly. Instead, use
            the :meth:`~PublishItem.create_item` method of the parent you wish
            to create the item under.

        :param name: The display name of the item to create.
        :param type_spec: The type specification for this item.
        :param type_display: The type display string.
        :param parent: The parent item for this instance.
        """

        # NOTE: since this object is serializable, care should be taken to
        # ensure data is maintained between the `to_dict` and `from_dict`
        # methods.

        self._active = True
        self._allows_context_change = True
        self._children = []
        self._context = None
        self._created_temp_files = []
        self._description = None
        self._enabled = True
        self._expanded = True
        self._global_properties = PublishData()
        self._icon_path = None
        self._icon_pixmap = None
        self._local_properties = defaultdict(PublishData)
        self._name = name
        self._parent = parent
        self._persistent = False
        self._tasks = []
        self._thumbnail_enabled = True
        self._thumbnail_explicit = True
        self._thumbnail_path = None
        self._thumbnail_pixmap = None
        self._type_display = type_display
        self._type_spec = type_spec

    def __iter__(self):
        """
        Iteration implementation for this item.

        Allows for traversal of all subitems. Yields each of the item's
        descendants in depth-first order.
        """
        for item in self._traverse_item(self):
            yield item

    def __del__(self):
        """
        Destructor.
        """

        # clean up temp files created by this item
        for temp_file in self._created_temp_files:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception, e:
                    logger.warning(
                        "Could not remove temporary file '%s': %s" % (temp_file, e)
                    )
                else:
                    logger.debug("Removed temp file '%s'" % temp_file)

    def to_dict(self):
        """
        Returns a dictionary representation of the publish item. Typically used
        during serialization.
        """

        # For the global and local properties, the values are pickled allowing
        # more flexibility with respect to what is stored there. Clients can add
        # anything they want to these dictionaries. We document that this isn't
        # guaranteed to work if non-picklable objects are stored in items
        # properties, so it's up to them to be conscious of what goes in there.
        converted_local_properties = {}
        for (k, prop) in self._local_properties.iteritems():
            converted_local_properties[k] = prop.to_dict()

        context_value = None

        # check _context here to avoid traversing parent. if no context manually
        # assigned to the item, it will inherit it from the parent or current
        # bundle context on the other side of deserialization.
        # TODO: implement dict from context and context from dict methods in
        # core. see internal ticket: SG-7690
        if self._context:
            context_value = {
                "project": self._context.project,
                "entity": self._context.entity,
                "step": self._context.step,
                "task": self._context.task,
                "user": self._context.user,
                "additional_entities": self._context.additional_entities,
                "source_entity": self._context.source_entity,
            }

        # build the full dictionary representation of this item
        return {
            "active": self.active,
            "allows_context_change": self._allows_context_change,
            "children": [c.to_dict() for c in self._children],
            "context": context_value,
            "description": self.description,
            "enabled": self.enabled,
            "expanded": self.expanded,
            "global_properties": self._global_properties.to_dict(),
            "icon_path": self._icon_path,
            "local_properties": converted_local_properties,
            "name": self.name,
            "persistent": self.persistent,
            "tasks": [t.to_dict() for t in self._tasks],
            "thumbnail_enabled": self._thumbnail_enabled,
            "thumbnail_explicit": self._thumbnail_explicit,
            "thumbnail_path": self._thumbnail_path,
            "type_display": self.type_display,
            "type_spec": self.type_spec,
        }

    def __repr__(self):
        """Representation of the item as a string."""
        return "<%s: %s>" % (self.__class__.__name__, self._name)

    def __str__(self):
        """Human readable string representation of the item"""
        return "%s (%s)" % (self._name, self._type_display)

    def add_task(self, plugin):
        """
        Create a new publish task and attach it to this item.

        :param plugin: The plugin instance this task will represent/execute.
        """

        # create the task item and add it to the tree
        child_task = PublishTask(plugin, self)
        self._tasks.append(child_task)

        return child_task

    def clear_tasks(self):
        """
        Clear all tasks for this item.
        """
        self._tasks = []

    def create_item(self, type_spec, type_display, name):
        """
        Factory method for generating new items.

        The ``type_spec`` is a string that represents the type of the item. This
        can be any string, but is typically defined by studio convention. This
        value is used by the publish plugins to identify which items to act
        upon.

        The basic Shotgun integrations, for example, use a hierarchical dot
        notation such as: ``file.image``, ``file.image.sequence``,
        ``file.movie``, and ``maya.session``.

        The current convention used within the shipped integrations is to
        classify files that exist on disk as ``file.{type}`` (``file.image`` or
        ``file.video`` for example). This classification is determined from the
        mimetype in the base collector. In addition, any sequence-based items
        are classified as ``file.{type}.sequence`` (``file.image.sequence`` for
        example).

        For items defined within a DCC-session that must be save or exported
        prior to publish, the shipped integrations use the form ``{dcc}.{type}``
        for the primary session item and ``{dcc}.{type}.{subtype}`` for items
        within the session.

        In Maya, for example, the primary session item would be of type
        ``maya.session`` and an item representing all geomtery in the session
        would be ``maya.session.geometry``.

        These are merely conventions used in the shipped integrations and can be
        altered to meet studio requirements. It is recommended to look at each
        of the publish plugins shipped with the publisher and housed in each of
        the toolkit engines to see what item types are supported by default.

        The ``type_display`` argument corresponds to the item type, but is used
        for display purposes only.

        Examples include: ``Image File``, ``Movie File``, and ``Maya Scene``.

        The ``name`` argument is the display name for the item instance. This
        can be the name of a file or a item name in Nuke or Houdini, or a
        combination of both. This value is displayed to the user and should make
        it easy for the user to identify what the item represents in terms of
        the current session or a file on disk.

        .. image:: ./resources/create_item_args.png

        |

        :param str type_spec: Item type, typically following a hierarchical dot
            notation.
        :param str type_display: Equivalent to the type, but for display
            purposes.
        :param str name: The name to represent the item in a UI. This can be a
            item name in a DCC or a file name.
        """

        child_item = PublishItem(
            name,
            type_spec,
            type_display,
            parent=self
        )
        self._children.append(child_item)

        return child_item

    def get_property(self, name, default_value=None):
        """
        This is a convenience method that will retrieve a property set on the
        item.

        If the property was set via :py:attr:`~local_properties`, then that will
        be returned. Otherwise, the value set via :py:attr:`~properties` will be
        returned. If the property is not set on the item, then the supplied
        ``default_value`` will be returned (default is ``None``).

        :param name: The property to retrieve.
        :param default_value: The value to return if the property is not set on
            the item.

        :return: The value of the supplied property.
        """

        local_properties = self._get_local_properties()

        return local_properties.get(name) or self.properties.get(name) or \
            default_value

    def get_thumbnail_as_path(self):
        """
        Returns the item's thumbnail as a path to a file on disk. If the
        thumbnail was originally supplied as a file path, that path will be
        returned. If the thumbnail was created via screen grab or set directly
        via ``QtGui.QPixmap``, this method will generate an image as a temp file
        on disk and return its path.

        .. warning:: This property may return ``None`` if run without a UI
            present and no thumbnail path as been set on the item.

        :returns: Path to a file on disk or None if no thumbnail set
        """

        # nothing to do if running without a UI
        if not sgtk.platform.current_engine().has_ui:
            return None

        # the thumbnail path was explicitly provided
        if self._thumbnail_path:
            return self._thumbnail_path

        if self.thumbnail is None:
            return None

        temp_path = tempfile.NamedTemporaryFile(
            suffix=".jpg",
            prefix="sgtk_thumb",
            delete=False
        ).name
        success = self.thumbnail.save(temp_path)

        if success:
            if os.path.getsize(temp_path) > 0:
                self._created_temp_files.append(temp_path)
            else:
                logger.debug(
                    "A zero-size thumbnail was written for %s, "
                    "no thumbnail will be returned." % self.name
                )
                return None
            return temp_path
        else:
            logger.warning(
                "Thumbnail save to disk failed. No thumbnail will be returned "
                "for %s." % self.name
            )
            return None

    def remove_item(self, child_item):
        """
        Remove the supplied child :ref:`publish-api-item` of this item.

        :param child_item: The child :ref:`publish-api-item` to remove.
        """

        if child_item not in self.children:
            raise sgtk.TankError(
                "Unable to remove child item. Item %s is not a child of %s in "
                "the publish tree." % (child_item, self)
            )

        self._children = [i for i in self._children if i != child_item]

    def set_icon_from_path(self, path):
        """
        Sets the icon for the item given a path to an image on disk. This path
        will be converted to a ``QtGui.QPixmap`` when the item is displayed.

        .. note:: The :py:attr:`~icon` is for use only in the publisher UI and
            is a small representation of item being published. The icon should
            not be confused with the item's :py:attr:`~thumbnail` which is
            typically associated with the resulting published item in Shotgun.

        :param str path: Path to a file on disk
        """
        self._icon_path = path

    def set_thumbnail_from_path(self, path):
        """
        Sets the thumbnail for the item given a path to an image on disk. This
        path will be converted to a ``QtGui.QPixmap`` when the item is
        displayed.

        .. note:: The :py:attr:`~thumbnail` is typically associated with the
            resulting published item in Shotgun. The :py:attr:`~thumbnail`
            should not be confused with the item's :py:attr:`~icon` which is for
            use only in the publisher UI and is a small representation of the
            item.

        :param str path: Path to a file on disk
        """
        self._thumbnail_path = path

    @property
    def active(self):
        """
        Returns the item's active state if it has been explicitly set, `None``
        otherwise.

        .. note:: This property is shared with :py:attr:`~checked` and can be
            used interchangeably to make code more readable depending on the
            context (with/without the UI).

        """
        return self._active

    @active.setter
    def active(self, is_active):
        """
        Explicitly set the active state.

        There are 3 active states that can be supplied:

        * ``True``: Set the item to be active
        * ``False``: Set the item to be inactive
        * ``None``: Clear the item's state, rely on inheritance within the tree
        """
        self._active = is_active

    @property
    def checked(self):
        """
        Boolean property to indicate that this item should be checked by
        default when displayed in a publish UI.

        .. note:: This property is shared with :py:attr:`~active` and can be
            used interchangeably to make code more readable depending on the
            context (with/without the UI).

        Please note that the final state of the node is also affected by
        the child tasks. Below are some examples of how this interaction
        plays out in practice:

        - If all child tasks/items return ``checked: False`` in their accept
          method, the parent item will be unchecked, regardless
          of the state of this property.

        - If one or more child tasks return ``checked: True`` and the item
          checked state is False, the item and all its sub-items will be
          unchecked.
        """
        return self._active

    @checked.setter
    def checked(self, is_checked):
        # setter for checked
        self._active = is_checked

    @property
    def children(self):
        """
        A generator that yields the immediate :ref:`publish-api-item` children of
        this item.

        .. note:: :ref:`publish-api-item` instances are iterators so if you need
            to traverse all descendant items, you can do this:

            .. code-block:: python

                for descendant in item:
                    # process descendant item
        """
        for child in self._children:
            yield child

    @property
    def context(self):
        """
        The :class:`sgtk.Context` associated with this item.

        If no context has been explicitly set for this item, the context will be
        inherited from the item's parent. If none of this item's parents have
        had a context set explicitly, the publisher's launch context will be
        returned.
        """

        if self._context:
            return self._context
        elif self.parent:
            return self.parent.context
        else:
            return sgtk.platform.current_bundle().context

    @context.setter
    def context(self, item_context):
        """
        Explicitly set the context of the item.

        :param item_context:
        :return:
        """
        self._context = item_context

    @property
    def context_change_allowed(self):
        """
        ``True`` if item allows context change, False otherwise.

        Default is ``True``
        """
        return self._allows_context_change

    @context_change_allowed.setter
    def context_change_allowed(self, allow):
        """
        Enable/disable context change for this item.
        """
        self._allows_context_change = allow

    @property
    def description(self):
        """
        The description of the item if it has been explicitly set, ``None``
        otherwise.
        """
        return self._description

    @description.setter
    def description(self, new_description):
        """Sets a new description for the item with the given string."""
        self._description = new_description

    @property
    def enabled(self):
        """
        Boolean property which indicates whether this item and its children
        should be enabled within a publish UI.
        """
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        # setter for enabled
        self._enabled = enabled

    @property
    def expanded(self):
        """
        Boolean property which indicates whether this item should be expanded to
        show its children when shown in a publish UI.
        """
        return self._expanded

    @expanded.setter
    def expanded(self, is_expanded):
        """Setter for the expanded property."""
        self._expanded = is_expanded

    @property
    def icon(self):
        """
        The associated icon, as a QPixmap.

        The icon is a small square image used to represent the item visually

        .. image:: ./resources/item_icon.png

        |

        If no icon has been defined for this node, the parent icon is returned,
        or a default one if not defined

        .. warning:: This property will return ``None`` when run without a UI
            present

        .. note:: The :py:attr:`~icon` is for use only in the publisher UI and
            is a small representation of item being published. The icon should
            not be confused with the item's :py:attr:`~thumbnail` which is
            typically associated with the resulting published item in Shotgun.
        """
        # nothing to do if running without a UI
        if not sgtk.platform.current_engine().has_ui:
            return None

        # defer import until needed and to avoid issues when running without UI
        from sgtk.platform.qt import QtGui

        if self._icon_path and not self._icon_pixmap:
            # we have a path but haven't yet created the pixmap. create it
            try:
                self._icon_pixmap = QtGui.QPixmap(self._icon_path)
            except Exception, e:
                logger.warning(
                    "%r: Could not load icon '%s': %s" %
                    (self, self._icon_path, e)
                )

        if self._icon_pixmap:
            return self._icon_pixmap
        elif self.parent:
            return self.parent.icon
        else:
            # return default
            return QtGui.QPixmap(":/tk_multi_publish2/item.png")

    @icon.setter
    def icon(self, pixmap):
        """Sets the icon."""
        self._icon_pixmap = pixmap

    @property
    def is_root(self):
        """
        Returns ``True`` if this the root :ref:`publish-api-item` in the tree,
        ``False`` otherwise.
        """
        return self.parent is None and self.name == "__root__"

    @property
    def local_properties(self):
        """
        A :class:`~.api.PublishData` instance that houses item properties local
        to the current :class:`~.base_hooks.PublishPlugin` instance. As such, it
        is expected that this property is only accessed from within a publish
        plugin. Attempts to access this property outside of a publish plugin
        will raise an ``AttributeError``.

        This property behaves like the local storage in python's threading
        module, except here, the data is local to the current publish plugin.

        You can get and set values for this property using standard dictionary
        notation or via dot notation.

        It is important to consider when to set a value via
        :py:attr:`~properties`` and when to use :py:attr:`~local_properties`.

        Setting the values on :py:attr:`~properties` is a way to globally share
        information between publish plugins. Values set via
        :py:attr:`~local_properties` will only be applied during the execution
        of the current plugin (similar to python's ``threading.local`` storage).

        A common scenario to consider is when you have multiple publish plugins
        acting on the same item. You may, for example, want the ``publish_name``
        and ``publish_version`` properties to be shared by each plugin, while
        setting the remaining properties on each plugin instance since they will
        be specific to that plugin's output. Example:

        .. code-block:: python

            # set shared properties on the item (potentially in the collector or
            # the first publish plugin). these values will be available to all
            # publish plugins attached to the item.
            item.properties.publish_name = "Gorilla"
            item.properties.publish_version = "0003"

            # set specific properties in subclasses of the base file publish
            # (this class). first publish plugin...
            item.local_properties.publish_template = "asset_fbx_template"
            item.local_properties.publish_type = "FBX File"

            # in another publish plugin...
            item.local_properties.publish_template = "asset_abc_template"
            item.local_properties.publish_type = "Alembic Cache"

        .. note:: If you plan to serialize your publish tree, you may run into
            issues if you add complex or non-serializable objects to the
            properties dictionary.
        """
        return self._get_local_properties()

    @property
    def name(self):
        """The display name of the item."""
        return self._name

    @name.setter
    def name(self, new_name):
        """Sets a new display name for the item with the given string."""
        self._name = new_name

    @property
    def parent(self):
        """The item's parent :ref:`publish-api-item`."""
        return self._parent

    @property
    def persistent(self):
        """
        Boolean indicator that the item should not be removed when the tree is
        cleared.
        """
        return self._persistent

    @persistent.setter
    def persistent(self, is_persistent):
        """Set the item to persistent or not.

        Only top-level items can be set to persistent.
        """

        if not self.parent or not self.parent.is_root:
            raise sgtk.TankError(
                "Only top-level tree items can be made persistent.")

        self._persistent = is_persistent

    @property
    def properties(self):
        """
        A :class:`PublishData` instance where arbitrary data can be stored on
        the item. The property itself is read-only (you can't assign a different
        :class:`PublishData` instance.

        This property provides a way to store data that is global across all
        attached publish plugins. It is also useful for accessing data stored
        on parent items that may be useful to plugin attached to child items.

        For properties that are local to the current plugin, see
        :py:attr:`~local_properties`.

        This property can also be used to store data on an items that may then
        be accessed by plugins attached to the item's children.

        .. note:: If you plan to serialize your publish tree, you may run into
          issues if you add complex or non-serializable objects to the
          properties dictionary.
        """
        return self._global_properties

    @property
    def tasks(self):
        """
        Returns a list of all :ref:`publish-api-task` instances attached to
        this item.
        """
        return self._tasks

    @property
    def thumbnail(self):
        """
        The associated thumbnail, as a :class:`QtGui.QPixmap`.

        The thumbnail is an image to represent the item visually such as a
        thumbnail of an image or a screenshot of a scene.

        If no thumbnail has been defined for this node, the parent thumbnail is
        returned, or None if no thumbnail exists.

        .. warning:: This will property return ``None`` when run without a UI
            present

        .. note:: The :py:attr:`~thumbnail` is typically associated with the
            resulting published item in Shotgun. The :py:attr:`~thumbnail`
            should not be confused with the item's :py:attr:`~icon` which is for
            use only in the publisher UI and is a small representation of the
        """

        # nothing to do if running without a UI
        if not sgtk.platform.current_engine().has_ui:
            return None

        # defer import until needed and to avoid issues when running without UI
        from sgtk.platform.qt import QtGui

        if self._thumbnail_path and not self._thumbnail_pixmap:
            # we have a path but haven't yet created the pixmap. create it
            try:
                self._thumbnail_pixmap = QtGui.QPixmap(self._thumbnail_path)
            except Exception, e:
                logger.warning(
                    "%r: Could not load icon '%s': %s" %
                    (self, self._icon_path, e)
                )

        if self._thumbnail_pixmap:
            return self._thumbnail_pixmap
        elif self.parent:
            return self.parent.thumbnail
        else:
            return None

    @thumbnail.setter
    def thumbnail(self, pixmap):
        """Sets the thumbnail """
        self._thumbnail_pixmap = pixmap

    @property
    def thumbnail_enabled(self):
        """
        Boolean property to indicate whether thumbnails can be interacted with
        for items displayed in a publish UI.

        * If ``True``, thumbnails will be visible and editable in the publish UI
          (via screen capture).
        * If ``False`` and a thumbnail has been set via the
          :py:attr:`~thumbnail` property, the thumbnail will be visible but
          screen capture will be disabled.
        * If ``False`` and no thumbnail has been specified, no thumbnail will
          appear in the UI.
        """
        return self._thumbnail_enabled

    @thumbnail_enabled.setter
    def thumbnail_enabled(self, enabled):
        # setter for thumbnail_enabled
        self._thumbnail_enabled = enabled

    @property
    def thumbnail_explicit(self):
        """
        Boolean property to indicate that thumbnail has been explicitly set.
        When this flag is on, the summary thumbnail should be ignored for this
        this specific item.
        """
        return self._thumbnail_explicit

    @thumbnail_explicit.setter
    def thumbnail_explicit(self, enabled):
        """Setter for _thumbnail_explicit."""
        self._thumbnail_explicit = enabled

    @property
    def type_spec(self):
        """
        The type specification for this item. This specification typically
        follows a hierarchical dot notation. For example, 'file', 'file.image',
        or 'file.movie'. This allows for a system whereby some publish plugins
        act on 'file.*' items (publish to SG for example) while other plugins
        may perform actions on a more specific set of items (for example
        uploading the media represented by 'file.image' or 'file.movie' items to
        SG as Versions). This is how the default integrations use this property
        on collected items.
        """
        return self._type_spec

    @type_spec.setter
    def type_spec(self, new_type_spec):
        """Sets the type spec for this object."""
        self._type_spec = new_type_spec

    # leaving this as a property() definition because it is called 'type'.
    # don't want to risk bad mojo with python trying to define `def type`.
    def _get_type(self):
        """
        .. warning:: **DEPRECATED**.  Use :py:attr:`~type_spec` instead
        """
        return self.type_spec

    def _set_type(self, new_type_spec):
        self.type_spec = new_type_spec

    # leaving this for backward compatibility
    type = property(_get_type, _set_type)

    @property
    def type_display(self):
        """
        The display string for this item's type.
        """
        return self._type_display

    @type_display.setter
    def type_display(self, new_type_display):
        """Set the type display for this object."""
        self._type_display = new_type_display

    @property
    def display_type(self):
        """
        .. warning:: **DEPRECATED**.  Use :py:attr:`~type_display` instead
        """
        return self.type_display

    @display_type.setter
    def display_type(self, new_type_display):
        """DEPRECATED setter."""
        self.type_display = new_type_display

    ############################################################################
    # internal methods

    def _get_local_properties(self):
        """
        Return properties local to the currently executing publish plugin.

        This is done by walking up the call stack to find a caller that is a
        Hook. This method will raise if no caller in the stack is a hook.
        """

        hook_object = None

        for frame_record in inspect.stack():
            frame_object = frame_record[0]
            if frame_object:
                calling_object = frame_object.f_locals.get("self")
                if calling_object and isinstance(calling_object, sgtk.hook.Hook):
                    hook_object = calling_object

        if not hook_object:
            raise AttributeError(
                "Could not determine the current publish plugin when accessing "
                "an item's local properties. Item: %s" % (self,))

        if not hasattr(hook_object, 'id'):
            raise AttributeError(
                "Could not determine the id for this publish plugin. This is"
                "required for storing local properties. Plugin: %s" %
                (hook_object,)
            )

        plugin_id = hook_object.id

        return self._local_properties[plugin_id]

    def _traverse_item(self, item):
        """
        A recursive method for generating all items in the tree, depth-first.
        """

        # yield each child item
        for child_item in item.children:
            yield child_item

            # now recurse over the each child's children. the recursion will
            # yield  the grand children back to this method. we need to yield
            # these back to the calling method. in later versions of python, the
            # `yield from` could be used to make this cleaner/clearer
            for grandchild_item in self._traverse_item(child_item):
                yield grandchild_item
