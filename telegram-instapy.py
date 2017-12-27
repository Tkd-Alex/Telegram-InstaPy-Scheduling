#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Import module
import logging, threading, time, json, datetime, random, sys, os

from telegram.ext import Updater, CommandHandler, Job, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from instapy import InstaPy
from configparser import SafeConfigParser
from pprint import pprint

# Create folder
if not os.path.exists("telegram-bot-data"):
    os.makedirs("telegram-bot-data")

config = SafeConfigParser()
config.read('telegram-bot-data/config.ini')

telegram_token = config.get('telegram', 'token');

# Get allowed id
allowed_id = []
with open('telegram-bot-data/allowed-id.txt') as f:
    for line in f:
        allowed_id.append(line.strip("\n"))

# Create empty thread variable
global thread_instaPy 
thread_instaPy = None

# Declare thread
class customThread (threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name
    def setTelegram(self, bot, chat_id):
        self.bot = bot
        self.chat_id = chat_id
    def run(self):
        start = datetime.datetime.now().replace(microsecond=0)
        self.bot.send_message(self.chat_id, text='InstaPy Bot start at {}'.format(time.strftime("%X")))
        
        threadRun()

        endTime = time.strftime("%X")
        end = datetime.datetime.now().replace(microsecond=0)
        self.bot.send_message(self.chat_id, text='InstaPy Bot end at {}\nExecution time {}'.format(time.strftime("%X"), end-start))
        
        # Read the last 9 line to get ended status of InstaPy.
        with open('logs/general.log', "r") as f:
            f.seek (0, 2)                   # Seek @ EOF
            fsize = f.tell()                # Get Size
            f.seek (max (fsize-1024, 0), 0) # Set pos @ last n chars
            lines = f.readlines()           # Read to end

        lines = lines[-9:]                  # Get last 10 lines
        message = ''.join(str(x.replace("INFO - ", "")) for x in lines)
        self.bot.send_message(self.chat_id, text=message)


def help(bot, update):
    update.message.reply_text('Hi! Use /set to start the bot')

def threadRun():
    try:
        #################################################
        # Put your instaPy code, the following it's mine ;)
        #################################################

        # Reset random
        random.seed(9001)

        # Get instagram data from config.ini
        insta_username = config.get('instapy', 'username');
        insta_password = config.get('instapy', 'password');
        
        # Login
        session = InstaPy(username=insta_username, password=insta_password, headless_browser=True, page_delay=random.randint(24,31), show_logs=True)
        session.login()

        # Comments
        session.set_do_comment(enabled=True, percentage=random.randint(30,55))
        comments = []
        # Read comments from file and shuffle
        with open('telegram-bot-data/resources/comments.txt') as f:
            for line in f:
                comments.append(line.strip("\n"))
        random.shuffle(comments)
        session.set_comments(comments)

        # Follow
        session.set_do_follow(enabled=True, percentage=random.randint(10,25), times=3)
        session.set_user_interact(amount=random.randint(7,13), randomize=True, percentage=random.randint(20,80), media='Photo')

        # Unfollow
        session.unfollow_users(amount=random.randint(10,40), onlyInstapyFollowed=True, onlyInstapyMethod='FIFO', sleep_delay=random.randint(50,60))
        
        # Limits
        session.set_lower_follower_count(limit = 800)
        session.set_upper_follower_count(limit = 5000)

        # Like
        hashtags = []
        # Read hashtags from file and shuffle
        with open('telegram-bot-data/resources/hashtags_' + str(random.randint(1,6)) +'.txt') as f:
            for line in f:
                hashtags.append(line.strip("\n").replace('#',''))
        random.shuffle(hashtags)
        session.set_smart_hashtags(hashtags, limit=random.randint(3,8), sort='top', log_tags=False)
        session.like_by_tags(amount=random.randint(6,15), use_smart_hashtags=True)
        #session.like_by_tags(['love'], amount=3)
        
        session.end()
    except:
        import traceback
        print(traceback.format_exc())

def _execThread(bot, chat_id):
    # If thread is not alive or not create start it.
    global thread_instaPy
    if not thread_instaPy or not thread_instaPy.isAlive():
        thread_instaPy = customThread("Thread-InstaPy")
        thread_instaPy.setTelegram(bot, chat_id)
        thread_instaPy.start()
    else:
        bot.send_message(chat_id, text='Bot already executing!')

def execThread(bot, job):
    _execThread(bot, job.context)

def now(bot, update):
    _execThread(bot, update.message.chat_id)

def statusThread(bot, update):
    # Responde with the status of thread.
    if not thread_instaPy or not thread_instaPy.isAlive():
        update.message.reply_text('InstaPy bot is OFF')
    else:
        update.message.reply_text('InstaPy bot is ON')

def set(bot, update, args, job_queue, chat_data):
    # Set a new job
    chat_id = update.message.chat_id
    if str(chat_id) in allowed_id:
        try:
            data = {'name': args[0], 'schedule': args[1], 'days': []}
            chat_data['tmpjob'] = data

            keyboard = [[InlineKeyboardButton("Sunday", callback_data='6'),
                         InlineKeyboardButton("Monday", callback_data='0'),
                         InlineKeyboardButton("Tuesday", callback_data='1'),
                         InlineKeyboardButton("Wednesday", callback_data='2')],
                         [InlineKeyboardButton("Thursday", callback_data='3'),
                         InlineKeyboardButton("Friday", callback_data='4'),
                         InlineKeyboardButton("Saturday", callback_data='5')],
                        [InlineKeyboardButton("Everyday", callback_data='-1')]]
        
            update.message.reply_text('Choose a day: ', reply_markup = InlineKeyboardMarkup(keyboard))  
        except (IndexError, ValueError):
            update.message.reply_text('Usage: /set <name_job> <hh:mm:ss>')     
    else:
        message = 'You have not the permission to use this bot.\nFor more details visit [Telegram-InstaPy-Scheduling](https://github.com/Tkd-Alex/Telegram-InstaPy-Scheduling)'
        update.message.reply_text(message, parse_mode='Markdown')

def dayChoose(bot, update, job_queue, chat_data):
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    query = update.callback_query
    chat_id = query.message.chat_id
    time = chat_data['tmpjob']['schedule'].split(':')
    name_job = chat_data['tmpjob']['name']

    if query.data == '-1':
        job = job_queue.run_daily(execThread, datetime.time(int(time[0]), int(time[1]), int(time[2])), context=chat_id, name=name_job)
        data = { 'name': name_job, 'schedule': chat_data['tmpjob']['schedule'], 'job': job, 'days': "Everyday" }
        chat_data[name_job] = data
        del chat_data['tmpjob']

        bot.edit_message_text(text = "Job setted!",
                              chat_id = query.message.chat_id,
                              message_id = query.message.message_id)
    elif query.data == '-2':
        selectedDays = ", ".join([days[i] for i in chat_data['tmpjob']['days']])
        job = job_queue.run_daily(execThread, datetime.time(int(time[0]), int(time[1]), int(time[2])), days=tuple(chat_data['tmpjob']['days']), context=chat_id, name=name_job)
        data = { 'name': name_job, 'schedule': chat_data['tmpjob']['schedule'], 'job': job, 'days': selectedDays }
        chat_data[name_job] = data
        del chat_data['tmpjob']

        bot.edit_message_text(text = "Job setted!",
                              chat_id = query.message.chat_id,
                              message_id = query.message.message_id)
    else:
        if int(query.data) not in chat_data['tmpjob']['days']:
            chat_data['tmpjob']['days'].append(int(query.data))
        
        keyboard = [[InlineKeyboardButton("Sunday", callback_data='6'),
                     InlineKeyboardButton("Monday", callback_data='0'),
                     InlineKeyboardButton("Tuesday", callback_data='1'),
                     InlineKeyboardButton("Wednesday", callback_data='2')],
                     [InlineKeyboardButton("Thursday", callback_data='3'),
                     InlineKeyboardButton("Friday", callback_data='4'),
                     InlineKeyboardButton("Saturday", callback_data='5')],
                     [InlineKeyboardButton("Confirm", callback_data='-2')]]

        selectedDays = ", ".join([days[i] for i in chat_data['tmpjob']['days']])
        bot.edit_message_text(text = "Select another day or confirm:\n{}".format(selectedDays),
                              chat_id = query.message.chat_id,
                              message_id = query.message.message_id,
                              reply_markup = InlineKeyboardMarkup(keyboard))

def unset(bot, update, args, chat_data):
    # Remove a job from list
    try:
        name_job = args[0]
        if not name_job in chat_data:
            update.message.reply_text('Job not found!')
            return

        job = chat_data[name_job]["job"]
        job.schedule_removal()
        del chat_data[name_job]

        update.message.reply_text('Job successfully unset!')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /unset <name_job>')


def printJobs(bot, update, chat_data):
    # Print the list of jobs
    message = ""
    if len(chat_data) > 0:    
        for job in chat_data:
            message = message + "- *Name:* {} *Schedule at*: {} *Days:* {}\n".format(chat_data[job]["name"], chat_data[job]["schedule"], chat_data[job]["days"])
        update.message.reply_text(message, parse_mode='Markdown')
    else:
        update.message.reply_text("Job not setted")

def main():
    updater = Updater(telegram_token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", help))
    dp.add_handler(CommandHandler("help", help))

    dp.add_handler(CommandHandler("status", statusThread))

    dp.add_handler(CommandHandler("set", set, pass_args=True, pass_job_queue=True, pass_chat_data=True))
    dp.add_handler(CommandHandler("now", now))

    dp.add_handler(CommandHandler("unset", unset, pass_args=True, pass_chat_data=True))
    dp.add_handler(CommandHandler("print", printJobs, pass_chat_data=True))

    dp.add_handler(CallbackQueryHandler(dayChoose, pass_job_queue=True, pass_chat_data=True))

    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
