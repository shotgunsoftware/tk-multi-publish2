
Collector
*********

The collector hook handles processing the current user’s session for items to
publish. It also handles processing any file paths that have been dragged and
dropped onto the Publisher. It’s primary purpose is to discover and classify
items to present to the user for publishing.

To define custom collection behavior for drag/drop or within a DCC, you simply
need to write a collector plugin or take over and modify one of the collectors
that come with the shipped integrations. For example, to allow publishing of
cameras in Maya, you could take over the Maya collector and add the logic for
creating publish items for each camera to be published in the current session.

----

Collector API
=============

.. py:currentmodule:: tk_multi_publish2.base_hooks

.. autoclass:: CollectorPlugin
    :show-inheritance:
    :members:
