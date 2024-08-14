#!/usr/bin/env python3

__author__ = "Christian Heider Lindbjerg"

import time


def benchmark_func(func, times=100000):
    """description"""
    start = time.time()
    result = None
    for _ in range(times):
        result = func()
    end = time.time()
    return end - start, result
