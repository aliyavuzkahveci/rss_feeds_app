"""
# -----------------------------------------------------------------------------#
#                                                                              #
#                            Python script                                     #
#                                                                              #
# -----------------------------------------------------------------------------#
Description  :
Implementation of User Authentication functionalities

# -----------------------------------------------------------------------------#
#                                                                              #
#       Copyright (c) 2023 , Ali Yavuz Kahveci.                                #
#                         All rights reserved                                  #
#                                                                              #
# -----------------------------------------------------------------------------#
"""
import typing

import structlog
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session, select
from starlette import status

from rss_feeds_backend.database import get_session
from rss_feeds_backend.db_models.user import User, UserOutput

LOGGER = structlog.get_logger()
URL_PREFIX = "/auth"
router = APIRouter(prefix=URL_PREFIX)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{URL_PREFIX}/token")


def get_current_user(
        token: str = Depends(oauth2_scheme),
        session: Session = Depends(get_session)) -> UserOutput:
    """
    Returns the currently logged in user details

    Args:
        token: oauth token provided when a user logs in
        session: a unique session for a logged in user

    Returns:
        user details containing the username and id (primary key in the DB Table)
    """
    query = select(User).where(User.username == token)
    user = session.exec(query).first()
    if user:
        LOGGER.info("The logged in user information is returned!")
        return UserOutput.from_orm(user)
    else:
        LOGGER.error(f"User '{token}' is not logged in!")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not logged in",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/token")
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        session: Session = Depends(get_session)) -> typing.Dict[str, typing.Any]:
    """
    Endpoint to implement login functionality

    Args:
        form_data: OAuth password data
        session: a unique session info

    Returns:
        the dictionary containing username and token type if user password is verified, exception otherwise
    """
    query = select(User).where(User.username == form_data.username)
    user = session.exec(query).first()
    if user and user.verify_password(form_data.password):
        return {"access_token": user.username, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")
