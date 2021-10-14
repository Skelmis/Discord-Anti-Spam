Migrating to 1.0
----------------

The biggest change from 0.x.x to 1.x.x is
that every is now more sanely named in regard to pep8.

Likely missing things here, if you'd like support
join our discord and we'd be happy to assist.

Changes
-------

- Extensions are now called plugins

- :py:class:`AntiSpamHandler` now takes an :py:class:`Options`
  class rather then kwargs to set options.

- `user_` -> `member_`

- When failing to send a message, it now sends it to the guild log channelS



Features
--------

- Added support for `Hikari` and all `discord.py` forks

- Added a guild log channel setting
    - `guild_` messages will be sent here if set, otherwise same as before

- New plugins:
    - :py:class:`AntiMassMention` - To stop people spam pinging

    - :py:class:`Stats` - For general package stats

    - :py:class:`AdminLogs` - An easy way to get evidence on punishments


Fixes
-----

-