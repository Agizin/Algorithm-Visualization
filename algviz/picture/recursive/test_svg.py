from . import svg

import unittest

class SVGHintTestCaseMixin:

    def test_margin_is_a_number(self):
        self.assert_positive_number(self.svg_hint.margin)

    def assert_positive_number(self, val):
        self.assertIsInstance(val, (float, int))
        self.assertGreaterEqual(val, 0)

    def test_pointer_size_is_tuple_of_numbers(self):
        width, height = self.svg_hint.pointer_size
        self.assert_positive_number(width)
        self.assert_positive_number(height)

    def test_computing_string_size(self):
        width, height = self.svg_hint.string_size("hello, world!")
        self.assert_positive_number(width)
        self.assert_positive_number(height)

    def test_null_size_is_tuple_of_numbers(self):
        width, height = self.svg_hint.null_size
        self.assert_positive_number(width)
        self.assert_positive_number(height)

    def test_array_margins_are_reasonable(self):
        self.assert_positive_number(self.svg_hint.array_border_margin)
        self.assert_positive_number(self.svg_hint.array_cell_sep)

class FullSVGPainterDefaultSVGHintTestCase(SVGHintTestCaseMixin, unittest.TestCase):
    def setUp(self):
        self.svg_hint = svg.FullSVGPainter({}).hint
