import sys
from dataclasses import dataclass
from io import FileIO


def parser(input: str) -> list[str]:
    cmds = []
    ix = 0
    cur_arg = ""
    try:
        while True:
            # print(ix, input[ix], repr(cur_arg), cmds)
            if input[ix] == "'":
                # consume single quotes
                ix += 1
                while input[ix] != "'":
                    cur_arg += input[ix]
                    ix += 1
                ix += 1
            elif input[ix] == '"':
                # consume double quotes
                ix += 1
                while input[ix] != '"':
                    if input[ix] == "\\":
                        ix += 1
                        # backslash
                        if input[ix] in '$`\\"':
                            cur_arg += input[ix]
                        else:
                            cur_arg += "\\"  # readd the skipped backlash
                            cur_arg += input[ix]
                    else:
                        cur_arg += input[ix]
                    ix += 1
                ix += 1
            elif input[ix] == "\\":
                ix += 1
                cur_arg += input[ix]
                ix += 1
            elif input[ix] == " ":
                if cur_arg:
                    cmds.append(cur_arg)
                    cur_arg = ""
                while input[ix] == " ":
                    ix += 1
            else:
                cur_arg += input[ix]
                ix += 1
    except IndexError:
        if cur_arg:
            cmds.append(cur_arg)

    return cmds


def split_on_redirects(
    inpt: str,
) -> tuple[str, tuple[str, str] | None, tuple[str, str] | None]:
    """
    Returns a tuple of the command, stdout, and stderr
    """
    cmd = ""
    stderr = stdout = None
    ix = 0
    hit_redirect = None
    mode = "w"
    string_size = len(inpt)
    try:
        # we keep going until we hit a redirect
        while True:
            # print(ix, string_size, inpt[ix])
            if inpt[ix] == ">":
                ix += 1
                hit_redirect = "stdout"
                if inpt[ix] == ">":
                    ix += 1
                    mode = "a"
                break
            elif inpt[ix] in "12":
                ix += 1
                if ix >= string_size:
                    # we have consumed a random 1
                    cmd += inpt[ix - 1]
                    break
                else:
                    if inpt[ix] == ">":
                        if inpt[ix - 1] == "1":
                            hit_redirect = "stdout"
                        else:
                            hit_redirect = "stderr"
                        ix += 1
                        if inpt[ix] == ">":
                            mode = "a"
                        break
                    else:
                        cmd += inpt[ix - 1]
                        cmd += inpt[ix]
                        ix += 1
            elif inpt[ix] == "\\":
                ix += 1
                if inpt[ix] == ">":
                    cmd += ">"
                else:
                    cmd += "\\"
                    cmd += inpt[ix]
                ix += 1
            else:
                cmd += inpt[ix]
                ix += 1
    except IndexError:
        pass

    while hit_redirect:
        # consume all the spaces
        try:
            while inpt[ix] == " ":
                ix += 1
        except IndexError:
            break

        if hit_redirect == "stdout":
            stdout_fname = ""
            try:
                # consume non-spaces
                while inpt[ix] != " ":
                    if inpt[ix] == "2":
                        ix += 1
                        try:
                            if inpt[ix] == ">":
                                stdout = (stdout_fname, mode)
                                hit_redirect = "stderr"
                                ix += 1
                                try:
                                    if inpt[ix] == ">":
                                        mode = "a"
                                        ix += 1
                                except IndexError:
                                    # doesn't change the mode
                                    pass
                        except IndexError:
                            # we hit the end. Re-add the missing 2 above
                            stdout_fname += "2"
                    else:
                        stdout_fname += inpt[ix]

                    ix += 1
                    if hit_redirect == "stderr":
                        break

                # having consumed the non-spaces, skip and keep going till you hit the 2>
                stdout = (stdout_fname, mode)
                hit_redirect = ""
                try:
                    while True:
                        if inpt[ix] == "2":
                            ix += 1
                            if inpt[ix] == ">":
                                hit_redirect = "stderr"
                                ix += 1
                                if inpt[ix] == ">":
                                    mode = "a"
                                break
                        else:
                            # skip everything else
                            ix += 1

                except IndexError:
                    # we ran till the end
                    pass
            except IndexError:
                pass
            stdout = (stdout_fname, mode)
        elif hit_redirect == "stderr":
            fname = ""
            try:
                while inpt[ix] != " ":
                    fname += inpt[ix]
                    ix += 1
            except IndexError:
                pass
            stderr = (fname, mode)
            hit_redirect = None
        else:
            ix += 1
            print(inpt[ix:])

    return cmd, stdout, stderr
