import unittest

from . import main
from algviz.parser import json_objects 
from algviz.interface import high_level

class MainTestCase(unittest.TestCase):
    def _test_make_svg(self, obj):
        decoded = json_objects.reads(high_level.string_snapshot(
            obj, var="foo"))

        self.assertIsInstance(main.make_svg(decoded, {"var": "foo"}),
                              str)

    def test_make_svg_int_array(self):
        self._test_make_svg([1, 2, 3, 4, 5])

    def test_make_svg_str(self):
        self._test_make_svg("hello, world!")

if __name__ == "__main__":
    unittest.main()
