"""
# -----------------------------------------------------------------------------#
#                                                                              #
#                            Python script                                     #
#                                                                              #
# -----------------------------------------------------------------------------#
Description  :
Implementation of Database related functionalities

# -----------------------------------------------------------------------------#
#                                                                              #
#       Copyright (c) 2023 , Ali Yavuz Kahveci.                                #
#                         All rights reserved                                  #
#                                                                              #
# -----------------------------------------------------------------------------#
"""
import typing
from pathlib import Path

import structlog
from sqlmodel import create_engine, Session, select

from rss_feeds_backend.db_models.feed import Feed
from rss_feeds_backend.db_models.post import Post

LOGGER = structlog.get_logger()
DB_PATH = Path(__file__).parents[0] / "rss_feeds.db"

engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False},  # Needed for SQLite
    echo=True  # Log generated SQL
)


def get_session():
    with Session(engine) as session:
        yield session


def insert_update_feed(feed: Feed) -> None:
    with Session(engine) as session:
        feed_from_db = fetch_feed_from_db(feed.link, session)
        if feed_from_db:
            LOGGER.info("Feed object will be updated")
            feed = update_feed_details(existing_feed=feed_from_db, new_feed=feed)
        else:
            LOGGER.info("Feed object will be added to the DB!")
        session.add(feed)
        session.commit()
        session.refresh(feed)


def fetch_feed_from_db(link: str, session: Session = get_session()) -> typing.Optional[Feed]:
    """
    Fetched the Feed object from the database

    Args:
        link: feed address used as an identifier
        session: session for DB connection

    Returns:
        Feed object if it exists, None otherwise
    """
    query = select(Feed).where(Feed.link == link)
    feed = session.exec(query).first()
    if feed:
        LOGGER.info(f"There exists a feed object in DB with the link '{link}'")
    else:
        LOGGER.info(f"There is no feed object in DB with the link '{link}'")
    return feed


def fetch_all_feeds_from_db(session: Session = get_session()) -> typing.List[Feed]:
    """
    Fetches all the Feed objects from the database

    Args:
        session: session for DB connection

    Returns:
        List of Feed objects
    """
    query = select(Feed)
    feed_list = session.exec(query).all()
    return feed_list


def fetch_post_from_db(guid: str, session: Session = get_session()) -> typing.Optional[Post]:
    """
    Fetches the Post object from the database

    Args:
        guid: post guid used as an identifier
        session: session for DB connection

    Returns:
        Post object if it exists, None otherwise
    """
    query = select(Post).where(Post.guid == guid)
    post = session.exec(query).first()
    if post:
        LOGGER.info(f"There exists a post object in DB with the guid '{guid}'")
    else:
        LOGGER.info(f"There is no post object in DB with the guid '{guid}'")
    return post


def fetch_all_posts_from_db(session: Session = get_session()) -> typing.List[Post]:
    """
    Fetches all the Feed objects from the database

    Args:
        session: session for DB connection

    Returns:
        List of Post objects
    """
    query = select(Post)
    post_list = session.exec(query).all()
    return post_list


def update_feed_details(existing_feed: Feed, new_feed: Feed) -> Feed:
    """
    Goes over the new feed and updates the existing feed object

    Args:
         existing_feed: existing feed object in the DB
         new_feed: new feed object instantiated from an RSS feed

    Returns:
        the updated Feed object
    """
    existing_feed.title = new_feed.title
    existing_feed.description = new_feed.description
    existing_feed.ttl = new_feed.ttl
    existing_feed.last_build_date = new_feed.last_build_date
    for new_post in new_feed.posts:
        if new_post in existing_feed.posts:
            LOGGER.info(f"Post '{new_post.guid}' already exists! Skipping...")
            continue
        existing_feed.posts.append(new_post)
    return existing_feed
