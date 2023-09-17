"""
# -----------------------------------------------------------------------------#
#                                                                              #
#                            Python script                                     #
#                                                                              #
# -----------------------------------------------------------------------------#
Description  :
Implementation of FeedCollector base object

# -----------------------------------------------------------------------------#
#                                                                              #
#       Copyright (c) 2023 , Ali Yavuz Kahveci.                                #
#                         All rights reserved                                  #
#                                                                              #
# -----------------------------------------------------------------------------#
"""
import abc
import typing
from types import TracebackType

import structlog

LOGGER = structlog.get_logger()


class FeedCollector(abc.ABC):
    """Base class for Feed Collection."""

    def __init__(self, feed_url: str) -> None:
        """
        Initialize the FeedCollector class with the provided configuration.

        Args:
            feed_url: the url address of the feed to collect
        """
        self.is_connection_available = False
        self.feed_url = feed_url

    @abc.abstractmethod
    def make_connection(self) -> bool:
        """
        Initiates a connection towards the configured endpoint
        """

    @abc.abstractmethod
    def close_connection(self) -> bool:
        """
        Closes the open connection to the configured endpoint
        """

    @abc.abstractmethod
    def get_feed_content(self) -> str:
        """
        Requests the current feed content

        Returns:
            the received status
        """

    def __enter__(self) -> typing.Any:
        """
        Enter with region, attempt to setup connection

        Returns:
            Self if successful in setting up the connection, exception otherwise
        """
        if self.make_connection():
            self.is_connection_available = True
            LOGGER.debug(f"Connection is set up successfully for URL: {self.feed_url}")
        else:
            LOGGER.warning(f"Failed to set up the connection for URL: {self.feed_url}!")
        return self

    def __exit__(
        self,
        exc_type: typing.Optional[typing.Type[BaseException]] = None,
        exc_val: typing.Optional[BaseException] = None,
        exc_tb: typing.Optional[TracebackType] = None,
    ) -> None:
        """
        Closes the connection

        Args:
            exc_type: The exception type
            exc_val: The exception value
            exc_tb: The exception traceback
        """
        if exc_type:
            LOGGER.error(f"Exception {exc_type} occurred with value {exc_val}")
            LOGGER.error(f"The stack trace: {exc_tb}")
        if not self.is_connection_available:
            return  # do not attempt to close the connection!
        if self.close_connection():
            LOGGER.debug(f"Connection is closed successfully for URL: {self.feed_url}.")
        else:
            LOGGER.warning(f"Failed to close the connection for URL: {self.feed_url}!")

    def __str__(self) -> str:
        """
        Returns the name of the class for better log messages

        Returns:
            name of the concrete class, not the abstract one!
        """
        return self.__class__.__name__
