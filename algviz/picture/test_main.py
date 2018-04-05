import unittest

from . import main
from algviz.parser import json_objects 
from algviz.interface import high_level

class MainTestCase(unittest.TestCase):
    def test_make_svg(self):
        decoded = json_objects.reads(high_level.string_snapshot(
            [1, 2, 3, 4, 5], var="foo"))

        self.assertIsInstance(main.make_svg(decoded, {"var": "foo"}),
                              str)

if __name__ == "__main__":
    unittest.main()
