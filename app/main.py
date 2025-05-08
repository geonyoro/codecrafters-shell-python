import re
import sys


def main():
    while True:
        sys.stdout.write("$ ")
        # Wait for user input
        command = input()
        mobj = re.match(r"exit (\d+)", command)
        if mobj:
            sys.exit(int(mobj[1]))
        print(f"{command}: command not found")


if __name__ == "__main__":
    main()
