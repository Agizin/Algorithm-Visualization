import abc
import svgutils.transform as svgutils
import os

from .elements import *
from .picture import Anchor, Picture
from .leaf_picture import StringLeaf
from .svg_engine import SVGEngine


class InternalPicture(Picture, metaclass = abc.ABCMeta):        
    pass
        
class ConnectionMap:
    class Connection:
        def __init__(self, start_point, connect_pic, anchor):
            self.start_point = start_point
            self.connect_pic = connect_pic
            if !connect_pic.is_drawn:
                connect_pic.draw()
            self.anchor = anchor
            self.left_shift_y = 0
            self.right_shift_y = 0

        def is_pointer(self):
            return False

    class PointerConnection(Connection):
        def __init__(self, start_point, connect_pic, anchor, pointer_style={}):
            self.pointer_style = pointer_style
            super().__init__(self, start_point, connect_pic, anchor)

        def is_pointer(self):
            return True
    
    def __init__(self, startPicture):
        self.connections = {}
        assert(isInstance(startPicture, InternalPicture))
        self.picture = startPicture
        
    def add_connection(self, point, connect_pic, anchor=None, pointer=True, pointer_style={}):
        if self.picture.width < point[0] or self.picture.height < point[1]:
            raise TypeError("Point not included in picture")
        if pointer:
            self.connections.append(PointerConnection(point, connect_pic, anchor, pointer_style))
        else:
            self.connections.append(Connection(point, connect_pic, anchor))

    def draw_connections(self):
        #TODO: reimplement with GraphViz?
        cur_pic_width = self.picture.width
        cur_pic_height = self.picture.height
        left_width = 0
        right_width = 0
        left_height = 0
        right_height = 0
        for connection in self.connections:
            if !connection.is_pointer():
                #in place connections dont change size of picture
                continue
            connect_size = connection.connect_pic.size
            if connection.anchor == Anchor.LEFT:
                #left anchor = picture should be placed to right of main picture
                right_width = max(connect_size[0], right_width)
                right_height += connect_size[1]
            elif connection.anchor == Anchor.RIGHT:
                #right anchor = picture placed on left of main picture
                left_width = max(connection_size[1], left_width)
                left_height += connect_size[1]
            else:
                #Otherwise, picture connected on whatever side its pointer is closes to
                #There are better ways to do this, but I wont improve unless graphviz doesn't pan out
                if connection.start_point[0] <= self.picture_size[0]/2:
                    left_width = max(connection_size[1], left_width)
                    left_height += connect_size[1]
                else:
                    right_width = max(connect_size[0], right_width)
                    right_height += connect_size[1]
        new_width = left_width + cur_pic_width + right_width
        new_height = max(left_height, cur_pic_height, right_height)
        main_svg = svgutils.fromfile(self.picture.filename)
        main_root = main_svg.getroot()
        main_root.moveto(left_width, 0)
        subpics = [main_root]
        pointers = []
        for connection in self.connections:
            subpic = connection.connect_pic
            anchor = connection.anchor
            anchorPos = connection.connect_pic.getAnchorPosition(anchor)
            if !connection.is_pointer():
                shift_x = left_width + connection.start_point[0] - anchorPos[0]
                shift_y = connection.start_point[1] -anchorPos[0]
            else:
                if anchor == Anchor.LEFT or anchor == Anchor.TOPLEFT:
                    pic_side = "right"
                elif anchor == Anchor.RIGHT or connection.start_point <= self.picture_size[0]/2:
                    pic_side = "left"
                else:
                    pic_side = "right"
                if pic_side == "left":
                    shift_x = 0
                    shift_y = self.left_shift_y
                    self.left_shift_y += subpic.height
                else:
                    shift_x = left_width + self.picture.width
                    shift_y = self.right_shift_y
                    self.right_shift_y += subpic.height
                newStartPoint = (connection.startPoint[0]+left_width, connection.startPoint[1])
                endPoint = (anchorPos[0]+shift_x, anchorPos[1]+shift_y)
                pointers.append(PointerElement(newStartPoint, endPoint, **self.pointer_style))
            subpic_svg = svgutils.fromfile(subpicture.filename)
            subpic_root = subpic_svg.getroot()
            subpic_root.moveto(shift_x, shift_y)
            subpics.append(subpic_root)
            if subpic.filename[:4].lower() == "temp":
                os.remove(subpicture.filename)
        new_svg = svgutils.SVGFigure("{!s}px".format(new_width), "{!s}px".format(new_height))
        new_svg.append(subpics)
        pointers_temp_file = "temp_pointers.svg"
        pointers_svg_engine = SVGEngine(pointers_temp_file, (new_width, new_height))
        for pointer in pointers:
            pointer.draw(pointers_svg_engine)
        pointers_svg_engine.save()
        pointers_svg = svgutils.fromfile(pointers_temp_file)
        pointers_root = pointers_svg.getroot()
        new_svg.append(pointers_root)
        os.remove(pointers_temp_file)
        new_svg.save(self.filename)
        self.picture.width = new_width
        self.picture.height = new_height
    
            
class TreePicture(InternalPicture): #should be in its own file but not for now b/c convenient

    class TreeNode(NodeElement):
        def __init__(self, center, data, width, height, shape=Shape.Circle, style={}, **kwargs):
            self.data = data
            self.childNodes = []
            self.edges = []
            self.edge_class = kwargs.pop('edge_class', EdgeElement)
            if !issubclass(self.edge_class, EdgeElement):
                raise TypeError("Expected {} is not an edge subclass".format(edge_class))
            self.edge_style = kwargs.pop("edge_style", {})
            self.scale_to_data = kwargs.pop("scale_to_data", True)
            if self.scale_to_data:
                data_picture = Picture.make_picture(node_data, style=self.style)
                if not isinstance(datapicture, structures.Pointer):
                    if !data_picture.is_drawn:
                        data_picture.draw()
                    margin = kwargs.get("margin", 10)
                    width = data_picture.width + margin
                    height = data_picture.height + margin
            super().__init__(center, width, height, shape, style, **kwargs)

        def is_leaf(self):
            return len(self.childNodes) == 0

        def add_child(self, child):
            if isinstance(child, TreeNode):
                self.childNodes.append(node)
            else:
                raise TypeError("{} is not a tree node".format(child))

        def add_childen(self, children):
            for child in children:
                self.add_child(child)

        def _make_edge(self, child):
            assert(child in children)
            source = self.center
            destination = (child.center[0], child.center[1]-child.height/2)
            newEdge = (self.edge_class)(source, destination, self.edge_style)
            return newEdge
            
        def draw(self, svg_engine):
            for child in self.childNodes:
                edge = self._make_edge(child)
                edge.draw(svg_engine)
                child.draw(svg_engine)
            super().draw(svg_engine)
    
    def __init__(self, tree_root, filename=None, style={}, **kwargs):
        self.root = tree_root
        self.style=style
        self.node_shape = kwargs.pop("node_shape", Shape.CIRCLE)
        self.node_width = kwargs.pop("node_width", 50)
        self.node_height = kwargs.pop("node_height", 50)
        self.edge_length = kwargs.pop("edge_length", 200)
        self.node_sep = kwargs.pop("node_sep", 10)
        self.pointer_style = kwargs.pop("pointer_Style", {})
        #TODO: better way to assign default values?

        self.width = self._width_estimate(self.root)
        self.height = self._height_estimate(self.root)
        InternalPicture.__init__(self, tree_root, filename, size)

    def _width_estimate(self, root):
        if root.is_leaf():
            return 2*self.node_radius+self.node_sep
        width = 0
        for child in root.children:
            child_width = self._pixel_width(child)
            width += child_width
        return width

    def _height_estimate(self, root):
        #TODO: improve height heuristic for tall trees.
        tree_height = root.tree_height()
        return tree_height*(2*self.node_radius + self.edge_length) - self.edge_length + self.node_sep

    def _layout_nodes(self, parent, level_roots, svg_engine):
        sub_widths = []
        for subtree in level_roots:
            sub_width = self.width_dict.get(subtree, self._pixel_width(subtree))
            if subtree in self.width_dict:
                sub_widths.append(self.width_dict[subtree])
            else:
                sub_width = self._pixel_width(subtree)
                self.width_dict[subtree] = sub_width
                sub_widths.append(sub_width)
        level_length = sum(sub_widths)
        y = parent.center[1] +self.edge_length
        far_x_bound = parent.center[0] - level_length/2
        for i in range(0, len(level_roots)):
            subtree = level_roots[i]
            sub_width = sub_widths[i]
            x = far_x_bound + sub_width/2
            far_x_bound += sub_width
            if subtree is not None:
                new_node = TreePicture.TreeNode((x,y), subtree.data,
                                                self.node_width, self.node_height,
                                                self.node_shape, style)
                parent.add_child(new_node)
                if not subtree.is_leaf():
                    self._layout_nodes(new_node, subtree.children)

    def _draw_data(self, root_node):
        """Draws/Connects Tree subpictures to the current picture"""
        node_queue = [root_node]
        connections = ConnectionMap(self)
        while len(node_queue) > 0:
            node = node_queue.pop(0)
            node_data = node.data #subpicture
            
            if (isinstance(node_data, StringLeaf) and node_data.size[0] < 2*node.radius
                and node_data.size[1] < node.radius):
                connections.add_connection(node.center, data_picture, anchor=Anchor.CENTER,
                                           pointer=False)
            else:
                node_center_x = node.center[0]
                picture_center_x = node_data.size[0]/2
                if node_center_x <= picture_center_x: #Node is on left side of picture
                    anchor = Anchor.RIGHT
                else:
                    anchor = Anchor.LEFT
                connections.add_connection(node.center, data_picture, anchor=anchor,
                                           pointer=True, pointer_style=self.pointer_style)
            for child in node.children:
                node_queue.append(child)
        connection_map.draw_connections()
                  

    def draw(self):
        if self.is_drawn and os.path.isfile(self.filename):
            return
        self.width_dict = {}
        root_x = self.size[0]/2
        root_y = self.node_radius + self.node_sep/2
        root_center = (root_x, root_y)
        root_node = TreePicture.TreeNode(root_center, self.root.data,
                                         self.node_width, self.node_height,
                                         self.node_shape, self.style)
        svg_engine = SVGEngine(self.filename, (self.width, self.height))
        self._layout_nodes(root_node, self.root.children)
        self.root.draw(svg_engine)
        svg_engine.save()
        self._draw_data(root_node)
        self.is_drawn = True
