import svgwrite

"""
Creates SVG file visualizing given tree

TODO: add values to tree nodes
"""

class Tree():
    def __init__(self, value, children = None):
        self.value = value
        self.children = children

    def __str__(self):
        return str(self.value)

    def add_child(t):
        self.children.append(t);

class TreeVisualizer():
    
    def __init__(self, svg_doc):
        self.svg_doc = svg_doc
        self.nodes = []
        self.width_dict = {}

    def __str__(self):
        return self.svg_doc.tostring()

    def save(self):
        self.svg_doc.save()

    def _width(self, root, radius, node_sep):
        if root in self.width_dict:
            return self.width_dict[root]
        if root.children is None:
            width = 2*radius + 2*node_sep
        else:
            width = 0
            for c in root.children:
               width += self._width(c, radius, node_sep)
        self.width_dict[root] = width
        return width

    def _draw(self, parent_center, level_nodes, **kwargs):
        radius = kwargs.get('radius', 50)
        edge_length = kwargs.get('edge_length', 200)
        node_sep = kwargs.get('node_sep', 10)

        if level_nodes != None:
            sub_widths = []
            for subtree in level_nodes:
                try:
                    sub_width = self.width_dict[subtree]
                except KeyError:
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
                self._draw((x,y), subtree.children, **kwargs)
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
                                          fill='white')
        self.svg_doc.add(parent_node)
            
            
    def draw(self, root, center, **kwargs):
        self._draw(center, root.children, **kwargs)

svg_document = svgwrite.Drawing(filename ='tree.svg',
                                size = ('600px','800px'))

tree = Tree('A',[Tree('DE',[Tree('GHI')]),Tree('JKL'),Tree('MNOP',[Tree('PQRST'),Tree('STUV')])])

tree_vis = TreeVisualizer(svg_document) 

tree_vis.draw(tree, (300, 100))

print(tree_vis)

tree_vis.save()

svg_doc2 = svgwrite.Drawing(filename='binary_tree.svg',
                            size = ('600px', '800px'))


tree2 = Tree('1', [Tree('2',[Tree('3'),Tree('4')]), Tree('5', [Tree('6'), Tree('7')])])

tree_vis2 = TreeVisualizer(svg_doc2)

tree_vis2.draw(tree2, (300,100))

print()
print(tree_vis2)

tree_vis2.save()
