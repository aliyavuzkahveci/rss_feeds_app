"""
# -----------------------------------------------------------------------------#
#                                                                              #
#                            Python script                                     #
#                                                                              #
# -----------------------------------------------------------------------------#
Description  :
Implementation of Feed related endpoints

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
from sqlmodel import Session, select
from starlette import status

from rss_feeds_backend.common.enums import FeedType
from rss_feeds_backend.common.registry import container
from rss_feeds_backend.database import fetch_feed_from_db, get_session, fetch_all_feeds_from_db
from rss_feeds_backend.db_models.feed import Feed
from rss_feeds_backend.db_models.user import User, ADMIN_NAME
from rss_feeds_backend.db_models.user_feed import UserFeed
from rss_feeds_backend.feed_processing.base.feed_processor import FeedProcessor
from rss_feeds_backend.feed_processing.feed_manager import FeedManager
from rss_feeds_backend.routers.authentication import get_current_user

LOGGER = structlog.get_logger()
router = APIRouter(prefix="/feed")


@router.post("/define")
async def define_feed(
        feed_link: str,
        feed_type: FeedType,
        session: Session = Depends(get_session),
        user: User = Depends(get_current_user)) -> typing.Dict[str, str]:
    """
    Defines a new feed to the system. This privilege is only provided to admin!

    Args:
        feed_link: the link to the feed source
        feed_type: the type of the feed
        session: a unique session for DB connection
        user: logged in user details

    Returns:
        the details about the operation result
    """
    if user.username != ADMIN_NAME:
        error_message = f"Only {ADMIN_NAME} can define a new feed!"
        LOGGER.error(error_message)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_message,
        )
    existing_feed = fetch_feed_from_db(link=feed_link, session=session)
    if existing_feed:
        LOGGER.warning(f"A Feed with the link '{feed_link}' is already defined!")
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail={
                "message": "This feed is already defined!",
                "title": existing_feed.title,
                "link": existing_feed.link,
            },
        )
    container.resolve(FeedManager).define_new_feed_processor(feed_link=feed_link, feed_type=feed_type)
    result_message = f"A new FeedProcessor is created for link: '{feed_link}' and type: '{feed_type}'"
    LOGGER.info(result_message)
    return {
        "result": "successful",
        "message": result_message,
        "explanation": "FeedProcessor will periodically retrieve RSS Feeds from the link and saves into the DB.",
    }


@router.get("/list")
async def list_feeds(
        session: Session = Depends(get_session),
        user: User = Depends(get_current_user),
) -> typing.List[Feed]:
    """
    Fetches all the defined Feeds from DB

    Args:
         session: a unique session for DB connection
         user: logged in user details

    Returns:
        all defined feeds from DB
    """
    return fetch_all_feeds_from_db(session)


@router.post("/refresh")
async def force_refresh(
        feed_link: str,
        session: Session = Depends(get_session),
        user: User = Depends(get_current_user),
) -> typing.Dict[str, str]:
    """
    Forcefully refresh a feed by calling the FeedProcessor object's function
    If the refresh is successful, background process starts again

    Args:
        feed_link: feed link as identifier to follow
        session: a unique session for DB connection
        user: logged in user details

    Returns:
        operation result with some detail message
    """
    feed_processor: typing.Optional[FeedProcessor] = None
    for fp_obj in container.resolve(FeedManager).feed_processor_list:
        if fp_obj.address == feed_link:
            feed_processor = fp_obj
            break
    if not feed_processor:
        message = f"There is no background process defined for feed with link: '{feed_link}'"
    elif feed_processor.is_alive():
        message = f"The background process for '{feed_link}' is running. So, no force refresh action can be taken!"
    elif not feed_processor.force_refresh_feed():
        message = f"Force refresh is not successful! The background process for '{feed_link}' will not be started!"
    else:
        feed_processor.start()
        message = f"Force refresh is successful. The background process for '{feed_link}' is started again."
        LOGGER.info(message)
        return {
            "result": "successful",
            "message": message,
        }
    LOGGER.warning(message)
    raise HTTPException(
        status_code=status.HTTP_412_PRECONDITION_FAILED,
        detail={
            "result": "fail",
            "message": message,
        },
    )



@router.get("/followed_list")
async def list_followed_feeds(
        session: Session = Depends(get_session),
        user: User = Depends(get_current_user),
) -> typing.List[Feed]:
    """
    Fetches all the followed Feeds by the user from DB

    Args:
         session: a unique session for DB connection
         user: logged in user details

    Returns:
        all followed feeds from DB
    """
    followed_feeds: typing.List[Feed] = []
    query = select(UserFeed).where(UserFeed.user_id == user.id)
    user_feed_list = session.exec(query).all()
    for user_feed in user_feed_list:
        query = select(Feed).where(Feed.id == user_feed.feed_id)
        feed = session.exec(query).first()
        if feed:
            followed_feeds.append(feed)
    return followed_feeds


@router.post("/follow")
async def follow_feed(
        feed_link: str,
        session: Session = Depends(get_session),
        user: User = Depends(get_current_user)) -> typing.Dict[str, str]:
    """
    Enables the user to follow the feed having the provided link

    Args:
        feed_link: feed link as identifier to follow
        session: a unique session for DB connection
        user: logged in user details

    Returns:
        operation result with some detail message
    """
    feed = _get_feed(feed_link, session)
    query = select(UserFeed).where(UserFeed.user_id == user.id)
    user_feed_list = session.exec(query).all()
    for user_feed in user_feed_list:
        if user_feed.feed_id == feed.id:
            error_message = f"The feed with link '{feed_link}' is already followed by the user '{user.username}'!"
            LOGGER.error(error_message)
            raise HTTPException(
                status_code=status.HTTP_412_PRECONDITION_FAILED,
                detail=error_message,
            )
    session.add(UserFeed(user_id=user.id, feed_id=feed.id))
    session.commit()
    result_message = f"Feed with link '{feed_link}' is now followed by the user '{user.username}'."
    return {
        "result": "successful",
        "message": result_message,
    }


@router.post("/unfollow")
async def unfollow_feed(
        feed_link: str,
        session: Session = Depends(get_session),
        user: User = Depends(get_current_user)) -> typing.Dict[str, str]:
    """
    Enables the user to unfollow the feed having the provided link

    Args:
        feed_link: feed link as identifier to follow
        session: a unique session for DB connection
        user: logged in user details

    Returns:
        operation result with some detail message
    """
    feed = _get_feed(feed_link, session)
    query = select(UserFeed).where(UserFeed.user_id == user.id, UserFeed.feed_id == feed.id)
    user_feed = session.exec(query).first()
    if not user_feed:
        error_message = f"The feed with link '{feed_link}' is not followed by the user '{user.username}'!"
        LOGGER.error(error_message)
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail=error_message,
        )
    session.delete(user_feed)
    session.commit()
    result_message = f"Feed with link '{feed_link}' is unfollowed by the user '{user.username}'."
    return {
        "result": "successful",
        "message": result_message,
    }


def _get_feed(feed_link: str, session: Session) -> Feed:
    """
    Fetches the feed object from DB or throws exception in case there is no feed matching in DB

    Args:
        feed_link: link to the feed source
        session: a unique session for DB connection

    Returns:
        Feed object from the DB
    """
    feed = fetch_feed_from_db(feed_link, session)
    if not feed:
        error_message = f"There is no Feed defined with the link '{feed_link}'"
        LOGGER.error(error_message)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_message,
        )
    return feed
