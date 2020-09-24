import discord
from discord.ext import commands

from AntiSpam import Guild
from AntiSpam.Exceptions import ObjectMismatch, DuplicateObject

"""
The overall handler & entry point from any discord bot,
this is responsible for handling interaction with Guilds etc
"""


# TODO Check on attempted kick/ban that the bot actually has perms
# TODO Possibly check that on init as well ^


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
        messageDuplicateCount=None,
        messageDuplicateAccuracy=None,
        ignorePerms=None,
        ignoreUsers=None,
        ignoreBots=None,
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
            The amount of 'warns' before a kick occurs
        banThreshold : int, optional
            The amount of 'kicks' that occur before a ban occurs
        messageInterval : int, optional
            Amount of time a message is kept before being discarded.
            Essentially the amount of time (In milliseconds) a message can count towards spam
        warnMessage : str, optional
            The message to be sent upon warnThreshold being reached
        kickMessage : str, optional
            The message to be sent up kickThreshold being reached
        banMessage : str, optional
            The message to be sent up banThreshold being reached
        messageDuplicateCount : int, optional
            Amount of duplicate messages needed to trip a punishment
        messageDuplicateKick : int, optional
            Amount of duplicate messages needed within messageInterval to trip a kick
        messageDuplicateBan : int, optional
            Amount of duplicate messages needed within messageInterval to trip a ban
        messageDuplicateAccuracy : float, optional
            How 'close' messages need to be to be registered as duplicates (Out of 100)
        ignorePerms : list, optional
            The perms (ID Form), that bypass anti-spam
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
            not isinstance(messageDuplicateCount, int)
            and messageDuplicateCount is not None
        ):
            raise ValueError("Expected messageDuplicateCount of type: int")

        if (
            not isinstance(messageDuplicateAccuracy, float)
            and messageDuplicateAccuracy is not None
        ):
            raise ValueError("Expected messageDuplicateAccuracy of type: int")

        if messageDuplicateAccuracy is not None:
            if 1 > messageDuplicateAccuracy or messageDuplicateAccuracy > 100:
                # Only accept values between 1 and 100
                raise ValueError("Expected messageDuplicateAccuracy between 1 and 100")

        if not isinstance(ignorePerms, list) and ignorePerms is not None:
            raise ValueError("Expected ignorePerms of type: list")

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
            "messageDuplicateCount": messageDuplicateCount
            or AntiSpamHandler.DEFAULTS.get("messageDuplicateCount"),
            "messageDuplicateAccuracy": messageDuplicateAccuracy
            or AntiSpamHandler.DEFAULTS.get("messageDuplicateAccuracy"),
            "ignorePerms": ignorePerms or AntiSpamHandler.DEFAULTS.get("ignorePerms"),
            "ignoreUsers": ignoreUsers or AntiSpamHandler.DEFAULTS.get("ignoreUsers"),
            "ignoreBots": ignoreBots or AntiSpamHandler.DEFAULTS.get("ignoreBots"),
        }

        self.bot = bot
        self._guilds = []

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

        if message.author.id == self.bot.user.id:
            return

        print(f"Propagating message for: {message.author.name}")

        guild = Guild(self.bot, message.guild.id, self.options)
        for guildObj in self.guilds:
            if guild == guildObj:
                guildObj.propagate(message)
                return

        self.guilds = guild
        guild.propagate(message)

    @property
    def guilds(self):
        return self._guilds

    @guilds.setter
    def guilds(self, value):
        """
        Raises
        ======
        DuplicateObject
            It won't maintain two message objects with the same
            id's, and it will complain about it haha
        ObjectMismatch
            Raised if `value` wasn't made by this person, so they
            shouldn't be the ones maintaining the reference
        """
        if not isinstance(value, Guild):
            raise ValueError("Expected Guild object")

        for guild in self._guilds:
            if guild == value:
                raise DuplicateObject

        self._guilds.append(value)
