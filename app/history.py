import os


def load_history_from_file(filename, hist):
    if not filename or not os.path.exists(filename):
        return
    with open(filename) as wfile:
        for line in wfile.readlines():
            line = line.strip()
            if not line:
                continue
            hist.append(line)


def write_history_to_file(filename, hist):
    if not filename:
        return
    with open(filename, "w") as wfile:
        for line in hist:
            wfile.write(line + "\n")
