import argparse
import random
from algviz.interface import visitors, high_level

class BinaryTree:
    def __init__(self, key=lambda x: x):
        self.data = None
        self._key = key
        self.left = None
        self.right = None

    def insert(self, val):
        if self.data is None:
            self.data = val
            self.left = BinaryTree()
            self.right = BinaryTree()
        elif self._key(self.data) < self._key(val):
            self.right.insert(val)
        else:
            self.left.insert(val)

class BTViz(visitors.TreeVisitor):
    def get_data(self, tree):
        return tree.data

    def iter_children(self, tree):
        yield tree.left
        yield tree.right

    def is_placeholder(self, tree):
        return tree is None or tree.data is None

def main():
    parser = argparse.ArgumentParser("Print JSON for a binary tree")
    parser.add_argument("size", type=int, help="size of the tree")
    args = parser.parse_args()
    data = list(range(args.size))
    random.shuffle(data)
    T = BinaryTree()
    for x in data:
        T.insert(x)
    high_level.show(T, api=BTViz, var="target")

if __name__ == "__main__":
    main()
