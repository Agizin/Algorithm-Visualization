from __future__ import print_function
import abc  # abstract base classes.  Don't worry too much about this
from collections import namedtuple

COMMENT_CHAR = "#"

class BinaryTreeIdentifier:
    # Don't worry about how abstract classes work in Python if you've never
    # seen them before.  Just notice the 4 abstract methods here.
    __metaclass__ = abc.ABCMeta

    # There are little problems with this visitor.  For instance, I assumed
    # every node would have either 0 or 2 children.
    @abc.abstractmethod
    def get_left(self, tree):
        raise NotImplementedError()
    @abc.abstractmethod
    def get_right(self, tree):
        raise NotImplementedError()
    @abc.abstractmethod
    def get_data(self, tree):
        raise NotImplementedError()
    @abc.abstractmethod
    def is_leaf(self, tree):
        return not (self.has_left(tree) or self.has_right(tree))

    @classmethod
    @abc.abstractmethod
    def has_left(cls, tree):
        raise NotImplemented
    @classmethod
    @abc.abstractmethod
    def has_right(cls, tree):
        raise NotImplemented
    
    @staticmethod
    def get_id(tree):
        return id(tree)  # not a good idea in all cases

class BinaryTreeVisitor:
    path_sep = " "

    def __init__(self, identifier):
        assert isinstance(identifier, BinaryTreeIdentifier)
        self.bti = identifier

    def visit(self, tree, prefix):
        print(prefix, ":", self.bti.get_data(tree))
        if not self.bti.is_leaf(tree):
            self.visit(self.bti.get_left(tree), prefix + self.path_sep + "left")
            self.visit(self.bti.get_right(tree), prefix + self.path_sep + "right")


class DifferentBinaryTreeVisitor(BinaryTreeVisitor):
    block_type_name = "binary_tree_block"

    def visit(self, tree, tree_name=None, parent_id="", relation="root", prefix="", _newblock=True):
        if _newblock:
            print("{} ({}) {{".format(self.block_type_name, tree_name))
        tree_id = self.bti.get_id(tree)
        print(prefix, end="")
        print("{} --{}--> {} --with-data-- {}".format(
            parent_id, relation, tree_id, self.bti.get_data(tree)))
        if self.bti.has_left(tree):
            self.visit(self.bti.get_left(tree),
                       parent_id=tree_id,
                       relation="left",
                       prefix=prefix+"  ",
                       _newblock=False)
        if self.bti.has_right(tree):
            self.visit(self.bti.get_right(tree), parent_id=tree_id,
                       relation="right",
                       prefix=prefix+"  ",
                       _newblock=False)
        if _newblock:
            print("}} {} end of {}".format(COMMENT_CHAR, self.block_type_name))

class UselessBinaryTree:
    # An example of a data structure to visualize
    # Note that this tree does not do anything useful.
    def __init__(self, contents):
        self.data = contents.pop()
        split = len(contents) // 2
        left, right = contents[:split], contents[split:]
        self.left = UselessBinaryTree(left) if left else None
        self.right = UselessBinaryTree(right) if right else None

class UselessBinaryTreeIdentifier(BinaryTreeIdentifier):
    # This will identify the tree features of UselessBinaryTree
    @staticmethod
    def get_left(x):
        return x.left

    @staticmethod
    def get_right(x):
        return x.right
    @classmethod
    def get_data(cls, x):
        # what to do with data is an open question
        if cls.is_leaf(x):
            return None
        return x.data

    @staticmethod
    def is_leaf(x):
        return x is None

    @classmethod
    def has_left(cls, x):
        return cls.get_left(x) is None

    @classmethod
    def has_right(cls, x):
        return cls.get_right(x) is None
    

# predefined_visitors = dict()

# # predefined_visitors[(UselessBinaryTree, None)] = UselessBinaryTreeIdentifier

# defaults = defaultdict(None)
# handlers[(UselessBinaryTree, None)] = UselessBinaryTreeIdentifier
# handlers[(UselessBinaryTree, "graph")] = UselessBinaryTreeAsGraphIdentifier

# _choose_visitor = {"object": ObjectVisitor}
# def choose_visitor(some_class):
#     result = _choose_visitor.get(some_class, None)
#     if result is not None:
#         return result
#     return choose_visitor(some_class.__bases__[0])

def visit_thing(thing, *args, hint=None, **kwargs):
    predefined_visitors[(type(thing), hint)].visit(
        thing, hint, *args, **kwargs)


class ArrayBinaryTreeIdentifier(BinaryTreeIdentifier):
    ArrayNode = namedtuple("ArrayNode", ("array", "index"))

    @classmethod
    def _fix_root(cls, tree):
        if isinstance(tree, cls.ArrayNode):
            return tree
        else:
            return cls.ArrayNode(tree, 0)

    @classmethod
    def has_left(cls, tree):
        tree = cls._fix_root(tree)
        return cls.get_left(tree).index < len(tree.array)

    @classmethod
    def has_right(cls, tree):
        tree = cls._fix_root(tree)
        return cls.get_right(tree).index < len(tree.array)

    @classmethod
    def get_left(cls, tree):
        tree = cls._fix_root(tree)
        return cls.ArrayNode(tree.array, tree.index * 2 + 1)

    @classmethod
    def get_right(cls, tree):
        tree = cls._fix_root(tree)
        return cls.ArrayNode(tree.array, tree.index * 2 + 2)

    @classmethod
    def get_data(cls, tree):
        tree = cls._fix_root(tree)
        return tree.array[tree.index]

    @classmethod
    def get_id(cls, tree):
        tree = cls._fix_root(tree)
        return "ArrayTree{}at{}".format(id(tree.array), tree.index)


def main():
    mytree = UselessBinaryTree([1, 2, 3, 4, 5, 6, 7, 8])
    visitor = BinaryTreeVisitor(UselessBinaryTreeIdentifier())
    other_visitor = DifferentBinaryTreeVisitor(UselessBinaryTreeIdentifier())
    # visitor.visit(mytree, "before_change")
    other_visitor.visit(mytree, "before_change")
    mytree.left = None
    # visitor.visit(mytree, "after_change")
    other_visitor.visit(mytree, "after_change")
    mytree.left = mytree.right
    other_visitor.visit(mytree, "weird")

def array_main():
    array_visitor = DifferentBinaryTreeVisitor(ArrayBinaryTreeIdentifier())
    array_visitor.visit([1, 2, 3, 4, 5, 6], "my_example_tree")


if __name__ == "__main__":
    # main()
    array_main()
    
