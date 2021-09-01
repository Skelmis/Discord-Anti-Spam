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
import datetime
import logging
from copy import deepcopy
from typing import Optional, Union

from attr import asdict


from .abc import Cache
from .core import Core
from .dataclasses import Guild, Options, CorePayload
from .caches import MemoryCache
from .enums import IgnoreType, ResetType
from .exceptions import (
    MissingGuildPermissions,
    ExtensionError,
    GuildNotFound,
    PropagateFailure,
)
from .factory import FactoryBuilder
from .base_plugin import BasePlugin


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

        member_kick_message : "Hey $MENTIONUSER, you are being kicked from $GUILDNAME for spamming/sending duplicate messages."
            The message to be sent to the user who is being warned

        member_ban_message : "Hey $MENTIONUSER, you are being banned from $GUILDNAME for spamming/sending duplicate messages."
            The message to be sent to the user who is being banned

        member_failed_kick_message : "I failed to punish you because I lack permissions, but still you shouldn't spam"
            The message to be sent to the user if the bot fails to kick them

        member_failed_ban_message : "I failed to punish you because I lack permissions, but still you shouldn't spam"
            The message to be sent to the user if the bot fails to ban them

        message_duplicate_count: 5
            The amount of duplicate messages needed within message_interval to trigger a punishment

        message_duplicate_accuracy: 90
            How 'close' messages need to be to be registered as duplicates (Out of 100)

        delete_spam: True
            Whether or not to delete messages marked as spam

            *Won't delete messages if* ``no_punish`` *is* ``True``

        ignore_perms: [8]
            The perms (ID Form), that bypass anti-spam

            **Not Implemented**

        ignored_members: []
            The users (ID Form), that bypass anti-spam

        ignored_channels: []
            Channels (ID Form), that bypass anti-spam

        ignored_roles: []
            The roles (ID Form), that bypass anti-spam

        ignored_guilds: []
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
            The time to delete the ``member_kick_message`` message

        guild_kick_message_delete_after: None
            The time to delete the ``guild_kick_message`` message

        user_ban_message_delete_after: None
            The time to delete the ``member_ban_message`` message

        guild_ban_message_delete_after: None
            The time to delete the ``guild_ban_message`` message

        delete_zero_width_chars: True
            Should zero width characters be removed from messages

        is_using_hikari: False
            Set this to True if you are using the package with hikari
            rather then discord.py


    """

    # TODO Add options for group spamming, rather then just per member.
    #      This could possibly be implemented at a Guild() level
    def __init__(
        self,
        bot,
        *,
        is_using_hikari: bool = False,
        options: Options = None,
        cache: Cache = None,
    ):
        # TODO Implement an async cache initialization somehow

        options = options or Options()
        if not isinstance(options, Options):
            raise ValueError("Expected `option`s of type `Option`")

        self.options = options

        if self.options.no_punish and (
            self.options.delete_spam
            or self.options.warn_only
            or self.options.per_channel_spam
        ):
            log.warning(
                "You are attempting to create an AntiSpamHandler with options that are mutually exclusive. "
                "Please note `no_punish` will over rule any other options you attempt to set which are "
                "mutually exclusive."
            )

        cache = cache or MemoryCache(self)
        if not issubclass(type(cache), Cache):
            raise ValueError("Expected `cache` that inherits from the `Cache` Protocol")

        # TODO We can't type check this. Just have to make an assumption the user is right till we error
        self.bot = bot
        self.cache = cache
        self.core = Core(self)

        self.pre_invoke_extensions = {}
        self.after_invoke_extensions = {}

        # Import these here to avoid errors when not having the
        # other lib installed, I think
        if is_using_hikari:
            from antispam.libs.hikari import Hikari

            self.lib_handler = Hikari(self)

        else:
            from antispam.libs.dpy import DPY

            self.lib_handler = DPY(self)

        log.info("Package initialized successfully")

    async def propagate(self, message) -> Optional[Union[CorePayload, dict]]:
        """
        This method is the base level intake for messages, then
        propagating it out to the relevant guild or creating one
        if that is required

        For what this returns please see the top of this page.

        Parameters
        ==========
        message : Union[discord.Message, hikari.messages.Message]
            The message that needs to be propagated out

        Returns
        =======
        dict
            A dictionary of useful information about the Member in question
        """
        try:
            propagate_data = await self.lib_handler.check_message_can_be_propagated(
                message=message
            )
        except PropagateFailure as e:
            return e.data

        log.debug(
            f"Propagating message for: {propagate_data.member_name}({propagate_data.member_id})"
        )

        try:
            guild = await self.cache.get_guild(guild_id=propagate_data.guild_id)
        except GuildNotFound:
            # Check we have perms to actually create this guild object
            # and punish based upon our guild wide permissions
            if not propagate_data.has_perms_to_make_guild:
                raise MissingGuildPermissions

            guild = Guild(id=propagate_data.guild_id, options=self.options)
            await self.cache.set_guild(guild)
            log.info(f"Created Guild: {guild.id}")

        pre_invoke_extensions = {}

        for pre_invoke_ext in self.pre_invoke_extensions.values():
            pre_invoke_return = await pre_invoke_ext.propagate(message)
            pre_invoke_extensions[pre_invoke_ext.__class__.__name__] = pre_invoke_return

            try:
                if pre_invoke_return.get("cancel_next_invocation"):
                    stats = self.after_invoke_extensions.get("stats")
                    if stats:
                        if hasattr(stats, "injectable_nonce"):
                            # Increment stats for invocation call stats
                            try:
                                stats.data["pre_invoke_calls"][pre_invoke_ext][
                                    "cancel_next_invocation_calls"
                                ] += 1
                            except KeyError:
                                stats.data["pre_invoke_calls"][pre_invoke_ext][
                                    "cancel_next_invocation_calls"
                                ] = 1

                    return pre_invoke_extensions
            except:
                pass

        main_return = await self.core.propagate(message, guild=guild)
        main_return.pre_invoke_extensions = pre_invoke_extensions

        for after_invoke_ext in self.after_invoke_extensions.values():
            after_invoke_return = await after_invoke_ext.propagate(message, main_return)
            main_return.after_invoke_extensions[
                after_invoke_ext.__class__.__name__
            ] = after_invoke_return

        return main_return

    def add_ignored_item(self, item: int, ignore_type: IgnoreType) -> None:
        """
        Add an item to the relevant ignore list

        Parameters
        ----------
        item : int
            The id of the thing to ignore
        ignore_type : IgnoreType
            An enum representing the item to ignore

        Raises
        ======
        ValueError
            item is not of type int or int convertible

        Notes
        =====
        This will silently ignore any attempts
        to add an item already added.
        """
        if not isinstance(ignore_type, IgnoreType):
            raise ValueError("Expected `ignore_type` to be of type IgnoreType")

        try:
            item = int(item)
        except (ValueError, TypeError):
            raise ValueError("Expected item of type: int")

        if ignore_type == IgnoreType.MEMBER:
            self.options.ignored_members.add(item)
        elif ignore_type == IgnoreType.CHANNEL:
            self.options.ignored_channels.add(item)
        elif ignore_type == IgnoreType.GUILD:
            self.options.ignored_guilds.add(item)
        # elif ignore_type == IgnoreType.ROLE:
        else:
            self.options.ignored_roles.add(item)

        log.debug(f"Ignored {ignore_type.name}: {item}")

    def remove_ignored_item(self, item: int, ignore_type: IgnoreType) -> None:
        """
        Remove an item from the relevant ignore list

        Parameters
        ----------
        item : int
            The id of the thing to un-ignore
        ignore_type : IgnoreType
            An enum representing the item to ignore

        Raises
        ======
        ValueError
            item is not of type int or int convertible

        Notes
        =====
        This will silently ignore any attempts
        to remove an item not ignored.
        """
        if not isinstance(ignore_type, IgnoreType):
            raise ValueError("Expected `ignore_type` to be of type IgnoreType")

        try:
            item = int(item)
        except (ValueError, TypeError):
            raise ValueError("Expected item of type: int")

        if ignore_type == IgnoreType.MEMBER:
            self.options.ignored_members.discard(item)
        elif ignore_type == IgnoreType.CHANNEL:
            self.options.ignored_channels.discard(item)
        elif ignore_type == IgnoreType.GUILD:
            self.options.ignored_guilds.discard(item)
        # elif ignore_type == IgnoreType.ROLE:
        else:
            self.options.ignored_roles.discard(item)

        log.debug(f"Un-Ignored {ignore_type.name}: {item}")

    async def add_guild_options(self, guild_id: int, options: Options) -> None:
        """
        Set a guild's options to a custom set, rather then the base level
        set used and defined in ASH initialization

        Warnings
        --------
        If using/modifying ``AntiSpamHandler.options`` to give to
        this method you will **also** be modifying the overall options.

        To get an options item you can modify freely call ``AntiSpamHandler.get_options()``,
        this method will give you an instance of the current options you are
        free to modify however you like.

        Notes
        =====
        This will override any current settings, if you wish
        to continue using existing settings and merely change some
        I suggest using the get_options method first and then giving
        those values back to this method with the changed arguments
        """
        if not isinstance(options, Options):
            raise ValueError("Expected options of type Options")

        try:
            guild = await self.cache.get_guild(guild_id=guild_id)
        except GuildNotFound:
            log.warning(
                f"I cannot ensure I have permissions to kick/ban ban people in guild: {guild_id}"
            )
            guild = Guild(id=guild_id, options=options)
            await self.cache.set_guild(guild)
            log.info(f"Created Guild: {guild.id}")
        else:
            guild.options = options

        log.info(f"Set custom options for guild: {guild_id}")

    async def get_guild_options(self, guild_id: int) -> Options:
        """
        Get the options dataclass for a given guild,
        if the guild doesnt exist raise an exception

        Parameters
        ----------
        guild_id : int
            The guild to get custom options for

        Returns
        -------
        Options
            The options for this guild

        Raises
        ------
        GuildNotFound
            This guild does not exist

        Notes
        -----
        This returns a copy of the options, if you wish to change
        the options on the guild you should use the package methods.

        """
        guild = await self.cache.get_guild(guild_id=guild_id)
        return deepcopy(guild.options)

    async def remove_guild_options(self, guild_id: int) -> None:
        """
        Reset a guilds options to the ASH options

        Parameters
        ----------
        guild_id : int
            The guild to reset

        Notes
        -----
        This method will silently ignore guilds that
        do not exist, as it is considered to have
        'removed' custom options due to how Guild's
        are created
        """
        try:
            guild = await self.cache.get_guild(guild_id=guild_id)
        except GuildNotFound:
            pass
        else:
            guild.options = self.options
            log.debug(f"Reset guild options for {guild_id}")

    async def reset_member_count(
        self, member_id: int, guild_id: int, reset_type: ResetType
    ) -> None:
        """
        Reset an internal counter attached
        to a User object

        Parameters
        ----------
        member_id : int
            The user to reset
        guild_id : int
            The guild they are attached to
        reset_type : ResetType
            An enum representing the
            counter to reset

        Notes
        =====
        Silently ignores if the User or
        Guild does not exist. This is because
        in the packages mind, the counts are
        'reset' since the default value is
        the reset value.

        """
        if not isinstance(reset_type, ResetType):
            raise ValueError("Expected reset_type of type ResetType")

        await self.cache.reset_member_count(member_id, guild_id, reset_type)

    async def add_guild_log_channel(self, log_channel: int, guild_id: int) -> None:
        """
        Registers a log channel on a guild internally

        Parameters
        ----------
        log_channel : int
            The channel id you wish to use for logging
        guild_id : int
            The id of the guild to store this on

        Notes
        -----
        Not setting a log channel means it will
        not send any punishment messages
        """
        if not isinstance(log_channel, int):
            raise ValueError("Expected log_channel with correct type")

        try:
            guild = await self.cache.get_guild(guild_id=guild_id)
            guild.log_channel_id = log_channel
        except GuildNotFound:
            guild = Guild(
                id=guild_id,
                options=self.options,
                log_channel_id=log_channel,
            )
            await self.cache.set_guild(guild)

    async def remove_guild_log_channel(self, guild_id: int) -> None:
        """
        Removes a registered guild log channel

        Parameters
        ----------
        guild_id : int
            The guild to remove it from

        Notes
        -----
        Silently ignores guilds which don't exist
        """
        try:
            guild = await self.cache.get_guild(guild_id)
            guild.log_channel_id = None
            await self.cache.set_guild(guild)
        except GuildNotFound:
            pass

    @staticmethod
    async def load_from_dict(bot, data: dict, *, raise_on_exception: bool = True):
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
        raise_on_exception : bool
            Whether or not to raise if an issue is encountered
            while trying to rebuild ``AntiSpamHandler`` from a saved state

            If you set this to False, and an exception occurs during the
            build process. This will return an ``AntiSpamHandler`` instance
            **without** any of the saved state and is equivalent to simply
            doing ``AntiSpamHandler(bot)``

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
        Any invalid input will error unless you set
        ``raise_on_exception`` to ``False`` in which case
        the following occurs

        If you set ``raise_on_exception`` to ``False``, and an exception occurs during the
        build process. This method will return an ``AntiSpamhandler`` instance
        **without** any of the saved state and is equivalent to simply
        doing ``AntiSpamHandler(bot)``

        """
        # TODO Add `cache` support
        try:
            ash = AntiSpamHandler(bot=bot, options=Options(**data["options"]))
            for guild in data["guilds"]:
                await ash.cache.set_guild(FactoryBuilder.create_guild_from_dict(guild))

            log.info("Loaded AntiSpamHandler from state")
        except Exception as e:
            if raise_on_exception:
                log.debug("Raising exception when attempting to load from state")
                raise e

            ash = AntiSpamHandler(bot=bot)
            log.info(
                "Failed to load AntiSpamHandler from state, returning a generic instance"
            )

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
        data = {"options": asdict(self.options), "guilds": []}
        for guild in await self.cache.get_all_guilds():
            data["guilds"].append(asdict(guild, recurse=True))

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
        subclass ``BasePlugin``
        """
        if not issubclass(type(extension), BasePlugin):
            log.debug("Failed to load extension due to class type issues")
            raise ExtensionError(
                "Expected extension that subclassed BasePlugin and was a class instance not class reference"
            )

        is_pre_invoke = getattr(extension, "is_pre_invoke", True)

        # propagate_signature = inspect.signature(getattr(extension, "propagate"))

        # Just accept that your not gonna be able to check
        # everything and its ultimately on the end developer
        # to get this correct rather then server-side validation

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
        else:
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
