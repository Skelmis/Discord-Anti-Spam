# DPY Anti-Spam
---

[![Build Status](https://travis-ci.com/Skelmis/DPY-Anti-Spam.svg?branch=master)](https://travis-ci.com/Skelmis/DPY-Anti-Spam)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Ever felt the need to handle spammers in your discord, but don't have the time or effort to do so yourself? 
This package aims to help solve that issue by handling all the required logic under the hood, as well as handling the spammers heh.

*I decided to create this after seeing a d.js alternative but not one for d.py, as far as I know.*

---
#### This project is now at a useable state, albiet a little dodgy.
---

How to use this right now?

Download the codebase:
```
> git clone https://github.com/Skelmis/DPY-Anti-Spam.git
```

A basic bot
```python
from discord.ext import commands
from AntiSpam import AntiSpamHandler

bot = commands.Bot(command_prefix="!")
bot.handler = AntiSpamHandler(bot)

@bot.event
async def on_ready():
    print(f"-----\nLogged in as: {bot.user.name} : {bot.user.id}\n-----")

@bot.event
async def on_message(message):
    bot.handler.propagate(message)

if __name__ == "__main__":
    bot.run("Bot Token")
```

And thats it!
Now, there will no doubt be bugs & changes etc. But, you can use this as is now and all I ask is you create an issue for anything you encounter while using this codebase.



---

### Build Ideology:
- OOP approach 
- Scalable -> Multi guild support out of the box
- Test Driven -> CI with Travis

I hope to maintain the above, however, I currently am attempting to `only` create a `working version`. After such is created, I will begin optimizations, code refactoring and general improvements.

---

### Helping out:
All help is appreciated, just create an issue or pull request!
See contributing.md for more details.

### License
This project is licensed under the MIT license