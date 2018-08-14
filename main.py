#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import module
import logging, time, json, datetime, random, sys, os, pickle
from telegram.ext import Updater, CommandHandler, Job, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from pprint import pprint

# New method for create multiple and different scripts
from scripts import scripts

# Thread class in another file
from thread import Thread

# Load settings
with open('settings.json') as f:
    settings = json.load(f)

telegram_token = settings['telegram_token']
allowed_id = settings['allowed_id']

# Load users
try:
    users = pickle.load(open('users.pickle', 'rb'))
except (FileNotFoundError, IOError):
    users = []
    pickle.dump(users, open('users.pickle', 'wb'))

# Create array with all threads
threads = {}

def help(bot, update):
    update.message.reply_text('Hi! Use /set to start the bot')

# def _execThread(bot, chat_id, name_job):
#     # If thread is not alive or not create start it.
#     global thread_instaPy
#     if not thread_instaPy or not thread_instaPy.isAlive():
#         thread_instaPy = Thread(name_job)
#         thread_instaPy.set_telegram(bot, chat_id)
#         thread_instaPy.start()
#     else:
#         bot.send_message(chat_id, text='Bot already executing!')

# def execThread(bot, job):
# 	_execThread(bot, job.context, job.name)

# def now(bot, update, args):
# 	if len(args) > 0:
# 		_execThread(bot, update.message.chat_id, args[0])
# 	else:
# 		_execThread(bot, update.message.chat_id, "Thread-Instapy")

def status_thread(bot, update, args):
    if len(args) != 0:
        message = ""
        for arg in args:
            if arg in threads:
                message += "\nName: **{}**, Account: **{}**, Script: **{}**, Status: **{}**".format(
                arg, threads[arg].username, threads[arg].script, "ON" if threads[arg].isAlive() else "OFF"
            )
            else:
                message += "\nName: **{}** not found in thread lists.".format(arg)
    else:
        message = "There are {} threads configured.".format(len(threads))
        index = 1
        for thread in threads:
            message += "\n{}) Name: **{}**, Account: **{}**, Script: **{}**, Status: **{}**".format(
                index, thread, threads[thread].username, threads[thread].script, "ON" if threads[thread].isAlive() else "OFF"
            )
            index += 1

def set(bot, update, args, job_queue, chat_data):
    if str(update.message.chat_id) in allowed_id:
        try:
            data = {'username': args[0], 'job_name': args[1], 'job_name': args[2], 'scheduled': args[3], 'days': []}
            chat_data['tmpjob'] = data

            keyboard = [[InlineKeyboardButton("Sunday", callback_data='6'),
                         InlineKeyboardButton("Monday", callback_data='0'),
                         InlineKeyboardButton("Tuesday", callback_data='1'),
                         InlineKeyboardButton("Wednesday", callback_data='2')],
                         [InlineKeyboardButton("Thursday", callback_data='3'),
                         InlineKeyboardButton("Friday", callback_data='4'),
                         InlineKeyboardButton("Saturday", callback_data='5')],
                        [InlineKeyboardButton("Everyday", callback_data='-1')]]
        
            update.message.reply_text('Choose a day: ', reply_markup=InlineKeyboardMarkup(keyboard))  
        except (IndexError, ValueError):
            update.message.reply_text('Usage: /set <username> <job_name> <script_name> <hh:mm:ss>')     
    else:
        message = 'You have not the permission to use this bot.\nFor more details visit [Telegram-InstaPy-Scheduling](https://github.com/Tkd-Alex/Telegram-InstaPy-Scheduling)'
        update.message.reply_text(message, parse_mode='Markdown')

def day_choose(bot, update, job_queue, chat_data):
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

def list_josb(bot, update, chat_data):
    # Print the list of jobs
    message = ""
    if len(chat_data) > 0:    
        for job in chat_data:
            message = message + "- *Name:* {} *Schedule at*: {} *Days:* {}\n".format(chat_data[job]["name"], chat_data[job]["schedule"], chat_data[job]["days"])
        update.message.reply_text(message, parse_mode='Markdown')
    else:
        update.message.reply_text("Job not setted")

def list_scripts(bot, update):
    message = "You have **{}** scripts configured.".format(len(scripts))
    index = 1
    for script in scripts:
        message += "\n{}) {}".format(index, script)
        index += 1
    update.message.reply_text(message, parse_mode='Markdown')

def add_user(bot, update, args):
    if str(update.message.chat_id) in allowed_id:
        try:
            usernames = [ a['username'].lower() for a in users ]
            if args[0].lower() in usernames:
                update.message.reply_text("Sorry, username **{}** is already saved.".format(args[0]), parse_mode='Markdown')
            else:
                users.append({
                    "username": args[0],
                    "password": args[1],
                    "proxy": None if len(args) < 3 else args[2] 
                })
                pickle.dump(users, open('users.pickle', 'wb'))
                update.message.reply_text("All done! **{}** correctly saved.".format(args[0]), parse_mode='Markdown')
        except (IndexError, ValueError):
            update.message.reply_text('Usage: /add_user <username> <password> <proxy:optional> ')     
    else:
        message = 'You have not the permission to use this bot.\nFor more details visit [Telegram-InstaPy-Scheduling](https://github.com/Tkd-Alex/Telegram-InstaPy-Scheduling)'
        update.message.reply_text(message, parse_mode='Markdown')

if __name__ == '__main__':
    updater = Updater(telegram_token)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", help))
    dp.add_handler(CommandHandler("help", help))

    dp.add_handler(CommandHandler("status", status_thread, pass_args=True))

    dp.add_handler(CommandHandler("set", set, pass_args=True, pass_job_queue=True, pass_chat_data=True))
    # dp.add_handler(CommandHandler("now", now, pass_args=True))

    dp.add_handler(CommandHandler("unset", unset, pass_args=True, pass_chat_data=True))
    dp.add_handler(CommandHandler("jobs", list_josb, pass_chat_data=True))

    dp.add_handler(CommandHandler("add_user", add_user, pass_chat_data=True))

    dp.add_handler(CommandHandler("scripts", list_scripts))

    dp.add_handler(CallbackQueryHandler(day_choose, pass_job_queue=True, pass_chat_data=True))

    updater.start_polling()

    updater.idle()
