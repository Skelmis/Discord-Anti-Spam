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
from copy import deepcopy
from string import Template

import discord

"""
A short utility for random functions which don't fit into an object
"""


def embed_to_string(embed) -> str:
    """
    Return the content of an embed,
    built to only return fields the package
    cares about for spam related issues

    Parameters
    ----------
    embed : discord.Embed
        The embed to turn into a string

    Returns
    -------
    str
        The content of the string
    """
    content = ""
    embed = embed.to_dict()

    if "title" in embed:
        content += f"{embed['title']}\n"

    if "description" in embed:
        content += f"{embed['description']}\n"

    if "footer" in embed:
        if "text" in embed["footer"]:
            content += f"{embed['footer']['text']}\n"

    if "author" in embed:
        if "name" in embed["author"]:
            content += f"{embed['author']['name']}\n"

    if "fields" in embed:
        for field in embed["fields"]:
            content += f"{field['name']}\n{field['value']}\n"

    return content


def dict_to_embed(data, message, counts) -> discord.Embed:
    """
    Given a dictionary, will attempt to build a
    valid discord.Embed object to return

    Parameters
    ----------
    data : dict
        The given item to try build an embed from
    message : discord.Message
        Where we get all our info from
    counts : dict
        Our current warn & kick counts

    Returns
    -------
    discord.Embed

    Notes
    -----
    For you smart-ass's out there. This does use ``discord.Embed.from_dict()``
    except this also lets you use templated strings within fields you
    smart cookies
    """
    allowed_avatars = ["$USERAVATAR", "$BOTAVATAR", "$GUILDICON"]

    if "title" in data:
        data["title"] = substitute_args(data["title"], message, counts)

    if "description" in data:
        data["description"] = substitute_args(data["description"], message, counts)

    if "footer" in data:
        if "text" in data["footer"]:
            data["footer"]["text"] = substitute_args(
                data["footer"]["text"], message, counts
            )

        if "icon_url" in data["footer"]:
            if data["footer"]["icon_url"] in allowed_avatars:
                data["footer"]["icon_url"] = substitute_args(
                    data["footer"]["icon_url"], message, counts
                )

    if "author" in data:
        if "name" in data["author"]:
            data["author"]["name"] = substitute_args(
                data["author"]["name"], message, counts
            )

        if "icon_url" in data["author"]:
            if data["author"]["icon_url"] in allowed_avatars:
                data["author"]["icon_url"] = substitute_args(
                    data["author"]["icon_url"], message, counts
                )

    if "fields" in data:
        for field in data["fields"]:
            name = substitute_args(field["name"], message, counts)
            value = substitute_args(field["value"], message, counts)
            field["name"] = name
            field["value"] = value

            if "inline" not in field:
                field["inline"] = True

    if "timestamp" in data:
        data["timestamp"] = message.created_at.isoformat()

    if "colour" in data:
        data["color"] = data["colour"]

    data["type"] = "rich"

    return discord.Embed.from_dict(data)


def substitute_args(message, value, counts) -> str:
    """
    Given the options string, return the string
    with the relevant values substituted in

    Parameters
    ----------
    message : str
        The string to substitute with values
    value : discord.Message
        Where we get our values from to substitute
    counts : dict
        Our current warn & kick counts

    Returns
    -------
    str
        The correctly substituted message

    """
    return Template(message).safe_substitute(
        {
            "MENTIONUSER": value.author.mention,
            "USERNAME": value.author.display_name,
            "USERID": value.author.id,
            "BOTNAME": value.guild.me.display_name,
            "BOTID": value.guild.me.id,
            "GUILDID": value.guild.id,
            "GUILDNAME": value.guild.name,
            "TIMESTAMPNOW": datetime.datetime.now().strftime("%I:%M:%S %p, %d/%m/%Y"),
            "TIMESTAMPTODAY": datetime.datetime.now().strftime("%d/%m/%Y"),
            "WARNCOUNT": counts["warn_count"],
            "KICKCOUNT": counts["kick_count"],
            "USERAVATAR": value.author.avatar_url,
            "BOTAVATAR": value.guild.me.avatar_url,
            "GUILDICON": value.guild.icon_url,
        }
    )


def transform_message(item, value, counts):
    """
    Given an item of two possible values, create
    and return the correct thing

    Parameters
    ----------
    item : [str, dict]
        Either a straight string or dict to turn in an embed
    value : discord.Message
        Where things come from
    counts : dict
        Our current warn & kick counts

    Returns
    -------
    [str, discord.Embed]

    """
    if isinstance(item, str):
        return substitute_args(item, value, counts)

    return dict_to_embed(deepcopy(item), value, counts)
