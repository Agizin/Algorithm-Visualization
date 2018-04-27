import unittest

from algviz.parser import structures
from . import rec_layout, elements, svg, layout_dispatch

class DisorganizedLayoutTestCase(unittest.TestCase):

    def setUp(self):
        self.svg_hint = svg.default_full_drawer().hint

    def test_pointer_requirement_thing(self):
        ptr = structures.Pointer(structures.String("hello world!", uid="thestring"),
                                 uid="theptr")
        ptr_layout = rec_layout.PointerLayout(ptr, svg_hint=self.svg_hint)
        str_layout = rec_layout.StringLayout(ptr.referent, svg_hint=self.svg_hint)
        requirements = list(ptr_layout.pointer_requirements())
        self.assertEqual(len(requirements), 1)
        self.assertEqual(requirements[0].ptr_obj, ptr)
        layout = rec_layout.CompositeLayout(ptr_layout, str_layout, svg_hint=self.svg_hint)
        self.assertEqual(list(layout.pointer_requirements()), [])
        self.assertTrue(any(isinstance(elt, elements.Arrow)
                            and elt.origin is ptr_layout.element
                            and elt.destination is str_layout.element
                            for elt in layout.elements()))

    def test_elements_is_repeatable(self):
        layout = rec_layout.SimpleTreeLayout(
            structures.Tree(structures.Null, uid="silly"),
            choose_child_cls=layout_dispatch.make_layout_chooser({}),
            svg_hint=self.svg_hint)
        layout.scale(10)
        def sum_coords(elts):
            return sum(pair[1].width + pair[1].height for pair in layout.elements()
                       if isinstance(pair, tuple))
        old_sum = sum_coords(layout.elements())
        self.assertEqual(old_sum, sum_coords(layout.elements()))
        layout.scale(10)
        self.assertEqual(old_sum * 10, sum_coords(layout.elements()))

# class RecursiveLayoutTestCase(unittest.TestCase):

#     # TODO -- test that elements() can be called twice without harm
        

class TreeLayoutTestCaseMixin(unittest.TestCase):
    layout_cls = None
    def object_to_draw(self):
        return structures.Tree(fuu)
