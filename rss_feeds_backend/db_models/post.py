"""
# -----------------------------------------------------------------------------#
#                                                                              #
#                            Python script                                     #
#                                                                              #
# -----------------------------------------------------------------------------#
Description  :
Implementation of Database Model class Post

# -----------------------------------------------------------------------------#
#                                                                              #
#       Copyright (c) 2023 , Ali Yavuz Kahveci.                                #
#                         All rights reserved                                  #
#                                                                              #
# -----------------------------------------------------------------------------#
"""
import typing
from datetime import datetime

from sqlalchemy import VARCHAR, Column
from sqlmodel import SQLModel, Field, Relationship


class Post(SQLModel, table=True):
    """Represents the Post object as a DB table"""
    id: typing.Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(nullable=False)
    link: str = Field(nullable=False)
    guid: str = Field(sa_column=Column("guid", VARCHAR, unique=True, index=True))
    description: str = Field(nullable=False)
    publication_date: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    feed: "Feed" = Relationship(back_populates="posts")
    feed_id: typing.Optional[int] = Field(default=None, foreign_key="feed.id")  # to make connection between two tables

    def __eq__(self, other: typing.Any) -> bool:
        """
        Checks the equality of two Post objects

        Args:
            other: another object

        Returns:
            True if objects have the same guid, False otherwise
        """
        if not isinstance(other, Post):
            return False
        return self.guid == other.guid
