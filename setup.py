import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Discord Anti-Spam",
    version="0.2.1",
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
)
