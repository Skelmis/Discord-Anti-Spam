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
A short utility for random functions which don't fit into an object
"""

# TODO Move classmethods here to free up performance


def embed_to_string(embed) -> str:
    """
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
