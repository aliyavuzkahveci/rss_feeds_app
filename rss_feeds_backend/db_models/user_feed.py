"""
# -----------------------------------------------------------------------------#
#                                                                              #
#                            Python script                                     #
#                                                                              #
# -----------------------------------------------------------------------------#
Description  :
Implementation of Database Model class to relate User and Feed objects

# -----------------------------------------------------------------------------#
#                                                                              #
#       Copyright (c) 2023 , Ali Yavuz Kahveci.                                #
#                         All rights reserved                                  #
#                                                                              #
# -----------------------------------------------------------------------------#
"""
import typing

from sqlmodel import SQLModel, Field


class UserFeed(SQLModel, table=True):
    """Represents users following feeds"""
    id: typing.Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(nullable=False)  # primary key of the User Table
    feed_id: int = Field(nullable=False)  # primary key of the Feed table
