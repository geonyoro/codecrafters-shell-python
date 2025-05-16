import os
import shlex
import subprocess
import sys
import typing

from app import commands

RUN_FUNC = typing.Callable[[str, dict[str, typing.Any]], None]

progs: dict[str, RUN_FUNC] = {
    "exit": lambda mobj, _: sys.exit(int(mobj[1])),
    "echo": commands.cmd_echo,
    "type": commands.cmd_type,
}

known_commands = list(progs.keys())

environ = {
    "known_commands": known_commands,
    "PATH": os.getenv("PATH", ""),
}


def cmd_cleaner(cmd: str) -> str:
    final_text = ""
    previous_quote_char = ""
    prev_char = ""
    for c in cmd:
        # this is a quote character
        if c in ["'", '"'] and (previous_quote_char == c or previous_quote_char == ""):
            if previous_quote_char == "":
                # we are starting a new quote
                previous_quote_char = c
            else:
                previous_quote_char = ""
        elif c == "\\":
            if prev_char == "\\":
                final_text += c
        elif c != " ":
            final_text += c
        elif c == " ":
            if previous_quote_char:
                # we are in a quote, we don't care, just add it
                final_text += c
            # elif prev_char == "\\":
            #     final_text += c
            else:
                # we not in a quote
                if prev_char == " ":
                    # we already added a space previously
                    pass
                else:
                    final_text += c

        else:  # c == " "
            raise ValueError(f"New char {c=}")

        prev_char = c
    return final_text


def main():
    while True:
        sys.stdout.write("$ ")
        # Wait for user input
        command = cmd_cleaner(input())
        prog, _, args = command.partition(" ")
        run_func = progs.get(prog)
        if run_func:
            run_func(args, environ)
            continue

        args = shlex.split(command)
        try:
            p = subprocess.run(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                # env=environ,
            )
        except FileNotFoundError:
            print(f"{command}: command not found")
        else:
            err = p.stderr
            out = p.stdout
            if err:
                print(err.decode().strip())
            elif out:
                print(out.decode().strip())


if __name__ == "__main__":
    main()
