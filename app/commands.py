import os
import typing


def cmd_type(args: list[str], environs: dict[str, typing.Any], stdout, stderr):
    paths = environs.get("PATH", "").split(":")
    for prog_name in args[1:]:
        prog_name = prog_name.strip()
        if prog_name in environs.get("known_commands", []):
            stdout.write(f"{prog_name} is a shell builtin\n")
            return

        for path in paths:
            if not os.path.exists(path):
                continue
            for name in os.listdir(path):
                if name == prog_name:
                    fullpath = os.path.join(path, name)
                    if not os.access(fullpath, os.X_OK):
                        continue
                    stdout.write(f"{prog_name} is {fullpath}\n")
                    return

        stdout.write(f"{prog_name}: not found\n")


def cmd_echo(args: list[str], stdout, stderr):
    stdout.write(" ".join(args))
    stdout.write("\n")


def cmd_pwd(args: list[str], stdout, stderr):
    stdout.write(f"{os.getcwd()}\n")


def cmd_cd(args: list[str], environs: dict[str, typing.Any], stdout, stderr):
    new_path = args[1]
    if new_path == "~":
        new_path = os.environ["HOME"]

        # parts = new_path.split("/")
    try:
        os.chdir(new_path)
    except FileNotFoundError:
        print(f"cd: {new_path}: No such file or directory")
