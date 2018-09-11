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

def reload_thread(thread):
    attribute = thread.return_attribute()
    new_thread = Thread(
        attribute['job_name'],
        attribute['script_name'],
        attribute['chat_id'],
        attribute['bot'],
        attribute['user']['username'],
        attribute['user']['password'],
        attribute['user']['proxy']
    )
    return 

def create_thread(bot, context):
    threads[context['job_name']] = Thread(
        context['job_name'],
        context['script_name'],
        context['chat_id'],
        bot,
        context['user']['username'],
        context['user']['password'],
        context['user']['proxy']
    )