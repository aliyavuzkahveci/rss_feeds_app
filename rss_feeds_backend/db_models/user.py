"""
# -----------------------------------------------------------------------------#
#                                                                              #
#                            Python script                                     #
#                                                                              #
# -----------------------------------------------------------------------------#
Description  :
Implementation of Database Model class User

# -----------------------------------------------------------------------------#
#                                                                              #
#       Copyright (c) 2023 , Ali Yavuz Kahveci.                                #
#                         All rights reserved                                  #
#                                                                              #
# -----------------------------------------------------------------------------#
"""
import typing

from passlib.context import CryptContext
from sqlalchemy import VARCHAR, Column, ARRAY, String
from sqlmodel import SQLModel, Field, Relationship

from rss_feeds_backend.db_models.feed import Feed

pwd_context = CryptContext(schemes=["bcrypt"])
ADMIN_NAME = "admin"
ADMIN_PASS = "12345678"


class UserOutput(SQLModel):
    """The return object for a user login"""
    id: int
    username: str


class User(SQLModel, table=True):
    """Represents user details in the DB to control access to the endpoints"""
    id: typing.Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(sa_column=Column("username", VARCHAR, unique=True, index=True))
    password_hash: str = ""

    def set_password(self, password: str) -> None:
        """
        Setting the passwords actually sets password_hash.

        Args:
            password: a new password to set
        """
        self.password_hash = pwd_context.hash(password)

    def verify_password(self, password: str) -> bool:
        """
        Verify given password by hashing and comparing to password_hash.

        Args:
            password: a password to check if it is correct

        Returns:
            True if password is correct, False otherwise
        """
        return pwd_context.verify(password, self.password_hash)
