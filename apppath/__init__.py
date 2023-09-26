#!/usr/bin/env python3
# -*- coding: utf-8 -*-

try:
    from importlib.resources import files
    from importlib.metadata import PackageNotFoundError
except (ModuleNotFoundError, ImportError) as e:
    from importlib_metadata import PackageNotFoundError
    from importlib_resources import files


from warg import package_is_editable, clean_string, get_version

__project__ = "Apppath"
__author__ = "Christian Heider Nielsen"
__version__ = "1.0.4"
__doc__ = r"""
Created on 27/04/2019

A class and a set of functions for providing for system-consensual path for apps to store data, logs, cache...

@author: cnheider
"""

__all__ = [
    "PROJECT_APP_PATH",
    "PROJECT_NAME",
    "PROJECT_VERSION",
    "PROJECT_ORGANISATION",
    "PROJECT_AUTHOR",
    "PROJECT_YEAR",
    "AppPath",
    "AppPathSubDirEnum",
    "open_app_path"
    # "INCLUDE_PROJECT_READMES",
    # "PACKAGE_DATA_PATH"
]

from .app_path import *
from .system_open_path_utilities import *

PROJECT_NAME = clean_string(__project__)
PROJECT_VERSION = __version__
PROJECT_YEAR = 2018
PROJECT_AUTHOR = clean_string(__author__)
PROJECT_ORGANISATION = clean_string("Pything")

PACKAGE_DATA_PATH = files(PROJECT_NAME) / "data"

try:
    DEVELOP = package_is_editable(PROJECT_NAME)
except PackageNotFoundError as e:
    DEVELOP = True


__version__ = get_version(__version__, append_time=DEVELOP)

__version_info__ = tuple(int(segment) for segment in __version__.split("."))

PROJECT_APP_PATH = AppPath(app_name=PROJECT_NAME, app_author=PROJECT_AUTHOR)

if __name__ == "__main__":
    print(__version__)
