import setuptools
import unittest


def my_test_suite():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover("testing", pattern="test_*.py")
    return test_suite


with open("readme.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Discord Anti-Spam",
    version="0.5.0",
    author="Skelmis",
    author_email="ethan@koldfusion.xyz",
    description="An easy to use package for anti-spam features in discord.py.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Skelmis/DPY-Anti-Spam",
    packages=setuptools.find_packages(),
    install_requires=["fuzzywuzzy>=0.18", "discord.py>=1"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
    ],
    python_requires=">=3.6",
    test_suite="setup.my_test_suite",
)
