"""
# -----------------------------------------------------------------------------#
#                                                                              #
#                            Python script                                     #
#                                                                              #
# -----------------------------------------------------------------------------#
Description  :
Implementation of XmlExtractor class

# -----------------------------------------------------------------------------#
#                                                                              #
#       Copyright (c) 2023 , Ali Yavuz Kahveci.                                #
#                         All rights reserved                                  #
#                                                                              #
# -----------------------------------------------------------------------------#
"""
import re
import typing
from datetime import datetime
from types import MappingProxyType

import structlog
from lxml import etree

from rss_feeds_backend.common.enums import FeedType
from rss_feeds_backend.db_models.feed import Feed
from rss_feeds_backend.db_models.post import Post
from rss_feeds_backend.feed_processing.base.feed_extractor import FeedExtractor, DEFAULT_TITLE, DEFAULT_DESCRIPTION, \
    DEFAULT_TTL
from rss_feeds_backend.feed_processing.feed_collectors.rest_api_get import EMPTY_STR

LOGGER = structlog.get_logger()
NAMESPACES = MappingProxyType(
    {
        "atom": "http://www.w3.org/2005/Atom",
    },
)
COMMON_XPATH = "./channel/"
FEED_XPATH_MAP = MappingProxyType(
    {
        "title": f"{COMMON_XPATH}title",
        "link": f"{COMMON_XPATH}atom:link",
        "description": f"{COMMON_XPATH}description",
        "ttl": f"{COMMON_XPATH}ttl",
        "last_build_date": f"{COMMON_XPATH}lastBuildDate",
    },
)
POST_ATTR_LIST = ("title", "link", "description", "guid", "pubDate")


class XmlExtractor(FeedExtractor):
    """class to perform extraction of feed details and posts from an XML feed content"""

    def __init__(self) -> None:
        """
        Initialize the XmlExtractor class with the provided parameters.
        """
        super().__init__(feed_type=FeedType.XML)

    def extract_feed(self, feed_content: str) -> typing.Optional[Feed]:
        """
        Goes over the feed content and extracts the feed info with posts

        Args:
            feed_content: the feed content in string

        Returns:
            Feed object containing the list of posts and other feed details
        """
        xml_content = re.sub(r'\bencoding="[-\w]+"', '', feed_content, count=1)  # remove encoding from xml content
        rss_root = etree.fromstring(xml_content)
        feed = self._initialize_feed_object(rss_root)
        if feed:
            feed.posts = self._extract_posts(rss_root, feed)
        return feed

    def _initialize_feed_object(self, element: "etree._Element") -> typing.Optional[Feed]:
        """
        Extracts the necessary values from xml to instantiate Feed object

        Args:
            element: xml element

        Returns:
            Feed object if mandatory fields exist, None otherwise
        """
        attr_readings: typing.Dict[str, str] = {}
        for attr, xpath in FEED_XPATH_MAP.items():
            child = element.find(xpath, namespaces=NAMESPACES)
            attr_value = self._get_child_text(child)
            if not attr_value:
                LOGGER.warning(f"For Feed attribute '{attr}', xpath: '{xpath}' does not exist in XML content!")
                continue
            attr_readings[attr] = attr_value
        return Feed(
            title=attr_readings.get("title", DEFAULT_TITLE),
            link=attr_readings.get("link"),
            description=attr_readings.get("description", DEFAULT_DESCRIPTION),
            ttl=int(attr_readings.get("ttl", DEFAULT_TTL)),
            last_build_date=self._convert_datetime(attr_readings.get("last_build_date")),
        )

    def _extract_posts(self, element: "etree._Element", feed: Feed) -> typing.List[Post]:
        """
        Iterates over all the 'item's in the rss xml and generates Post objects

        Args:
             element: root element of the rss xml content

        Returns:
            list of Post objects
        """
        posts: typing.List[Post] = []
        for item in element.findall(f"{COMMON_XPATH}item"):
            post = self._extract_post(item, feed)
            if post:
                posts.append(post)
        return posts

    def _extract_post(self, element: "etree._Element", feed: Feed) -> typing.Optional[Post]:
        """
        Extracts the necessary Post details from <item> xpath and generates Post object

        Args:
             element: xml object of <item>

        Returns:
            Post object if all the fields are extracted, None otherwise
        """
        post_attr_map: typing.Dict[str, str] = {}
        for child in element:
            if child.tag in POST_ATTR_LIST:
                post_attr_map[child.tag] = child.text
        if len(post_attr_map) != len(POST_ATTR_LIST):
            LOGGER.warning(f"Not all the POST class attributes are extracted!")
            return None
        return Post(
            title=post_attr_map.get("title", DEFAULT_TITLE),
            link=post_attr_map.get("link"),
            guid=post_attr_map.get("guid"),
            description=post_attr_map.get("description", DEFAULT_DESCRIPTION),
            publication_date=self._convert_datetime(post_attr_map.get("pubDate")),
        )

    @classmethod
    def _get_child_text(cls, child: typing.Optional["etree._Element"]) -> str:
        """
        Get and return the text values of the element

        Args:
            child: The element to get the text from

        Returns:
            The text values of the element
        """
        if child is None:
            return EMPTY_STR
        if child.tag.endswith('link'):  # special case for 'atom:link' xpath
            return child.attrib.get('href', EMPTY_STR)
        return child.text if child.text is not None else EMPTY_STR

    @classmethod
    def _convert_datetime(cls, datetime_reading: typing.Optional[str]) -> datetime:
        """
        Converts datetime from string to datetime object

        Args:
            datetime_reading: string reading of datetime from XML
        """
        if not datetime_reading:
            return datetime.now()
        # replace timezones with their hour counts
        datetime_reading = datetime_reading.replace("EDT", "-0400")
        datetime_reading = datetime_reading.replace("EST", "-0500")
        return datetime.strptime(datetime_reading, "%a, %d %b %Y %H:%M:%S %z")
