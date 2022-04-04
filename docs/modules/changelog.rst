Changelog
=========

A changelog that should be fairly up to date feature wise.

1.2.11 -> 1.3.0
--------------

New:
****

- The ``AdminLogs`` plugin now supports custom punishments
  via a new argument when initializing it.
  See the plugin for further info.

Fixes:
******

- Upgraded the nextcord ``Lib`` to support the latest release.
  This is not backwards compatible.

- ``AntiSpamTracker`` should now be library agnostic.

- ``AntiSpamTrackerSubclass`` example is now up to date.

Changes:
********

- All usages of ``user`` in AntiSpamTracker are now ``member``

- ``MaxMessageLimiter``:
    - New hard cap of 50
    - Is now guild wide
    - Punishment is a timeout for 5 minutes

- Default punishment scheme is to timeout members.

Removed:
********

- DPY as a default for the library options in init and load_from_dict.

1.2.8 -> 1.2.9
--------------

Fixed ``timeouts`` 'stacking' when they shouldn't have.

Resolved some issues with discord.py and forks where
default avatars would result in errors.

1.2.(3-7) -> 1.2.8
------------------

Fixed ``MongoCache`` and ``MyCustomTracker``.
These are also both now fully unit-tested.

1.2.2 -> 1.2.3
--------------

Fixed the ``AdminLogs`` plugin for timeouts.

1.2.1 -> 1.2.2
--------------

The big feature of this release is the new punishment
handling using discord timeouts. You can opt into
these by passing ``use_timeouts=True`` as an option.

This will be the become the default scheme in version 1.3.0.

New:
****

1) Added the ``times_timed_out`` field to ``Member``'s
2) Added ``member_was_timed_out`` field to ``CorePayload``
3) Added the following fields to ``Options``
    - ``use_timeouts``
    - ``member_timeout_message``
    - ``guild_log_timeout_message``
    - ``member_failed_timeout_message``
    - ``member_timeout_message_delete_after``
    - ``guild_log_timeout_message_delete_after``

Fixes:
******

1) ``Option`` attributes missing documentation
2) How the core handler used ``Options``
    Previously per-guild options were ignored in
    most situations, this has been fixed.

Deprecated:
***********

1) Library defaults
    In version 1.3.0 you will need to explicitly
    define the library you are running AntiSpam with.
2) MaxMessages Plugin
    It will be getting reworked in version 1.3.0, if
    you wish to preserve current behaviour save it locally.
3) Support for ``.name`` lookups in ignored channels & roles

Changes:
********

1) ``Lib`` impl changes
    Reworked the lib folder to provide explicit fork
    support and reduce duplicated code.
2) ``Options.is_per_channel_per_guild`` defaults
    This was changed to ``False`` to preserve the current
    behaviour once it is actually implemented.


1.2.0 -> 1.2.1
--------------

Fixes:
******

Mongo is no longer required when not using the ``MongoCache``

1.1.3 -> 1.2.0
--------------

New:
****

1. Added support for `Pincer. <https://pypi.org/project/pincer/>`_
    You can use this by passing the ``library=Library.Pincer``
    enum to your AntiSpamHandler during initialization.
2. New message templating option.
    ``$MENTIONBOT`` to mention your bot.
3. A method for changing caches.
    ``AntiSpamHandler.set_cache(new_cache)``
4. A new cache.
    ``MongoCache(AntiSpamHandler, "Mongo connection url")``

Fixed:
******

- ``Hikari`` regressions
- Some misc bugs


Changes:
********

- Modified ``Lib`` interface
    Check it out, its more DRY now.
- Modified ``Member``
    ``_in_guild`` is now ``internal_is_in_guild``

Removed:
********

- Extra installs for:
    ``DPY`` and ``hikari``

1.1.2 -> 1.1.3
--------------

Backwards compatible changes:

- Closed issue #73 on Github, this means you can now save plugin states.
    - Note only the shipped ``Stats`` plugin currently saves it's state.