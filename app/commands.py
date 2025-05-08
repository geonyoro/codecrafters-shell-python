import re
import typing


def cmd_type(mobj: re.Match, environs: dict[str, typing.Any]):
    prog_name = mobj[1]
    if prog_name in environs.get("known_commands", []):
        print(f"{prog_name} is a shell builtin")
    else:
        print(f"{prog_name}: not found")
