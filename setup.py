import re

from distutils.core import setup


with open("readme.md", "r") as fh:
    long_description = fh.read()

_version_regex = (
    r"^__version__ = ('|\")((?:[0-9]+\.)*[0-9]+(?:\.?([a-z]+)(?:\.?[0-9])?)?)\1$"
)

try:
    with open("antispam/__init__.py") as stream:
        match = re.search(_version_regex, stream.read(), re.MULTILINE)
        version = match.group(2)
except FileNotFoundError:
    version = "0.0.0"

setup(
    name="Discord Anti-Spam",
    version=version,
    author="Skelmis",
    author_email="ethan@koldfusion.xyz",
    description="An easy to use package for anti-spam features in discord.py.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Skelmis/DPY-Anti-Spam",
    packages=[
        "antispam",
        "antispam.caches",
        "antispam.caches.memory",
        "antispam.dataclasses",
        "antispam.enums",
        "antispam.plugins",
        "antispam.libs",
    ],
    install_requires=["fuzzywuzzy>=0.18", "discord.py>=1", "attrs"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
    ],
    python_requires=">=3.8",
)
