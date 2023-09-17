"""
# -----------------------------------------------------------------------------#
#                                                                              #
#                            Python script                                     #
#                                                                              #
# -----------------------------------------------------------------------------#
Description  :
Implementation of User related endpoints

# -----------------------------------------------------------------------------#
#                                                                              #
#       Copyright (c) 2023 , Ali Yavuz Kahveci.                                #
#                         All rights reserved                                  #
#                                                                              #
# -----------------------------------------------------------------------------#
"""
import structlog
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import SQLModel, Session
from starlette import status

from rss_feeds_backend.database import engine, get_session
from rss_feeds_backend.db_models.user import User, ADMIN_NAME, ADMIN_PASS
from rss_feeds_backend.routers.authentication import get_current_user

LOGGER = structlog.get_logger()
router = APIRouter(prefix="/user")


@router.post("/add", response_model=User)
async def user_add(
        username: str,
        password: str,
        session: Session = Depends(get_session),
        user: User = Depends(get_current_user)) -> User:
    """
    Adds a new user to the database. This privilege is only provided to admin!

    Args:
        username: name of the new user
        password: password of the new user
        session: a unique session for DB connection
        user: logged in user details

    Returns:
        a newly created user object
    """
    if user.username != ADMIN_NAME:
        error_message = f"Only {ADMIN_NAME} can create a new user!"
        LOGGER.error(error_message)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_message,
        )
    new_user = User(username=username)
    new_user.set_password(password)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user


def main():
    """Main function, creates admin user. Can be called from the terminal."""
    LOGGER.info("Creating DB Tables if necessary!")
    SQLModel.metadata.create_all(engine)
    LOGGER.info("This script will create an admin user and save it in the database.")

    with Session(engine) as session:
        user = User(username=ADMIN_NAME, followed_feeds=[])
        user.set_password(ADMIN_PASS)
        session.add(user)
        session.commit()


if __name__ == "__main__":
    main()
