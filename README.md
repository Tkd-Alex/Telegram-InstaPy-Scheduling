# Telegram-InstaPy-Scheduling
Telegram-InstaPy-Scheduling is bot for telegram which helps user to schedule [*InstaPy*](https://github.com/timgrossmann/InstaPy).

### What do you need
- [*python-telegram-bot*](https://github.com/python-telegram-bot/python-telegram-bot)
- InstaPy working on your pc/server.
- Telegram bot token.

### How to setup
1. Create a bot with [@BotFather](https://telegram.me/BotFather).
2. Rename *telegram-bot-data/config.ini.dist* => *telegram-bot-data/config.ini*.
3. Populare *config.ini* with your data. 
```
[telegram]
token = token_from_botfather
[instapy]
username = instagram_username
password = isntagram_password
 ```
> You can leave empty instapy section and get credentials as you prefer.
4. Rename *telegram-bot-data/allowed-id.txt.dist* => *telegram-bot-data/allowed-id.txt*.
5. Contact [@GiveChatId_Bot](https://telegram.me/GiveChatId_Bot) and get your chat id with */chatid* command
6. Write your chat id inside *allowed-id.txt*.
7. Insert your InstaPy script code inside *threadRun* function.
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
8. Launch *telegram-instapy.py*.

### Avaiable commands
- **/set** <name> <time>: create a new schedule. Select day/days from bot.
- **/unset**: delete schedule.
- **/print**: print all setted job.
- **/status**: print the status of InstaPy.
