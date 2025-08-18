import unittest

from app import parsers, pipelines
from app.completion import get_common_base

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

    def test_get_common_base(self):
        progs = ["xyz_foo", "xyz_foo_bar", "xyz_foo_bar_baz"]
        # for a wrong complet
        with self.subTest("wrong completion, nothing is found"):
            self.assertEqual("", get_common_base("a", progs))

        with self.subTest("partial completion on xyz_foo"):
            self.assertEqual("xyz_foo", get_common_base("x", progs))
            self.assertEqual("xyz_foo", get_common_base("xyz", progs))
            self.assertEqual("xyz_foo", get_common_base("xyz_", progs))
            self.assertEqual("xyz_foo", get_common_base("xyz_foo", progs))

        with self.subTest("partial completion on xyz_foo_bar"):
            self.assertEqual("xyz_foo_bar", get_common_base("xyz_foo_b", progs))

        with self.subTest("full completion"):
            self.assertEqual("xyz_foo_bar_baz", get_common_base("xyz_foo_bar_b", progs))

    def test_parse_multi_cmd(self):
        cmds = parsers.parse_multi_cmd("cat /tmp/x | wc")
        self.assertEqual(cmds, ["cat /tmp/x", "wc"])

    def test_setup_pipeline(self):
        cmds = ["cat /tmp/x", "head -n2", "wc -l"]
        p = pipelines.setup_pipeline(cmds)
        # there are 3 elements
        self.assertEqual(len(p), 3)

        # commands match up
        self.assertEqual(p[0].command, "cat /tmp/x")
        self.assertEqual(p[1].command, "head -n2")
        self.assertEqual(p[2].command, "wc -l")

        # first input and last output are none
        self.assertIsNone(p[0].stdin_pipe)
        self.assertIsNone(p[2].stdout_pipe)

        # the redirects are setup properly, output of each stage being input to
        # the next stage
        self.assertEqual(p[0].stdout_pipe, p[1].stdin_pipe, "output of 0 is input to 1")
        self.assertEqual(p[1].stdout_pipe, p[2].stdin_pipe, "output of 1 is input to 2")
