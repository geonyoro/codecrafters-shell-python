import re
import sys


def main():
    while True:
        sys.stdout.write("$ ")
        # Wait for user input
        command = input()
        m_exit = re.match(r"exit (\d+)", command)
        if m_exit:
            sys.exit(int(m_exit[1]))
        m_echo = re.match(r"echo (.*)", command)
        if m_echo:
            print(m_echo[1])
            continue

        print(f"{command}: command not found")


if __name__ == "__main__":
    main()
