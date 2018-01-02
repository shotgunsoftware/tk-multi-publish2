Publish Execution
=================

The publisher has several phases of execution that developers should be aware
of before implementing custom publishing workflows.

Collection & Acceptance
-----------------------

When the Publisher is launched, items for the current user session are collected
via the collector hook. The :meth:`~.CollectorPlugin.process_current_session`
method of the configured collector plugin will be executed.

Similarly, if the user drags and drops external files, or browses external files
via the file browser, the collector plugin's
:meth:`~.CollectorPlugin.process_file` method will be executed.

These methods will create items to be displayed in the Publisher interface.
These items represent the "things" to be published.

Before the collected items are showing in the UI however, they will be processed
for acceptance. Each configured publish plugin will have a chance to accept each
collected item.

This acceptance phase has two tiers. The first tier is done by comparing the
collected item's type to a list of filters provided by the publish plugin. If
the item's type matches one of the plugin's filters, the second tier of
acceptance is executed by running the publish plugin's
:meth:`~.PublishPlugin.accept` method.

All collected items will display one or more publish plugins that accepted them
as tasks to be executed in the interface. These will show up as child items in
the UI. Each of these tasks represents an instance of the associated
publish plugin. Conceptually, these are the "actions" to be performed on the
items.

Item Review
-----------

Once the acceptance phase is complete, the user can review the items, make
changes to the target context of each, provide publish descriptions, take screen
grabs, and update settings. Additional files can be dragged and dropped or
browsed for collection.

Publishing
----------

After the artist had taken the time to review the collected items, they can
perform one of two actions.

#. They can run a validation pass on the items. This will execute the
   :meth:`~.PublishPlugin.validate` method on each publish plugin in the list
   in the order in which they are displayed, passing in their parent item as
   the item to process. Any errors or warnings logged during this phase will be
   displayed in the UI.
#. The user can also decide to run the full publish pass. This will include all
   the validation steps above followed by execution of each plugin's
   :meth:`~.PublishPlugin.publish` and :meth:`~.PublishPlugin.finalize` methods.
   The publisher will execute the ``publish`` method of each task, followed by
   the execution of each task's ``finalize`` method. Again, the order will match
   the order of tasks in the interface.
