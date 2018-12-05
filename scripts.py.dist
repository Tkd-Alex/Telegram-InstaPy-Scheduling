#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random, time, traceback, instapy

# Create your script here:
def awesome(username, password, proxy):
    try:
        session = instapy.InstaPy(username=username, password=password)
        session.login()
        session.end()
    except:
        print(traceback.format_exc())

def biglikers(username, password, proxy):
    try:
        session = instapy.InstaPy(username=username, password=password)
        session.login()
        session.end()
    except:
        print(traceback.format_exc())


# !! Not delete the following code.

functions = [f for fname, f in sorted(globals().items()) if callable(f)]
scripts = {}
for function in functions:
    scripts[str(function.__name__).lower()] = function