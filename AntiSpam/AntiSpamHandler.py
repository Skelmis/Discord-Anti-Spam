"""
LICENSE
The MIT License (MIT)

Copyright (c) 2020-2021 Skelmis

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
LICENSE
"""
import inspect
import logging
from copy import deepcopy
from typing import Optional, Union
from unittest.mock import AsyncMock

import discord
from discord.ext import commands

from AntiSpam.Guild import Guild
from AntiSpam.Exceptions import (
    DuplicateObject,
    BaseASHException,
    MissingGuildPermissions,
    LogicError,
    ExtensionError,
)
from AntiSpam.BaseExtension import BaseExtension
from AntiSpam.User import User
from AntiSpam.static import Static

log = logging.getLogger(__name__)

"""
The overall handler & entry point from any discord bot,
this is responsible for handling interaction with Guilds etc
"""


class AntiSpamHandler:
    """
    The overall handler for the DPY Anti-spam package

    DEFAULTS:
        warn_threshold: 3
            This is the amount of duplicates that result in a warning within the message_interval

        kick_threshold: 2
            This is the amount of warns required before a kick is the next punishment

        ban_threshold: 2
            This is the amount of kicks required before a ban is the next punishment

        message_interval: 30000ms (30 Seconds)
            Amount of time a message is kept before being discarded. Essentially the amount of time (In milliseconds) a message can count towards spam

        guild_warn_message: "Hey $MENTIONUSER, please stop spamming/sending duplicate messages."
            The message to be sent in the guild upon warn_threshold being reached

        guild_kick_message: "$USERNAME was kicked for spamming/sending duplicate messages."
            The message to be sent in the guild upon kick_threshold being reached

        guild_ban_message: "$USERNAME was banned for spamming/sending duplicate messages."
            The message to be sent in the guild upon ban_threshold being reached

        user_kick_message : "Hey $MENTIONUSER, you are being kicked from $GUILDNAME for spamming/sending duplicate messages."
            The message to be sent to the user who is being warned

        user_ban_message : "Hey $MENTIONUSER, you are being banned from $GUILDNAME for spamming/sending duplicate messages."
            The message to be sent to the user who is being banned

        user_failed_kick_message : "I failed to punish you because I lack permissions, but still you shouldn't spam"
            The message to be sent to the user if the bot fails to kick them

        user_failed_ban_message : "I failed to punish you because I lack permissions, but still you shouldn't spam"
            The message to be sent to the user if the bot fails to ban them

        message_duplicate_count: 5
            The amount of duplicate messages needed within message_interval to trigger a punishment

        message_duplicate_accuracy: 90
            How 'close' messages need to be to be registered as duplicates (Out of 100)

        delete_spam: True
            Whether or not to delete messages marked as spam

        ignore_perms: [8]
            The perms (ID Form), that bypass anti-spam

            **Not Implemented**

        ignore_users: []
            The users (ID Form), that bypass anti-spam

        ignore_channels: []
            Channels (ID Form), that bypass anti-spam

        ignore_roles: []
            The roles (ID Form), that bypass anti-spam

        ignore_guilds: []
            Guilds (ID Form), that bypass anti-spam

        ignore_bots: True
            Should bots bypass anti-spam?

        warn_only: False
            Whether or not to only warn users,
            this means it will not kick or ban them

        no_punish: False
            Don't punish anyone, simply return
            whether or not they should be punished
            within propagate.
            This essentially lets the end user
            handle punishments themselves.

            To check if someone should be punished, use the returned
            value from the ``propagate`` method. If should_be_punished_this_message
            is True then this package believes they should be punished.
            Otherwise just ignore that message since it shouldn't be punished.

        per_channel_spam: False
            Track spam as per channel,
            rather then per guild.

        guild_warn_message_delete_after: None
            The time to delete the ``guild_warn_message`` message

        user_kick_message_delete_after: None
            The time to delete the ``user_kick_message`` message

        guild_kick_message_delete_after: None
            The time to delete the ``guild_kick_message`` message

        user_ban_message_delete_after: None
            The time to delete the ``user_ban_message`` message

        guild_ban_message_delete_after: None
            The time to delete the ``guild_ban_message`` message

    """

    # TODO Add options for group spamming, rather then just per member.
    #      This could possibly be implemented at a Guild() level
    def __init__(
        self,
        bot: Union[
            commands.Bot,
            commands.AutoShardedBot,
            discord.Client,
            discord.AutoShardedClient,
        ],
        **kwargs,
    ):
        """
        This is the first initialization of the entire spam handler,
        this is also where the initial options are set

        Parameters
        ----------
        bot : commands.Bot or commands.AutoShardedBot or disocrd.Client or discord.AutoShardedClient
            The commands.Bot or commands.AutoSharedBot or discord.Client or discord.AutoShardedClient instance
        warn_threshold : int, optional
            This is the amount of messages in a row that result in a warning within the message_interval
        kick_threshold : int, optional
            The amount of 'warns' before a kick occurs
        ban_threshold : int, optional
            The amount of 'kicks' that occur before a ban occurs
        message_interval : int, optional
            Amount of time a message is kept before being discarded.
            Essentially the amount of time (In milliseconds) a message can count towards spam
        guild_warn_message : Union[str, dict], optional
            The message to be sent in the guild upon warn_threshold being reached
        guild_kick_message : Union[str, dict], optional
            The message to be sent in the guild upon kick_threshold being reached
        guild_ban_message : Union[str, dict], optional
            The message to be sent in the guild upon ban_threshold being reached
        user_kick_message : Union[str, dict], optional
            The message to be sent to the user who is being warned
        user_ban_message : Union[str, dict], optional
            The message to be sent to the user who is being banned
        user_failed_kick_message : Union[str, dict], optional
            The message to be sent to the user if the bot fails to kick them
        user_failed_ban_message : Union[str, dict], optional
            The message to be sent to the user if the bot fails to ban them
        message_duplicate_count : int, optional
            Amount of duplicate messages needed to trip a punishment
        message_duplicate_accuracy : float, optional
            How 'close' messages need to be to be registered as duplicates (Out of 100)
        delete_spam : bool, optional
            Whether or not to delete any messages marked as spam
        ignore_perms : list, optional
            The perms (ID Form), that bypass anti-spam
        ignore_channels : list, optional
            The channels (ID Form) that are ignored
        ignore_roles : list, optional
            The roles (ID, Name) that are ignored
        ignore_guilds : list, optional
            The guilds (ID) that are ignored
        ignore_users : list, optional
            The users (ID Form), that bypass anti-spam
        ignore_bots : bool, optional
            Should bots bypass anti-spam?
        warn_only : bool, optional
            Only warn users?
        no_punish : bool, optional
            Dont punish users?
            Return if they should be punished or
            not without actually punishing them
        per_channel_spam : bool, optional
            Track spam as per channel,
            rather then per guild
        guild_warn_message_delete_after : int, optional
            The time to delete the ``guild_warn_message`` message
        user_kick_message_delete_after : int, optional
            The time to delete the ``user_kick_message`` message
        guild_kick_message_delete_after : int, optional
            The time to delete the ``guild_kick_message`` message
        user_ban_message_delete_after : int, optional
            The time to delete the ``user_ban_message`` message
        guild_ban_message_delete_after : int, optional
            The time to delete the ``guild_ban_message`` message
        """
        # Just gotta casually ignore_type check everything.
        if not isinstance(
            bot,
            (
                commands.Bot,
                commands.AutoShardedBot,
                discord.Client,
                discord.AutoShardedClient,
            ),
        ) and not isinstance(bot, AsyncMock):
            raise ValueError(
                "Expected bot of type commands.Bot, commands.AutoShardedBot, "
                "discord.Client or discord.AutoShardedClient"
            )

        self.options = self._ensure_options(**kwargs)

        if self.options.get("no_punish") and (
            self.options.get("delete_spam"),
            self.options.get("warn_only"),
            self.options.get("per_channel_spam"),
        ):
            log.warning(
                "You are attempting to create an AntiSpamHandler with options that are mutually exclusive. "
                "Please note `no_punish` will over rule any other options you attempt to set which are "
                "mutually exclusive."
            )

        self.bot = bot
        self._guilds = []

        self.pre_invoke_extensions = {}
        self.after_invoke_extensions = {}

        log.info("Package initialized successfully")

    async def propagate(self, message: discord.Message) -> Optional[dict]:
        """
        This method is the base level intake for messages, then
        propagating it out to the relevant guild or creating one
        if that is required

        For what this returns please see the top of this page.

        Parameters
        ==========
        message : discord.Message
            The message that needs to be propagated out

        Returns
        =======
        dict
            A dictionary of useful information about the user in question
        """
        if not isinstance(message, discord.Message) and not isinstance(
            message, AsyncMock
        ):
            log.debug("Invalid value given to propagate")
            raise ValueError("Expected message of ignore_type: discord.Message")

        # Ensure we only moderate actual guild messages
        if not message.guild:
            log.debug("Message was not in a guild")
            return {"status": "Ignoring messages from dm's"}

        # The bot is immune to spam
        if message.author.id == self.bot.user.id:
            log.debug("Message was from myself")
            return {"status": "Ignoring messages from myself (the bot)"}

        if isinstance(message.author, discord.User):
            log.warning(f"Given message with an author of type User")

        # Return if ignored bot
        if self.options["ignore_bots"] and message.author.bot:
            log.debug(f"I ignore bots, and this is a bot message: {message.author.id}")
            return {"status": "Ignoring messages from bots"}

        # Return if ignored member
        if message.author.id in self.options["ignore_users"]:
            log.debug(f"The user who sent this message is ignored: {message.author.id}")
            return {"status": f"Ignoring this user: {message.author.id}"}

        # Return if ignored channel
        if (
            message.channel.id in self.options["ignore_channels"]
            or message.channel.name in self.options["ignore_channels"]
        ):
            log.debug(f"{message.channel} is ignored")
            return {"status": f"Ignoring this channel: {message.channel.id}"}

        # Return if member has an ignored role
        try:
            user_roles = [role.id for role in message.author.roles]
            user_roles.extend([role.name for role in message.author.roles])
            for item in user_roles:
                if item in self.options.get("ignore_roles"):
                    log.debug(f"{item} is a part of ignored roles")
                    return {"status": f"Ignoring this role: {item}"}
        except AttributeError:
            log.warning(
                f"Could not compute ignore_roles for {message.author.name}({message.author.id})"
            )

        # Return if ignored guild
        if message.guild.id in self.options.get("ignore_guilds"):
            log.debug(f"{message.guild.id} is an ignored guild")
            return {"status": f"Ignoring this guild: {message.guild.id}"}

        log.debug(
            f"Propagating message for: {message.author.name}({message.author.id})"
        )

        guild = Guild(self.bot, message.guild.id, self.options)
        try:
            guild = next(iter(g for g in self.guilds if g == guild))
        except StopIteration:
            # Check we have perms to actually create this guild object
            # and punish based upon our guild wide permissions
            perms = message.guild.me.guild_permissions
            if not perms.kick_members or not perms.ban_members:
                raise MissingGuildPermissions

            self.guilds = guild
            log.info(f"Created Guild: {guild.id}")

        data = {"pre_invoke_extensions": [], "after_invoke_extensions": []}

        for pre_invoke_ext in self.pre_invoke_extensions.values():
            pre_invoke_return = await pre_invoke_ext.propagate(message)
            data["pre_invoke_extensions"].append(pre_invoke_return)

        main_return = await guild.propagate(message)

        for after_invoke_ext in self.after_invoke_extensions.values():
            after_invoke_return = await after_invoke_ext.propagate(message, main_return)
            data["after_invoke_extensions"].append(after_invoke_return)

        return {**main_return, **data}

    def add_ignored_item(self, item: int, ignore_type: str) -> None:
        """
        TODO Document this better with ignore_type notations
        Add an item to the relevant ignore list

        Parameters
        ----------
        item : int
            The id of the thing to ignore
        ignore_type : str
            A string representation of the ignored
            items overall container

        Raises
        ======
        BaseASHException
            Invalid ignore ignore_type
        ValueError
            item is not of ignore_type int or int convertible

        Notes
        =====
        This will silently ignore any attempts
        to add an item already added.
        """
        try:
            ignore_type = ignore_type.lower()
        except:
            raise ValueError("Expeced ignore_type of type: str")

        try:
            if not isinstance(item, int):
                item = int(item)
        except ValueError:
            raise ValueError("Expected item of type: int")

        if ignore_type == "member":
            if item not in self.options["ignore_users"]:
                self.options["ignore_users"].append(item)
        elif ignore_type == "channel":
            if item not in self.options["ignore_channels"]:
                self.options["ignore_channels"].append(item)
        elif ignore_type == "perm":
            if item not in self.options["ignore_perms"]:
                self.options["ignore_perms"].append(item)
        elif ignore_type == "guild":
            if item not in self.options["ignore_guilds"]:
                self.options["ignore_guilds"].append(item)
        elif ignore_type == "role":
            if item not in self.options["ignore_roles"]:
                self.options["ignore_roles"].append(item)
        else:
            raise BaseASHException("Invalid ignore ignore_type")

        log.debug(f"Ignored {ignore_type}: {item}")

    def remove_ignored_item(self, item: int, ignore_type: str) -> None:
        """
        Remove an item from the relevant ignore list

        Parameters
        ----------
        item : int
            The id of the thing to unignore
        ignore_type : str
            A string representation of the ignored
            items overall container

        Raises
        ======
        BaseASHException
            Invalid ignore ignore_type
        ValueError
            item is not of ignore_type int or int convertible

        Notes
        =====
        This will silently ignore any attempts
        to remove an item not ignored.
        """
        try:
            ignore_type = ignore_type.lower()
        except:
            raise ValueError("Expeced ignore_type of type: str")

        try:
            # TODO Handle more then just ints, take relevant objs as well
            if not isinstance(item, int):
                item = int(item)
        except ValueError:
            raise ValueError("Expected item of type: int")

        if ignore_type == "member":
            if item in self.options["ignore_users"]:
                index = self.options["ignore_users"].index(item)
                self.options["ignore_users"].pop(index)
        elif ignore_type == "channel":
            if item in self.options["ignore_channels"]:
                index = self.options["ignore_channels"].index(item)
                self.options["ignore_channels"].pop(index)
        elif ignore_type == "perm":
            if item in self.options["ignore_perms"]:
                index = self.options["ignore_perms"].index(item)
                self.options["ignore_perms"].pop(index)
        elif ignore_type == "guild":
            if item in self.options["ignore_guilds"]:
                index = self.options["ignore_guilds"].index(item)
                self.options["ignore_guilds"].pop(index)
        elif ignore_type == "role":
            if item in self.options["ignore_roles"]:
                index = self.options["ignore_roles"].index(item)
                self.options["ignore_roles"].pop(index)
        else:
            raise BaseASHException("Invalid ignore ignore_type")

        log.debug(f"Un-Ignored {ignore_type}: {item}")

    def add_custom_guild_options(self, guild_id: int, **kwargs):
        """
        Set a guild's options to a custom set, rather then the base level
        set used and defined in ASH initialization

        Parameters
        ----------
        guild_id : int
            The id of the guild to create
        warn_threshold : int, optional
            This is the amount of messages in a row that result in a warning within the message_interval
        kick_threshold : int, optional
            The amount of 'warns' before a kick occurs
        ban_threshold : int, optional
            The amount of 'kicks' that occur before a ban occurs
        message_interval : int, optional
            Amount of time a message is kept before being discarded.
            Essentially the amount of time (In milliseconds) a message can count towards spam
        guild_warn_message : Union[str, dict], optional
            The message to be sent in the guild upon warn_threshold being reached
        guild_kick_message : Union[str, dict], optional
            The message to be sent in the guild upon kick_threshold being reached
        guild_ban_message : Union[str, dict], optional
            The message to be sent in the guild upon ban_threshold being reached
        user_kick_message : Union[str, dict], optional
            The message to be sent to the user who is being warned
        user_ban_message : Union[str, dict], optional
            The message to be sent to the user who is being banned
        user_failed_kick_message : Union[str, dict], optional
            The message to be sent to the user if the bot fails to kick them
        user_failed_ban_message : Union[str, dict], optional
            The message to be sent to the user if the bot fails to ban them
        message_duplicate_count : int, optional
            Amount of duplicate messages needed to trip a punishment
        message_duplicate_accuracy : float, optional
            How 'close' messages need to be to be registered as duplicates (Out of 100)
        delete_spam : bool, optional
            Whether or not to delete any messages marked as spam
        ignore_perms : list, optional
            The perms (ID Form), that bypass anti-spam
        ignore_channels : list, optional
            The channels (ID Form) that are ignored
        ignore_roles : list, optional
            The roles (ID, Name) that are ignored
        ignore_guilds : list, optional
            The guilds (ID) that are ignored
        ignore_users : list, optional
            The users (ID Form), that bypass anti-spam
        ignore_bots : bool, optional
            Should bots bypass anti-spam?
        warn_only : bool, optional
            Only warn users?
        no_punish : bool, optional
            Dont punish users?
            Return if they should be punished or
            not without actually punishing them
        per_channel_spam : bool, optional
            Track spam as per channel,
            rather then per guild
        guild_warn_message_delete_after : int, optional
            The time to delete the ``guild_warn_message`` message
        user_kick_message_delete_after : int, optional
            The time to delete the ``user_kick_message`` message
        guild_kick_message_delete_after : int, optional
            The time to delete the ``guild_kick_message`` message
        user_ban_message_delete_after : int, optional
            The time to delete the ``user_ban_message`` message
        guild_ban_message_delete_after : int, optional
            The time to delete the ``guild_ban_message`` message

        Warnings
        --------
        If using ``AntiSpamTracker``, please call this
        method on that class instance. Not this one.

        Notes
        =====
        This will override any current settings, if you wish
        to continue using existing settings and merely change some
        I suggest using the get_options method first and then giving
        those values back to this method with the changed arguments
        """
        options = self._ensure_options(**kwargs)

        guild = Guild(self.bot, guild_id, options, custom_options=True)
        try:
            guild = next(iter(g for g in self.guilds if g == guild))
        except StopIteration:
            log.warning(
                f"I cannot ensure I have permissions to kick/ban ban people in guild: {guild_id}"
            )

            self.guilds = guild
            log.info(f"Created Guild: {guild.id}")
        else:
            guild.options = options
            guild.has_custom_options = True

        log.info(f"Set custom options for guild: {guild_id}")

    def get_guild_options(self, guild_id: int) -> tuple:
        """
        Get the options dictionary for a given guild,
        if the guild doesnt exist raise an exception

        Parameters
        ----------
        guild_id : int
            The guild to get custom options for

        Returns
        -------
        tuple
            The options for this guild as tuple[0] and tuple[1] is a bool
            which is used to say if the guild has custom options or not

            Be wary of the return value. It is in the format,
            (dict, boolean),
            where dict is the options and boolean is whether
            or not these options are custom

        Raises
        ------
        BaseASHException
            This guild does not exist

        Notes
        -----
        The value for tuple[1] is not checked/ensured at runtime.
        Be wary of this if you access guild and manually change
        options rather then using this libraries methods.

        Another thing to note is this returns a deepcopy of the
        options dictionary. This is to encourage usage of this
        libraries methods for changing options, rather then
        playing around with them yourself and potentially
        doing damage.

        """
        guild = Guild(self.bot, guild_id, self.options)
        try:
            guild = next(iter(g for g in self.guilds if g == guild))
        except StopIteration:
            raise BaseASHException("This guild does not exist")
        else:
            log.debug(f"Returned guild options for {guild_id}")
            return deepcopy(guild.options), guild.has_custom_options

    def remove_custom_guild_options(self, guild_id: int) -> None:
        """
        Reset a guilds options to the ASH options

        Parameters
        ----------
        guild_id : int
            The guild to reset

        Warnings
        --------
        If using ``AntiSpamTracker``, please call this
        method on that class instance. Not this one.

        Notes
        -----
        This method will silently ignore guilds that
        do not exist, as it is considered to have
        'removed' custom options due to how Guild's
        are created

        """
        guild = Guild(self.bot, guild_id, self.options)
        try:
            guild = next(iter(g for g in self.guilds if g == guild))
        except StopIteration:
            pass
        else:
            guild.options = self.options
            guild.has_custom_options = False

            log.debug(f"Reset guild options for {guild_id}")

    def reset_user_count(self, user_id: int, guild_id: int, counter: str) -> None:
        """
        Reset an internal counter attached
        to a User object

        Parameters
        ----------
        user_id : int
            The user to reset
        guild_id : int
            The guild they are attached to
        counter : str
            A str denoting which count
            to reset, Options are:\n
            ``warn_counter`` -> Reset the warn count\n
            ``kick_counter`` -> Reset the kick count

        Raises
        ======
        LogicError
            Invalid count to reset

        Notes
        =====
        Silently ignores if the User or
        Guild does not exist. This is because
        in the packages mind, the counts are
        'reset' since the default value is
        the reset value.

        """
        guild = Guild(self.bot, guild_id, self.options)
        try:
            guild = next(iter(g for g in self.guilds if g == guild))
        except StopIteration:
            return

        user = User(self.bot, user_id, guild_id=guild_id, options=guild.options)
        try:
            user = next(iter(u for u in guild.users if u == user))
        except StopIteration:
            return

        if counter.lower() == Static.WARNCOUNTER:
            user.warn_count = 0
            log.debug(f"Reset the warn count for user: {user_id}")
        elif counter.lower() == Static.KICKCOUNTER:
            user.kick_count = 0
            log.debug(f"Reset the kick count for user: {user_id}")
        else:
            raise LogicError("Invalid counter argument, please select a valid counter.")

    @staticmethod
    def load_from_dict(bot, data: dict):  # TODO typehint this correct
        """
        Can be used as an entry point when starting your bot
        to reload a previous state so you don't lose all of
        the previous punishment records, etc, etc

        Parameters
        ----------
        bot : commands.Bot
            The bot instance
        data : dict
            The data to load AntiSpamHandler from

        Returns
        -------
        AntiSpamHandler
            A new AntiSpamHandler instance where
            the state is equal to the provided dict

        Warnings
        --------
        Don't provide data that was not given to you
        outside of the ``save_to_dict`` method unless
        you are maintaining the correct format.

        Notes
        -----
        This method does not check for data conformity.
        Any invalid input will error.

        -----

        This is fairly computationally expensive. It deepcopies
        nearly everything lol.

        """
        ash = AntiSpamHandler(bot=bot, **data["options"])
        for guild in data["guilds"]:
            ash.guilds = Guild.load_from_dict(bot, guild)

        log.info("Loaded AntiSpamHandler from state")
        return ash

    async def save_to_dict(self) -> dict:
        """
        Creates a 'save point' of the current
        state for this handler which can then be
        used to restore state at a later date

        Returns
        -------
        dict
            The saved state in a dictionary form.
            You can give this to ``load_from_dict``
            to reload the saved state

        Notes
        -----
        For most expected use-case's the returned ``Messages``
        will be outdated, however, they are included
        as it is technically part of the current state.

        -----

        Note that is method is expensive in both time and memory.
        It has to iterate over every single stored class
        instance within the library and store it in a dictionary.

        For bigger bots, it is likely better you create this process
        yourself using generators in order to reduce overhead.

        Warnings
        --------
        Due to the already expensive nature of this method,
        all returned option dictionaries are not deepcopied.
        Modifying them during runtime will cause this library
        to begin using that modified copy.

        """
        data = {"options": self.options, "guilds": []}
        for guild in self._guilds:
            data["guilds"].append(await guild.save_to_dict())

        log.info("Saved AntiSpamHandler state")

        return data

    def register_extension(self, extension, force_overwrite=False) -> None:
        """
        Registers an extension for usage for within the package

        Parameters
        ----------
        extension
            The extension to register
        force_overwrite : bool
            Whether to overwrite any duplicates currently stored.

            Think of this as calling ``unregister_extension`` and
            then proceeding to call this method.

        Raises
        ------
        ExtensionError
            An extension with this name is already loaded

        Notes
        -----
        This must be a class instance, and must
        subclass ``BaseExtension``
        """
        if not issubclass(type(extension), BaseExtension):
            log.debug("Failed to load extension due to class type issues")
            raise ExtensionError(
                "Expected extension that subclassed BaseExtension and was a class instance not class reference"
            )

        # TODO Try explicitly check its actually a class instance rather then inferring it?

        if not inspect.iscoroutinefunction(getattr(extension, "propagate")):
            log.debug("Failed to load extension due to a failed propagate inspect")
            raise ExtensionError("Expected coro method for propagate")

        is_pre_invoke = getattr(extension, "is_pre_invoke", True)

        propagate_signature = inspect.signature(getattr(extension, "propagate"))
        takes_params = len(propagate_signature.parameters)

        # TODO Fix this
        """
        if is_pre_invoke and takes_params != 2:
            log.debug("Extension propagate failed to take the required arguments")
            raise ExtensionError("Pre-invoke propagate take should `self, message`")
        elif not is_pre_invoke and takes_params != 3:
            log.debug("Extension propagate failed to take the required arguments")
            raise ExtensionError(
                "After-invoke propagate should take `self, message, data`"
            )
        """

        cls_name = extension.__class__.__name__.lower()

        if (
            self.pre_invoke_extensions.get(cls_name)
            or self.after_invoke_extensions.get(cls_name)
        ) and not force_overwrite:
            log.debug("Duplicate extension load attempt")
            raise ExtensionError(
                "Error loading extension, an extension with this name already exists!"
            )

        if is_pre_invoke:
            log.info(f"Loading pre-invoke extension: {cls_name}")
            self.pre_invoke_extensions[cls_name] = extension
        elif not is_pre_invoke:
            log.info(f"Loading after-invoke extension: {cls_name}")
            self.after_invoke_extensions[cls_name] = extension

    def unregister_extension(self, extension_name: str) -> None:
        """
        Used to unregister or remove an extension that is
        currently loaded into AntiSpamHandler

        Parameters
        ----------
        extension_name : str
            The name of the class you want to unregister

        Raises
        ------
        ExtensionError
            This extension isn't loaded

        """
        has_popped_pre_invoke = False
        try:
            self.pre_invoke_extensions.pop(extension_name.lower())
            has_popped_pre_invoke = True
        except KeyError:
            pass

        try:
            self.after_invoke_extensions.pop(extension_name.lower())
        except KeyError:
            if not has_popped_pre_invoke:
                log.debug(
                    f"Failed to unload extension {extension_name} as it isn't loaded"
                )
                raise ExtensionError("An extension matching this name doesn't exist!")

        log.info(f"Unregistered extension {extension_name}")

    def _ensure_options(
        self,
        warn_threshold=None,
        kick_threshold=None,
        ban_threshold=None,
        message_interval=None,
        guild_warn_message=None,
        guild_kick_message=None,
        guild_ban_message=None,
        user_kick_message=None,
        user_ban_message=None,
        user_failed_kick_message=None,
        user_failed_ban_message=None,
        message_duplicate_count=None,
        message_duplicate_accuracy=None,
        delete_spam=None,
        ignore_perms=None,
        ignore_users=None,
        ignore_channels=None,
        ignore_roles=None,
        ignore_guilds=None,
        ignore_bots=None,
        warn_only=None,
        no_punish=None,
        per_channel_spam=None,
        guild_warn_message_delete_after=None,
        user_kick_message_delete_after=None,
        guild_kick_message_delete_after=None,
        user_ban_message_delete_after=None,
        guild_ban_message_delete_after=None,
    ):
        """
        Given the relevant arguments,
        validate and return the options dict

        Notes
        =====
        For args, view this class's __init__ docstring
        """
        if not isinstance(warn_threshold, int) and warn_threshold is not None:
            raise ValueError("Expected warn_threshold of type int")

        if not isinstance(kick_threshold, int) and kick_threshold is not None:
            raise ValueError("Expected kick_threshold of type int")

        if not isinstance(ban_threshold, int) and ban_threshold is not None:
            raise ValueError("Expected ban_threshold of type int")

        if not isinstance(message_interval, int) and message_interval is not None:
            raise ValueError("Expected message_interval of type int")

        if message_interval is not None and message_interval < 1000:
            raise BaseASHException("Minimum message_interval is 1 seconds (1000 ms)")

        if (
            not isinstance(guild_warn_message, (str, dict))
            and guild_warn_message is not None
        ):
            raise ValueError("Expected guild_warn_message of type str or dict")

        if (
            not isinstance(guild_kick_message, (str, dict))
            and guild_kick_message is not None
        ):
            raise ValueError("Expected guild_kick_message of type str or dict")

        if (
            not isinstance(guild_ban_message, (str, dict))
            and guild_ban_message is not None
        ):
            raise ValueError("Expected guild_ban_message of type str or dict")

        if (
            not isinstance(user_kick_message, (str, dict))
            and user_kick_message is not None
        ):
            raise ValueError("Expected user_kick_message of type str or dict")

        if (
            not isinstance(user_ban_message, (str, dict))
            and user_ban_message is not None
        ):
            raise ValueError("Expected user_ban_message of type str or dict")

        if (
            not isinstance(user_failed_kick_message, (str, dict))
            and user_failed_kick_message is not None
        ):
            raise ValueError("Expected user_failed_kick_message of type str or dict")

        if (
            not isinstance(user_failed_ban_message, (str, dict))
            and user_failed_ban_message is not None
        ):
            raise ValueError("Expected user_failed_ban_message of type str or dict")

        if (
            not isinstance(message_duplicate_count, int)
            and message_duplicate_count is not None
        ):
            raise ValueError("Expected message_duplicate_count of type int")

        # Convert message_duplicate_accuracy from int to float if exists
        if isinstance(message_duplicate_accuracy, int):
            message_duplicate_accuracy = float(message_duplicate_accuracy)
        if (
            not isinstance(message_duplicate_accuracy, float)
            and message_duplicate_accuracy is not None
        ):
            raise ValueError("Expected message_duplicate_accuracy of type float")
        if message_duplicate_accuracy is not None:
            if 1.0 > message_duplicate_accuracy or message_duplicate_accuracy > 100.0:
                # Only accept values between 1 and 100
                raise ValueError(
                    "Expected message_duplicate_accuracy between 1 and 100"
                )

        if not isinstance(delete_spam, bool) and delete_spam is not None:
            raise ValueError("Expected delete_spam of type bool")

        if not isinstance(ignore_perms, list) and ignore_perms is not None:
            raise ValueError("Expected ignore_perms of type list")

        if not isinstance(ignore_users, list) and ignore_users is not None:
            raise ValueError("Expected ignore_users of type list")

        if not isinstance(ignore_channels, list) and ignore_channels is not None:
            raise ValueError("Expected ignore_channels of type list")

        if not isinstance(ignore_roles, list) and ignore_roles is not None:
            raise ValueError("Expected ignore_roles of type list")

        if not isinstance(ignore_guilds, list) and ignore_guilds is not None:
            raise ValueError("Expected ignore_guilds of type list")

        if not isinstance(ignore_bots, bool) and ignore_bots is not None:
            raise ValueError("Expected ignore_bots of type bool")

        if not isinstance(warn_only, bool) and warn_only is not None:
            raise ValueError("Expected warn_only of type bool")

        if not isinstance(no_punish, bool) and no_punish is not None:
            raise ValueError("Expected no_punish of type bool")

        if not isinstance(per_channel_spam, bool) and per_channel_spam is not None:
            raise ValueError("Expected per_channel_spam of type bool")

        if (
            not isinstance(guild_warn_message_delete_after, int)
            and guild_warn_message_delete_after is not None
        ):
            raise ValueError("Expected guild_warn_message_delete_after of type int")

        if (
            not isinstance(user_kick_message_delete_after, int)
            and user_kick_message_delete_after is not None
        ):
            raise ValueError("Expected user_kick_message_delete_after of type int")

        if (
            not isinstance(guild_kick_message_delete_after, int)
            and guild_kick_message_delete_after is not None
        ):
            raise ValueError("Expected guild_kick_message_delete_after of type int")

        if (
            not isinstance(user_ban_message_delete_after, int)
            and user_ban_message_delete_after is not None
        ):
            raise ValueError("Expected user_ban_message_delete_after of type int")

        if (
            not isinstance(guild_ban_message_delete_after, int)
            and guild_ban_message_delete_after is not None
        ):
            raise ValueError("Expected guild_ban_message_delete_after of type int")

        if warn_only and no_punish:
            raise BaseASHException(
                "Cannot do BOTH warn_only and no_punish. Pick one and try again"
            )

        # Now we have ignore_type checked everything, lets do some logic
        if ignore_bots is None:
            ignore_bots = Static.DEFAULTS.get("ignore_bots")

        if ignore_roles is not None:
            placeholder_ignore_roles = []
            for item in ignore_roles:
                if isinstance(item, discord.Role):
                    placeholder_ignore_roles.append(item.id)
                elif isinstance(item, int):
                    placeholder_ignore_roles.append(item)
                elif isinstance(item, str):
                    placeholder_ignore_roles.append(item)
                else:
                    raise ValueError(
                        "Expected discord.Role or int or str for ignore_roles"
                    )
            ignore_roles = placeholder_ignore_roles

        if ignore_channels is not None:
            placeholder_ignore_channels = []
            for item in ignore_channels:
                if isinstance(item, discord.TextChannel):
                    placeholder_ignore_channels.extend([item.id])
                else:
                    placeholder_ignore_channels.append(item)
            ignore_channels = placeholder_ignore_channels

        if ignore_users is not None:
            placeholder_ignore_users = []
            for item in ignore_users:
                if isinstance(item, discord.User) or isinstance(item, discord.Member):
                    placeholder_ignore_users.append(item.id)
                else:
                    placeholder_ignore_users.append(item)
            ignore_users = placeholder_ignore_users

        return {
            "warn_threshold": warn_threshold or Static.DEFAULTS.get("warn_threshold"),
            "kick_threshold": kick_threshold or Static.DEFAULTS.get("kick_threshold"),
            "ban_threshold": ban_threshold or Static.DEFAULTS.get("ban_threshold"),
            "message_interval": message_interval
            or Static.DEFAULTS.get("message_interval"),
            "guild_warn_message": guild_warn_message
            or Static.DEFAULTS.get("guild_warn_message"),
            "guild_kick_message": guild_kick_message
            or Static.DEFAULTS.get("guild_kick_message"),
            "guild_ban_message": guild_ban_message
            or Static.DEFAULTS.get("guild_ban_message"),
            "user_kick_message": user_kick_message
            or Static.DEFAULTS.get("user_kick_message"),
            "user_ban_message": user_ban_message
            or Static.DEFAULTS.get("user_ban_message"),
            "user_failed_kick_message": user_failed_kick_message
            or Static.DEFAULTS.get("user_failed_kick_message"),
            "user_failed_ban_message": user_failed_ban_message
            or Static.DEFAULTS.get("user_failed_ban_message"),
            "message_duplicate_count": message_duplicate_count
            or Static.DEFAULTS.get("message_duplicate_count"),
            "message_duplicate_accuracy": message_duplicate_accuracy
            or Static.DEFAULTS.get("message_duplicate_accuracy"),
            "delete_spam": delete_spam or Static.DEFAULTS.get("delete_spam"),
            "ignore_perms": ignore_perms or Static.DEFAULTS.get("ignore_perms"),
            "ignore_users": ignore_users or Static.DEFAULTS.get("ignore_users"),
            "ignore_channels": ignore_channels
            or Static.DEFAULTS.get("ignore_channels"),
            "ignore_roles": ignore_roles or Static.DEFAULTS.get("ignore_roles"),
            "ignore_guilds": ignore_guilds or Static.DEFAULTS.get("ignore_guilds"),
            "ignore_bots": ignore_bots,
            "warn_only": warn_only or Static.DEFAULTS.get("warn_only"),
            "no_punish": no_punish or Static.DEFAULTS.get("no_punish"),
            "per_channel_spam": per_channel_spam
            or Static.DEFAULTS.get("per_channel_spam"),
            "guild_warn_message_delete_after": guild_warn_message_delete_after
            or Static.DEFAULTS.get("guild_warn_message_delete_after"),
            "user_kick_message_delete_after": user_kick_message_delete_after
            or Static.DEFAULTS.get("user_kick_message_delete_after"),
            "guild_kick_message_delete_after": guild_kick_message_delete_after
            or Static.DEFAULTS.get("guild_kick_message_delete_after"),
            "user_ban_message_delete_after": user_ban_message_delete_after
            or Static.DEFAULTS.get("user_ban_message_delete_after"),
            "guild_ban_message_delete_after": guild_ban_message_delete_after
            or Static.DEFAULTS.get("guild_ban_message_delete_after"),
        }

    # <-- Getter & Setters -->
    @property
    def guilds(self):
        return self._guilds

    @guilds.setter
    def guilds(self, value):
        """
        Raises
        ======
        ValueError
            value must be a Guild object
        DuplicateObject
            It won't maintain two guild objects with the same
            id's, and it will complain about it haha
        ObjectMismatch
            Raised if `value` wasn't made by this person, so they
            shouldn't be the ones maintaining the reference
        """
        if not isinstance(value, Guild):
            raise ValueError("Expected Guild object")

        if value in self._guilds:
            raise DuplicateObject

        log.debug(f"Added guild: {value}")
        self._guilds.append(value)
