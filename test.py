import unittest

from app import main

# line 1 is the input, line 2 is the output


def parse_ins_and_outs(test_cases: str) -> tuple[list, list]:
    ins = []
    outs = []
    for line in test_cases.split("\n"):
        if not line or line.startswith("#"):
            continue
        verb, _, cmd = line.partition(":")
        if verb not in ["in", "out"]:
            raise ValueError(f"Invalid {verb=}")
        if verb == "in":
            ins.append(cmd)
        else:
            outs.append(cmd)

    assert len(ins) == len(outs)
    return ins, outs


class Tests(unittest.TestCase):
    def _test_cmd_cleaner(self):
        test_cases = r"""
in:echo hello   world
out:echo hello world

in:echo 'shell hello'
out:echo shell hello

in:echo 'world     test'
out:echo world     test

in:echo "quz  hello"  "bar"
out:echo quz  hello bar

in:echo "bar"  "shell's"  "foo"
out:echo bar shell's foo

in:echo "before\   after"
out:echo before   after

in:echo world\ \ \ \ \ \ script
out:echo world      script

in:echo \\x
out:echo \x

in:echo shell\ \ \ \ \ \ hello
out:echo shell      hello

in:echo \'\"shell example\"\'
out:echo '"shell example"'

in:echo \n
out:echo n

in:example\ntest
out:examplentest

in:echo "/tmp/bar/f\n39" "/tmp/bar/f\64" "/tmp/bar/f'\'56"
out:echo /tmp/bar/fn39 /tmp/bar/f64 /tmp/bar/f''56

in:echo "hello'script'\\n'world"
out:echo hello'script'\n'world

in:echo "hello\"insidequotes"script\"
out:echo hello"insidequotesscript"

in:echo "hello'script'\\n'world"
out:echo hello'script'\n'world

in:echo "mixed\"quote'world'\\"
out:echo mixed"quote'world'\
"""
        ins, outs = parse_ins_and_outs(test_cases)
        for index, (input, output) in enumerate(zip(ins, outs)):
            with self.subTest(input=input, output=output):
                toutput = main.cmd_cleaner(input, test_index=index)
                self.assertEqual(output, toutput)

    def test_parser_v2(self):
        test_cases = r"""
in:echo hello   world
out:['echo', 'hello', 'world']
"""
        ins, outs = parse_ins_and_outs(test_cases)
        for input, raw_out in zip(ins, outs):
            output = eval(raw_out)
            pout = main.parser_v2(input)
            self.assertEqual(output, pout)
