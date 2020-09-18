import discord
from discord.ext import commands

"""
The overall handler & entry point from any discord bot,
this is responsible for handling interaction with Guilds etc
"""

# TODO Check on attempted kick/ban that the bot actually has perms
# TODO Possibly check that on init as well ^
import discord as discord


class AntiSpamHandler:
    """
    The overall handler for the DPY Anti-spam package

    DEFAULTS:
        warnThreshold: 3 -> This is the amount of messages in a row that result in a warning within the messageInterval
        kickThreshold: 5 -> This is the amount of messages in a row that result in a kick within the messageInterval
        banThreshold: 7 -> This is the amount of messages in a row that result in a ban within the messageInterval
        messageInterval: 2500 -> Amount of time a message is kept before being discarded.
                                 Essentially the amount of time (In milliseconds) a message can count towards spam
        warnMessage: "Hey {@user.mention}, please stop spamming" -> The message to be sent upon warnThreshold being reached
        kickMessage: "{@user.display_name} was kicked for spamming" -> The message to be sent up kickThreshold being reached
        banMessage: "{@user.display_name} was banned for spamming" -> The message to be sent up banThreshold being reached
        messageDuplicateWarn: 3 -> Amount of duplicate messages needed within messageInterval to trip a warning
        messageDuplicateKick: 7 -> Amount of duplicate messages needed within messageInterval to trip a kick
        messageDuplicateBan: 10 -> Amount of duplicate messages needed within messageInterval to trip a ban
        messageDuplicateAccuracy: 0.9 -> How 'close' messages need to be to be registered as duplicates (Out of 1)
        ignorePerms: [8] -> The perms (ID Form), that bypass anti-spam
        ignoreRoles: [] -> The roles (ID Form), that bypass anti-spam
        ignoreUsers: [] -> The users (ID Form), that bypass anti-spam
        ignoreBots: True -> Should bots bypass anti-spam? (True|False)

    """

    # TODO Add options for group spamming, rather then just per user.
    #      This could possibly be implemented at a Guild() level
    # TODO Add the ability to lockdown channels in certain situations
    # TODO Add bypass's for modes, so bypass warn mode. (Can be avoided by simply setting warn higher then kick)
    #      and that's how it will be implemented internally most likely
    # TODO Add the ability to toggle dm messages for log messages (To affected users)

    DEFAULTS = {
        "warnThreshold": 3,
        "kickThreshold": 5,
        "banThreshold": 7,
        "messageInterval": 2500,
        "warnMessage": "Hey {@user.mention}, please stop spamming.",
        "kickMessage": "{@user.display_name} was kicked for spamming.",
        "banMessage": "{@user.display_name} was banned for spamming",
        "messageDuplicateWarn": 3,
        "messageDuplicateKick": 7,
        "messageDuplicateBan": 10,
        "messageDuplicateAccuracy": 0.9,
        "ignorePerms": [8],
        "ignoreRoles": [],
        "ignoreUsers": [],
        "ignoreBots": True,
    }

    def __init__(
        self,
        bot: commands.Bot,
        *,
        warnThreshold=None,
        kickThreshold=None,
        banThreshold=None,
        messageInterval=None,
        warnMessage=None,
        kickMessage=None,
        banMessage=None,
        messageDuplicateWarn=None,
        messageDuplicateKick=None,
        messageDuplicateBan=None,
        messageDuplicateAccuracy=None,
        ignorePerms=None,
        ignoreRoles=None,
        ignoreUsers=None,
        ignoreBots=None
    ):
        """
        This is the first initialization of the entire spam handler,
        this is also where the initial options are set

        Parameters
        ----------
        bot : commands.Bot
            The commands.Bot instance
        warnThreshold : int, optional
            This is the amount of messages in a row that result in a warning within the messageInterval
        kickThreshold : int, optional
            This is the amount of messages in a row that result in a kick within the messageInterval
        banThreshold : int, optional
            This is the amount of messages in a row that result in a ban within the messageInterval
        messageInterval : int, optional
            Amount of time a message is kept before being discarded.
            Essentially the amount of time (In milliseconds) a message can count towards spam
        warnMessage : str, optional
            The message to be sent upon warnThreshold being reached
        kickMessage : str, optional
            The message to be sent up kickThreshold being reached
        banMessage : str, optional
            The message to be sent up banThreshold being reached
        messageDuplicateWarn : int, optional
            Amount of duplicate messages needed within messageInterval to trip a warning
        messageDuplicateKick : int, optional
            Amount of duplicate messages needed within messageInterval to trip a kick
        messageDuplicateBan : int, optional
            Amount of duplicate messages needed within messageInterval to trip a ban
        messageDuplicateAccuracy : float, optional
            How 'close' messages need to be to be registered as duplicates (Out of 1)
        ignorePerms : list, optional
            The perms (ID Form), that bypass anti-spam
        ignoreRoles : list, optional
            The roles (ID Form), that bypass anti-spam
        ignoreUsers : list, optional
            The users (ID Form), that bypass anti-spam
        ignoreBots : bool, optional
            Should bots bypass anti-spam?
        """
        # Just gotta casually type check everything.
        if not isinstance(bot, commands.Bot):
            raise ValueError("Expected channel of type: commands.Bot")

        if not isinstance(warnThreshold, int) and warnThreshold is not None:
            raise ValueError("Expected warnThreshold of type: int")

        if not isinstance(kickThreshold, int) and kickThreshold is not None:
            raise ValueError("Expected kickThreshold of type: int")

        if not isinstance(banThreshold, int) and banThreshold is not None:
            raise ValueError("Expected banThreshold of type: int")

        if not isinstance(messageInterval, int) and messageInterval is not None:
            raise ValueError("Expected messageInterval of type: int")

        if not isinstance(warnMessage, str) and warnMessage is not None:
            raise ValueError("Expected warnMessage of type: str")

        if not isinstance(kickMessage, str) and kickMessage is not None:
            raise ValueError("Expected kickMessage of type: str")

        if not isinstance(banMessage, str) and banMessage is not None:
            raise ValueError("Expected banMessage of type: str")

        if (
            not isinstance(messageDuplicateWarn, int)
            and messageDuplicateWarn is not None
        ):
            raise ValueError("Expected messageDuplicateWarn of type: int")

        if (
            not isinstance(messageDuplicateKick, int)
            and messageDuplicateKick is not None
        ):
            raise ValueError("Expected messageDuplicateKick of type: int")

        if not isinstance(messageDuplicateBan, int) and messageDuplicateBan is not None:
            raise ValueError("Expected messageDuplicateBan of type: int")

        if (
            not isinstance(messageDuplicateAccuracy, float)
            and messageDuplicateAccuracy is not None
        ):
            raise ValueError("Expected messageDuplicateAccuracy of type: int")

        if not isinstance(ignorePerms, list) and ignorePerms is not None:
            raise ValueError("Expected ignorePerms of type: list")

        if not isinstance(ignoreRoles, list) and ignoreRoles is not None:
            raise ValueError("Expected ignoreRoles of type: list")

        if not isinstance(ignoreUsers, list) and ignoreUsers is not None:
            raise ValueError("Expected ignoreUsers of type: list")

        if not isinstance(ignoreBots, bool) and ignoreBots is not None:
            raise ValueError("Expected ignoreBots of type: int")

        # Now we have type checked everything, lets do some logic
        self.options = {
            "warnThreshold": warnThreshold
            or AntiSpamHandler.DEFAULTS.get("warnThreshold"),
            "kickThreshold": kickThreshold
            or AntiSpamHandler.DEFAULTS.get("kickThreshold"),
            "banThreshold": banThreshold
            or AntiSpamHandler.DEFAULTS.get("banThreshold"),
            "messageInterval": messageInterval
            or AntiSpamHandler.DEFAULTS.get("messageInterval"),
            "warnMessage": warnMessage or AntiSpamHandler.DEFAULTS.get("warnMessage"),
            "kickMessage": kickMessage or AntiSpamHandler.DEFAULTS.get("kickMessage"),
            "banMessage": banMessage or AntiSpamHandler.DEFAULTS.get("banMessage"),
            "messageDuplicateWarn": messageDuplicateWarn
            or AntiSpamHandler.DEFAULTS.get("messageDuplicateWarn"),
            "messageDuplicateKick": messageDuplicateKick
            or AntiSpamHandler.DEFAULTS.get("messageDuplicateKick"),
            "messageDuplicateBan": messageDuplicateBan
            or AntiSpamHandler.DEFAULTS.get("messageDuplicateBan"),
            "messageDuplicateAccuracy": messageDuplicateAccuracy
            or AntiSpamHandler.DEFAULTS.get("messageDuplicateAccuracy"),
            "ignorePerms": ignorePerms or AntiSpamHandler.DEFAULTS.get("ignorePerms"),
            "ignoreRoles": ignoreRoles or AntiSpamHandler.DEFAULTS.get("ignoreRoles"),
            "ignoreUsers": ignoreUsers or AntiSpamHandler.DEFAULTS.get("ignoreUsers"),
            "ignoreBots": ignoreBots or AntiSpamHandler.DEFAULTS.get("ignoreBots"),
        }

        self.bot = bot

        if self.bot is None:
            raise ValueError("Invalid required inputs.")

        print(self.bot, self.options)

    def propagate(self, message: discord.Message):
        """
        This method is the base level intake for messages, then
        propagating it out to the relevant guild or creating one
        if that is required

        Parameters
        ==========
        message : discord.Message
            The message that needs to be propagated out
        """
        if not isinstance(message, discord.Message):
            raise ValueError("Expected message of type: discord.Message")
