from tree_svg import *

class BinaryTree(Tree):
    def __init__(self, value, left = None, right = None, name = None):
        self.value = value
        self.left = left
        self.right = right
        self.name = name

    def is_leaf(self):
        return self.left is None and self.right is None

    def add_left(self, t):
        if self.left is None:
            self.left = t

    def add_right(self, t):
        #TODO: add some exceptions if child can't be added
        if self.right is None:
            self.right = t

    def add_child(self, t):
        if self.left is None:
            self.add_left(t)
        elif self.right is None:
            self.add_right(t)

    def get_left(self):
        return self.left

    def get_right(self):
        return self.right
    
    def get_children(self):
        return [child for child in [self.left,self.right] if child is not None]

class BinaryTreeVisualizer(TreeVisualizer):
    def __init__(self, svg_doc):
        TreeVisualizer.__init__(self, svg_doc)
        self.distance_from_root_dict = {}
        self.root_depth = None

    def _depth(self, subtree_root, distance_from_root = 0):
        self.distance_from_root_dict[subtree_root] = distance_from_root
        if subtree_root.is_leaf():
            depth = 0
        else:
            depth = 1 + max(self._depth(subtree_root.left, distance_from_root+1),
                            self._depth(subtree_root.right, distance_from_root+1))
        return depth
    
    def _width(self, root, radius, node_sep):
        """Overwrites base Tree Visualizer width method.

        For aesthetic reasons, the width of every subtree from a given depth are equal."""

        leaf_width = 2*radius + 2*node_sep
        return leaf_width * 2**(self.root_depth - self.distance_from_root_dict[root])

    def draw(self, root, center, **kwargs):
        self.root_depth = self._depth(root)
        self._draw(center, root.get_children(), value=root.value, **kwargs)
        self.root_depth = None
        self.distance_from_root_dict = {}

def main():
    svg_doc = svgwrite.Drawing(filename='wacky_tree_legit.svg',
                                size = ('600px', '800px'))

    tree = BinaryTree('1000', BinaryTree('5',BinaryTree('-2'),BinaryTree('8')), BinaryTree('100'))

    tree_vis = BinaryTreeVisualizer(svg_doc)

    tree_vis.draw(tree, (300,100))

    print()
    print(tree_vis)

    tree_vis.save()

if __name__ == "__main__":
    main()
