"""
# -----------------------------------------------------------------------------#
#                                                                              #
#                            Python script                                     #
#                                                                              #
# -----------------------------------------------------------------------------#
Description  :
Implementation of Post related endpoints

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

from rss_feeds_backend.database import get_session, fetch_all_posts_from_db, fetch_post_from_db
from rss_feeds_backend.db_models.feed import Feed
from rss_feeds_backend.db_models.post import Post
from rss_feeds_backend.db_models.user import User
from rss_feeds_backend.db_models.user_feed import UserFeed
from rss_feeds_backend.db_models.user_post import UserPost
from rss_feeds_backend.routers.authentication import get_current_user

LOGGER = structlog.get_logger()
router = APIRouter(prefix="/post")


@router.get("/list")
async def list_posts(
        session: Session = Depends(get_session),
        user: User = Depends(get_current_user),
) -> typing.List[Post]:
    """
    Fetches all the Posts from DB

    Args:
         session: a unique session for DB connection
         user: logged in user details

    Returns:
        all defined feeds from DB
    """
    return fetch_all_posts_from_db(session)


@router.get("/list_filtered")
async def list_filtered_posts(
        filter_read: typing.Optional[bool] = None,
        filter_feed_link: typing.Optional[str] = None,
        filter_followed: typing.Optional[bool] = None,
        session: Session = Depends(get_session),
        user: User = Depends(get_current_user),
) -> typing.List[Post]:
    """
    Fetches all the Posts from DB

    Args:
        filter_read: flag to filter out posts according to their read status
        filter_feed_link: to filter out posts for certain Feeds
        filter_followed: flag to filter out posts if the feed is followed by the user
        session: a unique session for DB connection
        user: logged in user details

    Returns:
        all defined feeds from DB
    """
    posts = fetch_all_posts_from_db(session)
    if filter_read is not None:
        posts = _apply_read_unread_filter(posts, filter_read, session, user)
    if filter_feed_link is not None:
        posts = _apply_feed_filter(posts, filter_feed_link, session)
    if filter_followed is not None:
        posts = _apply_followed_filter(posts, filter_followed, session, user)
    return posts


@router.post("/toggle_read")
async def toggle_read(
        post_guid: str,
        mark_read: bool = True,
        session: Session = Depends(get_session),
        user: User = Depends(get_current_user)) -> typing.Dict[str, str]:
    """
    Marks a certain post as read or unread for the logged in user

    Args:
        post_guid: post guid as identifier to mark read/unread
        mark_read: Flag to set the post as read/unread
        session: a unique session for DB connection
        user: logged in user details

    Returns:
        operation result with some detail message
    """
    error_occurred: bool = False
    post = _get_post(post_guid, session)
    query = select(UserPost).where(UserPost.user_id == user.id, UserPost.post_id == post.id)
    user_post = session.exec(query).first()
    if user_post:
        if mark_read:
            message = f"The post with guid '{post_guid}' is already marked as read by user '{user.username}'!"
            error_occurred = True
        else:
            # mark the read Post as UNREAD
            session.delete(user_post)
            session.commit()
            message = f"The post with guid '{post_guid}' is marked as UNread for the user '{user.username}'"
    else:
        if mark_read:
            # if reached here, the Post can be marked as READ!
            session.add(UserPost(user_id=user.id, post_id=post.id))
            session.commit()
            message = f"Post with guid '{post_guid}' is marked as READ for the user '{user.username}'."
        else:
            message = f"The post with guid '{post_guid}' cannot be marked as UNread since it is not read beforehand!"
            error_occurred = True
    if error_occurred:
        LOGGER.error(message)
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail=message,
        )
    return {
        "result": "successful",
        "message": message,
    }


def _get_post(post_guid: str, session: Session) -> Post:
    """
    Fetches the post object from DB or throws exception in case there is no post matching in DB

    Args:
        post_guid: guid of the post
        session: a unique session for DB connection

    Returns:
        Post object from the DB
    """
    post = fetch_post_from_db(post_guid, session)
    if not post:
        error_message = f"There is no Post defined with the guid '{post_guid}'"
        LOGGER.error(error_message)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_message,
        )
    return post


def _apply_read_unread_filter(posts: typing.List[Post], read_flag: bool, session: Session, user: User):
    """
    Filter outs the posts according to their read state (Read vs UNread)

    Args:
        posts: the list of Posts to be filtered out
        read_flag: Flag to filter out Posts
        session: a unique session for DB connection
        user: logged in user details

    Returns:
        the filtered out list of Posts object
    """
    filtered_posts: typing.List[Post] = []
    for post in posts:
        query = select(UserPost).where(UserPost.user_id == user.id, UserPost.post_id == post.id)
        user_post = session.exec(query).first()  # marked as Read
        if user_post and read_flag:
            # filter out only Read Posts
            filtered_posts.append(post)
        elif not user_post and not read_flag:
            # filter out only UNread Posts
            filtered_posts.append(post)
    return filtered_posts


def _apply_feed_filter(posts: typing.List[Post], feed_link: str, session: Session):
    """
    Filter outs the posts according to which feed they belong to

    Args:
        posts: the list of Posts to be filtered out
        feed_link: feed link to filter out Posts
        session: a unique session for DB connection

    Returns:
        the filtered out list of Posts object
    """
    query = select(Feed).where(Feed.link == feed_link)
    feed = session.exec(query).first()
    filtered_posts: typing.List[Post] = []
    for post in posts:
        if post.feed_id == feed.id:
            filtered_posts.append(post)
    return filtered_posts


def _apply_followed_filter(posts: typing.List[Post], followed: bool, session: Session, user: User):
    """
    Filter outs the posts if the feed which they belong to is followed by the user

    Args:
        posts: the list of Posts to be filtered out
        followed: Flag to filter out Posts
        session: a unique session for DB connection
        user: logged in user details

    Returns:
        the filtered out list of Posts object
    """
    query = select(UserFeed).where(UserFeed.user_id == user.id)
    followed_feeds = session.exec(query).all()  # followed feeds
    followed_feed_id_list: typing.List[int] = []
    for feed in followed_feeds:
        followed_feed_id_list.append(feed.feed_id)
    filtered_posts: typing.List[Post] = []
    for post in posts:
        if followed and post.feed_id in followed_feed_id_list:
            # filter out followed Feeds' posts
            filtered_posts.append(post)
        elif not followed and post.feed_id not in followed_feed_id_list:
            # filter out unfollowed Feeds' posts
            filtered_posts.append(post)
    return filtered_posts
