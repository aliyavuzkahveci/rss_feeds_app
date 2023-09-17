"""
# -----------------------------------------------------------------------------#
#                                                                              #
#                            Python script                                     #
#                                                                              #
# -----------------------------------------------------------------------------#
Description  :
Implementation of FeedProccessor base object

# -----------------------------------------------------------------------------#
#                                                                              #
#       Copyright (c) 2023 , Ali Yavuz Kahveci.                                #
#                         All rights reserved                                  #
#                                                                              #
# -----------------------------------------------------------------------------#
"""
from time import sleep

import structlog
import threading
import typing

from rss_feeds_backend.common.enums import FeedType
from rss_feeds_backend.database import insert_update_feed
from rss_feeds_backend.feed_processing.base.feed_collector import FeedCollector
from rss_feeds_backend.feed_processing.base.feed_extractor import FeedExtractor
from rss_feeds_backend.feed_processing.feed_collectors.rest_api_get import EMPTY_STR

LOGGER = structlog.get_logger()
DEFAULT_WAIT_INTERVAL = 30.0  # 5 minutes
FALLBACK_WAIT_INTERVALS = (120.0, 300.0, 480.0)  # 2, 5, 8 minutes


class FeedProcessor(threading.Thread):
    """Thread-based class to periodically retrieve feeds from an address."""

    def __init__(self, feed_address: str, feed_type: FeedType = FeedType.UNDEFINED) -> None:
        """
        Initializes the FeedProcessor object

        Args:
            feed_address: the address to the feed
            feed_type: the type of the feed
        """
        super().__init__()
        self.address: str = feed_address
        self.feed_type: FeedType = feed_type
        self.feed_collector: typing.Optional[FeedCollector] = None
        self.feed_extractor: typing.Optional[FeedExtractor] = None
        self.stop_requested: bool = False

    def assign_collector(self, feed_collector: FeedCollector) -> None:
        """
        Sets the feed_collector object to be used to extract the feed details from a content

        Args:
            feed_collector: collector object to be used for receiving the feed details
        """
        if self.feed_collector:
            LOGGER.info("Feed Collector has been set before...")
        self.feed_collector = feed_collector
        LOGGER.debug(f"FeedCollector '{self.feed_collector}' is set for feed address: '{self.address}'")

    def assign_extractor(self, feed_extractor: FeedExtractor) -> None:
        """
        Sets the feed_extractor object to be used to extract the feed details from a content

        Args:
            feed_extractor: extractor object to be used for extracting the feed details
        """
        if self.feed_extractor:
            LOGGER.info("Feed Extractor has been set before...")
        self.feed_extractor = feed_extractor
        LOGGER.debug(f"FeedExtractor '{self.feed_extractor}' is set for feed address: '{self.address}'")

    def stop(self) -> None:
        """Sets the member variable flag to stop execution"""
        self.stop_requested = True
        LOGGER.info(f"Feed Processor for address '{self.address}' is asked to stop its execution!")

    def run(self) -> None:
        """
        Periodically executes to get the feed from the feed source and extract the content
        """
        assert self.feed_collector, "Feed Collector member object has to be set before starting the execution"
        assert self.feed_extractor, "Feed Extractor member object has to be set before starting the execution"
        fallback_index = 0
        while not self.stop_requested and fallback_index <= len(FALLBACK_WAIT_INTERVALS):
            if self._refresh_feed():
                fallback_index = 0
                sleep(DEFAULT_WAIT_INTERVAL)
            else:
                LOGGER.warning(f"Feed refresh failed!")
                if fallback_index < len(FALLBACK_WAIT_INTERVALS):
                    LOGGER.info(f"Will retry again after {FALLBACK_WAIT_INTERVALS[fallback_index]}seconds")
                    sleep(FALLBACK_WAIT_INTERVALS[fallback_index])
                fallback_index = fallback_index + 1
        LOGGER.info("The execution of feed refresh is completing...")

    def force_refresh_feed(self) -> bool:
        """
        Forcefully starts the process of feed refresh

        Returns:
             True if feed is refreshed, False otherwise
        """
        if self.is_alive():
            LOGGER.warning(f"Feed Processor thread for address '{self.address}' is already running!")
            return False
        return self._refresh_feed()

    def _refresh_feed(self) -> bool:
        """
        Performs a feed retrieve

        Returns:
            True if feed is successfully retrieved and refreshed, False otherwise
        """
        feed_content: str = EMPTY_STR
        with self.feed_collector as fc_obj:
            if fc_obj.is_connection_available:
                feed_content = fc_obj.get_feed_content()
        if feed_content:
            LOGGER.info("Feed is retrieved successfully!")
            feed = self.feed_extractor.extract_feed(feed_content)
            if feed:
                LOGGER.info("Feed object is instantiated!")
                insert_update_feed(feed)
                return True
        return False
