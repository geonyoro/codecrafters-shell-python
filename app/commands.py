import os
import sys
import typing
from dataclasses import dataclass


@dataclass
class CmdArgs:
    args: list[str]
    environs: dict[str, typing.Any]
    stdout: typing.IO
    stderr: typing.IO
    extra_args: dict[str, typing.Any]


def cmd_exit(ca: CmdArgs):
    sys.exit(int(ca.args[1]))


def cmd_type(ca: CmdArgs):
    paths = ca.environs.get("PATH", "").split(":")
    for prog_name in ca.args[1:]:
        prog_name = prog_name.strip()
        if prog_name in ca.environs.get("known_commands", []):
            ca.stdout.write(f"{prog_name} is a shell builtin\n")
            return

        for path in paths:
            if not os.path.exists(path):
                continue
            for name in os.listdir(path):
                if name == prog_name:
                    fullpath = os.path.join(path, name)
                    if not os.access(fullpath, os.X_OK):
                        continue
                    ca.stdout.write(f"{prog_name} is {fullpath}\n")
                    return

        ca.stdout.write(f"{prog_name}: not found\n")


def cmd_echo(ca: CmdArgs):
    ca.stdout.write(" ".join(ca.args[1:]))
    ca.stdout.write("\n")


def cmd_pwd(ca: CmdArgs):
    ca.stdout.write(f"{os.getcwd()}\n")


def cmd_cd(ca: CmdArgs):
    new_path = ca.args[1]
    if new_path == "~":
        new_path = os.environ["HOME"]

        # parts = new_path.split("/")
    try:
        os.chdir(new_path)
    except FileNotFoundError:
        ca.stdout.write(f"cd: {new_path}: No such file or directory\n")


def cmd_history(ca: CmdArgs):
    for ix, row in enumerate(ca.extra_args["history"], start=1):
        print(f"{ix} {row}")
