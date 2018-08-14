#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import module
import logging, time, json, datetime, random, sys, os
from telegram.ext import Updater, CommandHandler, Job, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from pprint import pprint

# New method for create multiple and different scripts
from scripts import scripts

# Thread class in another file
from thread import Thread

# Create folder
if not os.path.exists("telegram-bot-data"):
    os.makedirs("telegram-bot-data")

telegram_token = open("telegram-bot-data/token.txt","r").read().strip()
allowed_id = open("telegram-bot-data/allowed-id.txt","r").read().split("\n")

# Create empty thread variable
global thread_instaPy 
thread_instaPy = None

def help(bot, update):
    update.message.reply_text('Hi! Use /set to start the bot')

def _execThread(bot, chat_id, name_job):
    # If thread is not alive or not create start it.
    global thread_instaPy
    if not thread_instaPy or not thread_instaPy.isAlive():
        thread_instaPy = Thread(name_job)
        thread_instaPy.setTelegram(bot, chat_id)
        thread_instaPy.start()
    else:
        bot.send_message(chat_id, text='Bot already executing!')

def execThread(bot, job):
	_execThread(bot, job.context, job.name)

def now(bot, update, args):
	if len(args) > 0:
		_execThread(bot, update.message.chat_id, args[0])
	else:
		_execThread(bot, update.message.chat_id, "Thread-Instapy")

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

def print_jobs(bot, update, chat_data):
    # Print the list of jobs
    message = ""
    if len(chat_data) > 0:    
        for job in chat_data:
            message = message + "- *Name:* {} *Schedule at*: {} *Days:* {}\n".format(chat_data[job]["name"], chat_data[job]["schedule"], chat_data[job]["days"])
        update.message.reply_text(message, parse_mode='Markdown')
    else:
        update.message.reply_text("Job not setted")

if __name__ == '__main__':
    updater = Updater(telegram_token)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", help))
    dp.add_handler(CommandHandler("help", help))

    dp.add_handler(CommandHandler("status", statusThread))

    dp.add_handler(CommandHandler("set", set, pass_args=True, pass_job_queue=True, pass_chat_data=True))
    dp.add_handler(CommandHandler("now", now, pass_args=True))

    dp.add_handler(CommandHandler("unset", unset, pass_args=True, pass_chat_data=True))
    dp.add_handler(CommandHandler("print", print_jobs, pass_chat_data=True))

    dp.add_handler(CallbackQueryHandler(day_choose, pass_job_queue=True, pass_chat_data=True))

    updater.start_polling()

    updater.idle()
