import os
import typing


def cmd_type(args: list[str], environs: dict[str, typing.Any], stdout, stderr):
    paths = sorted(environs.get("PATH", "").split(":"))
    for prog_name in args[1:]:
        prog_name = prog_name.strip()
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


def cmd_echo(args: list[str], stdout, stderr):
    stdout.write(" ".join(args))
    stdout.write("\n")
