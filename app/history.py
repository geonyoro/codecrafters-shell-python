def load_history_from_file(filename, hist):
    with open(filename) as wfile:
        for line in wfile.readlines():
            line = line.strip()
            if not line:
                continue
            hist.append(line)
