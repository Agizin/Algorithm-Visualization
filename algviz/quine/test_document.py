from algviz.interface import testutil
import unittest

from . import document, parser, errors

class DocumentTestCase(testutil.TempFileTestMixin, unittest.TestCase):

    def test_simple_case(self):
        text = r"""
@algviz begin hidden
Three trailing spaces""" + "   " + r"""
@algviz end hidden
Hello, world!

@algviz begin code lang=python3 name=mycode
@algviz header
foo = [1, 2, 3]
@algviz snapshot foo
@algviz end code
"""
        doc = self.full_doc_from_text(text)
        self.assertEqual(doc.quine(), text, msg="ORIG:\n{!r}\nQUINE:\n{!r}".format(text, doc.quine()))

    def test_quine_should_be_verbatim(self):
        text = "Hello, world!"  # no newline
        self.assertEqual(self.full_doc_from_text(text).quine(), text)

    def test_no_duplicate_arguments(self):
        text = r"""
@algviz begin code lang=python3 lang=python2 name=bob
@algviz end
"""
        with self.assertRaisesRegex(errors.MacroSyntaxError, "argument .*lang.* given twice"):
            self.full_doc_from_text(text)

    def test_splitting_macro_args_simple(self):
        pos, keyword = document.MacroChunk.split_args("foo bar buzz a=b c=d")
        self.assertEqual(list(pos), ["foo", "bar", "buzz"])
        self.assertEqual([(k, v) for k, v in keyword.items()],
                         [("a", "b"), ("c", "d")])

    def test_invalid_keyword_args_to_code_chunk(self):
        text = r"""
@algviz begin code lang=python3 asdfgh=123 name=foo
@algviz end code
"""
        with self.assertRaisesRegex(errors.UnrecognizedMacroKeywordArgumentError,
                                    "[Uu]nrecognized keyword argument `asdfgh`"):
            self.full_doc_from_text(text)

    def full_doc_from_text(self, text):
        self.write_tempfile(text)
        return document.FullDocument.from_parsed_text(
            parser.parse(self.open_tempfile_read()))

if __name__ == "__main__":
    unittest.main()
