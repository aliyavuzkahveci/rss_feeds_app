"""
# -----------------------------------------------------------------------------#
#                                                                              #
#                            Python script                                     #
#                                                                              #
# -----------------------------------------------------------------------------#
Description  :
Implementation of Database Model class to mark Posts as read by User objects

# -----------------------------------------------------------------------------#
#                                                                              #
#       Copyright (c) 2023 , Ali Yavuz Kahveci.                                #
#                         All rights reserved                                  #
#                                                                              #
# -----------------------------------------------------------------------------#
"""
import typing

from sqlmodel import SQLModel, Field


class UserPost(SQLModel, table=True):
    """Represents users read posts"""
    id: typing.Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(nullable=False)  # primary key of the User Table
    post_id: int = Field(nullable=False)  # primary key of the Post table
