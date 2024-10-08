#!/usr/bin/env python3
import pytest

__author__ = "Christian Heider Lindbjerg"
__doc__ = ""

from apppath import AppPath

props = (
    "user_data",
    "user_config",
    "user_cache",
    "user_state",
    "user_log",
    "site_data",
    "site_config",
)


@pytest.mark.parametrize(
    ["app_name", "app_author"],
    (("MyApp", "cnheider"), ("YourApp", "you")),
    ids=["my", "you"],
)
def test_all(app_name: str, app_author: str):
    print("-- app dirs (with optional 'version')")
    dirs = AppPath(app_name, app_author, app_version="1.0", ensure_existence_on_access=False)
    for prop in props:
        print(f"{prop}: {getattr(dirs, prop)}")
    dirs.clean()


@pytest.mark.parametrize(
    ["app_name", "app_author"],
    (("MyApp", "cnheider"), ("YourApp", "you")),
    ids=["my", "you"],
)
def test_no_ver(app_name, app_author):
    print("\n-- app dirs (without optional 'version')")
    dirs = AppPath(app_name, app_author, ensure_existence_on_access=False)
    for prop in props:
        print(f"{prop}: {getattr(dirs, prop)}")
    dirs.clean()


@pytest.mark.parametrize(["app_name"], (("MyApp",), ("YourApp",)), ids=["my", "you"])
def test_author(app_name):
    print("\n-- app dirs (without optional '_app_author')")
    dirs = AppPath(app_name, ensure_existence_on_access=False)
    for prop in props:
        print(f"{prop}: {getattr(dirs, prop)}")
    dirs.clean()


@pytest.mark.parametrize(["app_name"], (("MyApp",), ("YourApp",)), ids=["my", "you"])
def test_no_author(app_name):
    print("\n-- app dirs (with disabled '_app_author')")
    dirs = AppPath(app_name, ensure_existence_on_access=False)
    for prop in props:
        print(f"{prop}: {getattr(dirs, prop)}")
    dirs.clean()


IGNORE = """
@pytest.fixture(autouse=True)
def run_around_tests():
    #Before

    yield

    #After
"""
