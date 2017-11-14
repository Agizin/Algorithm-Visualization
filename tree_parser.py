from tree_svg import *
import svgwrite
import random
import re

# [name_of_block|arg0|...|argn|contents]


LEFT_BRANCH = r"-+[lL][not whitespace]>"
BRANCH_TEMPLATE = r"-+({}[a-zA-Z]+)-*>"
LEFT_BRANCH = BRANCH_TEMPLATE.format("[lL]")
RIGHT_BRANCH = BRANCH_TEMPLATE.format("[rR]")

NAME_TOKEN = "[a-zA-Z_][a-zA-Z_0-9]*"

class BinTreeSyntaxElement:
    pass

class BinTreeNodeRelation(BinTreeSyntaxElement):

    def __init__(self, parent_name, child_name, is_left):
        self.is_left = is_left
        self.parent_name = parent_name
        self.child_name = child_name

class BinTreeNodeSpec(BinTreeSyntaxElement):
    """a declaration of a node"""
    def __init__(self, name, data, is_root=False):
        self.name = name
        self.data = data
        self.is_root = is_root

class InvalidTreeSpec(Exception):
    pass

def tree_from_relations(*relations):
    # nodes = set()
    nodes = {}
    root = None
    for rel in relations:
        if isinstance(rel, BinTreeNodeSpec):
            # nodes.add(Tree(rel.data, name=rel.name))
            nodes[rel.name] = Tree(rel.data, name=rel.name)
            if rel.is_root:
                if root is not None:
                    raise InvalidTreeSpec("Multiple roots specified: {} and {}"
                                          .format(root.name, rel.name))
                else:
                    root = nodes[rel.name]
    if root is None:
        raise InvalidTreeSpec("No root specified for tree {}".format(nodes))
    for rel in relations:
        if isinstance(rel, BinTreeNodeRelation) and rel.is_left:
            nodes[rel.parent_name].add_child(nodes[rel.child_name])
    for rel in relations:
        if isinstance(rel, BinTreeNodeRelation) and not rel.is_left:
            nodes[rel.parent_name].add_child(nodes[rel.child_name])

    return root


if __name__ ==  "__main__":
    my_nodes = [BinTreeNodeSpec(x, data=d) for (x, d) in [
        ("a", 5), ("b", 8), ("c", -2), ("d", 100)
    ]]
    my_nodes.append(BinTreeNodeSpec("e", data=1000, is_root=True))
    left = True
    right = False
    my_relations = [BinTreeNodeRelation(x, y, is_left=d) for (x, y, d) in [
        ("e", "a", left),
        ("a", "b", right),
        ("a", "c", left),
        ("e", "d", right),
    ]]
    all_things = [*my_nodes, *my_relations]
    random.shuffle(all_things)
    T = tree_from_relations(*all_things)
    # refactor this
    svg_document = svgwrite.Drawing(filename='wacky_tree.svg',
                                    size=('600px','800px'))
    tree_vis = TreeVisualizer(svg_document)
    tree_vis.draw(T, (300, 100))
    tree_vis.save()
