import unittest
import tempfile

from . import parser, errors

class ParserTestCase(unittest.TestCase):

    def _run_raw_parse(self, text):
        with tempfile.TemporaryFile("r+") as file:
            print(text, file=file, end="")
            file.flush()
            file.seek(0)
            return parser.parse(file)

    def _test_macro_free_chunk(self, text):
        self.assertEqual("\n".join(self._run_raw_parse(text)),
                         text)

    def test_no_newline_at_eof(self):
        self._test_macro_free_chunk("a\nb\nc\nhello, world!")
        self._test_macro_free_chunk("")
        self._test_macro_free_chunk("foo")

    def test_newline_at_eof(self):
        self._test_macro_free_chunk("\n")
        self._test_macro_free_chunk("\n\n")
        self._test_macro_free_chunk("hello, word!\n")
        self._test_macro_free_chunk("\nhello, word!\n" * 2)

    def test_unmatched_end_block_causes_error(self):
        with self.assertRaisesRegex(errors.AlgVizSyntaxError,
                                    "`.*end foo` on line . does not end anything"):
            self._run_raw_parse("@algviz end foo")

    def test_unmatched_begin_block_causes_error(self):
        with self.assertRaisesRegex(errors.AlgVizSyntaxError,
                                    "[Uu]nmatched `begin foo`"):
            self._run_raw_parse("@algviz begin foo\nla la la\n")

    def test_end_blocks_must_match_start_if_nonempty(self):
        text = """
@algviz begin foo
@algviz end bar
"""
        with self.assertRaisesRegex(errors.AlgVizSyntaxError,
                                    "`begin foo` ended with `end bar`"):
            self._run_raw_parse(text)

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
@algviz end two-level
random stuff
this is really just a test of the parser
we are still inside first nest
@algviz end
 @algviz end the space means this will not cause any issues

blank lines are OK
if i try to pop too many times i cause an error
@algviz command this is silly
"""
        parsed = self._run_raw_parse(text)
        self.assertEqual(
            parsed,
            ["", "Line 1 (after blank)", "Line 2", "begin {dafs",
             "this should all be outside", "@algiz begin spelled wrong",
             "still outside",
             parser.RawMacro(
                 command="command",
                 arguments="arg1:2 arg2:barney",
                 contents=None,
             ),
             parser.RawMacro(
                 command="nesting",
                 arguments="arga:dasf",
                 contents=[
                     "random stuff",
                     parser.RawMacro(
                         command="internal",
                         arguments="test case",
                         contents=None,
                     ),
                     parser.RawMacro(
                         command="two-level",
                         arguments="nesting",
                         contents=[],
                     ),
                     "random stuff",
                     "this is really just a test of the parser",
                     "we are still inside first nest",
                 ],
             ),
             " @algviz end the space means this will not cause any issues",
             "",
             "blank lines are OK",
             "if i try to pop too many times i cause an error",
             parser.RawMacro(
                 command="command",
                 arguments="this is silly",
                 contents=None,
             ),
             "",  # final line is empty 
            ])


if __name__ == "__main__":
    unittest.main()
