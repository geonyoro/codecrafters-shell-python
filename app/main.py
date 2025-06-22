import io
import os
import readline
import subprocess
import sys
import typing
from functools import lru_cache
from os.path import isfile

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


@lru_cache
def get_path_prog_names():
    env_path = os.environ.get("PATH", "")
    # env_path = "/tmp/p:"
    paths = set()
    for dir in env_path.split(":"):
        if not os.path.exists(dir):
            continue
        for path in os.listdir(dir):
            full = os.path.join(dir, path)
            if isfile(full) and os.access(full, os.X_OK):
                paths.add(path)
    return paths


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


# print(get_path_prog_names())


has_printed_bell = False


def completer_func(text, state):
    source_list = sorted(set(list(progs.keys()) + list(get_path_prog_names())))
    matches = [i for i in source_list if i.startswith(text)]
    if state == 0:
        if len(matches) == 1:
            return matches[0]
        elif len(matches) > 1:
            global has_printed_bell
            if not has_printed_bell:
                has_printed_bell = True
                sys.stdout.write("\a")
                print()
            else:
                print("  ".join(matches))
                print(f"$ {text}", end="")
    return None


def main():
    readline.parse_and_bind("tab: complete")
    readline.set_completer(completer_func)
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
