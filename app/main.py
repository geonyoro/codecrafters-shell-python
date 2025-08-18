import os
import readline
import shutil
import subprocess
import sys
import typing
from functools import lru_cache
from os.path import isfile

from app import commands, completion, parsers, pipelines

RUN_FUNC = typing.Callable[
    # args
    [commands.CmdArgs],  # cmd
    None,
]

progs: dict[str, RUN_FUNC] = {
    "exit": commands.cmd_exit,
    "echo": commands.cmd_echo,
    "type": commands.cmd_type,
    "pwd": commands.cmd_pwd,
    "cd": commands.cmd_cd,
    "history": commands.cmd_history,
}

known_commands = list(progs.keys())

custom_environ = {
    "known_commands": known_commands,
    "PATH": os.getenv("PATH", ""),
}


history = []
extra_args = {"history": history}


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
    # clone original input
    orig_stdin = os.dup(0)
    while True:
        os.dup2(orig_stdin, 0)
        sys.stdout.write("$ ")
        # Wait for user input, multi_cmd is a parent command with pipes and everything
        raw_cmd = input()
        history.append(raw_cmd)
        multi_cmd, stdout_fname, stderr_fname = parsers.split_on_redirects(raw_cmd)
        stderr = pipelines.get_stderr(stderr_fname=stderr_fname)

        cmds = parsers.parse_multi_cmd(multi_cmd)
        last_index = len(cmds) - 1
        pcmds = pipelines.setup_pipeline(cmds)
        for index, pcmd in enumerate(pcmds):
            is_last_index = index == last_index
            in_child = False
            if is_last_index:
                # final command should be run in the same process as the parent
                # hence no forking
                stdout = pipelines.get_stdout(stdout_fname=stdout_fname)
            else:
                pid = os.fork()
                in_child = pid == 0
                assert (
                    pcmd.fd_stdout
                )  # this must exist since this is a command earlier in the pipeline
                stdout = open(pcmd.fd_stdout, "w")
                if not in_child:
                    # parent continues next round to fork another set
                    continue
                # in child, will be reading from stdin.r and writing to stdout.w
                # close others
                # if pcmd.stdin_pipe:
                #     os.close(pcmd.stdin_pipe.w)
                # if pcmd.stdout_pipe:
                #     os.close(pcmd.stdout_pipe.r)

            # only children, or last_index parent can run here
            if not in_child:
                assert is_last_index

            args = parsers.parser(pcmd.command)
            prog = args[0]
            run_func = progs.get(prog)
            if run_func:
                cmd_args = commands.CmdArgs(
                    args=args,
                    environs=custom_environ,
                    stdout=stdout,
                    stderr=stderr,
                    extra_args=extra_args,
                )
                run_func(cmd_args)
            elif not shutil.which(prog):
                stdout.write(f"{prog}: not found\n")
                continue
            else:
                if pcmd.fd_stdin:
                    stdin = open(pcmd.fd_stdin)
                else:
                    stdin = None
                subprocess.call(args, stdin=stdin, stdout=stdout, stderr=stderr)
            if in_child:
                return


if __name__ == "__main__":
    main()
