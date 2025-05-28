def handle_input(input_str):
    cmd = []
    cur_arg = ""
    it = iter(input_str)
    try:
        c = next(it)
        while True:
            if c == "'":
                c = next(it)
                while c != "'":
                    cur_arg += c
                    c = next(it)
            elif c == '"':
                c = next(it)
                while c != '"':
                    if c == "\\":
                        c = next(it)
                        if c in '\\$"':
                            cur_arg += c
                            c = next(it)
                        else:
                            cur_arg += "\\"
                    else:
                        cur_arg += c
                        c = next(it)
                c = next(it)
            elif c == "\\":
                c = next(it)
                cur_arg += c
                c = next(it)
            elif c == " ":
                cmd.append(cur_arg)
                cur_arg = ""
                while c == " ":
                    c = next(it)
            else:
                cur_arg += c
                c = next(it)

    except StopIteration:
        cmd.append(cur_arg)

    return cmd


if __name__ == "__main__":
    print("$ ", end="")
    print(handle_input(input()))
