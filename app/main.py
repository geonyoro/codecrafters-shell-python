import os
import re
import sys
import typing

from app import commands


class Prog:
    def __init__(
        self,
        name,
        _regexp,
        runfunc: typing.Callable[[re.Match, dict[str, typing.Any]], None],
    ):
        self._name = name
        self._regexp = _regexp
        self._runfunc = runfunc

    @property
    def name(self) -> str:
        return self._name

    @property
    def regexp(self) -> str:
        return self._regexp

    def run(self, match: re.Match, environ: dict):
        return self._runfunc(match, environ)


progs = (
    Prog("exit", r"exit (\d+)", lambda mobj, _: sys.exit(int(mobj[1]))),
    Prog("echo", r"echo (.*)", lambda mobj, _: print(mobj[1])),
    Prog("type", r"type (.*)", commands.cmd_type),
)

known_commands = [i.name for i in progs]

environ = {
    "known_commands": known_commands,
    "PATH": os.getenv("PATH", ""),
}


def main():
    while True:
        sys.stdout.write("$ ")
        # Wait for user input
        command = input()
        found_prog = False
        for prog in progs:
            mobj = re.match(prog.regexp, command)
            if mobj:
                prog.run(mobj, environ)
                found_prog = True
                break

        if not found_prog:
            print(f"{command}: command not found")


if __name__ == "__main__":
    main()
