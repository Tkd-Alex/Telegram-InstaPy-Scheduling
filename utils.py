#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime

def parse_time(time):
    time = time.split(":")
    h = int( time[0] )
    m = int( time[1] )
    s = int( time[2] )
    time = datetime.time(h, m, s)
    return time