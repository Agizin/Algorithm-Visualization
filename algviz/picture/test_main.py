import unittest
import os

from . import main
from algviz.parser import json_objects 
from algviz.interface import high_level

class MainTestCase(unittest.TestCase):
    def _test_make_svg(self, obj):
        decoded = json_objects.reads(high_level.string_snapshot(
            obj, var="foo"))

        self.assertIsSVG(main.make_svg(decoded, {"var": "foo"}))

    def assertIsSVG(self, text):
        self.assertIsInstance(text, str)

    def test_make_svg_int_array(self):
        self._test_make_svg([1, 2, 3, 4, 5])

    def test_make_svg_str(self):
        self._test_make_svg("hello, world!")

    def _test_from_filename(self, filename):
        with open(filename, "r") as f:
            decoded = json_objects.read(f)
        self.assertIsSVG(main.make_svg(decoded, {"var": "target"}))

    def test_json_from_test_cases_directory(self):
        directory = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "test_cases")
        json_files = [os.path.join(directory, filename)
                      for filename in os.listdir(directory)
                      if filename.endswith(".json")]
        for filename in json_files:
            self._test_from_filename(filename)
        

if __name__ == "__main__":
    unittest.main()
