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
_____________________________________________________________

INFO [2018-12-16 18:28:29] [tkd_alex]  --> Total people unfollowed : 397

"""

def username_stripper(line, username):
    line = line[line.find("[{}]".format(username)):]
    line = line.replace("[{}]".format(username), "")
    return line.strip()

def clear_lines(message, username=None):
    lines = message.replace('-->', '').split('\n') # Remove arrow
    # Clear lines, remove space and INFO [2018-12-16 18:28:29] [tkd_alex]
    message = '\n'.join( ( line.strip() if username is None else username_stripper(line, username) )  for line in lines if line.strip() != "")
    return message

def parse_loglines(lines, username=None):
    # Merge the string by new line char. Keep the text between 'sessional live report' and 'OOOOOO'
    message = '\n'.join(x for x in lines)
    if 'Session ended!' in message:
        message = message[message.find('Sessional Live Report'):message.find('OOOOOO')]
        lines = message.split('\n')
        message = '\n'.join(line.strip() for line in lines if line.strip() != "")
        for boldword in [ "LIKED", "COMMENTED", "FOLLOWED", "UNFOLLOWED", "INAPPROPRIATE", "NOT VALID" ]:
            message = message.replace("ALREADY {}".format(boldword), "<b>ALREADY {}</b>".format(boldword))
            message = message.replace("|> {}".format(boldword), "|> <b>{}</b>".format(boldword))
        return message
    else:
        message = clear_lines(message, username)
        return message.split('\n')[-1] # Return the last line of logs.