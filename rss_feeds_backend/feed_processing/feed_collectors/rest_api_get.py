"""
# -----------------------------------------------------------------------------#
#                                                                              #
#                            Python script                                     #
#                                                                              #
# -----------------------------------------------------------------------------#
Description  :
Implementation of RestApiGet base object

# -----------------------------------------------------------------------------#
#                                                                              #
#       Copyright (c) 2023 , Ali Yavuz Kahveci.                                #
#                         All rights reserved                                  #
#                                                                              #
# -----------------------------------------------------------------------------#
"""
import typing

import requests
import structlog
from requests.auth import HTTPBasicAuth

from rss_feeds_backend.feed_processing.base.feed_collector import FeedCollector

LOGGER = structlog.get_logger()
REQUEST_TIMEOUT = 3  # seconds
EMPTY_STR = ""


class RestApiGet(FeedCollector):
    """Definition of class for status check of servers."""

    def __init__(
            self,
            feed_url: str,
            username: typing.Optional[str] = None,
            password: typing.Optional[str] = None,
    ) -> None:
        """
        Initializes the FeedCollector class with the provided configuration

        Args:
            feed_url: the url address of the feed to collect
            username: optional credential to access to feed service
            password: optional credential to access to feed service
        """
        super().__init__(feed_url)  # initialize the parent object
        self.username: typing.Optional[str] = username
        self.password: typing.Optional[str] = password

    def make_connection(self) -> bool:
        """
        Initiates a connection towards the configured endpoint

        Returns:
            True if connection is established successfully, False otherwise
        """
        if self.feed_url:
            return True
        LOGGER.warning("Server URL is not set! Connection cannot be made!")
        return False

    def close_connection(self) -> bool:
        """
        Closes the open connection to the configured endpoint

        Returns:
            True if connection is closed successfully, False otherwise
        """
        return True

    def get_feed_content(self) -> str:
        """
        Requests the current feed content

        Returns:
            the received status
        """
        result = self._rest_get()
        if result:
            LOGGER.info(f"REST GET is successful from url '{self.feed_url}'")
            return result
        LOGGER.info(f"REST GET is failed! No reply from url '{self.feed_url}'!")
        return EMPTY_STR

    def _rest_get(self) -> typing.Optional[str]:  # noqa: WPS212
        """
        Makes a REST GET call and returns the response content

        Returns:
            response content if GET call returns success, None otherwise
        """
        if not self.feed_url:
            LOGGER.warning("server_url is a mandatory member to set for RestApiGet objects!")
            return None
        try:
            response = requests.get(
                url=self.feed_url,
                auth=HTTPBasicAuth(self.username, self.password) if self.username and self.password else None,
                verify=False,
                timeout=REQUEST_TIMEOUT,
            )
        except requests.exceptions.RequestException as exc:
            LOGGER.error(f"Exception occurred during request get: {exc}")
            return None
        return response.text if self._check_get_response(response) else None

    @classmethod
    def _check_get_response(cls, response: requests.Response) -> bool:
        """
        Check if the status code is ok

        Args:
            response: The http response object

        Returns:
            True if the response is ok otherwise False
        """
        try:
            response.raise_for_status()
        except requests.HTTPError as error:
            LOGGER.warning(f"Request failed. Error message: {str(error)}")
            return False
        return True
