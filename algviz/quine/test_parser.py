import unittest
import tempfile

from . import parser

class ParserTestCase(unittest.TestCase):

    def _run_raw_parse(self, text):
        with tempfile.TemporaryFile("r+") as file:
            print(text, file=file, end="")
            file.flush()
            file.seek(0)
            return parser.parse(file)

    def test_simple_case_with_double_nesting(self):
        text = """
Line 1 (after blank)
Line 2
begin {dafs
this should all be outside
@algiz begin spelled wrong
still outside
@algviz command arg1:2 arg2:barney
@algviz begin nesting arga:dasf
random stuff
@algviz internal test case
@algviz begin two-level nesting
@algviz end These arguments will be ignored
random stuff
this is really just a test of the parser
we are still inside first nest
@algviz end ignore this
 @algviz end the space means this will not cause any issues

blank lines are OK
if i try to pop too many times i leave the parser
@algviz command this is silly
@algviz end the rest will be ignored

azqwsxdefrgthyjuik,ol.p;
"""
        parsed = self._run_raw_parse(text)
        self.assertEqual(
            parsed,
            ["", "Line 1 (after blank)", "Line 2", "begin {dafs",
             "this should all be outside", "@algiz begin spelled wrong",
             "still outside",
             {
                 "command": "command",
                 "arguments":  "arg1:2 arg2:barney",
             },
             {
                 "command": "nesting",
                 "arguments": "arga:dasf",
                 "contents": [
                     "random stuff",
                     {
                         "command": "internal",
                         "arguments": "test case",
                     },
                     {
                         "command": "two-level",
                         "arguments": "nesting",
                         "contents": [],
                     },
                     "random stuff",
                     "this is really just a test of the parser",
                     "we are still inside first nest",
                 ],
             },
             " @algviz end the space means this will not cause any issues",
             "",
             "blank lines are OK",
             "if i try to pop too many times i leave the parser",
             {
                 "command": "command",
                 "arguments": "this is silly",
             },
            ])


if __name__ == "__main__":
    unittest.main()
