.. _publish-api:

Publish API
===========

The publish API gives developers access to the underlying data structures and
methods used by the publish UI. They can use this interface to build more
advanced custom publish workflows.

The primary interface to the API is the :ref:`publish-api-manager` class which
exposes the same ``collection``, ``validation``, ``publish``, and ``finalize``
methods that drive the Publisher UI. The manager contains a reference to a
:ref:`publish-api-tree` instance that operates on the hierarchy of
:ref:`publish-api-item` instances (the "things" to be published), each of which
can have associated :ref:`publish-api-task` instances that define how the
items are to be processed.

The code below shows how to execute a complete publish using this API:

.. code-block:: python

    # need to have an engine running in a context where the publisher has been
    # configured.
    engine = sgtk.platform.current_engine()

    # get the publish app instance from the engine's list of configured apps
    publish_app = engine.apps.get("tk-multi-publish2")

    # ensure we have the publisher instance.
    if not publish_app:
        raise Exception("The publisher is not configured for this context.")

    # create a new publish manager instance
    manager = publish_app.create_publish_manager()

    # now we can run the collector that is configured for this context
    manager.collect_session()

    # collect some external files to publish
    manager.collect_files([path1, path2, path3])

    # validate the items to publish
    tasks_failed_validation = manager.validate()

    # oops, some tasks are invalid. see if they can be fixed
    if tasks_failed_validation:
        fix_invalid_tasks(tasks_failed_validation)
        # try again here or bail

    # all good. let's publish and finalize
    try:
        manager.publish()
        # If a plugin needed to version up a file name after publish
        # it would be done in the finalize.
        manager.finalize()
    except Exception as error:
        logger.error("There was trouble trying to publish!")
        logger.error("Error: %s", error)

See the documentation for each of these classes below for more detail on how
to use them.

.. _publish-api-manager:

PublishManager
--------------

This class gives developers direct access to the same methods and data
structures used by the Publish UI. You can create an instance of this class
directly via the configured publish app like this:

.. code-block:: python

    # need to have an engine running in a context where the publisher has been
    # configured.
    engine = sgtk.platform.current_engine()

    # get the publish app instance from the engine's list of configured apps
    publish_app = engine.apps.get("tk-multi-publish2")

    # ensure we have the publisher instance.
    if not publish_app:
        raise Exception("The publisher is not configured for this context.")

    # create a new publish manager instance
    manager = publish_app.create_publish_manager()

.. py:currentmodule:: tk_multi_publish2.api

.. autoclass:: PublishManager
    :members:

.. _publish-api-tree:

PublishTree
-----------

.. py:currentmodule:: tk_multi_publish2.api

.. autoclass:: PublishTree
    :members:
    :exclude-members: __init__, from_dict, to_dict, save, load,

.. _publish-api-item:

PublishItem
-----------

.. py:currentmodule:: tk_multi_publish2.api

.. autoclass:: PublishItem
    :members:
    :exclude-members: __init__, add_task, to_dict, from_dict, clear_tasks

.. _publish-api-task:

PublishTask
-----------

.. py:currentmodule:: tk_multi_publish2.api
.. autoclass:: PublishTask
    :members:
    :exclude-members: from_dict, to_dict, __init__, is_same_task_type, publish, finalize, validate, plugin

.. _publish-api-data:

PublishData
-----------

.. py:currentmodule:: tk_multi_publish2.api
.. autoclass:: PublishData
    :members:
    :exclude-members: to_dict, from_dict, __init__
    :show-inheritance:

.. _publish-api-setting:

PluginSetting
-------------

.. py:currentmodule:: tk_multi_publish2.api
.. autoclass:: PluginSetting
    :members:
    :show-inheritance:
