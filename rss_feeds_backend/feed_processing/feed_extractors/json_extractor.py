"""
# -----------------------------------------------------------------------------#
#                                                                              #
#                            Python script                                     #
#                                                                              #
# -----------------------------------------------------------------------------#
Description  :
Implementation of JsonExtractor class

# -----------------------------------------------------------------------------#
#                                                                              #
#       Copyright (c) 2023 , Ali Yavuz Kahveci.                                #
#                         All rights reserved                                  #
#                                                                              #
# -----------------------------------------------------------------------------#
"""
import typing

from rss_feeds_backend.common.enums import FeedType
from rss_feeds_backend.db_models.feed import Feed
from rss_feeds_backend.feed_processing.base.feed_extractor import FeedExtractor


class JsonExtractor(FeedExtractor):
    """class to perform extraction of feed details and posts from a JSON feed content"""

    def __init__(self) -> None:
        """
        Initialize the JsonExtractor class with the provided parameters.
        """
        super().__init__(feed_type=FeedType.JSON)

    def extract_feed(self, feed_content: str) -> typing.Optional[Feed]:
        """
        Goes over the feed content and extracts the feed info with posts

        Args:
            feed_content: the feed content in string

        Returns:
            Feed object containing the list of posts and other feed details
        """