import abc
import svgutils.transform as svgutils
import os

from .picture import Picture
from .leaf_picture import StringLeaf
from .svg_engine import SVGEngine

# structure_map = {structures.String : StringLeaf, structures.TreeNode : internal_picture.TreePicture} #better way to implement?
# def make_picture(structure, *args, **kwargs):
#     return structure_map[type(structure)](structure, *args, **kwargs)


class InternalPicture(Picture, metaclass = abc.ABCMeta):
    class Node(metaclass = abc.ABCMeta):
        def __init__(self, center):
            self.center = center

        @abc.abstractmethod
        def draw(self, svg_engine):
            pass

    class CircleNode(Node):
        def __init__(self, center, radius = 50, **kwargs):
            self.radius = radius
            self.properties = kwargs
            InternalPicture.Node.__init__(self, center)

        def draw(self, svg_engine):
            svg_engine.draw_circle(self.center, self.radius, **self.properties)

    def combine_svg(self, connection_dict):
        """Current picture is connected to its subpictures.
        This method must be passed a dictionary that maps connection points in the
        current picture to a 2-tuple of subpicture and the
        position/orientation of its connection (e.g. a Left position will connect the
        current picture to the left side of the subpicture). If the position is None,
        then the subpicture will overlap the current picture at the connection point."""
        #TODO: expand to allow top, bottom, positions (at least).
        #TODO: add kwarg to scale down subpictures
        assert self.size is not None
        current_size = self.size
        left_width = 0
        right_width = 0
        left_height = 0
        right_height = 0
        for main_point, connection in connection_dict.items():
            subpicture = connection[0]
            cxn_position = connection[1]
            if cxn_position == "Left":
                #left connection point = placement on right of current picture
                right_width = max(subpicture.size[0], right_width)
                right_height += subpicture.size[1]
            elif cxn_position == "Right":
                #placement on left of current picture
                left_width += max(subpicture.size[0], left_width)
                left_height += subpicture.size[1]
        new_size_x = left_width+self.size[0]+right_width
        new_size_y = max(left_height, self.size[1], right_width)
        new_svg = svgutils.SVGFigure("{!s}px".format(new_size_x), "{!s}px".format(new_size_y))
        main_svg = svgutils.fromfile(self.filename)
        main_root = main_svg.getroot()
        main_root.moveto(left_width, 0)
        subpics = [main_root]
        #svg_engine = SVGEngine(self.filename, self.size)
        left_cur_shift_y = 0
        right_cur_shift_y = 0
        for main_point, connection in connection_dict.items():
            subpicture = connection[0]
            cxn_position = connection[1]
            cxn_point = subpicture.get_connection_point(cxn_position)
            #TODO: move svgutils interactions to SVGEngine?
            subpic_svg = svgutils.fromfile(subpicture.filename)
            subpic_root = subpic_svg.getroot()
            if cxn_position is None:
                #no connection point, image centered at main point
                shift_x = main_point[0] - subpicture.size[0]/2
                shift_y = main_point[1] - subpicture.size[1]/2
            elif cxn_position == "Left":
                shift_x = left_width + self.size[0]
                shift_y = left_cur_shift_y
                left_cur_shift_y += subpicture.size[1]
            else: #right connection
                shift_x = 0
                shift_y = right_cur_shift_y
                right_cur_shift_y += subpicture.size[1]
            subpic_root.moveto(shift_x, shift_y, scale=0.95)
            #if cxn_point is not None:
            #    cxn_point = (cxn_point[0]+shift_x, cxn_point[1]+shift_y)
            #    svg_engine.draw_arrow(main_point, cxn_point)
            subpics.append(subpic_root)
            if subpicture.filename[:4].lower() == "temp":
                os.remove(subpicture.filename)
        #svg_engine.save()
        new_svg.append(subpics)
        new_svg.save(self.filename)
            
            
class TreePicture(InternalPicture): #should be in its own file but not for now b/c convenient

    class TreeNode(InternalPicture.CircleNode):
        def __init__(self, center, data, children = None, **kwargs):
            self.children = [] if children is None else children
            kwargs["fill_opacity"] = kwargs.get("fill_opacity", 1)
            radius = kwargs.pop("radius", None)
            self.properties = kwargs
            if isinstance(data, Picture):
                self.data = data
            else:
                self.data = Picture.make_picture(data, **kwargs)
            InternalPicture.CircleNode.__init__(self, center, radius, **kwargs)

        def is_leaf(self):
            return len(self.children) == 0

        def add_child(self, node):
            if self.is_leaf():
                self.children = [node]
            else:
                self.children.append(node)
    
    def __init__(self, tree_root, filename=None, size=None, **kwargs):
        self.root = tree_root
        self.root_node = None
        self.node_radius = kwargs.pop("node_radius", 50)
        self.edge_length = kwargs.pop("edge_length", 200)
        self.node_sep = kwargs.pop("node_sep", 10)
        self.properties = kwargs
        InternalPicture.__init__(self, tree_root, filename, size)

    def _pixel_width(self, root):
        if root.is_leaf():
            return 2*self.node_radius+2*self.node_sep
        width = 0
        for child in root.children:
            child_width = self._pixel_width(child)
            width += child_width
        return width

    def _pixel_height(self, root):
        #TODO: improve height heuristic for tall trees.
        tree_height = root.tree_height()
        return tree_height*(2*self.node_radius + self.edge_length) - self.edge_length + self.node_sep

    def _build_nodes(self, parent, level_roots):
        sub_widths = []
        for subtree in level_roots:
            sub_width = self.width_dict.get(subtree, self._pixel_width(subtree))
            if subtree in self.width_dict:
                sub_widths.appen(self.width_dict[subtree])
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
                new_node = TreePicture.TreeNode((x,y), subtree.data, radius=self.node_radius, **self.properties)
                parent.add_child(new_node)
                if not subtree.is_leaf():
                    self._build_nodes(new_node, subtree.children)

    def lay_out(self):
        if self.filename is None:
            self.filename = self._tempname()
        if self.size is None:
            self.size = (self._pixel_width(self.root), self._pixel_height(self.root))
        self.width_dict = {}
        root_x = self.size[0]/2
        root_y = self.node_radius + self.node_sep/2
        root_center = (root_x, root_y)
        root_node = TreePicture.TreeNode(root_center, self.root.data,
                                        radius=self.node_radius,**self.properties)
        self._build_nodes(root_node, self.root.children)
        self.root_node = root_node

    def _draw_nodes(self, parent, svg_engine):
        if parent.is_leaf():
            parent.draw(svg_engine)
        else:
            for child_node in parent.children:
                edge = svg_engine.draw_line(parent.center, child_node.center, **self.properties)
                #TODO: create an edge class
                self._draw_nodes(child_node, svg_engine)
            parent.draw(svg_engine)

    def _draw_data(self):
        """Draws/Connects Tree subpictures to the current picture"""
        node_queue = [self.root_node]
        connection_dict = {} #connection point on tree mapped to 2-tuple of subpicture and connection position, i.e. left, right, etc
        while len(node_queue) > 0:
            node = node_queue.pop(0)
            node_data = node.data #subpicture
            node_data.draw()
            if (isinstance(node_data, StringLeaf) and node_data.size[0] < node.radius
                and node_data.size[1] < node.radius):
                #Strings of small size are placed within the node
                node_data.draw()
                upper_left_x = node.center[0] - node_data.size[0]/2
                upper_left_y = node.center[1] - node_data.size[1]/2
                connection_dict[(upper_left_x,upper_left_y)] = (node_data, None)
            else:
                node_center_x = node.center[0]
                picure_center_x = node_data.size[0]/2
                if node_center_x <= picture_center_x: #Node is on left side of picture
                    position = "Right" #Right side of data will be connected to left of picture
                else:
                    position = "Left"
                connection_dict[node.center] = (node_data, position)
            for child in node.children:
                node_queue.append(child)
        self.combine_svg(connection_dict)
                  

    def draw(self):
        if self.root_node is None:
            self.lay_out()
        svg_engine = SVGEngine(self.filename, self.size)
        self._draw_nodes(self.root_node, svg_engine)
        svg_engine.save()
        self._draw_data()
