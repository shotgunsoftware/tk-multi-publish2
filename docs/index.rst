Shotgun Publisher API reference, |release|
##########################################

Overview
********

The Publish app is a highly customizable workflow tool that allows studios to
track the data being created by artists and control how it is shared. The app
can be modified for studio-specific needs by way of hooks that control how items
are identified for presentation to artists for publishing and how those items
are then processed.

The graphic below outlines the major concepts of the publish2 app and API. The
links on the left can be used to examine each of these concepts in detail.

----

.. image:: ./resources/publish_overview.png

----

The underlying API used by the publish UI is also available to studios for
more advanced use cases such as studio-specific publish interfaces or deferred
processing of publish items. See the :ref:`publish-api` section for more
information.

The following sections outline all of the hooks and APIs available to studios
for publish workflow building and customization.

.. toctree::
    :maxdepth: 2

    execution
    customizing
    api
    logging
    utility
    application
