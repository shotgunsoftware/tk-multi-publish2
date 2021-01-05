
Utilities
*********

The publisher provides some utility methods that are generally useful for
writing publish plugins that aren't driven by templates. These methods are used
by the basic Shotgun integration to infer information from file paths when
templates are not available. This includes version and frame number
identification, publish display name, image sequence paths, etc.

.. note:: These utility methods are exposed via the publisher's ``util`` module,
   but the implementation for most of them lives within the app's ``path_info``
   hook. Studios can override these path processing methods to account for their
   own naming conventions and path structures.

The utilty method are documented below:

.. automodule:: tk_multi_publish2.util
    :members:
    :exclude-members: get_conflicting_publishes, clear_status_for_conflicting_publishes
