print("$ ", end="")
input_str = input()
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

print(cmd)
