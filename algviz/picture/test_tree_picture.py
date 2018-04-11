
from .picture import *
import os
import inspect
from algviz.parser import structures

filepath = os.path.abspath(os.path.dirname(__file__))
test_dir = os.path.join(filepath, "test_output")

def test_single_char(test_dir, outfile):
    a = structures.String("A")
    pic = StringLeaf(a)
    pic.draw()
    pic.save(os.path.join(test_dir, outfile))

def test_long_string(test_dir, outfile):
    s = structures.String("Antidisestablishmentarianism")
    pic = StringLeaf(s)
    pic.draw()
    pic.save(os.path.join(test_dir, outfile))

def test_single_tree_node(test_dir, outfile):
    a = structures.String("A")
    node = structures.TreeNode(a, uid=1)
    pic = TreePicture(node)
    pic.draw()
    pic.save(os.path.join(test_dir, outfile))

def test_single_node_long_string(test_dir, outfile):
    s = structures.String("Musicality")
    node = structures.TreeNode(s, uid=1)
    pic = TreePicture(node)
    pic.draw()
    pic.save(os.path.join(test_dir, outfile))

def test_simple_tree(test_dir, outfile):
    a = structures.String("A", uid=1)
    b = structures.String("B", uid=2)
    c = structures.String("C", uid=3)
    d = structures.String("D", uid=4)
    t1 = structures.TreeNode(d, uid=5)
    t2 = structures.TreeNode(b, [t1], uid=6)
    t3 = structures.TreeNode(c, uid=7)
    t4 = structures.TreeNode(a, [t2, t3], uid=8)
    pic = TreePicture(t4)
    pic.draw()
    pic.save(os.path.join(test_dir, outfile))

def test_long_string_tree(test_dir, outfile):
    a = structures.String("Alberto", uid=1)
    b = structures.String("Betty", uid=2)
    c = structures.String("Carlos", uid=3)
    d = structures.String("Denny", uid=4)
    e = structures.String("Ethan", uid=9)
    f = structures.String("Frances", uid=10)
    g = structures.String("Gloria", uid=11)
    t7 = structures.TreeNode(g, uid=14)
    t6 = structures.TreeNode(e, [t7],uid = 12)
    t5 = structures.TreeNode(f, uid=13)
    t4 = structures.TreeNode(d, uid=5)
    t3 = structures.TreeNode(b, [t4, t5, t6], uid=6)
    t2 = structures.TreeNode(c, uid=7)
    t1 = structures.TreeNode(a, [t2, t3], uid=8)
    pic = TreePicture(t1)
    pic.draw()
    pic.save(os.path.join(test_dir, outfile))

if __name__ == "__main__":
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
    test_single_char(test_dir, "01_char.svg")
    test_long_string(test_dir, "02_string.svg")
    test_single_tree_node(test_dir, "03_node.svg")
    test_single_node_long_string(test_dir, "04_long_node.svg")
    test_simple_tree(test_dir, "05_simple_tree.svg")
    test_long_string_tree(test_dir, "06_test_long_string_tree.svg")
