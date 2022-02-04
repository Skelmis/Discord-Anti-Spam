Message Templating
==================

This package utilises safe conversions for message arguments within strings.

*These use discord.py terms. But the package will work with the library
you are using seamlessly. Don't worry about not seeing exact matches.*

Templating Options
-------------------

The following are all the options you as the user have:

* **$MENTIONMEMBER** - This will attempt to mention the user, uses ``discord.Member.mention``
* **$MEMBERNAME** - This will attempt to state the user's name, uses ``discord.Member.display_name``
* **$MEMBERID** - This will attempt to state the user's id, uses ``discord.Member.id``

* **$BOTNAME** - This will attempt to state your bots name, uses ``discord.Guild.me.name``
* **$BOTID** - This will attempt to state your bots id, uses ``discord.Guild.me.id``
* **$MENTIONBOT** - This will attempt to mention your bot, uses ``discord.Guild.me.mention``

* **$GUILDNAME** - This will attempt to state the guild's name, uses ``discord.Guild.name``
* **$GUILDID** - This will attempt to state the guild's id, uses ``discord.Guild.id``

* **$TIMESTAMPNOW** - This exact time formatted as hh:mm:ss AM/PM, dd/mm/yyyy, uses ``datetime.datetime.now()``
* **$TIMESTAMPTODAY** - Today's date formatted as dd/mm/yyyy, uses ``datetime.datetime.now()``

* **$WARNCOUNT** - How many times the user has been warned so far, uses ``AntiSpam.User.warn_count``
* **$KICKCOUNT** - How many times the user has been removed from the guild so far, uses ``AntiSpam.User.kick_count``


The following are special case's for embeds:

* **$MEMBERAVATAR** - This will attempt to display the user's avatar, uses ``discord.Member.avatar_url``
* **$BOTAVATAR** - This will attempt to display the bots avatar, uses ``discord.Guild.me.avatar_url``
* **$GUILDICON** - This will attempt to display the guilds icon, uses ``discord.Guild.icon_url``

*Note: Example usages not final. Usage works in discord.py 1.x.x and 2.x.x + hikari*

The above are valid in the following uses:

1. ``discord.Embed.set_author(url="")``
2. ``discord.Embed.set_footer(icon_url="")``

*There are currently no plans to support either* ``discord.Embed.image`` *or* ``discord.Embed.thumbnail``

Templating Usage
-----------------

You can include the above options in the following arguments
when you initialize the package:

* **guild_warn_message**
* **guild_kick_message**
* **guild_ban_message**
* **user_kick_message**
* **user_ban_message**

Embed Templating
-----------------

The above options can also be used within embeds, these also support templating with
the options defined above. These options are available in the following fields:

1. **title**, ``discord.Embed.title``
2. **description**, ``discord.Embed.description``
3. **author** -> **name** in ``discord.Embed.set_author(name="")``
4. **footer** -> **text** in ``discord.Embed.set_footer(text="")``
5. **name** & **value** in ``discord.Embed.add_field(name="", value="")``

*NOTE: You can add the timestamp field also.
Provided it exists, it will be replaced with* ``discord.Message.created_at``
*, no value required.*

