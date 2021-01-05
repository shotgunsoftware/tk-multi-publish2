
Publish Customization
=====================

The sections below identify the entry points for customizing publish workflows.
For a broad overview of how publish execution works, see the
:ref:`publish-execution` doc.

.. _publish-collector:

Collector Hook
--------------

The collector hook handles processing the current user’s session to identify
what will be published. It also handles processing any file paths that have been
dragged/dropped onto the Publisher or added manually via the
:ref:`publish-api`. Once the collector identifies what is to be published,
:ref:`Publish Item <publish-api-item>` instances are created within the tree
and presented to the user.

.. note:: For more information on how to take over, subclass, and manage hooks,
    see the :ref:`Hooks <sgtk_hook_docs>` documentation.

----

Collector Hook API
__________________

.. py:currentmodule:: tk_multi_publish2.base_hooks
.. autoclass:: CollectorPlugin
    :show-inheritance:
    :members:


.. _publish-plugin:

Publish Plugin
--------------

Publish plugins are hooks that handle processing of collected publish items.
After all items have been collected, the Publisher attempts to match the items
with the appropriate publish plugins. All matched plugins show up as child tasks
within the publish item hierarchy.

With ``v2.0.0`` of the publisher and higher, each plugin can define a custom UI
that allows users to make changes to the publish settings prior to publishing.
See the methods and properties section below for details on how to implement a
custom publish plugin UI.

.. note:: For more information on how to take over, subclass, and manage hooks,
    see the :ref:`Hooks <sgtk_hook_docs>` documentation.

----

Publish Plugin API
__________________

.. py:currentmodule:: tk_multi_publish2.base_hooks
.. autoclass:: PublishPlugin
    :show-inheritance:
    :members:

Post Phase Hook
---------------

.. py:currentmodule:: tk_multi_publish2.base_hooks
.. autoclass:: PostPhaseHook
    :show-inheritance:
    :members:
