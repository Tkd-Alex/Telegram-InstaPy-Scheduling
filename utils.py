#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime, re
from process import Process

def parse_time(time):
    time = time.split(":")
    h = int( time[0] )
    m = int( time[1] )
    s = int( time[2] )
    time = datetime.time(h, m, s)
    return time

def reload_process(process):
    attribute = process.return_attribute()
    new_process = Process(
        attribute['instapy_path'],
        attribute['job_name'],
        attribute['script_name'],
        attribute['chat_id'],
        attribute['bot'],
        attribute['user']['username'],
        attribute['user']['password'],
        proxy=attribute['user']['proxy']
    )
    return new_process


