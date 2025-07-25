import os
import readline
import subprocess
import sys
import typing
from functools import lru_cache
from os.path import isfile

from app import commands, completion, parsers

RUN_FUNC = typing.Callable[
    # args
    [
        list[str],  # cmd
        dict[str, typing.Any],  # environ
        typing.Any,  # stdout
        typing.Any,  # stderr
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
    global has_printed_bell
    source_list = sorted(set(list(progs.keys()) + list(get_path_prog_names())))
    matches = [i for i in source_list if i.startswith(text)]
    # print(f"{matches=} {state=}")
    base = completion.get_common_base(text, matches)
    if state == 0:
        if len(matches) == 1:
            has_printed_bell = False
            return f"{matches[0]} "
        elif base and base != text:
            # there's a base and it has introduced a change
            has_printed_bell = False
            return f"{base}"
        elif len(matches) > 1:
            if not has_printed_bell:
                has_printed_bell = True
                sys.stdout.write("\a")
                print()
            else:
                print("  ".join(matches))
                print(f"$ {text}", end="")
                has_printed_bell = False
    return None


def main():
    readline.parse_and_bind("tab: complete")
    readline.set_completer(completer_func)
    while True:
        sys.stdout.write("$ ")
        # Wait for user input
        multi_cmd, stdout_fname, stderr_fname = parsers.split_on_redirects(input())
        if stderr_fname:
            stderr = open(stderr_fname[0], mode=stderr_fname[1])
        else:
            stderr = sys.stderr

        cmds = parsers.parse_multi_cmd(multi_cmd)
        last_index = len(cmds) - 1
        stdin = None
        for index, cmd in enumerate(cmds):
            is_last_run = index == last_index
            if is_last_run:
                if stdout_fname:
                    stdout = open(stdout_fname[0], mode=stdout_fname[1])
                else:
                    stdout = sys.stdout
            else:
                stdout = subprocess.PIPE

            args = parsers.parser(cmd)
            prog = args[0]
            run_func = progs.get(prog)
            if run_func:
                run_func(args, environ, stdout, stderr)
                continue

            try:
                p = subprocess.Popen(
                    args,
                    stdin=stdin,
                    stdout=stdout,
                    stderr=stderr,
                    # env=environ,
                )
                if is_last_run:
                    p.wait()
                stdin = p.stdout
            except FileNotFoundError:
                print(f"{args[0]}: command not found")
            else:
                if is_last_run:
                    for entry in (p.stderr, p.stdout):
                        if entry:
                            output = entry.read()
                            print(output, repr(output))

        # sys.stdout.write("\n")


if __name__ == "__main__":
    main()
