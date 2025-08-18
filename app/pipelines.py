import os
import sys
from dataclasses import dataclass
from typing import IO


@dataclass
class Pipe:
    w: int
    r: int


@dataclass
class Command:
    command: str
    stdout_pipe: Pipe | None
    stdin_pipe: Pipe | None

    @property
    def fd_stdout(self) -> int | None:
        # sdtout_pipe is the newly created pipe. That is read from by the next command,
        # so for sdtout perform a write.
        if self.stdout_pipe:
            return self.stdout_pipe.w

    @property
    def fd_stdin(self) -> int | None:
        # stdin_pipe is the previous pipe. That is written to during stdout,
        # so for stdin perform a read
        if self.stdin_pipe:
            return self.stdin_pipe.r


def setup_pipeline(cmds: list[str]) -> list[Command]:
    p = []
    last_index = len(cmds) - 1
    previous_pipe = None
    for index, cmd in enumerate(cmds):
        is_last_index = index == last_index
        if is_last_index:
            pipe = None
        else:
            r, w = os.pipe()
            pipe = Pipe(w=w, r=r)
        p.append(Command(command=cmd, stdin_pipe=previous_pipe, stdout_pipe=pipe))
        if not is_last_index:
            previous_pipe = pipe

    return p


def get_stderr(stderr_fname: tuple[str, str] | None) -> IO:
    if stderr_fname:
        return open(stderr_fname[0], mode=stderr_fname[1])
    else:
        return sys.stderr


def get_stdout(stdout_fname: tuple[str, str] | None) -> IO:
    if stdout_fname:
        return open(stdout_fname[0], mode=stdout_fname[1])
    else:
        return sys.stdout
