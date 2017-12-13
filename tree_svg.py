import svgwrite
from visualizer import *

"""
Creates SVG file visualizing given tree

TODO: add better values to tree nodes
"""

class Tree():
    def __init__(self, value, children = None, name=None):
        self.is_binary = False
        self.value = value
        self.children = [] if children is None else children
        self.name = name

    def __str__(self):
        return str(self.value)

    def is_leaf(self):
        return not bool(self.children)

    def add_child(self, t):
        self.children.append(t);

    def get_children(self):
        return self.children

class TreeVisualizer(Visualizer):
    
    def __init__(self, svg_doc):
        Visualizer.__init__(self, svg_doc)
        self.width_dict = {}

    def _width(self, root, radius, node_sep):
        if root in self.width_dict:
            return self.width_dict[root]
        if root.is_leaf():
            width = 2*radius + 2*node_sep
        else:
            width = 0
            for c in root.get_children():
               width += self._width(c, radius, node_sep)
            assert width > 0
        self.width_dict[root] = width
        return width

    def _draw(self, parent_center, level_nodes, value=None, **kwargs):
        radius = kwargs.get('radius', 50)
        edge_length = kwargs.get('edge_length', 200)
        node_sep = kwargs.get('node_sep', 10)

        if level_nodes != None:
            sub_widths = []
            for subtree in level_nodes:
                sub_width = self._width(subtree, radius, node_sep)
                sub_widths.append(sub_width)
            level_length = sum(sub_widths)
            y = parent_center[1]+edge_length
            far_x_bound = parent_center[0] - level_length/2
            for i in range(0,len(level_nodes)):
                subtree = level_nodes[i]
                sub_width = sub_widths[i]
                x = far_x_bound + sub_width/2
                far_x_bound = far_x_bound + sub_width
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

            text_size = 25
            
            text = self.svg_doc.text(text_str,
                                     insert = parent_center,
                                     font_size=text_size,
                                     text_anchor="middle",
                                     dominant_baseline="central")
            self.svg_doc.add(text)

    def draw(self, root, center, **kwargs):
        self._draw(center, root.get_children(), value=root.value, **kwargs)
        self.width_dict = {}

def main():

    svg_document = svgwrite.Drawing(filename ='tree_1.svg',
                                    size = ('600px','800px'))

    tree = Tree('A',[Tree('DE',[Tree('GHI')]),Tree('JKL'),Tree('MNOP',[Tree('PQRST'),Tree('STUV')])])

    tree_vis = TreeVisualizer(svg_document) 

    tree_vis.draw(tree, (300, 100))

    print(tree_vis)

    tree_vis.save()

    svg_doc2 = svgwrite.Drawing(filename='tree_2.svg',
                                size = ('600px', '800px'))


    tree2 = Tree('1', [Tree('2',[Tree('3'),Tree('4')]), Tree('5', [Tree('6'), Tree('7')])])

    tree_vis2 = TreeVisualizer(svg_doc2)

    tree_vis2.draw(tree2, (300,100))

    print()
    print(tree_vis2)

    tree_vis2.save()


if __name__ == "__main__":
    main()
