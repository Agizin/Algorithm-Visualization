import abc
import sys
import svgutils.transform as svgutils
from time import time
from inspect import isabstract

from algviz.parser import structures
from .elements import *
from .anchor import Anchor
from .connection_map import ConnectionMap
from .svg_engine import DEFAULTS, SVGEngine

assert(sys.version_info >= (3,6))

class DataStructureException(TypeError):
    """Type Error indicates that a  DataStructure instance or subclass was expected 
    and an appropriate one was not recieved"""
    pass

class Picture(object, metaclass=abc.ABCMeta):
    structure_map = {} #Maps a Data Structure subclass to the Picture subclass that visualizes it.

    @staticmethod
    def make_picture(structure, *args, **kwargs):
        """Selects a picture class for the given structure."""
        #TODO: add rules for slecting between picture classes that have same structure type.
        if not isinstance(structure, structures.DataStructure):
            raise DataStructureException("Expected structure to be instance of DataStructure, got {}"
                                         .format(type(structure)))
        if type(structure) not in Picture.structure_map:
            raise DataStructureException("No picture class found for structure: {}"
                                         .format(type(structure)))
        pic_class = Picture.structure_map[type(structure)]
        return pic_class(structure, *args, **kwargs)

    @staticmethod
    @abc.abstractmethod
    def get_structure_type():
        pass

    def __init_subclass__(cls, **kwargs):
        """Called when Picture is subclassed.
        As subclasses are initialized, we add their respective structure types to the structure_map."""
        super().__init_subclass__(**kwargs)
        if not isabstract(cls):
            structure_type = cls.get_structure_type()
            if structure_type is None or not issubclass(structure_type, structures.DataStructure):
                raise DataStructureException("Can only create picture of data structures, not: {}"
                                             .format(structure_type))
            Picture.structure_map[structure_type] = cls

    def __init__(self, structure, width, height, **kwargs):
        self.structure = structure #data structure that this picture represents
        self.width = width
        self.height = height
        self.svg_str = ''

    def __str__(self):
        return self.svg_str

    def getSVG(self):
        return self.svg_str

    def writeSVG(self, svg_string):
        self.svg_str = svg_string

    def save(self, filename):
        if(self.is_drawn()):
            if isinstance(self.svg_str,bytes):
                writemode = 'wb'
            elif isinstance(self.svg_str,str):
                writemode = 'w'
            else:
                raise Exception('Svg is neither string nor bytes')
            with open(filename, writemode) as f:
                f.write(self.svg_str)
        else:
            raise Exception("picture not drawn")

    def is_drawn(self):
        return len(self.svg_str) != 0

    def scale_down(self, new_width, new_height):
        if not self.is_drawn():
            self.draw()
        if new_width <= self.width and new_height <= self.height:
            return
        old_svg = svgutils.fromstring(self.getSVG())
        old_pic = old_svg.getroot()
        if abs(new_width-self.width) <= abs(new_height-self.height):
            scale_factor = new_width/float(self.width)
        else:
            scale_factor = new_height/float(self.height)
        old_pic.scale_xy(x=scale_factor, y=scale_factor)
        self.width = self.width*scale_factor
        self.height = self.height*scale_factor
        new_svg = svgutils.SVGFigure((self.width, self.height))
        new_svg.append([old_pic])
        self.writeSVG(new_svg.to_str())

    def get_anchor_position(self, anchor):
        return (anchor.value[0]*self.width, anchor.value[1]*self.height)

    @abc.abstractmethod
    def draw(self):
        pass        
        
class InternalPicture(Picture, metaclass = abc.ABCMeta):        
    pass            
            
class TreePicture(InternalPicture):
    
    class TreeNode(NodeElement):
        def __init__(self, center, data, width, height, shape=Shape.CIRCLE, style={}, **kwargs):
            self.data = data
            self.childNodes = []
            self.edges = []
            self.edge_class = kwargs.pop('edge_class', EdgeElement)
            if not issubclass(self.edge_class, EdgeElement):
                raise TypeError("Expected {} is not an edge subclass".format(edge_class))
            self.edge_style = kwargs.pop("edge_style", {})
            self.scale_up_to_data = kwargs.pop("scale_up_to_data", False)
            if self.scale_up_to_data:
                data_picture = Picture.make_picture(data, style=style)
                if not isinstance(data_picture, structures.Pointer):
                    if not data_picture.is_drawn:
                        data_picture.draw()
                    margin = kwargs.get("margin", 15)
                    width = max(width, data_picture.width + margin)
                    height = max(height, data_picture.height + margin)
            super().__init__(center, width, height, shape, style, **kwargs)

        def is_leaf(self):
            return len(self.childNodes) == 0

        def add_child(self, child):
            if isinstance(child, TreePicture.TreeNode):
                self.childNodes.append(child)
            else:
                raise TypeError("{} is not a tree node".format(child))

        def add_childen(self, children):
            for child in children:
                self.add_child(child)

        def _make_edge(self, child):
            assert(child in self.childNodes)
            source = self.center
            destination = (child.center[0], child.center[1]-child.height/2)
            newEdge = self.edge_class(source, destination, self.edge_style)
            return newEdge
            
        def draw(self, svg_engine):
            for child in self.childNodes:
                edge = self._make_edge(child)
                edge.draw(svg_engine)
                child.draw(svg_engine)
            super().draw(svg_engine)

    @staticmethod
    def get_structure_type():
        return structures.TreeNode
    
    def __init__(self, tree_root, style={}, **kwargs):
        self.root = tree_root
        self.style=style
        self.node_shape = kwargs.pop("node_shape", Shape.CIRCLE)
        self.node_width = kwargs.pop("node_width", 100)
        self.node_height = kwargs.pop("node_height", 100)
        self.edge_length = kwargs.pop("edge_length", 200)
        self.node_sep = kwargs.pop("node_sep", 10)
        self.pointer_style = kwargs.pop("pointer_Style", {})
        #TODO: better way to assign default values?
        width = self._width_estimate(self.root)
        height = self._height_estimate(self.root)
        super().__init__(tree_root, width, height)

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
        return tree_height*(2*self.node_width + self.edge_length) - self.edge_length
    
            
    def _layout_nodes(self, parent, level_roots):
        sub_widths = []
        for subtree in level_roots:
            sub_width = self.width_dict.get(subtree, self._width_estimate(subtree))
            if subtree in self.width_dict:
                sub_widths.append(self.width_dict[subtree])
            else:
                sub_width = self._width_estimate(subtree)
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
                                                self.node_shape, self.style)
                parent.add_child(new_node)
                if not subtree.is_leaf():
                    self._layout_nodes(new_node, subtree.children)

    def _draw_data(self, root_node):
        """Draws/Connects Tree subpictures to the current picture"""
        node_queue = [root_node]
        connections = ConnectionMap(self)
        while len(node_queue) > 0:
            node = node_queue.pop(0)
            if isinstance(node.data, structures.Pointer):
                pointerTo = Picture.make_picture(node.data.referent, style=self.style)
                connections.add_connection(node.center, pointerTo, anchor=anchor, pointer=True)
                node_center_x = node.center[0]
                picture_center_x = node_data.width/2
                if node_center_x <= picture_center_x: #Node is on left side of picture
                    anchor = Anchor.RIGHT
                else:
                    anchor = Anchor.LEFT
                connections.add_connection(node.center, pointerTo, anchor=anchor,
                                           pointer=True, pointer_style=self.pointer_style)
            else:
                #If not a pointer, we scale the subpicture fit into node
                node_data_pic = Picture.make_picture(node.data, style=self.style)
                node_data_pic.scale_down(node.width, node.height)
                connections.add_connection(node.center, node_data_pic, anchor=Anchor.CENTER, pointer=False)
            for child in node.childNodes:
                node_queue.append(child)
        connections.draw_connections()

    def draw(self):
        if self.is_drawn():
            return
        self.width_dict = {}
        root_x = self.width/2
        root_y = self.node_height + self.node_sep/2
        root_center = (root_x, root_y)
        root_node = TreePicture.TreeNode(root_center, self.root.data,
                                         self.node_width, self.node_height,
                                         self.node_shape, self.style)
        svg_engine = SVGEngine(self.width, self.height)
        self._layout_nodes(root_node, self.root.children)
        root_node.draw(svg_engine)
        self.writeSVG(str(svg_engine))
        self._draw_data(root_node)

class LeafPicture(Picture, metaclass=abc.ABCMeta):
    pass

class StringLeaf(LeafPicture):

    @staticmethod
    def get_structure_type():
        return structures.String

    def __init__(self, text, font_size=DEFAULTS["font_size"], **kwargs):
        self.text = str(text)
        try:
            self.font_size = int(font_size)
        except ValueError:
            self.font_size = int(font_size[:-2]) #removes units (pt,cm,etc.) from font size string
        width = self.font_size*(len(self.text)) #text width is heuristically determined, will be inexact.
        height = self.font_size+1
        super().__init__(text, width, height)
        kwargs["stroke_width"] = kwargs.get("stroke_width", "1")
        kwargs["fill"] = kwargs.get("fill", "black")
        self.properties = kwargs

    def draw(self, position = None):
        svg = SVGEngine(self.width, self.height)
        svg.draw_text_default(self.text, (0,self.font_size), **self.properties)
        self.writeSVG(str(svg))

    def text_length(self):
        return len(self.text)


