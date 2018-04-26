import collections
import math

from . import visitors

class BitmapArrayVisitor(visitors.ArrayVisitor):
    """Interpret an `int` as an array of 0s and 1s"""

    def __init__(self, output_mngr, *args, data_visitor=None, **kwargs):
        if data_visitor is None:
            data_visitor = visitors.NumberVisitor(output_mngr)
        super().__init__(output_mngr, *args, data_visitor=data_visitor, **kwargs)

    def length(self, x):
        return math.ceil(math.log(x, 2))

    def get_item(self, x, i):
        # Return the i'th bit of x
        return int(bool(x & (2**i)))

class ListTreeVisitor(visitors.TreeVisitor):
    """Interpret a list as a binary tree"""
    _Node = collections.namedtuple("_Node", ("list_", "index"))
    def _wrap(self, tree):
        if isinstance(tree, self._Node):
            return tree
        return self._Node(tree, 0)

    def is_placeholder(self, tree):
        tree = self._wrap(tree)
        return tree.index >= len(tree.list_)

    def get_data(self, tree):
        tree = self._wrap(tree)
        return tree.list_[tree.index]

    def iter_children(self, tree):
        tree = self._wrap(tree)
        for i in (1, 2):
            yield self._Node(tree.list_, 2 * tree.index + i)
