# Telegram-InstaPy-Scheduling
Telegram-InstaPy-Scheduling is bot for telegram which helps user to schedule [*InstaPy*](https://github.com/timgrossmann/InstaPy).

### What do you need
- [*python-telegram-bot*](https://github.com/python-telegram-bot/python-telegram-bot)
- InstaPy working on your pc/server.
- Telegram bot token.

### How to setup
1. Clone this repo in your InstaPy folder.
2. Create a bot with [@BotFather](https://telegram.me/BotFather).
3. Rename *telegram-bot-data/config.ini.dist* => *telegram-bot-data/config.ini*.
4. Populate *config.ini* with your data. 
```
[telegram]
token = token_from_botfather
[instapy]
username = instagram_username
password = isntagram_password
 ```
> You can leave empty instapy section and get credentials as you prefer.
5. Rename *telegram-bot-data/allowed-id.txt.dist* => *telegram-bot-data/allowed-id.txt*.
6. Contact [@GiveChatId_Bot](https://telegram.me/GiveChatId_Bot) and get your chat id with */chatid* command
7. Write your chat id inside *allowed-id.txt*.
8. Insert your InstaPy script code inside *threadRun* function.
```python
def threadRun():
    try:
        #################################################
        # Put your instaPy code, the following it's mine ;)
        #################################################
        
        # Get instagram data from config.ini
        insta_username = config.get('instapy', 'username');
        insta_password = config.get('instapy', 'password');
        
        # Login
        session = InstaPy(username=insta_username, password=insta_password, nogui=True)
        session.login()

        # Like
        hashtags = ["#telegram"]
        session.like_by_tags(hashtags, amount=5)
        
        session.end()
    except:
        import traceback
        print(traceback.format_exc())
```
9. Launch *telegram-instapy.py*.

### Avaiable commands
| Command | Parameters              | Description                                      |
|---------|-------------------------|--------------------------------------------------|
| /set    | \<name\> \<hh:mm:ss\>   | Create a new schedule. Select the day from bot.  |
| /unset  | \<name\>                | Delete a schedule.                               |
| /print  |                         | Print all setted jobs                            |
| /status |                         | Print the status of InstaPy.                     |

