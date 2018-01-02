
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
