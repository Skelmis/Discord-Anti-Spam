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


class Static:
    # The default options for ASH
    DEFAULTS = {
        "warnThreshold": 3,
        "kickThreshold": 2,
        "banThreshold": 2,
        "messageInterval": 30000,  # 30 Seconds
        "warnMessage": "Hey $MENTIONUSER, please stop spamming/sending duplicate messages.",
        "kickMessage": "$USERNAME was kicked for spamming/sending duplicate messages.",
        "banMessage": "$USERNAME was banned for spamming/sending duplicate messages.",
        "messageDuplicateCount": 5,
        "messageDuplicateAccuracy": 90,
        "ignorePerms": [8],
        "ignoreUsers": [],
        "ignoreChannels": [],
        "ignoreRoles": [],
        "ignoreGuilds": [],
        "ignoreBots": True,
    }
    BAN = "ban"
    KICK = "kick"
