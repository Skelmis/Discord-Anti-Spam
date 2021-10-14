Migrating to 1.0
================

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

- When failing to send a message, it now sends it to the guild log channels

- Some type param's are now enums. See :py:class:`IgnoreType` and :py:class:`ResetType`

- :py:method:`AntiSpamHandler.propagate` now returns :py:class:`CorePayload` instead of a dict

- Some misc methods on the handler have signature changes

- Package is typed more, however not fully. This is still a work in progress

- Misc changes, no doubt I've missed heaps

Features
--------

- Added support for `Hikari` and all `discord.py` forks

- Added a guild log channel setting
    - `guild_` messages will be sent here if set, otherwise same as before
    - :py:method:`AntiSpamHandler.add_guild_log_channel`
    - :py:method:`AntiSpamHandler.remove_guild_log_channel`

- Abstracted logic and data storage to be separate. This means you
  can setup your own cache such as redis. See :py:class:`Cache`

- Now features an easy way to clean up your cache. See :py:method:`AntiSpamHandler.clean_cache`

- New plugins:
    - :py:class:`AntiMassMention` - To stop people spam pinging

    - :py:class:`Stats` - For general package stats

    - :py:class:`AdminLogs` - An easy way to get evidence on punishments

- Plugins now have direct access to storage within the cache.
  You should be interacting with :py:class:`PluginCache` for this.

- Plugins now support blacklisting to stop runs on certain guilds.
  See Plugin Blacklisting under ``Package Plugin System``

- Roughly ``150%`` faster then 0.x.x on small test cases

- Fully tested, no more pesky regression bugs

- Further documented

- More comprehensive logging, this is greatly improved compared to 0.x.x

Fixes
-----

- When the package attempts to delete spam messages, it will
  now actually delete *all* messages marked as spam rather then
  just the last one.

- Logging now lazily computes variables, this should be a decent speedup