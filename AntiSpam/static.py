"""
The MIT License (MIT)

Copyright (c) 2020 Skelmis

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

"""
A simple, small file devoted to maintaining all the relevant static
things associated with this project. Should help to keep everything
findable, readable, modifiable etc
"""

# TODO Add what you can and can't use message substitution things
#      Things like $MENTIONUSER and what they do, etc, etc


class Static:
    # The default options for ASH
    DEFAULTS = {
        "warn_threshold": 3,
        "kick_threshold": 2,
        "ban_threshold": 2,
        "message_interval": 30000,  # 30 Seconds
        "warn_message": "Hey $MENTIONUSER, please stop spamming/sending duplicate messages.",
        "kick_message": "$USERNAME was kicked for spamming/sending duplicate messages.",
        "ban_message": "$USERNAME was banned for spamming/sending duplicate messages.",
        "message_duplicate_count": 5,
        "message_duplicate_accuracy": 90,
        "ignore_perms": [8],
        "ignore_users": [],
        "ignore_channels": [],
        "ignore_roles": [],
        "ignore_guilds": [],
        "ignore_bots": True,
    }
    BAN = "ban"
    KICK = "kick"
