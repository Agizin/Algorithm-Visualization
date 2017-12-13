from tree_svg import *

class BinaryTree(Tree):
    def __init__(self, value, left = None, right = None, name = None):
        self.is_binary = True
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
        return [self.left, self.right]

class BinaryTreeVisualizer(TreeVisualizer):
    def __init__(self, svg_doc):
        TreeVisualizer.__init__(self, svg_doc)
        self.distance_from_root_dict = {}
        self.root_depth = None

    def _depth(self, subtree_root, distance_from_root = 0):
        if subtree_root is not None:
            self.distance_from_root_dict[subtree_root] = distance_from_root
        if subtree_root is None:
            depth = 0
        elif subtree_root.is_leaf():
           depth = 0
        else:
            depth = 1 + max(self._depth(subtree_root.left, distance_from_root+1),
                            self._depth(subtree_root.right, distance_from_root+1))
        return depth
    
    def _width(self, root, radius, node_sep):
        """Overwrites base Tree Visualizer width method.

        For aesthetic reasons, the width of every subtree from a given depth are equal."""

        if root is None:
            return 0
        leaf_width = 2*radius + 2*node_sep
        return leaf_width * 2**(self.root_depth - self.distance_from_root_dict[root])

    def _draw(self, parent_center, level_nodes, value=None, **kwargs):
        radius = kwargs.get('radius', 50)
        edge_length = kwargs.get('edge_length', 200)
        node_sep = kwargs.get('node_sep', 10)
	
        if any(level_nodes): #checks that node is not a leaf
            left = level_nodes[0]
            right = level_nodes[1]
            sub_width = max(self._width(left, radius, node_sep),
                                 self._width(right, radius, node_sep))
            y=parent_center[1]+edge_length
            for subtree in [left,right]:
                if subtree is left:
                    x = parent_center[0] - sub_width/2
                else:
                    x = parent_center[0] + sub_width/2
                if subtree is not None:
                    self._draw((x,y), subtree.get_children(), value=subtree.value, **kwargs)
                    top = (x, y-radius)
                    edge = self.svg_doc.line(start = parent_center,
                                             end = top,
                                             stroke_width='3',
                                             stroke='black')
                    self.svg_doc.add(edge)
                
        parent_node = self.svg_doc.circle(center = parent_center,
                                          r = radius,
                                          stroke_width='3',
                                          stroke='black',
                                          fill="white",
                                          fill_opacity="1",  # 0 for debugging
        )
        self.svg_doc.add(parent_node)
            
        if value:
            #prints value in node, imperfect
            text_str = str(value)
            if len(text_str) <= 2:
                text_size = '40px'
                text_insert_x = parent_center[0] - 12*len(text_str)
            elif len(text_str) <= 10:
                text_size = str(40 - 3*(len(text_str))) + 'px'
                text_insert_x = parent_center[0] - 9*len(text_str)
            else:
                text_size = '10'
            text_insert_y = parent_center[1] + 10
            
            text = self.svg_doc.text(text_str,
                                     insert = parent_center,
                                     font_size=text_size,
                                     text_anchor="middle",
                                     dominant_baseline="central")
            self.svg_doc.add(text)

    def draw(self, root, center, **kwargs):
        self.root_depth = self._depth(root)
        self._draw(center, root.get_children(), value=root.value, **kwargs)
        self.root_depth = None
        self.distance_from_root_dict = {}

def main():
    svg_doc = svgwrite.Drawing(filename='binary_tree2.svg',
                                size = ('600px', '800px'))

    tree = BinaryTree('0', BinaryTree('1',BinaryTree('3'),BinaryTree('4')), BinaryTree('2',None,BinaryTree('6')))

    tree_vis = BinaryTreeVisualizer(svg_doc)

    tree_vis.draw(tree, (300,100))

    print()
    print(tree_vis)

    tree_vis.save()

if __name__ == "__main__":
    main()
