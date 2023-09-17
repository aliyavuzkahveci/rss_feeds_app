"""
# -----------------------------------------------------------------------------#
#                                                                              #
#                            Python script                                     #
#                                                                              #
# -----------------------------------------------------------------------------#
Description  :
Implementation of RSS Feed Backend application initialization

# -----------------------------------------------------------------------------#
#                                                                              #
#       Copyright (c) 2023 , Ali Yavuz Kahveci.                                #
#                         All rights reserved                                  #
#                                                                              #
# -----------------------------------------------------------------------------#
"""
from fastapi import FastAPI
from sqlmodel import SQLModel, Session
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from rss_feeds_backend.database import engine, fetch_all_feeds_from_db
from rss_feeds_backend.exceptions import BadRequestException
from rss_feeds_backend.common.enums import FeedType
from rss_feeds_backend.common.registry import container
from rss_feeds_backend.feed_processing.feed_manager import FeedManager
from rss_feeds_backend.routers import authentication, users, feed, post

app = FastAPI(title="RSS Feeds")
app.include_router(authentication.router)
app.include_router(users.router)
app.include_router(feed.router)
app.include_router(post.router)


origins = [
    "http://localhost:8000",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    """Executed when application is starting."""
    SQLModel.metadata.create_all(engine)
    feed_manager = FeedManager()
    with Session(engine) as session:
        for feed_db in fetch_all_feeds_from_db(session):
            feed_manager.define_new_feed_processor(feed_db.link, FeedType.XML)
    container.register(FeedManager, instance=feed_manager)  # register FeedManager to access throughout the code!


@app.on_event("shutdown")
def on_shutdown() -> None:
    """Executed when application is shutting down."""
    container.resolve(FeedManager).stop_all_processors()


@app.exception_handler(BadRequestException)
async def unicorn_exception_handler(request: Request, exc: BadRequestException):
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={"message": "Bad Request"},
    )
