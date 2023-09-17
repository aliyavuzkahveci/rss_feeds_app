#!/usr/bin/env python
import os
import sys
from pathlib import Path

from setuptools import setup


CURRENT_DIR = Path(__file__).parent
APP_NAME = "rss_feeds_backend"
sys.path.insert(0, str(CURRENT_DIR))


def get_long_description() -> str:
    readme_md = CURRENT_DIR / "README.md"
    with open(readme_md, encoding="utf8") as ld_file:
        return ld_file.read()


def package_files(directory):
    paths = []
    for (path, _, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join("..", path, filename))
    return paths


extra_files = package_files(os.path.join(CURRENT_DIR, APP_NAME))

setup(
    name=APP_NAME,
    version="0.0.1",
    description="RSS (Really Simple Syndication) Feeds",
    long_description=f"{get_long_description()}\n\n",
    author="Ali Yavuz Kahveci",
    author_email="aliyavuzkahveci@gmail.com",
    url="",
    packages=[APP_NAME],
    package_data={"": extra_files},
    zip_safe=False,
    keywords=APP_NAME,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.11",
    ],
    license="",
    test_suite="test",
    install_requires=[
        "annotated-types==0.5.0",
        "anyio==3.7.1",
        "bcrypt==4.0.1",
        "certifi==2023.7.22",
        "charset-normalizer==3.2.0 ",
        "click==8.1.6",
        "colorama==0.4.6",
        "dnspython==2.4.1",
        "email-validator==2.0.0.post2",
        "fastapi==0.101.0",
        "greenlet==2.0.2",
        "h11==0.14.0",
        "httpcore==0.17.3",
        "httptools==0.6.0",
        "httpx==0.24.1",
        "idna==3.4",
        "itsdangerous==2.1.2",
        "Jinja2==3.1.2",
        "lxml==4.9.3",
        "MarkupSafe==2.1.3",
        "orjson==3.9.3",
        "passlib==1.7.4",
        "punq==0.6.2",
        "pydantic==1.10.12",
        "python-dotenv==1.0.0",
        "python-multipart==0.0.6",
        "PyYAML==6.0.1",
        "requests==2.31.0",
        "sniffio==1.3.0",
        "SQLAlchemy==1.4.41",
        "sqlalchemy2-stubs==0.0.2a35",
        "sqlmodel==0.0.8",
        "starlette==0.27.0",
        "structlog==23.1.0",
        "typing_extensions==4.7.1",
        "ujson==5.8.0",
        "urllib3==2.0.4",
        "uvicorn==0.23.2",
        "watchfiles==0.19.0",
        "websockets==11.0.3",
    ],
    setup_requires=[],
    tests_require=[],
    extras_require={
        "dev": [
        ],
    },
    entry_points={
        "console_scripts": [
            "rss_feeds_backend=rss_feeds_backend.main:main",
        ],
    },
)
