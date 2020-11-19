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

import datetime
import logging
import time

import discord
from discord.ext import commands

from AntiSpam import Guild, static
from AntiSpam.Exceptions import (
    ObjectMismatch,
    DuplicateObject,
    BaseASHException,
    MissingGuildPermissions,
)
from AntiSpam.static import Static

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
        warnThreshold: 3
            This is the amount of duplicates that result in a warning within the messageInterval

        kickThreshold: 2
            This is the amount of warns required before a kick is the next punishment

        banThreshold: 2
            This is the amount of kicks required before a ban is the next punishment

        messageInterval: 30000ms (30 Seconds)
            Amount of time a message is kept before being discarded. Essentially the amount of time (In milliseconds) a message can count towards spam

        warnMessage: "Hey $MENTIONUSER, please stop spamming/sending duplicate messages."
            The message to be sent upon warnThreshold being reached

        kickMessage: "$USERNAME was kicked for spamming/sending duplicate messages."
            The message to be sent up kickThreshold being reached

        banMessage: "$USERNAME was banned for spamming/sending duplicate messages."
            The message to be sent up banThreshold being reached

        messageDuplicateCount: 5
            The amount of duplicate messages needed within messageInterval to trigger a punishment

        messageDuplicateAccuracy: 90
            How 'close' messages need to be to be registered as duplicates (Out of 100)

        ignorePerms: [8]
            The perms (ID Form), that bypass anti-spam

            *Not Implemented*

        ignoreUsers: []
            The users (ID Form), that bypass anti-spam

        ignoreChannels: []
            Channels (ID Form), that bypass anti-spam

        ignoreRoles: []
            The roles (ID Form), that bypass anti-spam

        ignoreGuilds: []
            Guilds (ID Form), that bypass anti-spam

        ignoreBots: True
            Should bots bypass anti-spam? (True|False)
    """

    # TODO Add options for group spamming, rather then just per user.
    #      This could possibly be implemented at a Guild() level
    # TODO Add the ability to lockdown channels in certain situations
    # TODO Add bypass's for modes, so bypass warn mode. (Can be avoided by simply setting warn higher then kick)
    #      and that's how it will be implemented internally most likely
    # TODO Add the ability to toggle dm messages for log messages (To affected users)

    def __init__(
        self,
        bot: commands.Bot,
        verboseLevel=0,
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
        ignoreChannels=None,
        ignoreRoles=None,
        ignoreGuilds=None,
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

        if not isinstance(verboseLevel, int):
            raise ValueError("Verbosity should be an int between 0-5")

        if not isinstance(warnThreshold, int) and warnThreshold is not None:
            raise ValueError("Expected warnThreshold of type: int")

        if not isinstance(kickThreshold, int) and kickThreshold is not None:
            raise ValueError("Expected kickThreshold of type: int")

        if not isinstance(banThreshold, int) and banThreshold is not None:
            raise ValueError("Expected banThreshold of type: int")

        if not isinstance(messageInterval, int) and messageInterval is not None:
            raise ValueError("Expected messageInterval of type: int")

        if messageInterval is not None and messageInterval < 1000:
            raise BaseASHException("Minimum messageInterval is 1 seconds (1000 ms)")

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

        if not isinstance(ignoreChannels, list) and ignoreChannels is not None:
            raise ValueError("Expected ignoreChannels of type: list")

        if not isinstance(ignoreRoles, list) and ignoreRoles is not None:
            raise ValueError("Expected ignoreRoles of type: list")

        if not isinstance(ignoreGuilds, list) and ignoreGuilds is not None:
            raise ValueError("Expected ignoreGuilds of type: list")

        if not isinstance(ignoreBots, bool) and ignoreBots is not None:
            raise ValueError("Expected ignoreBots of type: int")

        # Now we have type checked everything, lets do some logic
        if ignoreBots is None:
            ignoreBots = Static.DEFAULTS.get("ignoreBots")

        # TODO Turn ignoreRoles into a valid list of roles

        self.options = {
            "warnThreshold": warnThreshold or Static.DEFAULTS.get("warnThreshold"),
            "kickThreshold": kickThreshold or Static.DEFAULTS.get("kickThreshold"),
            "banThreshold": banThreshold or Static.DEFAULTS.get("banThreshold"),
            "messageInterval": messageInterval
            or Static.DEFAULTS.get("messageInterval"),
            "warnMessage": warnMessage or Static.DEFAULTS.get("warnMessage"),
            "kickMessage": kickMessage or Static.DEFAULTS.get("kickMessage"),
            "banMessage": banMessage or Static.DEFAULTS.get("banMessage"),
            "messageDuplicateCount": messageDuplicateCount
            or Static.DEFAULTS.get("messageDuplicateCount"),
            "messageDuplicateAccuracy": messageDuplicateAccuracy
            or Static.DEFAULTS.get("messageDuplicateAccuracy"),
            "ignorePerms": ignorePerms or Static.DEFAULTS.get("ignorePerms"),
            "ignoreUsers": ignoreUsers or Static.DEFAULTS.get("ignoreUsers"),
            "ignoreChannels": ignoreChannels or Static.DEFAULTS.get("ignoreChannels"),
            "ignoreRoles": ignoreRoles or Static.DEFAULTS.get("ignoreRoles"),
            "ignoreGuilds": ignoreGuilds or Static.DEFAULTS.get("ignoreGuilds"),
            "ignoreBots": ignoreBots,
        }

        self.bot = bot
        self._guilds = []

        logging.basicConfig(
            format="%(asctime)s | %(levelname)s | %(module)s | %(message)s",
            datefmt="%d/%m/%Y %I:%M:%S %p",
        )
        self.logger = logging.getLogger(__name__)
        if verboseLevel == 0:
            self.logger.setLevel(level=logging.NOTSET)
        elif verboseLevel == 1:
            self.logger.setLevel(level=logging.DEBUG)
        elif verboseLevel == 2:
            self.logger.setLevel(level=logging.INFO)
        elif verboseLevel == 3:
            self.logger.setLevel(level=logging.WARNING)
        elif verboseLevel == 4:
            self.logger.setLevel(level=logging.ERROR)
        elif verboseLevel == 5:
            self.logger.setLevel(level=logging.CRITICAL)

    def propagate(self, message: discord.Message) -> None:
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

        # Ensure we only moderate actual guild messages
        if not message.guild:
            return

        if message.author.id == self.bot.user.id:
            return

        # Return if ignored bot
        if self.options["ignoreBots"] and message.author.bot:
            return

        # Return if ignored user
        if message.author.id in self.options["ignoreUsers"]:
            return

        # Return if ignored channel
        if message.channel.id in self.options["ignoreChannels"]:
            return

        # Return if user has an ignored role
        userRolesId = [role.id for role in message.author.roles]
        for userRoleId in userRolesId:
            if userRoleId in self.options.get("ignoreRoles"):
                return

        # Return if ignored guild
        if message.guild.id in self.options.get("ignoreGuilds"):
            return

        self.logger.debug(
            f"Propagating message for: {message.author.name}({message.author.id})"
        )

        guild = Guild(self.bot, message.guild.id, self.options, logger=self.logger)
        for guildObj in self.guilds:
            if guild == guildObj:
                guildObj.propagate(message)
                return
        else:
            # Check we have perms to actually create this guild object
            # and punish based upon our guild wide permissions
            perms = message.guild.me.guild_permissions
            if not perms.kick_members or not perms.ban_members:
                raise MissingGuildPermissions

        self.guilds = guild
        self.logger.info(f"Created Guild: {guild.id}")

        guild.propagate(message)

    def AddIgnoredItem(self, item: int, type: str) -> None:
        """
        Add an item to the relevant ignore list

        Parameters
        ----------
        item : int
            The id of the thing to ignore
        type : str
            A string representation of the ignored
            items overall container

        Raises
        ======
        BaseASHException
            Invalid ignore type
        ValueError
            item is not of type int or int convertible

        Notes
        =====
        This will silently ignore any attempts
        to add an item already added.
        """
        type = type.lower()
        if not isinstance(item, int):
            item = int(item)

        if type == "user":
            if item not in self.options["ignoreUsers"]:
                self.options["ignoreUsers"].append(item)
        elif type == "channel":
            if item not in self.options["ignoreChannels"]:
                self.options["ignoreChannels"].append(item)
        elif type == "perm":
            if item not in self.options["ignorePerms"]:
                self.options["ignorePerms"].append(item)
        elif type == "guild":
            if item not in self.options["ignoreGuilds"]:
                self.options["ignoreGuilds"].append(item)
        elif type == "role":
            if item not in self.options["ignoreRoles"]:
                self.options["ignoreRoles"].append(item)
        else:
            raise BaseASHException("Invalid ignore type")

        self.logger.debug(f"Ignored {type}: {item}")

    def RemoveIgnoredItem(self, item: int, type: str) -> None:
        """
        Remove an item from the relevant ignore list

        Parameters
        ----------
        item : int
            The id of the thing to unignore
        type : str
            A string representation of the ignored
            items overall container

        Raises
        ======
        BaseASHException
            Invalid ignore type
        ValueError
            item is not of type int or int convertible

        Notes
        =====
        This will silently ignore any attempts
        to remove an item not ignored.
        """
        type = type.lower()
        if not isinstance(item, int):
            item = int(item)

        if type == "user":
            if item in self.options["ignoreUsers"]:
                index = self.options["ignoreUsers"].index(item)
                self.options["ignoreUsers"].pop(index)
        elif type == "channel":
            if item in self.options["ignoreChannels"]:
                index = self.options["ignoreChannels"].index(item)
                self.options["ignoreChannels"].pop(index)
        elif type == "perm":
            if item in self.options["ignorePerms"]:
                index = self.options["ignorePerms"].index(item)
                self.options["ignorePerms"].pop(index)
        else:
            raise BaseASHException("Invalid ignore type")

        self.logger.debug(f"Un-Ignored {type}: {item}")

    # <-- Getter & Setters -->
    @property
    def guilds(self):
        return self._guilds

    @guilds.setter
    def guilds(self, value):
        """
        Raises
        ======
        DuplicateObject
            It won't maintain two guild objects with the same
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
