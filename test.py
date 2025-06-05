import unittest

from app import parsers

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
    def test_parser(self):
        test_cases = r"""
in:echo hello   world
out:['echo', 'hello', 'world']
in:echo 'shell hello'
out:['echo', 'shell hello']
in:echo 'world     test'
out:['echo', 'world     test']
in:echo "quz  hello"  "bar"
out:['echo', 'quz  hello', 'bar']
in:echo "bar"  "shell's"  "foo"
out:['echo', 'bar', "shell's", 'foo']
in:echo "before\   after"
out:['echo', 'before\\   after']
in:echo world\ \ \ \ \ \ script
out:['echo', 'world      script']
in:echo \\x
out:['echo', '\\x']
in:echo shell\ \ \ \ \ \ hello
out:['echo', 'shell      hello']
in:echo \'\"shell example\"\'
out:['echo', '\'"shell', 'example"\'']
in:echo \n
out:['echo', 'n']
in:example\ntest
out:['examplentest']
in:echo "/tmp/bar/f\n39" "/tmp/bar/f\64" "/tmp/bar/f'\'56"
out:['echo', '/tmp/bar/f\\n39', '/tmp/bar/f\\64', "/tmp/bar/f'\\'56"]
in:echo "hello'script'\\n'world"
out:['echo', "hello'script'\\n'world"]
in:echo "hello\"insidequotes"script\"
out:['echo', 'hello"insidequotesscript"']
in:echo "hello'script'\\n'world"
out:['echo', "hello'script'\\n'world"]
in:echo "mixed\"quote'world'\\"
out:['echo', 'mixed"quote\'world\'\\']
"""
        ins, outs = parse_ins_and_outs(test_cases)
        for input, raw_out in zip(ins, outs):
            print(input)
            output = eval(raw_out)
            pout = parsers.parser(input)
            self.assertEqual(output, pout)

    def test_split_on_redirects(self):
        test_cases = r"""
in:echo 1 >1
out:(("echo 1 "),("1","w"),None)

in:echo 1>hello
out:(("echo "),("hello","w"),None)

in:echo 1> hello
out:(("echo "),("hello","w"),None)

in:echo > hello
out:(("echo "),("hello","w"),None)

in:echo x  x >> /tmp/hello
out:(("echo x  x "),("/tmp/hello","a"),None)

in:echo x  x 1>> /tmp/hello
out:(("echo x  x "),("/tmp/hello","a"),None)

in:echo 2> hello
out:(("echo "),None,("hello","w"))

in:echo > hello 2> goodbye
out:(("echo "),("hello","w"),("goodbye","w"))
"""
        ins, outs = parse_ins_and_outs(test_cases)
        for input, raw_out in zip(ins, outs):
            output = eval(raw_out)
            with self.subTest(input=input, output=output):
                pout = parsers.split_on_redirects(input)
                self.assertEqual(output, pout)
