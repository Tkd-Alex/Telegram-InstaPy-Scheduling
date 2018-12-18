#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import multiprocessing, datetime, json, time, os, sys
from stringparse import parse_loglines
from scripts import scripts

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

class Process (multiprocessing.Process):
    def __init__(self, instapy_path, job_name, script_name, chat_id, bot, username, password, proxy=None):
        multiprocessing.Process.__init__(self)
        self.instapy_path = instapy_path
        self.job_name = job_name
        self.script_name = script_name
        self.chat_id = chat_id 
        self.bot = bot
        self.username = username
        self.password = password
        self.proxy = proxy
    
    def return_attribute(self):
        return {
            "instapy_path": self.instapy_path,
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

    # self.bot.send_message does not work if called by the parent.
    def end(self, forced=True):
        if forced is True:
            self.terminate()
        
        end = datetime.datetime.now().replace(microsecond=0)
        self.bot.send_message(self.chat_id, text='InstaPy Bot end at {}\nExecution time {}'.format(time.strftime("%X"), end-self.start))
        
        with open('{}/logs/{}/general.log'.format(self.instapy_path, self.username), "r") as f:
            lines = f.readlines()
        
        message = parse_loglines( lines[-20:], self.username )
        self.bot.send_message(self.chat_id, text=message, parse_mode='HTML')
        
    def run(self):
        sys.path.append(self.instapy_path)  
        from instapy import InstaPy      

        self.start = datetime.datetime.now().replace(microsecond=0)
        self.bot.send_message(self.chat_id, text='InstaPy Bot - {} start at {}'.format(self.job_name, time.strftime("%X")))
        
        scripts[self.script_name](InstaPy, self.username, self.password, self.proxy)

        self.end(forced=False)
        