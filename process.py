#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import multiprocessing, datetime, json, time
from scripts import scripts

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

class Process (multiprocessing.Process):
    def __init__(self, job_name, script_name, chat_id, bot, username, password, proxy=None):
        multiprocessing.Process.__init__(self)
        self.job_name = job_name
        self.script_name = script_name
        self.chat_id = chat_id 
        self.bot = bot
        self.username = username
        self.password = password
        self.proxy = proxy
    
    def return_attribute(self):
        return {
            "job_name": self.job_name,
            "script_name": self.script_name,
            "chat_id": self.chat_id ,
            "bot": self.bot,
            "user": {
                "username": self.username,
                "password": self.password,
                "proxy": self.proxy
            }
        }

    def run(self):
        start = datetime.datetime.now().replace(microsecond=0)
        self.bot.send_message(self.chat_id, text='InstaPy Bot - {} start at {}'.format(self.job_name, time.strftime("%X")))
        
        scripts[self.script_name](self.username, self.password, self.proxy)
        
        end = datetime.datetime.now().replace(microsecond=0)
        self.bot.send_message(self.chat_id, text='InstaPy Bot end at {}\nExecution time {}'.format(time.strftime("%X"), end-start))
        
        with open('logs/{}/general.log'.format(self.username), "r") as f:
            lines = f.readlines()
        
        self.bot.send_message(self.chat_id, text=parse_loglines( lines[-20:] ), parse_mode='HTML')