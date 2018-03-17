import abc
import os.path
from time import time
import svgutils.transform as svgutils

from algviz.parser import structures
from .elements import *
from .anchor import Anchor
from .connection_map import ConnectionMap
from .svg_engine import DEFAULTS, SVGEngine

class DataStructureException(TypeError):
    """indicates that an instance of structures.DataStructure was expected"""
    pass

class Picture(metaclass=abc.ABCMeta):
    structure_type = None #Indicates structure from parser/structures that this picture subclass draws. Every subclass must replace this with subclass of structures.DataStructure

    @staticmethod
    def make_picture(structure, *args, **kwargs):
        #Selects a picture class for the given structure. I'm open to any cleaner ways to implement this. I like this better than a dict though.
        #TODO: add rules for slecting between picture classes that have same structure type.
        if not isinstance(structure, structures.DataStructure):
            raise DataStructureException("Expectedn structure to be instance of DataStructure, got {}"
                                         .format(type(structure)))
        for pic_class in Picture.__subclasses__():
            if pic_class.structure_type == type(structure):
                return pic_class(structure, *args, **kwargs)

    def __init__(self, structure, filename=None, size=None, **kwargs):
        self.structure = structure #data structure that this picture represents
        self.size = size #a requirement on max bounding box size, if None then no requirement
        self.is_drawn = False
        
        if filename is None: #name of svg file
            filename = self._tempname()
        self.filename = filename
        
    def _tempname(self):
        time_str = str(time()).replace('.','')
        try:
            uid = self.structure.uid
        except AttributeError:
            raise DataStructureException("Expected Data Structure, got {}".format(type(self.structure)))
        return "temp_{}_{}.svg".format(uid, time_str)

    def scale(self, new_size):
        if not os.path.isfile(self.filename):
            raise IOError("Picture {} must be drawn before it can be scaled".format(self.filename))
        old_svg = svgutils.fromfile(self.filename)
        old_pic = old_svg.getroot()
        if abs(new_size[0]-self.size[0]) <= abs(new_size[1]-self.size[1]):
            scale_factor = new_size[0]/float(self.size[0])
        else:
            scale_factor = new_size[1]/float(self.size[1])
        old_pic.scale_xy(x=scale_factor, y=scale_factor)
        new_svg = svgutils.SVGFigure(new_size)
        new_svg.append([old_pic])
        new_svg.save(self.filename)
        self.size= new_size

    def getAnchorPosition(self, anchor):
        return (anchor.value[0]*width, anchor.value[1]*height)

    @abc.abstractmethod
    def draw(self):
        pass        
        
class InternalPicture(Picture, metaclass = abc.ABCMeta):        
    pass            
            
class TreePicture(InternalPicture): #should be in its own file but not for now b/c convenient
    structure_type = structures.TreeNode
    
    class TreeNode(NodeElement):
        def __init__(self, center, data, width, height, shape=Shape.CIRCLE, style={}, **kwargs):
            self.data = data
            self.childNodes = []
            self.edges = []
            self.edge_class = kwargs.pop('edge_class', EdgeElement)
            if not issubclass(self.edge_class, EdgeElement):
                raise TypeError("Expected {} is not an edge subclass".format(edge_class))
            self.edge_style = kwargs.pop("edge_style", {})
            self.scale_to_data = kwargs.pop("scale_to_data", True)
            if self.scale_to_data:
                data_picture = Picture.make_picture(data, style=style)
                if not isinstance(data_picture, structures.Pointer):
                    if not data_picture.is_drawn:
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
        size = (self.width, self.height)
        super().__init__(tree_root, filename, size)

    def _width_estimate(self, root):
        if root.is_leaf():
            return 2*self.node_width+self.node_sep
        width = 0
        for child in root.children:
            child_width = self._width_estimate(child)
            width += child_width
        return width

    def _height_estimate(self, root):
        #TODO: improve height heuristic for tall trees.
        tree_height = root.tree_height()
        return tree_height*(2*self.node_width + self.edge_length) - self.edge_length + self.node_sep


    def _layout_nodes(self, parent, level_roots, svg_engine):
        sub_widths = []
        for subtree in level_roots:
            sub_width = self.width_dict.get(subtree, self._width_estimate(subtree))
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
        root_y = self.node_height + self.node_sep/2
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

class LeafPicture(Picture, metaclass=abc.ABCMeta):
    pass

class StringLeaf(LeafPicture):
    structure_type = structures.TreeNode

    def __init__(self, text, font_size=DEFAULTS["font_size"], filename=None, size=None, **kwargs):
        self.text = str(text)
        try:
            self.font_size = int(font_size)
        except ValueError:
            self.font_size = int(font_size[:-2]) #removes units (pt,cm,etc.) from font size string
        size = (self.font_size*(len(self.text)), self.font_size+2) #text width is heuristically determined, will be inexact. TODO: scale font size down if given picture size
        LeafPicture.__init__(self, text, filename, size)
        kwargs["stroke_width"] = kwargs.get("stroke_width", "1")
        kwargs["fill"] = kwargs.get("fill", "black")
        self.properties = kwargs

    def draw(self, position = None):

        svg = SVGEngine(self.filename, self.size)
        svg.draw_text_default(self.text, (0,self.font_size), **self.properties)
        svg.save()

    def text_length(self):
        return len(self.text)
