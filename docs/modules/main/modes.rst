Possible Modes
==============

How to setup n use Antispam for different things.

Unless otherwise noted, 'spam' means messages that are
basically the same.

Default
-------

The default mode administers antispam on a per member per guild basis.
This means that every single message sent by someone counts towards
there spam threshold, this is great because it means people who spam
in one channel and people who spam 1 message per channel both get caught.

Per Member Per Channel
----------------------

The package also supports the ability to track spam per member per channel.
This means that if you spam a single channel you will get punished, however
if you send the same message in different channels your fine. You can set this
using the following ``Options(per_channel_spam=True)``

Max Message Amount
------------------

Unlike other methods, this punishes members if they simply send more then
``x`` messages within ``y`` time period.
You can find this plugin here :py:class:`MaxMessageLimiter`
