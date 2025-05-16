import unittest

from app import main


class Tests(unittest.TestCase):
    def test_cmd_cleaner(self):
        for input, output in {
            # "echo hello world": "echo hello world",
            # "echo hello   world": "echo hello world",
            # "echo 'shell hello'": "echo shell hello",
            # "echo 'world     test'": "echo world     test",
            # 'echo "quz  hello"  "bar"': "echo quz  hello bar",
            # 'echo "bar"  "shell\'s"  "foo"': "echo bar shell's foo",
            # r'echo "before\   after"': r"echo before\   after",
            r"echo world\ \ \ \ \ \ script": "echo world      script",
            r"echo \\x": r"echo \x",
            r"echo shell\ \ \ \ \ \ hello": "echo shell      hello",
        }.items():
            with self.subTest(input=input, output=output):
                toutput = main.cmd_cleaner(input)
                self.assertEqual(output, toutput)
