"""
# -----------------------------------------------------------------------------#
#                                                                              #
#                            Python script                                     #
#                                                                              #
# -----------------------------------------------------------------------------#
Description  :
Implementation of FeedExtractor base class

# -----------------------------------------------------------------------------#
#                                                                              #
#       Copyright (c) 2023 , Ali Yavuz Kahveci.                                #
#                         All rights reserved                                  #
#                                                                              #
# -----------------------------------------------------------------------------#
"""
import abc
import typing

from rss_feeds_backend.common.enums import FeedType
from rss_feeds_backend.db_models.feed import Feed

DEFAULT_TITLE = "Title Could Not Be Found"
DEFAULT_DESCRIPTION = "There is no Description in this Feed"
DEFAULT_TTL = -1


class FeedExtractor(abc.ABC):
    """Base class to perform extraction of feed details and posts from a feed content"""

    def __init__(self, feed_type: FeedType) -> None:
        """
        Initialize the FeedExtractor class with the provided parameters.

        Args:
            feed_type: the type of the feed to collect
        """
        self.feed_type = feed_type

    @abc.abstractmethod
    def extract_feed(self, feed_content: str) -> typing.Optional[Feed]:
        """
        Goes over the feed content and extracts the feed info with posts

        Args:
            feed_content: the feed content in string

        Returns:
            Feed object containing the list of posts and other feed details
        """
