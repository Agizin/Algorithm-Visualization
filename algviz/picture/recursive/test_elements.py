import unittest
import collections
from . import elements


class RectElementTestCaseMixin:

    def _make_element(self, width, height):
        return self.element_cls(width, height)

    def test_scaling(self):
        elt = self._make_element(5, 5)
        elt.scale(2.5)
        self.assertEqual(elt.width, 12.5)
        self.assertEqual(elt.width, elt.height)

class NodeElementTestCase(RectElementTestCaseMixin, unittest.TestCase):
    element_cls = elements.NodeElement

class PointerSourceTestCase(RectElementTestCaseMixin, unittest.TestCase):
    element_cls = elements.PointerSource

class StringElementTestCase(RectElementTestCaseMixin, unittest.TestCase):
    element_cls = elements.StringElement
    def _make_element(self, width, height):
        return self.element_cls(width, height, text="sample")

class NullElementTestCase(RectElementTestCaseMixin, unittest.TestCase):
    element_cls = elements.NullElement

class DecorationTestCaseMixin:

    def test_can_scale_decoration(self):
        self._make_element().scale(5)

class ArrowTestCase(DecorationTestCaseMixin, unittest.TestCase):
    element_cls = elements.Arrow
    def _make_element(self):
        return self.element_cls(elements.NodeElement(1, 2),
                                elements.NodeElement(3, 4))

class StraightArrowTestCase(ArrowTestCase):
    element_cls = elements.StraightArrow

class SplineArrowTestCase(ArrowTestCase):
    element_cls = elements.SplineArrow

if __name__ == "__main__":
    unittest.main()
