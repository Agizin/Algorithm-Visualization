import unittest
import collections
from . import elements

class AnchorTestCase(unittest.TestCase):
    TestRectangle = collections.namedtuple("TestRectangle", ("width", "height"))

    def test_bottom_right_corner_anchor(self):
        # The top left corner of a rectangle of width 10 and height 6, with its
        # bottom right corner at (0, 0), would be (-10, -6).
        self.assertEqual(tuple(elements.top_left_corner(
            self.TestRectangle(width=10, height=6),
            (0, 0),
            elements.Anchor.bottom_right)),
                         (-10, -6))
                         
            
    def test_center_anchor(self):
        self.assertEqual(tuple(elements.top_left_corner(
            self.TestRectangle(width=300, height=7),
            (5, 10),
            elements.Anchor.center)),
                         (-145, 6.5))

    def test_anchor_translate(self):
        self.assertEqual(tuple(elements.anchor_translate(
            self.TestRectangle(width=100, height=50),
            (0, 0),
            elements.Anchor.left,
            elements.Anchor.top)),
                         (50, -25))

    def test_from_top_left_corner(self):

        self.assertEqual(tuple(elements.from_top_left_corner(
            self.TestRectangle(width=50, height=70),
            (0, 0),
            anchor=elements.Anchor.center)),
                         (25, 35))

if __name__ == "__main__":
    unittest.main()
