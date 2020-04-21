#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import module
import logging
import time
import json
import datetime
import random
import sys
import os
import pickle
import plac
import subprocess

# Colored terminal
from termcolor import colored, cprint

# Database Jobs and Users storage
from tinydb import TinyDB, Query

# Telegram imports
from telegram.ext import Updater, CommandHandler, Job, CallbackQueryHandler, MessageHandler, Filters, ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove

# Process class in another file
from process import Process, reload_process

from stringparse import parse_time, clear_lines
import utils
from codecs import open

# Create array of all users
users = []
# Create dictionary with all process
process_array = {}
# Create dictionary of all scripts availables
scripts = {}

dict_settings = {
    "telegram_token": None,
    "allowed_id": None,
    "instapy_folder": None,
    "users_path": "users.pickle",
    "project_path": "./"
}

database = None

profiles = ["example1", "example2", "example3"]
var = [0]
n = len(profiles)
keyboard = var[:]*n

def start(bot, update):
    for x in range(len(profiles)):
        keyboard[x] = [InlineKeyboardButton(profiles[x], callback_data=profiles.index(profiles[x]))]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Please choose:', reply_markup=reply_markup)


def button(bot, update):
    query = update.callback_query
    query.edit_message_text((query.data))
    if (query.data) == 1:
        list_scripts(bot, update)


def help(bot, update):
    reply_keyboard = [['/now', '/users', '/set']]
    update.message.reply_text('Hello {}. What you want to do today?'.format(update.message.from_user.first_name),
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

# To display server date and time


def timenow(bot, update):
    message = '<b>Current Date and Time:</b> ' + \
        '{0:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
    update.message.reply_text(message, parse_mode='HTML')


def logs(bot, update, args):
    if str(update.message.chat_id) in dict_settings['allowed_id']:
        try:
            usernames = [a['username'].lower() for a in users]
            if not args[0].lower() in usernames:
                update.message.reply_text(
                    "Sorry, username <b>{}</b> is not saved.".format(args[0]), parse_mode='HTML')
                return
            logsline = int(args[1])
            with open('/home/elizaveta11perevalova_gmail_com/0.6.6/logs/{}/general.log'.format(dict_settings['instapy_folder'], args[0].lower()), "r", encoding="utf-8") as f:
                lines = f.readlines()
            lines = lines[-(logsline + 20):]  # Prevent empty lines
            message = '\n'.join(x for x in lines)
            message = clear_lines(
                '\n'.join(x for x in lines), username=args[0].lower())
            lines = message.split('\n')[-logsline:]
            message = '\n'.join(x for x in lines)
            update.message.reply_text(
                message, disable_web_page_preview=True, parse_mode='HTML')

        except (IndexError, ValueError):
            update.message.reply_text('Usage: /logs <username> <logs_line>')
    else:
        message = 'You have not the permission to use this bot.\nFor more details visit [Telegram-InstaPy-Scheduling](https://github.com/Tkd-Alex/Telegram-InstaPy-Scheduling)'
        update.message.reply_text(message, parse_mode='Markdown')


def now(bot, update, args):
    if str(update.message.chat_id) in dict_settings['allowed_id']:
        try:
            usernames = [a['username'].lower() for a in users]
            if not args[1].lower() in usernames:
                update.message.reply_text(
                    "Sorry, username <b>{}</b> is not saved.".format(args[1]), parse_mode='HTML')
                return

            if not args[0] in scripts:
                update.message.reply_text(
                    "Sorry, script named <b>{}</b> is not in your scripts file.".format(args[0]), parse_mode='HTML')
                return

            job_name = "{}_temp_{}".format(args[0], int(time.time()))
            for user in users:
                if user['username'].lower() == args[1].lower():
                    break

            process_array[job_name] = Process(
                dict_settings['instapy_folder'],
                job_name,
                args[0],
                update.message.chat_id,
                bot,
                user['username'],
                user['password'],
                scripts,
                proxy=user['proxy']
            )
            process_array[job_name].start()
        except (IndexError, ValueError):
            update.message.reply_text('Usage: /now <script_name> <username>')
    else:
        message = 'You have not the permission to use this bot.\nFor more details visit [Telegram-InstaPy-Scheduling](https://github.com/Tkd-Alex/Telegram-InstaPy-Scheduling)'
        update.message.reply_text(message, parse_mode='Markdown')


def stop(bot, update, args):
    if str(update.message.chat_id) in dict_settings['allowed_id']:
        try:
            if not args[0] in process_array:
                update.message.reply_text(
                    "Sorry, job named <b>{}</b> is not in jobs array.".format(args[0]), parse_mode='HTML')
                return

            if process_array[args[0]].is_alive():
                process_array[args[0]].end()
                update.message.reply_text(
                    "Job <b>{}</b> ended. Wait for process response".format(args[0]), parse_mode='HTML')
                time.sleep(3)
                del process_array[args[0]]
            else:
                update.message.reply_text(
                    "Job <b>{}</b> not running".format(args[0]), parse_mode='HTML')

        except (IndexError, ValueError):
            update.message.reply_text('Usage: /stop <job_name>')
    else:
        message = 'You have not the permission to use this bot.\nFor more details visit [Telegram-InstaPy-Scheduling](https://github.com/Tkd-Alex/Telegram-InstaPy-Scheduling)'
        update.message.reply_text(message, parse_mode='Markdown')


def exec_process(bot, job):
    if process_array[job.name].is_alive():
        bot.send_message(process_array[job.name].chat_id,
                         text="Sorry <b>{}</b> already executing!".format(job.name), parse_mode='HTML')
    else:
        process_array[job.name] = reload_process(
            process_array[job.name], scripts)
        process_array[job.name].start()


def create_process(bot, context):
    process_array[context['job_name']] = Process(
        dict_settings['instapy_folder'],
        context['job_name'],
        context['script_name'],
        context['chat_id'],
        bot,
        context['user']['username'],
        context['user']['password'],
        scripts,
        proxy=context['user']['proxy']
    )


def status_process(bot, update, args):
    if str(update.message.chat_id) in dict_settings['allowed_id']:
        if len(args) != 0:
            message = ""
            for arg in args:
                if arg in process_array:
                    message += "\n<b>Name:</b> {} <b>Account:</b> {} <b>Script:</b> {} <b>Status:</b> {}".format(
                        arg, process_array[arg].username, process_array[arg].script_name, "ON" if process_array[arg].is_alive(
                        ) else "OFF"
                    )
                else:
                    message += "\n<b>Name:</b> {} not found in process lists.".format(
                        arg)
        else:
            message = "There are {} process configured.".format(
                len(process_array))
            index = 1
            for proc in process_array:
                message += "\n{}) <b>Name:</b> {} <b>Account:</b> {} <b>Script:</b> {} <b>Status:</b> {}".format(
                    index, proc, process_array[proc].username, process_array[proc].script_name, "ON" if process_array[proc].is_alive(
                    ) else "OFF"
                )
                index += 1

        update.message.reply_text(message, parse_mode='HTML')
    else:
        message = 'You have not the permission to use this bot.\nFor more details visit [Telegram-InstaPy-Scheduling](https://github.com/Tkd-Alex/Telegram-InstaPy-Scheduling)'
        update.message.reply_text(message, parse_mode='Markdown')


def set_job(bot, update, args, job_queue, chat_data):
    if str(update.message.chat_id) in dict_settings['allowed_id']:
        try:
            usernames = [a['username'].lower() for a in users]
            if not args[0].lower() in usernames:
                update.message.reply_text(
                    "Sorry, username <b>{}</b> is not saved.".format(args[0]), parse_mode='HTML')
                return

            jobs_list = utils.return_elements(
                database, owner=str(update.message.chat_id), entity="job")
            if args[1] in chat_data or args[1] in jobs_list or args[1] in process_array:
                update.message.reply_text(
                    "Sorry, job named <b>{}</b> is already used.".format(args[1]), parse_mode='HTML')
                return

            if not args[2] in scripts:
                update.message.reply_text(
                    "Sorry, script named <b>{}</b> is not in your scripts file.".format(args[2]), parse_mode='HTML')
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

            update.message.reply_text(
                'Choose a day: ', reply_markup=InlineKeyboardMarkup(keyboard))
        except (IndexError, ValueError):
            update.message.reply_text(
                'Usage: /set <username> <job_name> <script_name> <hh:mm:ss>')

    else:
        message = 'You have not the permission to use this bot.\nFor more details visit [Telegram-InstaPy-Scheduling](https://github.com/Tkd-Alex/Telegram-InstaPy-Scheduling)'
        update.message.reply_text(message, parse_mode='Markdown')


def persistend_job(bot, job_queue, chat_data, days, chat_id, message_id=None, db_persist=True):
    if chat_data['tmpjob']['job_name'] not in chat_data:
        context = {
            "job_name": chat_data['tmpjob']['job_name'],
            "script_name": chat_data['tmpjob']['script_name'],
            "user": None,
            "chat_id": chat_id,
        }

        for user in users:
            if user['username'].lower() == chat_data['tmpjob']['username']:
                context['user'] = user
                break

        create_process(bot, context)
        job_name = chat_data['tmpjob']['job_name']
        scheduled_time = parse_time(chat_data['tmpjob']['scheduled'])

        # DAYS MANAGEMENT REQUIRE A REFACTORY.

        if chat_data['tmpjob']['days'] == "Everyday":
            job = job_queue.run_daily(
                exec_process, scheduled_time, context=context, name=job_name)
            selected_days = "Everyday"
        else:
            chat_data['tmpjob']['days'] = utils.fix_days(days)
            selected_days = ", ".join([utils.days[i]
                                       for i in chat_data['tmpjob']['days']])
            job = job_queue.run_daily(exec_process, scheduled_time, days=tuple(
                chat_data['tmpjob']['days']), context=context, name=job_name)

        data = {
            'name': job_name,
            "script_name": chat_data['tmpjob']['script_name'],
            'scheduled': chat_data['tmpjob']['scheduled'],
            "username": chat_data['tmpjob']['username'],
        }

        data['days'] = selected_days

        if db_persist is True:
            utils.save_element(database, data, owner=chat_id, entity="job")
            bot.edit_message_text(text="Job <b>{}</b> set!".format(job_name),
                                  chat_id=chat_id, message_id=message_id, parse_mode='HTML')
        else:
            bot.send_message(
                text="Job <b>{}</b> set!".format(job_name), chat_id=chat_id, parse_mode='HTML')

        data['job'] = job
        chat_data[job_name] = data
        del chat_data['tmpjob']


def day_choose(bot, update, job_queue, chat_data):
    query = update.callback_query
    if query.data == '-1' or query.data == '-2':
        chat_data['tmpjob']['days'] = "Everyday" if query.data == '-1' else chat_data['tmpjob']['days']
        persistend_job(bot, job_queue, chat_data, days=chat_data['tmpjob']['days'],
                       chat_id=query.message.chat_id, message_id=query.message.message_id)
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

        selected_days = ", ".join([utils.days[i]
                                   for i in chat_data['tmpjob']['days']])
        bot.edit_message_text(text="Select another day or confirm:\n{}".format(selected_days),
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id,
                              reply_markup=InlineKeyboardMarkup(keyboard))


def unset(bot, update, args, chat_data):
    if str(update.message.chat_id) in dict_settings['allowed_id']:
        try:
            job_name = args[0]
            if job_name in chat_data and job_name in process_array:
                job = chat_data[job_name]["job"]
                job.schedule_removal()

                del process_array[job_name]
                del chat_data[job_name]

                utils.delete_job(database, job_name,
                                 owner=str(update.message.chat_id))

                update.message.reply_text(
                    'Job <b>{}</b> successfully unset!'.format(job_name), parse_mode='HTML')
            else:
                update.message.reply_text(
                    "Sorry, job named <b>{}</b> was not found.".format(job_name), parse_mode='HTML')
        except (IndexError, ValueError):
            update.message.reply_text('Usage: /unset <job_name>')
    else:
        message = 'You have not the permission to use this bot.\nFor more details visit [Telegram-InstaPy-Scheduling](https://github.com/Tkd-Alex/Telegram-InstaPy-Scheduling)'
        update.message.reply_text(message, parse_mode='Markdown')


def reload_jobs(bot, update, job_queue, chat_data):
    if str(update.message.chat_id) in dict_settings['allowed_id']:
        jobs_list = utils.return_elements(
            database, owner=str(update.message.chat_id), entity="job")
        for singlejob in jobs_list:
            chat_data['tmpjob'] = singlejob
            chat_data['tmpjob']['job_name'] = chat_data['tmpjob']['name']
            persistend_job(bot, job_queue, chat_data,
                           days=chat_data['tmpjob']['days'], chat_id=update.message.chat_id, db_persist=False)
    else:
        message = 'You have not the permission to use this bot.\nFor more details visit [Telegram-InstaPy-Scheduling](https://github.com/Tkd-Alex/Telegram-InstaPy-Scheduling)'
        update.message.reply_text(message, parse_mode='Markdown')


def list_jobs(bot, update, chat_data):
    message = ""
    if len(chat_data) > 0:
        for job in chat_data:
            message = message + "<b>Job name:</b> {}\n<b>Script name:</b> {}\n<b>Username:</b> {}\n<b>Schedule at</b>: {}\n<b>Days:</b> {}\n==========\n".format(
                chat_data[job]["name"], chat_data[job]["script_name"], chat_data[job]["username"], chat_data[job]["scheduled"], chat_data[job]["days"])
        update.message.reply_text(message, parse_mode='HTML')
    else:
        update.message.reply_text(
            "You are <b>0</b> jobs set", parse_mode='HTML')


def list_scripts(bot, update):
    message = "You have <b>{}</b> scripts configured.".format(len(scripts))
    index = 1
    for script in scripts:
        message += "\n{}) <b>{}</b>".format(index, script)
        index += 1
    update.message.reply_text(message, parse_mode='HTML')


def add_user(bot, update, args):
    if str(update.message.chat_id) in dict_settings['allowed_id']:
        try:
            usernames = [a['username'].lower() for a in users]
            if args[0].lower() in usernames:
                update.message.reply_text(
                    "Sorry, username <b>{}</b> is already saved.".format(args[0]), parse_mode='HTML')
            else:
                users.append({
                    "username": args[0],
                    "password": args[1],
                    "proxy": None if len(args) < 3 else args[2]
                })
                pickle.dump(users, open('users.pickle', 'wb'))
                update.message.reply_text(
                    "All done! <b>{}</b> correctly saved.".format(args[0]), parse_mode='HTML')
        except (IndexError, ValueError):
            update.message.reply_text(
                'Usage: /add_user <username> <password> <proxy:optional> ')
    else:
        message = 'You have not the permission to use this bot.\nFor more details visit [Telegram-InstaPy-Scheduling](https://github.com/Tkd-Alex/Telegram-InstaPy-Scheduling)'
        update.message.reply_text(message, parse_mode='Markdown')


def delete_user(bot, update, args):
    if str(update.message.chat_id) in dict_settings['allowed_id']:
        try:
            usernames = [a['username'].lower() for a in users]
            if not args[0].lower() in usernames:
                update.message.reply_text(
                    "Sorry, username <b>{}</b> is not saved.".format(args[0]), parse_mode='HTML')
            else:
                for i in range(0, len(users)):
                    if users[i]['username'].lower() == args[0].lower():
                        del users[i]
                        break
                pickle.dump(users, open('users.pickle', 'wb'))
                update.message.reply_text(
                    "All done! <b>{}</b> correctly deleted.".format(args[0]), parse_mode='HTML')
        except (IndexError, ValueError):
            update.message.reply_text('Usage: /delete_user <username>')
    else:
        message = 'You have not the permission to use this bot.\nFor more details visit [Telegram-InstaPy-Scheduling](https://github.com/Tkd-Alex/Telegram-InstaPy-Scheduling)'
        update.message.reply_text(message, parse_mode='Markdown')


def print_users(bot, update):
    if str(update.message.chat_id) in dict_settings['allowed_id']:
        usernames = [a['username'].lower() for a in users]
        message = "You have <b>{}</b> accounts configured.".format(
            len(usernames))
        index = 1
        for username in usernames:
            message += "\n{}) <b>{}</b>".format(index, username)
            index += 1
        update.message.reply_text(message, parse_mode='HTML')
    else:
        message = 'You have not the permission to use this bot.\nFor more details visit [Telegram-InstaPy-Scheduling](https://github.com/Tkd-Alex/Telegram-InstaPy-Scheduling)'
        update.message.reply_text(message, parse_mode='Markdown')


def error(bot, update, error):
    logger.error('Update "%s" caused error "%s"' % (update, error))


@plac.annotations(setting_file=("Path of settings.json file", "option", "s", str))
def main(setting_file='settings.json'):
    global scripts
    global users
    global dict_settings
    global database

    try:
        cprint("Load setting file from: \"%s\"" % setting_file, "green")
        with open(setting_file) as f:
            settings_json = json.load(f)
    except (FileNotFoundError):
        cprint("[ERROR] %s is not defined!" % setting_file, "red")
        sys.exit(1)

    for key in dict_settings:
        result, value, message = utils.safe_load_settings(key, settings_json)
        if result is False:
            cprint("[ERROR] {}".format(message), "red")
            if key not in ["telegram_token", "instapy_folder", "allowed_id"]:
                cprint("[WARNING] Load default value of: {} : {}".format(
                    key, dict_settings[key]), "yellow")
            else:
                sys.exit()
        else:
            dict_settings[key] = value
            cprint("[SUCCESS] {}".format(message), "green")

    if dict_settings['project_path'] != "./":
        sys.path.insert(0, dict_settings['project_path'])

    try:
        from scripts import Scripts
    except (ModuleNotFoundError):
        cprint("[ERROR] Require \"scripts.py\" file!", "red")
        sys.exit(1)

    scripts = Scripts().scripts

    try:
        users = pickle.load(
            open(dict_settings['project_path'] + dict_settings['users_path'], 'rb'))
        cprint("[SUCCESS] Load users list from: {}".format(
            dict_settings['users_path']), "green")
    except (FileNotFoundError, IOError):
        pickle.dump(users, open(
            dict_settings['project_path'] + dict_settings['users_path'], 'wb'))
        cprint("[WARNING] Init user list in: {}".format(
            dict_settings['users_path']), "yellow")

    database = TinyDB('./db.json')

    updater = Updater(dict_settings['telegram_token'], request_kwargs={
                      'read_timeout': 20, 'connect_timeout': 20})

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    dp.add_handler(CommandHandler("status", status_process, pass_args=True))
    dp.add_handler(CommandHandler("logs", logs,  pass_args=True))

    dp.add_handler(CommandHandler("set", set_job, pass_args=True,
                                  pass_job_queue=True, pass_chat_data=True))
    dp.add_handler(CommandHandler("now", now, pass_args=True))
    dp.add_handler(CommandHandler("stop", stop, pass_args=True))

    dp.add_handler(CommandHandler(
        "unset", unset, pass_args=True, pass_chat_data=True))
    dp.add_handler(CommandHandler("jobs", list_jobs, pass_chat_data=True))
    dp.add_handler(CommandHandler("reload", reload_jobs,
                                  pass_job_queue=True, pass_chat_data=True))

    dp.add_handler(CommandHandler("add_user", add_user, pass_args=True))
    dp.add_handler(CommandHandler("delete_user", delete_user, pass_args=True))
    dp.add_handler(CommandHandler("users", print_users))

    dp.add_handler(CommandHandler("scripts", list_scripts))

    dp.add_handler(CommandHandler("time", timenow))

    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(CallbackQueryHandler(
        day_choose, pass_job_queue=True, pass_chat_data=True))

    dp.add_error_handler(error)

    updater.start_polling(timeout=25)

    cprint("TELEGRAM-INSTAPY-SCHEDULING IS READY!", "green")

    updater.idle()

    sys.exit(0)


if __name__ == '__main__':
    plac.call(main)
