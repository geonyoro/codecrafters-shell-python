import os
import re
import typing


def cmd_type(mobj: re.Match, environs: dict[str, typing.Any]):
    prog_name = mobj[1]
    paths = environs.get("PATH", "").split(":")
    if prog_name in environs.get("known_commands", []):
        print(f"{prog_name} is a shell builtin")
        return

    for path in paths:
        if not os.path.exists(path):
            continue
        for name in os.listdir(path):
            if name == prog_name:
                fullpath = os.path.join(path, name)
                print(f"{prog_name} is {fullpath}")
                return

    print(f"{prog_name}: not found")


def cmd_echo(mobj: re.Match, _):
    text = mobj[1]
    if text.startswith("'"):
        text = text[1:]
    if text.endswith("'"):
        text = text[:-1]
    print(text)
