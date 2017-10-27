import svgwrite

"""
Creates SVG file visualizing given tree

Note that if there are too many nodes on a layer, they currently will overlap
"""

class Tree():
    def __init__(self, value, children = []):
        self.value = value
        self.children = children

    def add_child(t):
        self.children.append(t);

def draw_tree(svg_doc, root, center): 
    if root.children != []:
        x = center[0]
        y = center[1]
        num_children = len(root.children)
        child_centers = []
        if num_children % 2 == 1:
            mid = int(num_children/2)
            for i in range(0, num_children):
                child = root.children[i]
                child_y = y + 200
                if i <= mid:
                    child_x = x - (mid-i)*110
                else:
                    child_x = x + (i-mid)*110
                child_centers.append((child_x, child_y))
        else:
            half = int(num_children/2)-1
            for i in range(0, num_children):
                child = root.children[i]
                child_y = y + 200
                if i <= half:
                    child_x = x - ((half-i)*110+55)
                else:
                    child_x = x + ((i-half-1)*110+55)
                child_centers.append((child_x, child_y))
        for i in range(0,num_children):
            child = root.children[i]
            child_center = child_centers[i]
            child_top = (child_center[0], child_center[1] - 50)
            child_edge = svg_doc.line(start = center,
                                      end = child_top,
                                      stroke_width = '3',
                                      stroke='black')
            svg_doc.add(child_edge)
            draw_tree(svg_doc, child, child_center)
            
    node = svg_doc.circle(center = center,
                          r = 50,
                          stroke_width = '3',
                          stroke ='black',
                          fill='white')
    svg_doc.add(node)

    if root.value:
        text_str = str(root.value)
        #text_insert_x = center[0]-10*(len(text_str)-1)
        if len(text_str) <= 2:
            text_size = '40px'
            text_insert_x = center[0] - 12*len(text_str)
        elif len(text_str) <= 10:
            text_size = str(40 - 3*(len(text_str))) + 'px'
            text_insert_x = center[0] - 9*len(text_str)
        else:
            text_size = '10'
        text_insert_y = center[1] + 10
            
        text = svg_doc.text(text_str,
                            insert = (text_insert_x, text_insert_y),
                            font_size=text_size)
        svg_doc.add(text)

svg_document = svgwrite.Drawing(filename ='tree.svg',
                                size = ('600px','800px'))

tree = Tree('A',[Tree('DE',[Tree('GHI')]),Tree('JKL'),Tree('MNOP',[Tree('PQRST'),Tree('STUV')])])

draw_tree(svg_document, tree, (300, 100))

print(svg_document.tostring())

svg_document.save()
