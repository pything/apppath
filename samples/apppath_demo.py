#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Christian Heider Lindbjerg"
__doc__ = r"""

           Created on 05/04/2020
           """

from apppath import AppPath

if __name__ == "__main__":

    def main():
        """description"""
        apppath = AppPath("AppPath")
        print(apppath.user_config)
        print(apppath.user_log)
        print(apppath.user_data)
        print(apppath.user_cache)

    main()
