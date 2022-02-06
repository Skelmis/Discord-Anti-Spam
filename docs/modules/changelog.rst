Changelog
=========

A changelog that should be fairly up to date feature wise.

1.1.3 -> 2.0.0
--------------

New:
****

1. Added support for `Pincer. <https://pypi.org/project/pincer/>`_
    You can use this by passing the ``library=Library.Pincer``
    enum to your AntiSpamHandler during initialization.
2. New message templating option.
    ``$MENTIONBOT`` to mention your bot.
3. A method for changing caches.
    ``AntiSpamHandler.set_cache(...)``
4. A new cache.
    ``MongoCache(AntiSpamHandler, "Mongo connection url")``

Fixed:
******

- ``Hikari`` regressions


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