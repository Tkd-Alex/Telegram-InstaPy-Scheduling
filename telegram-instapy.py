#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Import module
import logging, threading, time, json, datetime, random, sys, os

from telegram.ext import Updater, CommandHandler, Job
from instapy import InstaPy
from ConfigParser import SafeConfigParser

# Create folder
if not os.path.exists("telegram-bot-data"):
    os.makedirs("telegram-bot-data")

config = SafeConfigParser()
config.read('telegram-bot-data/config.ini')

telegram_token = config.get('telegram', 'token');

# Redirect to null
old_stdout = sys.stdout
sys.stdout = open(os.devnull, 'w')

# Create empty thread variable
thread_instaPy = None

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Declare thread
class customThread (threading.Thread):
    def __init__(self, name):
    	threading.Thread.__init__(self)
        self.name = name
    def setTelegram(self, bot, job):
        self.bot = bot
        self.job = job
    def run(self):
        # Redirect stout to file
        sys.stdout = open('telegram-bot-data/log-file.txt', 'wb')

        start = datetime.datetime.now().replace(microsecond=0)
        print("InstaPy Bot start at {}".format(time.strftime("%X")))
        self.bot.send_message(self.job.context, text='InstaPy Bot start at {}'.format(time.strftime("%X")))
        
        threadRun()

        endTime = time.strftime("%X")
        end = datetime.datetime.now().replace(microsecond=0)
        print("InstaPy Bot end at {}\nExecution time {}".format(endTime, end-start))
        #self.bot.send_message(self.job.context, text='InstaPy Bot end at {}! Execution time {}'.format(time.strftime("%X"), end-start))
        
        sys.stdout.flush()
        time.sleep(1)

        # Read the last 9 line to get ended status of InstaPy.
        with open('telegram-bot-data/log-file.txt', "r") as f:
            f.seek (0, 2)                   # Seek @ EOF
            fsize = f.tell()                # Get Size
            f.seek (max (fsize-1024, 0), 0) # Set pos @ last n chars
            lines = f.readlines()           # Read to end

        lines = lines[-9:]                  # Get last 9 lines
        message = ''.join(str(x) for x in lines)
        self.bot.send_message(self.job.context, text=message)

        # Come back to null
        sys.stdout = open(os.devnull, 'w')	


def help(bot, update):
    update.message.reply_text('Hi! Use /set to start the bot')

def threadRun():
    try:
        # Reset random
        random.seed(9001)

        # Get instagram data from config.ini
        insta_username = config.get('instapy', 'username');
        insta_password = config.get('instapy', 'password');
        
        # Login
        session = InstaPy(username=insta_username, password=insta_password, nogui=True, page_delay=30)
        session.login()

        # Comments
        session.set_do_comment(enabled=True, percentage=random.randint(45,60))
        comments = []
        # Read comments from file and shuffle
        with open('telegram-bot-data/resources/comments.txt') as f:
            for line in f:
                comments.append(line.strip("\n"))
        random.shuffle(comments)
        
        session.set_comments(comments)

        # Follow
        session.set_do_follow(enabled=True, percentage=random.randint(45,60), times=3)
        session.set_user_interact(amount=10, random=True, percentage=random.randint(55,70), media='Photo')

        # Unfollow
        session.unfollow_users(amount=random.randint(10,20), onlyInstapyFollowed=True)

        # Limits
        #session.set_lower_follower_count(limit = 800)
        #session.set_upper_follower_count(limit = 2500)

        # Like
        hashtags = []
        # Read hashtags from file and shuffle
        with open('telegram-bot-data/resources/hashtags_' + str(random.randint(1,6)) +'.txt') as f:
            for line in f:
                hashtags.append(line.strip("\n"))
        random.shuffle(hashtags)
        
        session.like_by_tags(hashtags, amount=random.randint(6,12))
        
        session.end()
    except:
        import traceback
        print(traceback.format_exc())

def execThread(bot, job):
    # If thread is not alive or not create start it.
    if not thread_instaPy or not thread_instaPy.isAlive():
        global thread_instaPy
        thread_instaPy = customThread("Thread-InstaPy")
        thread_instaPy.setTelegram(bot, job)
        thread_instaPy.start()
    else:
        bot.send_message(job.context, text='Bot already executing!')

def statusThread(bot, update):
    # Responde with the status of thread.
    if not thread_instaPy or not thread_instaPy.isAlive():
        update.message.reply_text('InstaPy bot is OFF')
    else:
        update.message.reply_text('InstaPy bot is ON')

def set(bot, update, args, job_queue, chat_data):
    # Set a new job
    try:
        chat_id = update.message.chat_id
        name_job = args[0]
        time = args[1].split(':')

        job = job_queue.run_daily(execThread, datetime.time(int(time[0]), int(time[1]), int(time[2])), context=chat_id, name=name_job)
        chat_data[name_job] = job

        update.message.reply_text('Job setted!')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /set <name_job> <h:m:s>')

def unset(bot, update, args, chat_data):
    # Remove a job from list
    try:
        name_job = args[0]
        if not name_job in chat_data:
            update.message.reply_text('Job not found!')
            return

        job = chat_data[name_job]
        job.schedule_removal()
        del chat_data[name_job]

        update.message.reply_text('Job successfully unset!')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /unset <name_job>')


def print_job(bot, update, chat_data):
    # Print the list of jobs
    update.message.reply_text(str(chat_data))

def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))


def main():
    updater = Updater(telegram_token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", help))
    dp.add_handler(CommandHandler("help", help))

    dp.add_handler(CommandHandler("status", statusThread))

    dp.add_handler(CommandHandler("set", set, pass_args=True, pass_job_queue=True, pass_chat_data=True))

    dp.add_handler(CommandHandler("unset", unset, pass_args=True, pass_chat_data=True))
    dp.add_handler(CommandHandler("print", print_job, pass_chat_data=True))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    print("-- BOT STARTED -- at {}".format(datetime.datetime.now().replace(microsecond=0)))
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
