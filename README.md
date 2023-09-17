
<h2 align="center">RSS Feeds Backend Application</h2>
This project contains implementation of an RSS (**RDF [Resource Description Framework] Site Summary**) feeds backend application.
It allows users to be registered to the system via admin account and subscribe to some RSS Feeds channels.

<h3>Requirements:</h3>
**Python 3.11.0** to install package. 

Library dependencies are provided in **requirements.txt** and **requirements-dev.txt** files.

<h3> Installation & Execution </h3>
The application is provided with an installation package.
The user needs to execute the following command to install the application:

```
  pip install rss_feeds_backend-0.0.1-py3-none-any.whl
  rss_feeds_backend
```

---
<h4 align="center">Coding Style and Tools:</h4>
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/black-000000.svg"></a>
<a href="https://github.com/PyCQA/flake8"><img alt="flake8" src="https://img.shields.io/badge/flake8-000000.svg"></a>
<a href="https://github.com/PyCQA/prospector"><img alt="prospector" src="https://img.shields.io/badge/prospector-000000.svg"></a>
<a href="https://github.com/pytest-dev/pytest"><img alt="pytest" src="https://img.shields.io/badge/pytest-000000.svg"></a>
<a href="https://github.com/pytest-dev/pytest-cov"><img alt="pytest-cov" src="https://img.shields.io/badge/pytest_cov-000000.svg"></a>
<a href="https://github.com/pytest-dev/pytest-bdd"><img alt="pytest-bdd" src="https://img.shields.io/badge/pytest_bdd-000000.svg"></a>
<a href="https://github.com/pytest-dev/pytest-mock"><img alt="pytest-mock" src="https://img.shields.io/badge/pytest_mock-000000.svg"></a>
<a href="https://github.com/ktosiek/pytest-freezegun"><img alt="pytest-freezegun" src="https://img.shields.io/badge/pytest_freezegun-000000.svg"></a>
<a href="https://github.com/python/mypy"><img alt="mypy" src="https://img.shields.io/badge/mypy-000000.svg"></a>
---

<h3> List of Endpoints </h3>

The application is accessible via 127.0.0.1:8000.
The list of endpoints can be viewed via "127.0.0.1:8000/docs" or "127.0.0.1:8000/redoc"
The OpenAPI endpoint is at "127.0.0.1:8000/openapi.json"
that allows the user to see all the details of endpoints as a json content.
The publicly available endpoints are as follows:

1. **/auth/token** => lets the user login to the lottery system

2. **/user/add** => enables adding a new user to the system. admin is privileged to do so.

3. **/feed/define** => defines a new feed to the system. admin is provided to do so!

4. **/feed/list** => returns all the defined Feeds from DB

5. **/feed/refresh** => forcefully refresh a feed

6. **/feed/followed_list** => returns all the followed Feeds by the user from DB

7. **/feed/follow** => enables the user to follow the feed having the provided link

8. **/feed** => enables the user to unfollow the feed having the provided link

9. **/post/list** => returns all the Posts from DB

10. **/post/list_filtered** => returns all the Posts from DB

11. **/post/toggle_read** => marks a certain post as read or unread for the logged in user


<h3> Brief Explanation of the Application </h3>

RSS Feeds Backend Application is implemented using Python 3.11.
As the backend framework, FastAPI is utilized.
Apart from the endpoints, a multi-threaded approach is adapted to fetch the feeds from their source address in the background.
Users can decide to follow RSS Feed sources. Also, they can mark posts as read or unread.



<h3> Steps to Create a Wheel Installation Package </h3>

```
python -m pip install setuptools --force-reinstall
python -m pip install setuptools_scm
python -m pip install -r requirements.txt
python -m pip install wheel
python setup.py bdist_wheel
```