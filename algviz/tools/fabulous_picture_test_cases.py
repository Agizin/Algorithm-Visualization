from algviz.picture.fabulous.picture import *
import os
import inspect
from algviz.parser import structures
from algviz.picture.fabulous.main import make_svg

filepath = os.path.abspath(os.path.dirname(__file__))
test_dir = os.path.join(filepath, "test_output")

def test_single_char(test_dir, outfile):
    """Tests drawing of string with length 1 character"""
    a = structures.String("A")
    pic = StringLeaf(a)
    pic.draw()
    pic.save(os.path.join(test_dir, outfile))

def test_long_string(test_dir, outfile):
    """Tests drawing of string with long length"""
    s = structures.String("Antidisestablishmentarianism")
    pic = StringLeaf(s)
    pic.draw()
    pic.save(os.path.join(test_dir, outfile))

def test_single_tree_node(test_dir, outfile):
    """Tests drawing of a single tree node"""
    a = structures.String("A")
    node = structures.TreeNode(a, uid=1)
    pic = TreePicture(node)
    pic.draw()
    pic.save(os.path.join(test_dir, outfile))

def test_single_node_long_string(test_dir, outfile):
    """Tets drawing of a single node containing a long string"""
    s = structures.String("Musicality")
    node = structures.TreeNode(s, uid=1)
    pic = TreePicture(node)
    pic.draw()
    pic.save(os.path.join(test_dir, outfile))

def test_simple_tree(test_dir, outfile):
    """Tests drawing a simple tree structure with nodes containing only characters"""
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
    """Tests a relatively complex tree structure with nodes containg strings of variable length"""
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

def test_nested_tree(test_dir, outfile):
    """Tests drawing of a tree node containg a tree rather than a string"""
    a = structures.String("A", uid=1)
    b = structures.String("B", uid=2)
    c = structures.String("C", uid=4)
    inner1 = structures.TreeNode(c, uid=5)
    inner2 = structures.TreeNode(b, uid=6)
    inner3 = structures.TreeNode(a, [inner2, inner1], uid=7)
    d = structures.String("D", uid=8)
    e = structures.String("E", uid=9)
    t1 = structures.TreeNode(d, uid=10)
    t2 = structures.TreeNode(e, uid=11)
    t3 = structures.TreeNode(inner3, [t1,t2], uid=12)
    pic = TreePicture(t3)
    pic.draw()
    pic.save(os.path.join(test_dir, outfile))

def test_pointer_tree(test_dir, outfile):
    """Tests drawing of trees with pointers to other trees"""
    a = structures.String("A", uid=1)
    b = structures.String("B", uid=2)
    c = structures.String("C", uid=4)
    inner1 = structures.TreeNode(c, uid=5)
    inner2 = structures.TreeNode(b, uid=6)
    inner3 = structures.TreeNode(a, [inner2, inner1], uid=7)
    pointer = structures.Pointer(inner3)
    d = structures.String("D", uid=8)
    e = structures.String("E", uid=9)
    t1 = structures.TreeNode(d, uid=10)
    t2 = structures.TreeNode(e, uid=11)
    pointer2 = structures.Pointer(t2)
    t3 = structures.TreeNode(pointer2, uid=13)
    t4 = structures.TreeNode(pointer, [t1,t3], uid=12)
    pic = TreePicture(t4)
    pic.draw()
    pic.save(os.path.join(test_dir, outfile))

def test_null_children_tree(test_dir, outfile):
    """Tests drawing of trees wuith null valued children"""
    a = structures.String("a", uid=1)
    b = structures.String("b", uid=2)
    c = structures.String("c", uid=3)
    t1 = structures.TreeNode(b, [None], uid=4)
    t2 = structures.TreeNode(c, [None, None], uid=5)
    t3 = structures.TreeNode(a, [t1, None, t2], uid=6)
    pic = TreePicture(t3)
    pic.draw()
    pic.save(os.path.join(test_dir, outfile))

def test_main(test_dir, outfile):
    """Tests generating svg by calling main file"""
    s = structures.String("Testing main file...", uid=1)
    svg = make_svg(s, None, {})
    with open(os.path.join(test_dir, outfile), 'w') as f:
        f.write(svg)

if __name__ == "__main__":
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
    test_single_char(test_dir, "01_char.svg")
    test_long_string(test_dir, "02_string.svg")
    test_single_tree_node(test_dir, "03_node.svg")
    test_single_node_long_string(test_dir, "04_long_node.svg")
    test_simple_tree(test_dir, "05_simple_tree.svg")
    test_long_string_tree(test_dir, "06_complex_string_tree.svg")
    test_nested_tree(test_dir, "07_nested_tree.svg")
    test_pointer_tree(test_dir, "08_pointer_tree.svg")
    test_null_children_tree(test_dir, "09_null_child_tree.svg")
    test_main(test_dir, "10_test_main.svg")
