
Publish Plugins
***************

Publish plugins are hooks that handle processing of collected publish items.
After all items have been collected, the Publisher attempts to match the items
with the appropriate publish plugins. All matched plugins show up as child tasks
within the publish item hierarchy.

With ``tk-multi-publish2 v2.0.0`` and higher, each plugin can define a custom UI
that allows users to make changes to the publish settings prior to publishing.
See the methods and properties section below for details on how to implement a
custom publish plugin UI.

Like the collectors, you can override one of the shipped publish plugins or
write your own to meet the particular needs of your studio.

----

Publish Plugin API
==================

.. py:currentmodule:: tk_multi_publish2.base_hooks

.. autoclass:: PublishPlugin
    :show-inheritance:
    :members:

----

Publish Items
=============

Publish items are the individual UI elements displayed to the user for
publishing. These items are created during the collection phase of the
publisher. Items can be displayed in a flat list for example when a collection
of unrelated files are dragged and dropped into the publisher. Alternatively,
items can be displayed in a hierarchy when it is important to show some
relationship between them.

.. py:currentmodule:: tk_multi_publish2.processing

.. autoclass:: Item
    :members:
    :exclude-members: __init__, tasks, add_task, is_root, remove_item, create_invisible_root_item

----

Settings
========

.. autoclass:: Setting
    :members: