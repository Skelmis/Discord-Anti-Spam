"""
The MIT License (MIT)

Copyright (c) 2020-Current Skelmis

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
import functools
import logging
from copy import deepcopy
from typing import TYPE_CHECKING, Dict, Optional, Set, Type, Union

from attr import asdict

from antispam.abc import Cache
from antispam.base_plugin import BasePlugin
from antispam.caches import MemoryCache
from antispam.core import Core
from antispam.dataclasses import CorePayload, Guild, Options
from antispam.deprecation import mark_deprecated
from antispam.enums import IgnoreType, Library, ResetType
from antispam.exceptions import (
    GuildNotFound,
    InvalidMessage,
    InvocationCancelled,
    MissingGuildPermissions,
    PluginError,
    PropagateFailure,
    UnsupportedAction,
)
from antispam.factory import FactoryBuilder
from antispam.util import get_aware_time

if TYPE_CHECKING:  # pragma: no cover
    from antispam.plugins import Stats

log = logging.getLogger(__name__)

"""
The overall handler & entry point from any discord bot,
this is responsible for handling interaction with Guilds etc
"""


def ensure_init(func):
    """Ensures all cache related operations
    are done on an initialized cache.
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        handler = args[0]
        if handler.needs_init:
            await handler.init()

        return await func(*args, **kwargs)

    return wrapper


class AntiSpamHandler:
    """The overall handler for the DPY Anti-spam package"""

    def __init__(
        self,
        bot,
        library: Library,
        *,
        options: Options = None,
        cache: Cache = None,
    ):
        """
        AntiSpamHandler entry point.

        Parameters
        ----------
        bot
            A reference to your discord bot object.
        library : Library, Optional
            An enum denoting the library this AntiSpamHandler.
            See :py:class:`antispam.enums.library.Library` for more
        options : Options, Optional
            An instance of your custom Options
            the handler should use
        cache : Cache, Optional
            Your choice of backend caching
        """

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

        if self.options.use_timeouts and self.options.warn_only:
            log.warning(
                "You are attempting to create an AntiSpamHandler with options that are mutually exclusive. "
                "Please note `use_timeouts` will over rule any other options you attempt to set which are "
                "mutually exclusive."
            )

        cache = cache or MemoryCache(self)
        if not issubclass(type(cache), Cache):
            raise ValueError("Expected `cache` that inherits from the `Cache` Protocol")

        self.bot = bot
        self.cache = cache
        self.core = Core(self)

        self.needs_init = True

        self.pre_invoke_plugins: Dict[str, BasePlugin] = {}
        self.after_invoke_plugins: Dict[str, BasePlugin] = {}

        # Import these here to avoid errors when not
        # having the other lib installed
        self.lib_handler = None
        if library == Library.HIKARI:
            from antispam.libs.lib_hikari import Hikari

            self.lib_handler = Hikari(self)

        elif library == Library.DISNAKE:
            from antispam.libs.dpy_forks.lib_disnake import Disnake

            self.lib_handler = Disnake(self)

        elif library == Library.ENHANCED_DPY:
            from antispam.libs.dpy_forks.lib_enhanced_dpy import EnhancedDPY

            self.lib_handler = EnhancedDPY(self)

        elif library == Library.NEXTCORD:
            from antispam.libs.dpy_forks.lib_nextcord import Nextcord

            self.lib_handler = Nextcord(self)

        elif library == Library.PYCORD:
            raise UnsupportedAction(
                "Py-cord is no longer officially supported, please see the following url for support:\n"
                "https://gist.github.com/Skelmis/b15a64f11c2ef89a7c6083ff455774a2"
            )

        elif library == Library.CUSTOM:
            pass

        elif library == Library.DPY:
            from antispam.libs.dpy import DPY

            self.lib_handler = DPY(self)
        else:
            raise UnsupportedAction(
                "You must set a library for usage. See here for choices: "
                "https://dpy-anti-spam.readthedocs.io/en/latest/modules/interactions/enums.html#antispam.enums.Library"
            )

        log.info("Package instance created")

    async def init(self) -> None:
        """
        This method provides a means to initialize any
        async calls cleanly and without asyncio madness.

        Notes
        -----
        This method is guaranteed to be called before the
        first time propagate runs. However, it will not
        be run when the class is initialized.

        """
        await self.cache.initialize()

        if self.lib_handler is None:
            raise UnsupportedAction("lib_handler needs to be set before usage.")

        self.needs_init = False

        log.info("Init has been called, everything is now definitely setup.")

    @ensure_init
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

        log.info(
            "Propagating message for %s(%s) in guild(%s)",
            propagate_data.member_name,
            propagate_data.member_id,
            propagate_data.guild_id,
        )

        try:
            guild = await self.cache.get_guild(guild_id=propagate_data.guild_id)
        except GuildNotFound:
            # Check we have perms to actually create this guild object
            # and punish based upon our guild wide permissions
            if (
                not propagate_data.has_perms_to_make_guild
                and not self.options.no_punish
            ):
                raise MissingGuildPermissions

            guild = Guild(id=propagate_data.guild_id, options=self.options)
            await self.cache.set_guild(guild)
            log.info("Created Guild(id=%s)", guild.id)

        pre_invoke_extensions = {}

        for pre_invoke_ext in self.pre_invoke_plugins.values():
            if guild.id in pre_invoke_ext.blacklisted_guilds:
                # https://github.com/Skelmis/DPY-Anti-Spam/issues/65
                continue

            pre_invoke_return = await pre_invoke_ext.propagate(message)
            pre_invoke_extensions[pre_invoke_ext.__class__.__name__] = pre_invoke_return

            try:
                if pre_invoke_return.get("cancel_next_invocation"):
                    stats: Optional[BasePlugin] = self.after_invoke_plugins.get("stats")
                    if stats:
                        if hasattr(stats, "injectable_nonce"):
                            # Increment stats for invocation call stats
                            stats: "Stats" = stats  # type: ignore
                            try:
                                stats.data["pre_invoke_calls"][
                                    pre_invoke_ext.__class__.__name__
                                ]["cancel_next_invocation_calls"] += 1
                            except KeyError:
                                if (
                                    pre_invoke_ext.__class__.__name__
                                    not in stats.data["pre_invoke_calls"]
                                ):
                                    stats.data["pre_invoke_calls"][
                                        pre_invoke_ext.__class__.__name__
                                    ] = {}

                                stats.data["pre_invoke_calls"][
                                    pre_invoke_ext.__class__.__name__
                                ]["cancel_next_invocation_calls"] = 1

                    raise InvocationCancelled
            except InvocationCancelled as e:
                # Propagate this on further
                raise e from None
            except:
                pass

        try:
            main_return = await self.core.propagate(message, guild=guild)
            main_return.pre_invoke_extensions = pre_invoke_extensions
        except InvalidMessage as e:
            return {"status": e.message}

        for after_invoke_ext in self.after_invoke_plugins.values():
            if guild.id in after_invoke_ext.blacklisted_guilds:
                # https://github.com/Skelmis/DPY-Anti-Spam/issues/65
                continue

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

        log.info("Added %s as an ignored item under bucket %s", item, ignore_type.name)

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

        log.info(
            "Removed %s as an ignored item under bucket %s", item, ignore_type.name
        )

    @ensure_init
    async def add_guild_options(self, guild_id: int, options: Options) -> None:
        """
        Set a guild's options to a custom set, rather then the base level
        set used and defined in ASH initialization

        Warnings
        --------
        If using/modifying ``AntiSpamHandler.options`` to give to
        this method you will **also** be modifying the overall options.

        To get an options item you can modify freely call :py:meth:`antispam.AntiSpamHandler.get_options`
        this method will give you an instance of the current options you are
        free to modify however you like.

        Notes
        =====
        This will override any current settings, if you wish
        to continue using existing settings and merely change some
        I suggest using the ``get_options`` method first and then giving
        those values back to this method with the changed arguments
        """
        if not isinstance(options, Options):
            raise ValueError("Expected options of type Options")

        try:
            guild = await self.cache.get_guild(guild_id=guild_id)
        except GuildNotFound:
            log.warning(
                "I cannot ensure I have permissions to kick/ban ban people in Guild(id=%s)",
                guild_id,
            )
            guild = Guild(id=guild_id, options=options)
            log.info("Created Guild(id=%s)", guild.id)
        else:
            guild.options = options

        await self.cache.set_guild(guild)
        log.info("Set custom options for guild(%s)", guild_id)

    @ensure_init
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

    async def get_options(self) -> Options:
        """
        Returns a safe to modify instance of this
        handlers options.

        Returns
        -------
        Options
            The safe to use options
        """
        return deepcopy(self.options)

    @ensure_init
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
            await self.cache.set_guild(guild)
            log.debug("Reset options for Guild(id=%s)", guild_id)

    @ensure_init
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

    @ensure_init
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

    @ensure_init
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
    async def load_from_dict(
        bot,
        data: dict,
        library: Library,
        *,
        raise_on_exception: bool = True,
        plugins: Set[Type[BasePlugin]] = None,
    ):
        """
        Can be used as an entry point when starting your bot
        to reload a previous state so you don't lose all of
        the previous punishment records, etc, etc

        Parameters
        ----------
        bot
            The bot instance
        data : dict
            The data to load AntiSpamHandler from
        library: Library
            The :py:class:`Library` you are using.
        raise_on_exception : bool
            Whether or not to raise if an issue is encountered
            while trying to rebuild ``AntiSpamHandler`` from a saved state

            If you set this to False, and an exception occurs during the
            build process. This will return an ``AntiSpamHandler`` instance
            **without** any of the saved state and is equivalent to simply
            doing ``AntiSpamHandler(bot)``
        plugins : Set[Type[antispam.BasePlugin]]
            A set for plugin lookups if you want to initialise
            plugins from an initial saved state. This should follow the format.

            .. code-block:: python

                {ClassReference}

            So for example:

            .. code-block:: python
                :linenos:

                class Plugin(BasePlugin):
                    pass

                # Where you load ASH
                await AntiSpamHandler.load_from_dict(..., ..., plugins={Plugin}

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
        build process. This method will return an ``AntiSpamHandler`` instance
        **without** any of the saved state and is equivalent to simply
        doing ``AntiSpamHandler(bot)``

        This will simply ignore the saved state of plugins that don't have
        a ``plugins`` mapping.

        """
        # TODO Add redis cache here
        plugins = plugins or {}
        plugins: Dict[str, Type[BasePlugin]] = {
            class_ref.__name__: class_ref for class_ref in plugins
        }

        caches = {"MemoryCache": MemoryCache}

        try:
            ash = AntiSpamHandler(
                bot=bot, options=Options(**data["options"]), library=library
            )
            cache_type = data["cache"]
            ash.cache = caches[cache_type](ash)
            for guild in data["guilds"]:
                await ash.cache.set_guild(FactoryBuilder.create_guild_from_dict(guild))

            if pre_invoke_plugins := data.get("pre_invoke_plugins"):
                for plugin, plugin_data in pre_invoke_plugins.items():
                    if plugin_class_ref := plugins.get(plugin):
                        ash.register_plugin(
                            await plugin_class_ref.load_from_dict(ash, plugin_data)
                        )
                    else:
                        log.debug("Skipping state loading for %s", plugin)

            if after_invoke_plugins := data.get("after_invoke_plugins"):
                for plugin, plugin_data in after_invoke_plugins.items():
                    if plugin_class_ref := plugins.get(plugin):
                        plugin = await plugin_class_ref.load_from_dict(ash, plugin_data)
                        plugin.is_pre_invoke = False
                        ash.register_plugin(plugin)
                    else:
                        log.debug("Skipping state loading for %s", plugin)

            log.info("Loaded AntiSpamHandler from state")
        except Exception as e:
            if raise_on_exception:
                log.debug("Raising exception when attempting to load from state")
                raise e

            ash = AntiSpamHandler(bot=bot, library=library)
            log.info(
                "Failed to load AntiSpamHandler from state, returning a generic instance"
            )

        return ash

    @ensure_init
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

        Note that is method is expensive in both time and memory.
        It has to iterate over every single stored class
        instance within the library and store it in a dictionary.

        For bigger bots, it is likely better you create this process
        yourself using generators in order to reduce overhead.

        This will return saved Plugin states where the Plugin has
        implemented the ``save_to_dict`` method.

        Warnings
        --------
        Due to the already expensive nature of this method,
        all returned option dictionaries are not deepcopied.
        Modifying them during runtime will cause this library
        to begin using that modified copy.

        """
        data = {
            "options": asdict(self.options),
            "cache": self.cache.__class__.__name__,
            "guilds": [],
            "pre_invoke_plugins": {},
            "after_invoke_plugins": {},
        }
        async for guild in self.cache.get_all_guilds():  # pragma: no cover
            data["guilds"].append(asdict(guild, recurse=True))

        for plugin in self.pre_invoke_plugins.values():
            try:
                data["pre_invoke_plugins"][
                    plugin.__class__.__name__
                ] = await plugin.save_to_dict()
            except NotImplementedError:
                continue

        for plugin in self.after_invoke_plugins.values():
            try:
                data["after_invoke_plugins"][
                    plugin.__class__.__name__
                ] = await plugin.save_to_dict()
            except NotImplementedError:
                continue

        log.info("Saved AntiSpamHandler state")

        return data

    def register_plugin(self, plugin, force_overwrite=False) -> None:
        """
        Registers a plugin for usage for within the package

        Parameters
        ----------
        plugin
            The plugin to register
        force_overwrite : bool
            Whether to overwrite any duplicates currently stored.

            Think of this as calling ``unregister_extension`` and
            then proceeding to call this method.

        Raises
        ------
        PluginError
            A plugin with this name is already loaded

        Notes
        -----
        This must be a class instance, and must
        subclass ``BasePlugin``
        """
        if not issubclass(type(plugin), BasePlugin):
            log.debug("Failed to load extension due to class type issues")
            raise PluginError(
                "Expected extension that subclassed BasePlugin and was a class instance not class reference"
            )

        is_pre_invoke = getattr(plugin, "is_pre_invoke", True)

        # propagate_signature = inspect.signature(getattr(extension, "propagate"))

        # Just accept that your not gonna be able to check
        # everything and its ultimately on the end developer
        # to get this correct rather then server-side validation

        cls_name = plugin.__class__.__name__.lower()

        if (
            self.pre_invoke_plugins.get(cls_name)
            or self.after_invoke_plugins.get(cls_name)
        ) and not force_overwrite:
            log.debug("Duplicate extension load attempt")
            raise PluginError(
                "Error loading extension, an extension with this name already exists!"
            )

        if is_pre_invoke:
            log.info("Loading pre-invoke extension: %s", cls_name)
            self.pre_invoke_plugins[cls_name] = plugin
        else:
            log.info("Loading after-invoke extension: %s", cls_name)
            self.after_invoke_plugins[cls_name] = plugin

    def unregister_plugin(self, plugin_name: str) -> None:
        """
        Used to unregister or remove a plugin that is
        currently loaded into AntiSpamHandler

        Parameters
        ----------
        plugin_name : str
            The name of the class you want to unregister

        Raises
        ------
        PluginError
            This extension isn't loaded

        """
        has_popped_pre_invoke = False
        try:
            self.pre_invoke_plugins.pop(plugin_name.lower())
            has_popped_pre_invoke = True
        except KeyError:
            pass

        try:
            self.after_invoke_plugins.pop(plugin_name.lower())
        except KeyError:
            if not has_popped_pre_invoke:
                log.debug(
                    "Failed to unload extension %s as it isn't currently loaded",
                    plugin_name,
                )
                raise PluginError("An extension matching this name doesn't exist!")

        log.info("Unregistered extension: %s", plugin_name)

    async def clean_cache(self, strict=False) -> None:
        """
        Cleans the internal cache, pruning
        any old/un-needed entries.

        Non Strict mode:
         - Member deletion criteria:
            - warn_count == default
            - kick_count == default
            - duplicate_counter == default
            - duplicate_channel_counter_dict == default
            - addons dict == default
            - Also must have no active messages after cleaning.

         - Guild deletion criteria:
            - options are not custom
            - log_channel_id is not set
            - addons dict == default
            - Also must have no members stored

        Strict mode:
         - Member deletion criteria
            - Has no active messages

         - Guild deletion criteria
            - Does not have custom options
            - log_channel_id is not set
            - Has no active members

        Parameters
        ----------
        strict : bool
            Toggles the above


        Notes
        -----
        This is expensive, and likely
        only required to be run every so often
        depending on how high traffic your bot is.
        """
        # In a nutshell,
        # Get entire cache and loop over
        # Build a list of 'still valid' cache entries
        # Drop the previous cache
        # Insert the new list of 'still valid' entries, this is now the cache

        # Ideally I don't want to load this cache into memory
        cache = []
        async for guild in self.cache.get_all_guilds():
            new_guild = Guild(guild.id)
            for member in guild.members.values():
                FactoryBuilder.clean_old_messages(
                    member, get_aware_time(), self.options
                )

                if strict and len(member.messages) != 0:
                    new_guild.members[member.id] = member
                elif (
                    len(member.messages) != 0
                    or member.kick_count != 0
                    or member.warn_count != 0
                    or member.duplicate_counter != 1
                    or bool(member.duplicate_channel_counter_dict)
                    or bool(member.addons)
                ):
                    new_guild.members[member.id] = member

            # Clean guild
            predicate = (
                guild.options != self.options
                or guild.log_channel_id is not None
                or bool(new_guild.members)
            )
            if strict and predicate:
                new_guild.options = guild.options
                new_guild.log_channel_id = guild.log_channel_id
                cache.append(new_guild)
            elif predicate or bool(guild.addons):
                new_guild.addons = guild.addons
                new_guild.options = guild.options
                new_guild.log_channel_id = guild.log_channel_id
                cache.append(new_guild)

        await self.cache.drop()

        for guild in cache:
            await self.cache.set_guild(guild)

        log.info("Cleaned the internal cache")

    async def visualize(
        self, content: str, message, warn_count: int = 1, kick_count: int = 2
    ):
        """
        Wraps around :py:meth:`antispam.abc.Lib.visualizer` as a convenience
        """
        target = await self.lib_handler.visualizer(
            content=content,
            message=message,
            warn_count=warn_count,
            kick_count=kick_count,
        )
        return target

    def set_cache(self, cache: Cache) -> None:
        """
        Change the AntiSpamHandler internal cache
        to be the one provided.

        .. code-block:: python
            :linenos:

            bot.handler = AntiSpamHandler(bot)
            cache = MongoCache(bot.handler, "Connection_url")
            bot.handler.set_cache(cache)

        Parameters
        ----------
        cache: Cache
            The cache to change it to.

        Raises
        ------
        ValueError
            The provided cache was not of the expected type.

        """
        if not issubclass(type(cache), Cache):
            raise ValueError("Expected `cache` that inherits from the `Cache` Protocol")

        self.cache = cache
        log.info(
            "Changed the AntiSpamHandler cache to use %s", cache.__class__.__name__
        )
