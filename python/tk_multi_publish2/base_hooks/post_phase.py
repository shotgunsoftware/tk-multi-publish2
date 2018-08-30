# Copyright (c) 2018 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk

HookBaseClass = sgtk.get_hook_baseclass()


class PostPhaseHook(HookBaseClass):
    """
    This hook defines methods that are executed after each phase of a publish:
    validation, publish, and finalization. Each method receives the publish
    tree instance being used by the publisher, giving full control to further
    curate the publish tree including the publish items and the tasks attached
    to them. See the :class:`PublishTree` documentation for additional details
    on how to traverse the tree and manipulate it.
    """

    def post_validate(self, publish_tree, failed_to_validate):
        """
        This method is executed after the validation pass has completed for each
        item in the tree.

        A :class:`~PublishTree` instance representing the items to publish, and
        their associated tasks, is supplied as an argument. The tree can be
        traversed in this method to inspect the items and tasks and process them
        collectively. The instance can also be used to save the state of the
        tree to disk for execution later or on another machine.

        A list of items that failed to validate is also supplied. For additional
        details on why validation failed for an item, you can customize the
        publish plugins to store information in the item's properties and then
        access that information here.

        For example:

        .. code-block:: python

            # in the publish plugin...
            item.properties.validation_failed_because = "File is empty."

            # in post_validate...
            for item in failed_to_validate:
                reason = item.properties.validation_failed_because

        The return value of this method can be used to override the results of
        the individual item validations. By returning ``True``, the method will
        indicate that validation was successful (even if some items failed to
        validate). Conversely, by returning ``False``, the method will indicate
        to the publisher that validation has failed and halt further execution.

        :param publish_tree: The :class:`~PublishTree` instance representing
            the items to be published.
        :param list failed_to_validate: A list of :class:`~PublishItem`
            instances representing all items that failed to validate.

        :return: ``True`` if validation was successful, ``False`` otherwise.
        """
        self.logger.debug("Executing post validate hook method...")

        # by default, return True if all items validated
        return not failed_to_validate

    def post_publish(self, publish_tree):
        """
        This method is executed after the publish pass has completed for each
        item in the tree, before the finalize pass.

        A :class:`~PublishTree` instance representing the items that were
        published is supplied as an argument. The tree can be traversed in this
        method to inspect the items and process them collectively.

        Studios can override this method to process the publishes collectively
        prior to any cleanup that happens in the finalize pass.

        :param publish_tree: The :class:`~PublishTree` instance representing
            the items to be published.
        """
        self.logger.debug("Executing post publish hook method...")

    def post_finalize(self, publish_tree):
        """
        This method is executed after the finalize pass has completed for each
        item in the tree.

        A :class:`~PublishTree` instance representing the items that were
        published and finalized is supplied as an argument. The tree can be
        traversed in this method to inspect the items and process them
        collectively.

        Studios can override this method to process the publishes collectively
        after any cleanup that happens in the finalize pass.

        :param publish_tree: The :class:`~PublishTree` instance representing
            the items to be published.
        """
        self.logger.debug("Executing post finalize hook method...")
