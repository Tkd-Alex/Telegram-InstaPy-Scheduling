import threading, datetime, json

class Thread (threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name
    
    def set_elegram(self, bot, chat_id):
        self.bot = bot
        self.chat_id = chat_id
    
    def run(self):
        start = datetime.datetime.now().replace(microsecond=0)
        self.bot.send_message(self.chat_id, text='InstaPy Bot - {} start at {}'.format(self.name, time.strftime("%X")))
        
        if self.name.lower() == "follow-trick":
        	instapy_script.follow_trick(config.get('instapy', 'username'), config.get('instapy', 'password'))
        else:
        	instapy_script.daily(config.get('instapy', 'username'), config.get('instapy', 'password'))

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