"""
# -----------------------------------------------------------------------------#
#                                                                              #
#                            Python script                                     #
#                                                                              #
# -----------------------------------------------------------------------------#
Description  :
Implementation of FeedFactory class

# -----------------------------------------------------------------------------#
#                                                                              #
#       Copyright (c) 2023 , Ali Yavuz Kahveci.                                #
#                         All rights reserved                                  #
#                                                                              #
# -----------------------------------------------------------------------------#
"""
import typing
from types import MappingProxyType

import structlog

from rss_feeds_backend.common.enums import FeedType, FeedSourceType
from rss_feeds_backend.feed_processing.base.feed_collector import FeedCollector
from rss_feeds_backend.feed_processing.base.feed_extractor import FeedExtractor
from rss_feeds_backend.feed_processing.feed_collectors.rest_api_get import RestApiGet
from rss_feeds_backend.feed_processing.feed_extractors.json_extractor import JsonExtractor
from rss_feeds_backend.feed_processing.feed_extractors.xml_extractor import XmlExtractor

LOGGER = structlog.get_logger()
FEED_COLLECTOR_MAP = MappingProxyType(
    {
        FeedSourceType.REST: RestApiGet,
    },
)
FEED_EXTRACTOR_MAP = MappingProxyType(
    {
        FeedType.XML: XmlExtractor,
        FeedType.JSON: JsonExtractor,
    },
)


class FeedFactory:
    """Factory class to instantiate FeedCollector and FeedExtractor objects"""

    @classmethod
    def initialize_feed_collector(
            cls,
            feed_url: str,
            feed_source_type: FeedSourceType = FeedSourceType.REST,
    ) -> typing.Optional[FeedCollector]:
        """
        Instantiates a FeedCollector object according to the feed source type

        Args:
            feed_url: address where the feed can be retrieved
            feed_source_type: Type of the feed source

        Returns:
            FeedCollector object if initializes, None otherwise
        """
        fc_class = FEED_COLLECTOR_MAP.get(feed_source_type)
        fc_obj: typing.Optional[FeedCollector] = None
        if fc_class:
            fc_obj = fc_class(feed_url=feed_url)
            LOGGER.info(f"FeedCollector is initialized for source type: '{feed_source_type}' and url: '{feed_url}'")
        else:
            LOGGER.warning(f"There is no FeedCollector class for feed source type: {feed_source_type}!")
        return fc_obj

    @classmethod
    def initialize_feed_extractor(cls, feed_type: FeedType) -> typing.Optional[FeedExtractor]:
        """
        Instantiates a FeedExtractor object according to the feed type

        Args:
            feed_type: type of the feed

        Returns:
            FeedExtractor object if initializes, None otherwise
        """
        fe_cls = FEED_EXTRACTOR_MAP.get(feed_type)
        fe_obj: typing.Optional[FeedExtractor] = None
        if fe_cls:
            fe_obj = fe_cls()
            LOGGER.info(f"FeedExtractor is initialized for feed type: '{feed_type}'")
        else:
            LOGGER.warning(f"There is no FeedExtractor class for feed type: {feed_type}!")
        return fe_obj
