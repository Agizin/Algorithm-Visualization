import unittest
from . import code_macros

class CodeMacroTestCase(unittest.TestCase):

    def test_python_snapshot(self):
        self.assertEqual(
            code_macros.python3_snapshot(["h"], {"var": "h", "api": "Foo"}),
            "algviz.high_level.show(h, api=Foo, var='h')")

        self.assertEqual(
            code_macros.python3_snapshot(["h"], {"var": "h", "api": "Bar",
                                                 "indent": "7"}),
            "       algviz.high_level.show(h, api=Bar, var='h')")

if __name__ == "__main__":
    unittest.main()
