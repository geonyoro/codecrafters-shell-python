import os
import shlex
import subprocess
import sys
import typing

from app import commands

RUN_FUNC = typing.Callable[[str, dict[str, typing.Any]], None]

progs: dict[str, RUN_FUNC] = {
    "exit": lambda mobj, _: sys.exit(int(mobj[1])),
    "echo": lambda args, _: commands.cmd_echo(cmd_cleaner(args), _),
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


def cmd_cleaner(cmd: str, **kwargs) -> str:
    final_text = ""
    previous_quote_char = ""
    prev_char = ""
    ix = -1
    while True:
        ix += 1
        if ix == len(cmd):
            break
        c = cmd[ix]
        if is_quote(c):
            if is_backslash(prev_char):
                final_text += c
            # this is a quote character
            elif previous_quote_char == c or previous_quote_char == "":
                if previous_quote_char == "":
                    # we are starting a new quote
                    previous_quote_char = c
                else:
                    # matches closing quote, clear previous quote
                    previous_quote_char = ""
            else:
                final_text += c
        elif is_backslash(c):
            # either a backslash in a quote section (keep literal)
            # or a backslash after another one
            if previous_quote_char or is_backslash(prev_char):
                final_text += c
        elif c != " ":
            final_text += c
        elif c == " ":
            if previous_quote_char:
                # we are in a quote, we don't care, just add it
                final_text += c
            else:
                # we not in a quote
                if prev_char == " ":
                    # we already added a space previously
                    pass
                else:
                    final_text += c
        else:
            raise_uncaught(2, c, prev_char, previous_quote_char, final_text)

        prev_char = c
    return final_text


def main():
    while True:
        sys.stdout.write("$ ")
        # Wait for user input
        command = input()
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
