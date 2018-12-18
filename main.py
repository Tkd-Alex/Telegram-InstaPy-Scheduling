#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import module
import logging, time, json, datetime
import random, sys, os, pickle

# Telegram imports
from telegram.ext import Updater, CommandHandler, Job, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# New method for create multiple and different scripts
from scripts import scripts

# Process class in another file
from process import Process, reload_process

from stringparse import parse_time, clear_lines

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

# Create array with all process
process_array = {}

def help(bot, update):
    update.message.reply_text('Hi! Use /set to start the bot')

def logs(bot, update, args):
    if str(update.message.chat_id) in allowed_id:
        try:
            usernames = [ a['username'].lower() for a in users ]
            if not args[0].lower() in usernames:
                update.message.reply_text("Sorry, username <b>{}</b> is not saved.".format(args[0]), parse_mode='HTML')
                return
            logsline = int( args[1] )
            with open('{}/logs/{}/general.log'.format(settings['instapy_folder'], args[0].lower()), "r") as f:
                lines = f.readlines()
            lines = lines[-(logsline+20):] # Prevent empty lines
            message = '\n'.join(x for x in lines)
            message = clear_lines( '\n'.join(x for x in lines), username=args[0].lower() )
            lines = message.split('\n')[-logsline:]
            message = '\n'.join(x for x in lines)
            update.message.reply_text(message, parse_mode='HTML')

        except (IndexError, ValueError):
            update.message.reply_text('Usage: /logs <username> <logs_line>')
    else:
        message = 'You have not the permission to use this bot.\nFor more details visit [Telegram-InstaPy-Scheduling](https://github.com/Tkd-Alex/Telegram-InstaPy-Scheduling)'
        update.message.reply_text(message, parse_mode='Markdown')

def now(bot, update, args):
    if str(update.message.chat_id) in allowed_id:
        try:
            usernames = [ a['username'].lower() for a in users ]
            if not args[1].lower() in usernames:
                update.message.reply_text("Sorry, username <b>{}</b> is not saved.".format(args[1]), parse_mode='HTML')
                return

            if not args[0] in scripts:
                update.message.reply_text("Sorry, script named <b>{}</b> is not in your scripts file.".format(args[0]), parse_mode='HTML')
                return

            job_name = "{}_temp_{}".format(args[0], 1)
            for user in users:
                if user['username'].lower() == args[1].lower():
                    break
            process_array[job_name] = Process(
                settings['instapy_folder'],
                job_name,
                args[0],
                update.message.chat_id,
                bot,
                user['username'],
                user['password'],
                proxy=user['proxy']
            )
            process_array[job_name].start()       
        except (IndexError, ValueError):
            update.message.reply_text('Usage: /now <script_name> <username>')
    else:
        message = 'You have not the permission to use this bot.\nFor more details visit [Telegram-InstaPy-Scheduling](https://github.com/Tkd-Alex/Telegram-InstaPy-Scheduling)'
        update.message.reply_text(message, parse_mode='Markdown')

"""
def stop(bot, update, args):
    if str(update.message.chat_id) in allowed_id:
        try:
            if not args[0] in process_array:
                update.message.reply_text("Sorry, job named <b>{}</b> is not in jobs array.".format(args[0]), parse_mode='HTML')
                return

            if process_array[args[0]].is_alive():
                process_array[args[0]].end()
                update.message.reply_text("Job <b>{}</b> ended. Wait for process response".format(args[0]), parse_mode='HTML')

                time.sleep(10)
                del process_array[args[0]]
            else:
                pdate.message.reply_text("Job <b>{}</b> not running".format(args[0]), parse_mode='HTML')

        except (IndexError, ValueError):
            update.message.reply_text('Usage: /stop <job_name>')
    else:
        message = 'You have not the permission to use this bot.\nFor more details visit [Telegram-InstaPy-Scheduling](https://github.com/Tkd-Alex/Telegram-InstaPy-Scheduling)'
        update.message.reply_text(message, parse_mode='Markdown')
"""

def exec_process(bot, job):
    if process_array[job.name].is_alive():
        bot.send_message(process_array[job.name].chat_id, text="Sorry <b>{}</b> already executing!".format(job.name), parse_mode='HTML')
    else:
        process_array[job.name] = reload_process(process_array[job.name])
        process_array[job.name].start()

def create_process(bot, context):
    process_array[context['job_name']] = Process(
        settings['instapy_folder'],
        context['job_name'],
        context['script_name'],
        context['chat_id'],
        bot,
        context['user']['username'],
        context['user']['password'],
        proxy=context['user']['proxy']
    )

def status_process(bot, update, args):
    if str(update.message.chat_id) in allowed_id:
        if len(args) != 0:
            message = ""
            for arg in args:
                if arg in process_array:
                    message += "\n<b>Name:</b> {} <b>Account:</b> {} <b>Script:</b> {} <b>Status:</b> {}".format(
                    arg, process_array[arg].username, process_array[arg].script_name, "ON" if process_array[arg].is_alive() else "OFF"
                )
                else:
                    message += "\n<b>Name:</b> {} not found in process lists.".format(arg)
        else:
            message = "There are {} process configured.".format(len(process_array))
            index = 1
            for proc in process_array:
                message += "\n{}) <b>Name:</b> {} <b>Account:</b> {} <b>Script:</b> {} <b>Status:</b> {}".format(
                    index, proc, process_array[proc].username, process_array[proc].script_name, "ON" if process_array[proc].is_alive() else "OFF"
                )
                index += 1

        update.message.reply_text(message, parse_mode='HTML')
    else:
        message = 'You have not the permission to use this bot.\nFor more details visit [Telegram-InstaPy-Scheduling](https://github.com/Tkd-Alex/Telegram-InstaPy-Scheduling)'
        update.message.reply_text(message, parse_mode='Markdown')

def set(bot, update, args, job_queue, chat_data):
    if str(update.message.chat_id) in allowed_id:
        try:
            usernames = [ a['username'].lower() for a in users ]
            if not args[0].lower() in usernames:
                update.message.reply_text("Sorry, username <b>{}</b> is not saved.".format(args[0]), parse_mode='HTML')
                return

            if args[1] in chat_data or args[1] in process_array:
                update.message.reply_text("Sorry, job named <b>{}</b> is already used.".format(args[1]), parse_mode='HTML')
                return

            if not args[2] in scripts:
                update.message.reply_text("Sorry, script named <b>{}</b> is not in your scripts file.".format(args[2]), parse_mode='HTML')
                return

            data = {
                'username': args[0], 
                'job_name': args[1], 
                'script_name': args[2], 
                'scheduled': args[3], 
                'days': []
            }
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
    
    scheduled_time = parse_time(chat_data['tmpjob']['scheduled'])
    name_job = chat_data['tmpjob']['job_name']

    if query.data == '-1' or query.data == '-2':
        context = {
            "job_name": chat_data['tmpjob']['job_name'],
            "script_name": chat_data['tmpjob']['script_name'],
            "user": None,
            "chat_id": query.message.chat_id,
        }

        for user in users:
            if user['username'].lower() == chat_data['tmpjob']['username']:
                context['user'] = user
                break

        create_process(bot, context)
    
        if query.data == '-1':
            job = job_queue.run_daily(exec_process, scheduled_time, context=context, name=name_job)
        else:
            selected_days = ", ".join([days[i] for i in chat_data['tmpjob']['days']])
            job = job_queue.run_daily(exec_process, scheduled_time, days=tuple(chat_data['tmpjob']['days']), context=context, name=name_job)

        data = {
            'name': name_job,
            "script_name": chat_data['tmpjob']['script_name'],
            'scheduled': chat_data['tmpjob']['scheduled'],
            "username": chat_data['tmpjob']['username'],
            'job': job, 
            'days': "Everyday" if query.data == '-1' else selected_days 
        }
        chat_data[name_job] = data
        del chat_data['tmpjob']

        bot.edit_message_text(text="Job <b>{}</b> setted!".format(name_job), chat_id=query.message.chat_id, message_id=query.message.message_id, parse_mode='HTML')
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

        selected_days = ", ".join([days[i] for i in chat_data['tmpjob']['days']])
        bot.edit_message_text(text = "Select another day or confirm:\n{}".format(selected_days),
                            chat_id = query.message.chat_id,
                            message_id = query.message.message_id,
                            reply_markup = InlineKeyboardMarkup(keyboard))

def unset(bot, update, args, chat_data):
    if str(update.message.chat_id) in allowed_id:
        try:
            name_job = args[0]
            if name_job in chat_data and name_job in process_array:
                job = chat_data[name_job]["job"]
                job.schedule_removal()

                del process_array[name_job]
                del chat_data[name_job]

                update.message.reply_text('Job <b>{}</b> successfully unset!'.format(name_job), parse_mode='HTML')
            else:
                update.message.reply_text("Sorry, job named <b>{}</b> was not found.".format(name_job), parse_mode='HTML')
        except (IndexError, ValueError):
            update.message.reply_text('Usage: /unset <name_job>')   
    else:
        message = 'You have not the permission to use this bot.\nFor more details visit [Telegram-InstaPy-Scheduling](https://github.com/Tkd-Alex/Telegram-InstaPy-Scheduling)'
        update.message.reply_text(message, parse_mode='Markdown')

def list_jobs(bot, update, chat_data):
    message = ""
    if len(chat_data) > 0:    
        for job in chat_data:
            message = message + "- <b>Job name:</b> {} <b>Script name:</b> {} <b>Username:</b> {} <b>Schedule at</b>: {} <b>Days:</b> {}\n".format(
                chat_data[job]["name"], chat_data[job]["script_name"], chat_data[job]["username"], chat_data[job]["scheduled"], chat_data[job]["days"])
        update.message.reply_text(message, parse_mode='HTML')
    else:
        update.message.reply_text("You are 0 jobs setted")
    
def list_scripts(bot, update):
    message = "You have <b>{}</b> scripts configured.".format(len(scripts))
    index = 1
    for script in scripts:
        message += "\n{}) <b>{}</b>".format(index, script)
        index += 1
    update.message.reply_text(message, parse_mode='HTML')

def add_user(bot, update, args):
    if str(update.message.chat_id) in allowed_id:
        try:
            usernames = [ a['username'].lower() for a in users ]
            if args[0].lower() in usernames:
                update.message.reply_text("Sorry, username <b>{}</b> is already saved.".format(args[0]), parse_mode='HTML')
            else:
                users.append({
                    "username": args[0],
                    "password": args[1],
                    "proxy": None if len(args) < 3 else args[2] 
                })
                pickle.dump(users, open('users.pickle', 'wb'))
                update.message.reply_text("All done! <b>{}</b> correctly saved.".format(args[0]), parse_mode='HTML')
        except (IndexError, ValueError):
            update.message.reply_text('Usage: /add_user <username> <password> <proxy:optional> ')     
    else:
        message = 'You have not the permission to use this bot.\nFor more details visit [Telegram-InstaPy-Scheduling](https://github.com/Tkd-Alex/Telegram-InstaPy-Scheduling)'
        update.message.reply_text(message, parse_mode='Markdown')

def delete_user(bot, update, args):
    if str(update.message.chat_id) in allowed_id:
        try:
            usernames = [ a['username'].lower() for a in users ]
            if not args[0].lower() in usernames:
                update.message.reply_text("Sorry, username <b>{}</b> is not saved.".format(args[0]), parse_mode='HTML')
            else:
                for i in range(0, len(users)):
                    if users[i]['username'].lower() == args[0].lower():
                        del users[i]
                        break
                pickle.dump(users, open('users.pickle', 'wb'))
                update.message.reply_text("All done! <b>{}</b> correctly deleted.".format(args[0]), parse_mode='HTML')
        except (IndexError, ValueError):
            update.message.reply_text('Usage: /delete_user <username>')     
    else:
        message = 'You have not the permission to use this bot.\nFor more details visit [Telegram-InstaPy-Scheduling](https://github.com/Tkd-Alex/Telegram-InstaPy-Scheduling)'
        update.message.reply_text(message, parse_mode='Markdown')

def print_users(bot, update):
    if str(update.message.chat_id) in allowed_id:
        usernames = [ a['username'].lower() for a in users ]
        message = "You have <b>{}</b> accounts configured.".format(len(usernames))
        index = 1
        for username in usernames:
            message += "\n{}) <b>{}</b>".format(index, username)
            index += 1
        update.message.reply_text(message, parse_mode='HTML')
    else:
        message = 'You have not the permission to use this bot.\nFor more details visit [Telegram-InstaPy-Scheduling](https://github.com/Tkd-Alex/Telegram-InstaPy-Scheduling)'
        update.message.reply_text(message, parse_mode='Markdown')

if __name__ == '__main__':
    updater = Updater(telegram_token)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", help))
    dp.add_handler(CommandHandler("help", help))

    dp.add_handler(CommandHandler("status", status_process, pass_args=True))
    dp.add_handler(CommandHandler("logs", logs,  pass_args=True))

    dp.add_handler(CommandHandler("set", set, pass_args=True, pass_job_queue=True, pass_chat_data=True))
    dp.add_handler(CommandHandler("now", now, pass_args=True))
    # dp.add_handler(CommandHandler("stop", stop, pass_args=True))

    dp.add_handler(CommandHandler("unset", unset, pass_args=True, pass_chat_data=True))
    dp.add_handler(CommandHandler("jobs", list_jobs, pass_chat_data=True))

    dp.add_handler(CommandHandler("add_user", add_user, pass_args=True))
    dp.add_handler(CommandHandler("delete_user", delete_user, pass_args=True))
    dp.add_handler(CommandHandler("users", print_users))

    dp.add_handler(CommandHandler("scripts", list_scripts))

    dp.add_handler(CallbackQueryHandler(day_choose, pass_job_queue=True, pass_chat_data=True))

    updater.start_polling()

    updater.idle()
