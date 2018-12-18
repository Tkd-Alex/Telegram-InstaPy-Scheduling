#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime, re

def parse_time(time):
    time = time.split(":")
    h = int( time[0] )
    m = int( time[1] )
    s = int( time[2] )
    time = datetime.time(h, m, s)
    return time

"""
INFO [2018-12-05 19:22:48] [tkd_alex]  Sessional Live Report:
        |> LIKED 62 images  |  ALREADY LIKED: 1
        |> COMMENTED on 0 images
        |> FOLLOWED 25 users  |  ALREADY FOLLOWED: 0
        |> UNFOLLOWED 0 users
        |> INAPPROPRIATE images: 344
        |> NOT VALID users: 142
On session start was FOLLOWING 6708 users & had 17371 FOLLOWERS

OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO
INFO [2018-12-05 19:22:48] [tkd_alex]  Session ended!
oooooooooooooooooooooooooooooooooooooooooooooooooooo
"""
def parse_loglines(lines):
    # Merge the string by new line char. Keep the text between 'sessional live report' and 'OOOOOO'
    message = '\n'.join(x for x in lines)
    message = message[message.find('Sessional Live Report'):message.find('OOOOOO')]
    lines = message.split('\n')
    message = '\n'.join(x.strip() for x in lines if x.strip() != "")
    for boldword in [ "LIKED", "COMMENTED", "FOLLOWED", "UNFOLLOWED", "INAPPROPRIATE", "NOT VALID" ]:
        message = message.replace("ALREADY {}".format(boldword), "<b>ALREADY {}</b>".format(boldword))
        message = message.replace("|> {}".format(boldword), "|> <b>{}</b>".format(boldword))
    return message