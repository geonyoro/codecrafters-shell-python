import io
import os
import shlex
import subprocess
import sys
import typing
from io import FileIO

from app import commands, parsers

RUN_FUNC = typing.Callable[
    # args
    [
        list[str],  # cmd
        dict[str, typing.Any],  # environ
        io.FileIO,  # stdout
        io.FileIO,  # stderr
    ],  # cmd
    None,
]

progs: dict[str, RUN_FUNC] = {
    "exit": lambda cmd, *args, **kwargs: sys.exit(int(cmd[1])),
    "echo": lambda args, _, stdout, stderr: commands.cmd_echo(args[1:], stdout, stderr),
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
        cmd, stdout_fname, stderr_fname = parsers.split_on_redirects(input())
        if stdout_fname:
            stdout = open(stdout_fname[0], mode=stdout_fname[1])
        else:
            stdout = sys.stdout

        if stderr_fname:
            stderr = open(stderr_fname[0], mode=stderr_fname[1])
        else:
            stderr = sys.stderr

        args = parsers.parser(cmd)
        prog = args[0]
        run_func = progs.get(prog)
        if run_func:
            run_func(args, environ, stdout, stderr)
            continue

        try:
            p = subprocess.run(
                args,
                stdout=stdout,
                stderr=stderr,
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
