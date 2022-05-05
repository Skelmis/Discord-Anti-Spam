# DPY Anti-Spam
---

[![Pytest](https://github.com/Skelmis/DPY-Anti-Spam/actions/workflows/pytest.yml/badge.svg?branch=master)](https://github.com/Skelmis/DPY-Anti-Spam/actions/workflows/pytest.yml)
[![Coverage Status](https://coveralls.io/repos/github/Skelmis/Discord-Anti-Spam/badge.svg?branch=master)](https://coveralls.io/github/Skelmis/Discord-Anti-Spam?branch=master)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI download month](https://img.shields.io/pypi/dm/Discord-Anti-Spam.svg)](https://pypi.python.org/pypi/Discord-Anti-Spam/)
[![Discord](https://img.shields.io/discord/780784732484141077.svg?label=&logo=discord&logoColor=ffffff&color=7389D8&labelColor=6A7EC2)](https://discord.gg/BqPNSH2jPg)

Ever felt the need to handle spammers in your discord, but don't have the time or effort to do so yourself? 
This package aims to help solve that issue by handling all the required logic under the hood, as well as handling the spammers.


---
How to use this right now?

Download the codebase:
```
> pip install Discord-Anti-Spam
```

A basic bot

```python
import discord
from discord.ext import commands
from antispam import AntiSpamHandler
from antispam.enums import Library

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
bot.handler = AntiSpamHandler(bot, library=Library.DPY)


@bot.event
async def on_ready():
    print(f"-----\nLogged in as: {bot.user.name} : {bot.user.id}\n-----")


@bot.event
async def on_message(message):
    await bot.handler.propagate(message)
    await bot.process_commands(message)


if __name__ == "__main__":
    bot.run("Bot Token")
```

And that's it!
Now, there will no doubt be bugs & changes etc. But, you can use this as is now and all I ask is you create an issue for anything you encounter while using this codebase.

#### Docs can be found [here](https://dpy-anti-spam.readthedocs.io/en/latest/?)

---

### Support

Want realtime help? Join the discord [here](https://discord.gg/BqPNSH2jPg).

---

### License
This project is licensed under the MIT license
