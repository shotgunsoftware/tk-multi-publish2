Hooks
=====

Apart from the core collector and publish plugin hooks and settings, many other
parts of the publishing process and GUI can be customized by defining and extending
various hook configurations. The specifications are defined in the ``info.yml``
file at the root of the code repository.


Publishing
----------

.. code-block:: yaml
    :caption: info.yml

    post_phase:
        type: hook
        description:
          "A hook that defines logic to be executed after each phase of publish
          execution including validation, publish, and finalization. This allows
          for very specific curation and customization of the publish tree
          during a publish session. Serializing the publish tree to disk after
          validation, for example is possible via this hook."
        default_value: "{self}/post_phase.py"

    pre_publish:
        type: hook
        description:
          "This hook defines logic to be executed before showing the publish
          dialog. There may be conditions that need to be checked before allowing
          the user to proceed to publishing."
        default_value: "{self}/pre_publish.py"

    path_info:
        type: hook
        description:
          "This hook contains methods that are used during publishing to infer
           information from file paths. This includes version and frame number
           identification, publish display name, image sequence paths, etc."
        default_value: "{self}/path_info.py"

    thumbnail_generator:
        type: hook
        description:
          "This hook contains methods that are used during publishing to auto
          generate a thumbnail from the file being published."
        default_value: "{self}/thumbnail_generator.py"

GUI
---

For basic GUI customizations, these configurations can be used/modified:

.. code-block:: yaml
    :caption: info.yml

    display_name:
        type: str
        default_value: Publish
        description: Specify the name that should be used in menus and the main
                     publish dialog

    display_action_name:
        type: str
        default_value: Publish
        description: "Shorter version of display_name setting, used as button name."


Display Hook and Settings
^^^^^^^^^^^^^^^^^^^^^^^^^

.. versionadded:: v2.x.x

When more advanced GUI customizations are needed, the ``display`` configuration
can be used to extend and customize the display hook and any settings to feed into
it.

.. code-block:: yaml
    :caption: info.yml

    display:
        type: dict
        description: Hook and settings that implements the values of various GUI
                     elements of the publish dialog such as window title, menu name
                     that launches the dialog, button label, etc.
        items:
            hook: {type: hook}
            settings: {type: dict, allows_empty: True}
        default_value:
            hook: "{self}/display_hook.py"
            settings: {}

By default, it uses the values from ``display_name`` and ``display_action_name``
configurations across various menu text, window title, button label, etc.

These can all be overridden as much as needed. The ``display:settings`` values
are free for developers to define and use as they see fit for their custom
``display:hook`` implementations.

Here is an exaggerated simple example where each part are defined via custom
``display:settings``, except ``menu_properties()`` which remains inherited from the
default ``{self}/display_hook.py``.

.. code-block:: yaml
    :caption: Example tk-config-default2/env/includes/settings/tk-multi-publish2.yml
    :emphasize-lines: 11-19

    settings.tk-multi-publish2.standalone:
      collector: "{self}/collector.py"
      publish_plugins:
      - name: Publish to Flow Production Tracking
        hook: "{self}/publish_file.py"
        settings: {}
      - name: Upload for review
        hook: "{self}/upload_version.py"
        settings: {}
      help_url: *help_url
      display:
        hook:
          "{self}/display_hook.py\
          :{config}/hooks/tk-multi-publish2/display_hook.py"
        settings:
          action_name: Verb
          button_name: Click Me
          window_title: I'm Here
          menu_name: Publish Stuff
      location: "@apps.tk-multi-publish2.location"

.. code-block:: python
    :caption: Example tk-config-default2/hooks/tk-multi-publish2/display_hook.py

    import sgtk

    HookBaseClass = sgtk.get_hook_baseclass()


    class SettingsBasedDisplayHook(HookBaseClass):
        """Hook that defines how the action to show the publish dialog is displayed."""

        @property
        def action_name(self) -> str:
            """Text (verb) used when referring to the _Publish_ action in the GUI."""
            return self.settings["action_name"]

        @property
        def button_name(self) -> str:
            """Label text used for the _Publish_ button."""
            return self.settings["button_name"]

        @property
        def window_title(self) -> str:
            """Window title used for `.Engine.show_modal`/`.Engine.show_dialog`."""
            return self.settings["window_title"]

        @property
        def menu_name(self) -> str:
            """Command name used when registering the show dialog command to menus."""
            return self.settings["menu_name"]
