import os
import re
import typing


def cmd_type(mobj: re.Match, environs: dict[str, typing.Any]):
    prog_name = mobj[1]
    paths = environs.get("PATH", "").split(":")
    if prog_name in environs.get("known_commands", []):
        print(f"{prog_name} is a shell builtin")
        return

    for path in paths:
        if not os.path.exists(path):
            continue
        for name in os.listdir(path):
            if name == prog_name:
                fullpath = os.path.join(path, name)
                print(f"{prog_name} is {fullpath}")
                return

    print(f"{prog_name}: not found")


def cmd_echo(mobj: re.Match, _):
    text = mobj[1]
    final_text = ""
    previous_quote_char = ""
    prev_char = ""
    for c in text:
        if c in ["'", '"'] and (previous_quote_char == c or previous_quote_char == ""):
            if previous_quote_char == "":
                # we are starting a new quote
                previous_quote_char = c
            else:
                previous_quote_char = ""
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

        else:  # c == " "
            raise ValueError(f"New char {c=}")

        prev_char = c
    print(final_text)
