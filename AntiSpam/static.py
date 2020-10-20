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
        "messageInterval": 2500,
        "warnMessage": "Hey $MENTIONUSER, please stop spamming/sending duplicate messages.",
        "kickMessage": "$USERNAME was kicked for spamming/sending duplicate messages.",
        "banMessage": "$USERNAME was banned for spamming/sending duplicate messages.",
        "messageDuplicateCount": 5,
        "messageDuplicateAccuracy": 90,
        "ignorePerms": [8],
        "ignoreUsers": [],
        "ignoreBots": True,
    }
    BAN = "ban"
    KICK = "kick"
