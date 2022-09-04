from pathlib import Path
from typing import Union, List


def count_lines(directory: Union[str, List[str]]):
    """Count Python LOC in a given directory."""
    if isinstance(directory, str):
        directories = [directory]
    else:
        directories = directory

    total_lines: int = 0
    print("{:>10} |{:>10} | {:<20}".format("ADDED", "TOTAL", "FILE"))
    print("{:->11}|{:->11}|{:->20}".format("", "", ""))
    for directory in directories:
        for path in Path(directory).rglob("*.py"):
            with open(path.absolute(), "r") as f:
                newlines = f.readlines()
                newlines = len(newlines)
                total_lines += newlines
                print(
                    "{:>10} |{:>10} | {:<20}".format(newlines, total_lines, str(path))
                )


count_lines(["./antispam", "./tests"])
