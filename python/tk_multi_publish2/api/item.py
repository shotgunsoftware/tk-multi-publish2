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

import sgtk

from .data import PublishData
from .task import PublishTask

logger = sgtk.platform.get_logger(__name__)


class PublishItem(object):
    """
    Items represent a "thing" to be operated on. This can be a file on disk
    or an object of some type in an artist's session.
    """

    @classmethod
    def from_dict(cls, item_dict, parent=None):
        """
        Create a publish item instance given the supplied dictionary. The
        supplied dictionary is typically the result of calling ``to_dict`` on
        a publish item instance during serialization.
        """

        new_item = PublishItem(
            item_dict["name"],
            item_dict["type_spec"],
            item_dict["type_display"]
        )

        new_item._active = item_dict["active"]
        new_item._description = item_dict["description"]

        for child_dict in item_dict["children"]:
            new_item._children.append(
                PublishItem.from_dict(child_dict, parent=new_item)
            )

        new_item._global_properties = PublishData(
            **item_dict["global_properties"])

        for (k, prop_dict) in item_dict["local_properties"].iteritems():
            new_item._local_properties[k] = PublishData(**prop_dict)

        new_item._parent = parent

        new_item._persistent = item_dict["persistent"]

        if item_dict["context"]:
            new_item._context = sgtk.Context(
                sgtk.platform.current_bundle().sgtk,
                **item_dict["context"]
            )

        for task_dict in item_dict["tasks"]:
            new_item._tasks.append(
                PublishTask.from_dict(task_dict, item=new_item)
            )

        return new_item

    def __init__(self, name, type_spec, type_display, parent=None):
        """
        Initialize an item in the tree.

        :param name: The display name of the item to create.
        :param type_spec: The type specification for this item.
        :param type_display: The type display string.

        NOTE: Items store an explicit state that may not represent its actual
        state within the overall publish tree. For example, if no ``context``
        has been set on the item, it will be inherited from its parent in the
        publish tree.
        """

        # NOTE: since this object is serializable, any members added should be
        # simple python types or serializable objects.

        # These members are common to all tree items.
        self._active = True
        self._children = []
        self._context = None
        self._description = None
        self._global_properties = PublishData()
        self._local_properties = defaultdict(PublishData)
        self._name = name
        self._parent = parent
        self._persistent = False
        self._tasks = []
        self._type_display = type_display
        self._type_spec = type_spec

    def __iter__(self):
        """Iterates over the item's descendents, depth first."""

        for item in self._traverse_item(self):
            yield item

    def to_dict(self):
        """
        Returns a dictionary representation of the publish item. Typically used
        during serialization.
        """

        converted_local_properties = {}
        for (k, prop) in self._local_properties.iteritems():
            converted_local_properties[k] = prop.to_dict()

        context_value = None
        # check _context here to avoid traversing parent. if no context manually
        # assigned to the item, it will inherit it from the parent or current
        # bundle context on deserialize.
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

        return {
            "active": self.active,
            "children": [c.to_dict() for c in self._children],
            "context": context_value,
            "description": self.description,
            "global_properties": self._global_properties.to_dict(),
            "local_properties": converted_local_properties,
            "name": self.name,
            "persistent": self.persistent,
            "tasks": [t.to_dict() for t in self._tasks],
            "type_display": self.type_display,
            "type_spec": self.type_spec,
        }

    def __repr__(self):
        """Representation of the item as a string."""
        return "<%s: %s>" % (self.__class__.__name__, self._name)

    def __str__(self):
        """Human readable string representation of the item"""
        return "%s (%s)" % (self._name, self._type_display)

    def remove_child(self, child_item):
        """
        Remove the supplied child of this item.

        :param child_item: The child item to remove from the current item.
        """

        if child_item not in self.children:
            raise sgtk.TankError(
                "Unable to remove child item. Item %s is not a child of %s in "
                "the publish tree." % (child_item, self)
            )

        self._children = [i for i in self._children if i != child_item]

    def create_item(self, item_type, display_type, name):
        """
        Factory method for generating new items.

        The ``item_type`` is a string that represents the type of the item. This
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

        The ``display_type`` argument corresponds to the item type, but is used
        for display purposes only.

        Examples include: ``Image File``, ``Movie File``, and ``Maya Scene``.

        The ``name`` argument is the display name for the item instance. This
        can be the name of a file or a item name in Nuke or Houdini, or a
        combination of both. This value is displayed to the user and should make
        it easy for the user to identify what the item represents in terms of
        the current session or a file on disk.

        .. image:: ./resources/create_item_args.png

        |

        :param str item_type: Item type, typically following a hierarchical dot
            notation.
        :param str display_type: Equivalent to the type, but for display
            purposes.
        :param str name: The name to represent the item in a UI. This can be a
            item name in a DCC or a file name.
        """

        child_item = PublishItem(
            name,
            item_type,
            display_type,
            parent=self
        )
        self._children.append(child_item)

        return child_item

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

    def get_property(self, name, default_value=None):
        """
        This is a convenience method that will retrieve a property set on the
        item.

        If the property was set via :meth:`PublishItem.local_properties`, then
        that will be returned. Otherwise, the value set via
        :meth:`Item.properties` will be returned. If the property is not set on
        the item, then the supplied ``default_value`` will be returned (default
        is ``None``).

        :param name: The property to retrieve.
        :param default_value: The value to return if the property is not set on
            the item.

        :return: The value of the supplied property.
        """

        local_properties = self._get_local_properties()

        return local_properties.get(name) or self.properties.get(name) or \
            default_value

    @property
    def active(self):
        """
        Returns the item's active state if it has been explicitly set, `None``
        otherwise
        """
        return self._active

    @active.setter
    def active(self, active_state):
        """
        Explicitly set the active state.

        There are 3 active states that can be supplied:

        * ``True``: Set the item to be active
        * ``False``: Set the item to be inactive
        * ``None``: Clear the item's state, rely on inheritance within the tree
        """
        self._active = active_state

    @property
    def children(self):
        """Return the children of this item."""
        return self._children

    @property
    def context(self):
        """
        Returns the context of the item if it has been explicitly set, ``None``
        otherwise.
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
    def description(self):
        """
        The description of the item if it has been explicitly set,
        ``None`` otherwise.
        """
        return self._description

    @description.setter
    def description(self, new_description):
        """Sets a new description for the item with the given string."""
        self._description = new_description

    @property
    def is_root(self):
        """Returns ``True`` if this item is the root, ``False`` otherwise."""
        return self.parent is None and self.name == "__root__"

    @property
    def local_properties(self):
        """
        A :class:`PublishData` instance that houses item properties local to
        the current publish plugin instance. As such, it is expected that this
        property is only accessed from within a publish plugin. Attempts to
        access this property outside of a publish plugin will raise an
        ``AttributeError``.

        This property behaves like the local storage in python's threading
        module, except here, the data is local to the current publish plugin.

        You can get and set values for this property using standard dictionary
        notation or via dot notation.

        It is important to consider when to set a value via
        :meth:`Item.properties`` and when to use :meth:`Item.local_properties`.
        Setting the values on ``item.properties`` is a way to globally share
        information between publish plugins. Values set via
        ``item.local_properties`` will only be applied during the execution of
        the current plugin (similar to python's ``threading.local`` storage).

        A common scenario to consider is when you have multiple publish plugins
        acting on the same item. You may, for example, want the ``publish_name``
        and ``publish_version`` to be shared by each plugin, while setting the
        remaining properties on each plugin instance since they will be specific
        to that plugin's output.

        Example::

            # set shared properties on the item (potentially in the collector or
            # the first publish plugin). these values will be available to all
            # publish plugins attached to the item.
            item.properties.publish_name = "Gorilla"
            item.properties.publish_version = "0003"

            # set specific properties in subclasses of the base file publish (this
            # class). first publish plugin...
            item.local_properties.publish_template = "asset_fbx_template"
            item.local_properties.publish_type = "FBX File"

            # in another publish plugin...
            item.local_properties.publish_template = "asset_abc_template"
            item.local_properties.publish_type = "Alembic Cache"
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
        """The item's parent item."""
        return self._parent

    @property
    def persistent(self):
        """Indicates if the item should be removed when the tree is cleared."""
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
        ``PublishData`` instance.

        This property provides a way to store data that is global across all
        attached publish plugins. It is also useful for accessing data stored
        on parent items that may be useful to plugin attached to child items.

        For properties that are local to the current plugin, see
        ``local_properties``.

        This property can also be used to store data on an items that may then
        be accessed by plugins attached to the item's children.
        """
        return self._global_properties

    @property
    def tasks(self):
        """Returns a list of all tasks attached to this item."""
        return self._tasks

    @property
    def type_spec(self):
        """
        The type specification for this item. This specification follows a
        hierarchical dot notation. For example, 'file', 'file.image',
        'file.quicktime' or 'maya_scene'. This specification is up to the client
        code to define in terms of formatting and meaning.
        """
        return self._type_spec

    @property
    def type_display(self):
        """
        The display string for this item's type.
        """
        return self._type_display

    def _get_local_properties(self):
        """
        Return properties local to the currently executing publish plugin.

        This is done in a separate method to allow access to any method in this
        class. We look 2 levels up in the stack to get the calling plugin class.
        If this is called more than one level deep in this class, expect issues.
        """

        # TODO: walk up the stack to see if this is called by a hook

        # try to determine the current publish plugin
        calling_object = inspect.stack()[2][0].f_locals.get("self")

        if not calling_object or not isinstance(calling_object, sgtk.hook.Hook):
            raise AttributeError(
                "Could not determine the current publish plugin when accessing "
                "an item's local properties. Item: %s" % (self,))

        if not hasattr(calling_object, 'id'):
            raise AttributeError(
                "Could not determine the id for this publish plugin. This is"
                "required for storing local properties. Plugin: %s" %
                (calling_object,)
            )

        plugin_id = calling_object.id

        if plugin_id not in self._local_properties:
            self._local_properties[plugin_id] = PublishData()

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

    # TODO: consider these when we get to the UI portion. we can't remove them
    # because we don't want to break the API, but we need to figure how how they
    # make sense without a UI in play.
    def set_icon_from_path(self, path):
        pass

    def set_thumbnail_from_path(self, path):
        pass

    def get_thumbnail_as_path(self):
        return None


