"""
# -----------------------------------------------------------------------------#
#                                                                              #
#                            Python script                                     #
#                                                                              #
# -----------------------------------------------------------------------------#
Description  :
Implementation of Database Model class Feed

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

from rss_feeds_backend.db_models.post import Post


class Feed(SQLModel, table=True):
    """Represents the Feed object as a DB table"""
    id: typing.Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(nullable=False)
    link: str = Field(sa_column=Column("link", VARCHAR, unique=True, index=True))
    description: str = Field(nullable=False)
    ttl: int = Field(nullable=False)
    last_build_date: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    posts: typing.List[Post] = Relationship(back_populates="feed")
