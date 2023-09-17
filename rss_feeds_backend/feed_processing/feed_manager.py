"""
# -----------------------------------------------------------------------------#
#                                                                              #
#                            Python script                                     #
#                                                                              #
# -----------------------------------------------------------------------------#
Description  :
Implementation of FeedManager class

# -----------------------------------------------------------------------------#
#                                                                              #
#       Copyright (c) 2023 , Ali Yavuz Kahveci.                                #
#                         All rights reserved                                  #
#                                                                              #
# -----------------------------------------------------------------------------#
"""
import typing

import structlog

from rss_feeds_backend.common.enums import FeedType
from rss_feeds_backend.feed_processing.base.feed_processor import FeedProcessor
from rss_feeds_backend.feed_processing.feed_factory import FeedFactory

LOGGER = structlog.get_logger()


class FeedManager:
    """Manager class to keep FeedProcessor objects and manager their lifecycle"""

    def __init__(self) -> None:
        """Initializes the FeedManager object"""
        self.feed_processor_list: typing.List[FeedProcessor] = []  # start with empty list!

    def stop_all_processors(self) -> None:
        """Stops all the running FeedProcessors"""
        for fp_obj in self.feed_processor_list:
            fp_obj.stop()
        for fp_obj in self.feed_processor_list:
            fp_obj.join()  # wait for threads to finish their execution!

    def define_new_feed_processor(self, feed_link: str, feed_type: FeedType) -> None:
        """
        Creates a new FeedProcessor object and starts execution

        Args:
            feed_link: the address of the feed source
            feed_type: the type of the feed
        """
        fp_obj = FeedProcessor(feed_address=feed_link, feed_type=feed_type)
        fp_obj.assign_collector(FeedFactory.initialize_feed_collector(feed_url=feed_link))
        fp_obj.assign_extractor(FeedFactory.initialize_feed_extractor(feed_type=feed_type))
        fp_obj.start()
        self.feed_processor_list.append(fp_obj)

    def _check_feed_exists(self, feed_link: str) -> bool:
        """
        Iterates over the feed list to check if the candidate feed is already in the list

        Args:
            feed_link: the address to the feed source

        Returns:
            True if feed exists, False otherwise
        """
        for fp_obj in self.feed_processor_list:
            if fp_obj.address == feed_link:
                LOGGER.info(f"A FeedProcessor for link '{feed_link}' already exists in the list!")
                return True
        LOGGER.info(f"There is no FeedProcessor for link '{feed_link}'")
        return False
