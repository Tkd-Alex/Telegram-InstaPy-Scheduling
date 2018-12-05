#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading, datetime, json, time
from scripts import scripts
from thread_utils import parse_loglines

class Thread (threading.Thread):
    def __init__(self, job_name, script_name, chat_id, bot, username, password, proxy=None):
        threading.Thread.__init__(self)
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