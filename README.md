# Telegram-InstaPy-Scheduling v2!
Telegram-InstaPy-Scheduling is bot for telegram which helps user to schedule [*InstaPy*](https://github.com/timgrossmann/InstaPy).

### What's new?
- Run multiple scripts simultaneously.
- Configure your scripts in an easy way!
- Create user lists.

### What you need
- This repo and all _requirements.txt_ installed.
- InstaPy working on your pc/server.
- Telegram bot token.

### How to setup
1. Create a bot with [@BotFather](https://telegram.me/BotFather).
2. Rename *settings.json.dist* => *settings.json*.
3. Contact [@GiveChatId_Bot](https://telegram.me/GiveChatId_Bot) and get your chat id with */chatid* command
1. Clone this repo into any folder
1. Install requirements with `pip install -r requirements.txt`
4. Populate *settings.json* with your data. `instapy_folder` is the path to your InstaPy installation.
```
{
    "telegram_token": "xxxx",
    "instapy_folder": "/home/xxxx/GitHub/instapy_bot",
    "allowed_id": [ "chat_id from GiveChatId_Bot", "342342" ],
    "project_path": [ "/path_where_you_want_load_your_files" ], # Optional, default: ./
    "users_file": "new_user_list_file.pickle"                   # Optional, default: users.pickle
}
```
5. Write your personal scripts:
#### How? 
- Rename *scripts.py.dist* in *scripts.py* and edit it.
- Create a function with any name and copy your InstaPy script inside it, for example **(Make sure your first param is InstaPy)**:
```python
def script_for_big_like(InstaPy, username, password, proxy):
    session = InstaPy(username=username, password=password)
    session.login()
    
    # your stuff here, e.g.
    session.like_by_tags(['natgeo', 'world'], amount=10)
    
    session.end()
```
- Save and exit.
- Launch *main.py*. You can pass the *settings.json* from outside this folder, print help: *main.py -h* for other info.

### Avaiable commands
#### Users management
| Command      | Parameters                                    | Description           |
|--------------|-----------------------------------------------|-----------------------|
| /add_user    | \<username\> \<password\> \<proxy:optional\>  | Save new user.        |
| /delete_user | \<username\>                                  | Delete an user.       |
| /users       |                                               | Print all users saved |

#### Jobs management
| Command  | Parameters                                             | Description                                      |
|----------|--------------------------------------------------------|--------------------------------------------------|
| /set     | \<username\> \<job_name\> \<script_name\> \<hh:mm:ss\> | Create a new schedule. Select the day from bot.  |
| /unset   | \<job_name\>                                           | Delete a schedule.                               |
| /jobs    |                                                        | Print all jobs that have been set                |
| /reload  |                                                        | Jobs are saved in db now. Use this cmd to reload.|
| /scripts |                                                        | Print all your scripts                           |
| /status  | \<job_name:optional\>                                  | Print the status of all your thread or a single thread.   |
| /logs    | \<username\> \<line_number\>                           | Show n lines of username/general.log file.       |
| /now     | \<script_name\> \<username\>                           | Run immediately.                                 |
| /stop    | \<job_name\>                                           | Stop immediately.                                |

