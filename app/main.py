import os
import shlex
import subprocess
import sys
import typing

from app import commands, parsers

RUN_FUNC = typing.Callable[[list[str], dict[str, typing.Any]], None]

progs: dict[str, RUN_FUNC] = {
    "exit": lambda args, _: sys.exit(int(args[1])),
    "echo": lambda args, _: commands.cmd_echo(args[1:], _),
    "type": commands.cmd_type,
}

known_commands = list(progs.keys())

environ = {
    "known_commands": known_commands,
    "PATH": os.getenv("PATH", ""),
}


def raise_uncaught(num, c, prev_char, previous_quote_char, final_text):
    raise ValueError(
        f"Uncaught: {num=}, {c=}, {prev_char=}, {previous_quote_char=}, {final_text=}"
    )


def is_quote(c: str) -> bool:
    return c in ["'", '"']


def is_backslash(c: str) -> bool:
    return c == "\\"


def is_space(c: str) -> bool:
    return c == " "


def main():
    while True:
        sys.stdout.write("$ ")
        # Wait for user input
        args = parsers.parser(input())
        prog = args[0]
        run_func = progs.get(prog)
        if run_func:
            run_func(args, environ)
            continue

        try:
            p = subprocess.run(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                # env=environ,
            )
        except FileNotFoundError:
            print(f"{args[0]}: command not found")
        else:
            err = p.stderr
            out = p.stdout
            if err:
                print(err.decode().strip())
            elif out:
                print(out.decode().strip())


if __name__ == "__main__":
    main()
