import abc
import sys
import svgutils.transform as svgutils
from time import time
from inspect import isabstract
from math import floor

from algviz.parser import structures
from .elements import *
from .anchor import Anchor
from .composition_engine import CompositionEngine
from .svg_engine import DEFAULTS, SVGEngine

assert(sys.version_info >= (3,6))

"""
Picture classes are abstractions of SVGs representing data structures.
"""

class DataStructureException(TypeError):
    """Type Error indicates that a  DataStructure instance or subclass was expected 
    and an appropriate one was not recieved"""
    pass

class Picture(object, metaclass=abc.ABCMeta):
    """Picture classes are abstractions of SVGs representing data structures.

    Each picture subclass should specify the type of structure it represents and the logic
    for drawing it to an SVG."""
    
    structure_map = {} #Maps a Data Structure subclass to the Picture subclass that visualizes it.

    @staticmethod
    def make_picture(structure, *args, **kwargs):
        """Selects a picture class for the given structure. 
        Use this method to create a picture class of an unknown structure"""
        #TODO: add rules for selecting between picture classes that have same structure type.
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
        """Method should return the structure type (from parser.structures) that this class visualizes"""
        pass

    def __init_subclass__(cls, **kwargs):
        """Called when Picture is subclassed.
        As subclasses are initialized, we add their respective structure types to the structure_map."""
        super().__init_subclass__(**kwargs)
        if not isabstract(cls):
            structure_types = cls.get_structure_type()
            assert(len(structure_types) > 0)
            for structure_type in structure_types:
                Picture.structure_map[structure_type] = cls

    def __init__(self, structure, width, height, **kwargs):
        self.structure = structure #data structure that this picture represents
        self.width = width #width of the SVG (pixels)
        self.height = height #height of the SVG (pixels)
        self.svg_str = None #Contains the contents of the SVG. Note: may be represented as a string or as bytes.

    def __str__(self):
        return str(self.svg_str)

    def getSVG(self):
        """Returns svg. Note: may be a string or bytes object"""
        return self.svg_str

    def writeSVG(self, svg_string):
        if isinstance(svg_string, str):
            self.svg_str = svg_string
        elif isinstance(svg_string, bytes):
            self.svg_str = svg_string.decode("utf-8")
        else:
            raise TypeError("Can only write an SVG as from a string or bytes instance, got {}".format(type(svg_string)))

    def save(self, filename):
        """Saves the SVG represented to the given filename."""
        if not self.is_drawn():
            self.draw()
        if isinstance(self.svg_str,bytes):
            writemode = 'wb'
        elif isinstance(self.svg_str,str):
            writemode = 'w'
        else:
            raise Exception('Svg is neither string nor bytes')
        with open(filename, writemode) as f:
            f.write(self.svg_str)

    def is_drawn(self):
        return self.svg_str is not None

    def scale_down(self, new_width, new_height):
        """Scales the picture SVG proportionally to below the given dimensions"""
        if not self.is_drawn():
            self.draw()
        if new_width >= self.width and new_height >= self.height:
            return
        old_svg = svgutils.fromstring(str(self))
        old_pic = old_svg.getroot()
        if new_width-self.width <= new_height-self.height:
            scale_factor = new_width/float(self.width)
        else:
            scale_factor = new_height/float(self.height)
        self.width = self.width*scale_factor
        self.height = self.height*scale_factor
        if isinstance(self,StringLeaf): #for some reason, svg_utils doesnt resize text correctly
            self.font_size = floor(self.height)
            self.draw()
        else:
            old_pic.scale_xy(x=scale_factor, y=scale_factor)
            new_svg = svgutils.SVGFigure((self.width, self.height))
            new_svg.append([old_pic])
            self.writeSVG(new_svg.to_str())

    def scale_down_percent(self, p):
        p = float(p)
        if p <= 0 or p>=1:
            raise ValueError("{} must be a float greater than zero up to one".format(p))
        self.scale_down(self.width*p, self.height*p)

    def get_anchor_position(self, anchor):
        """When given an anchor (see: anchor.py), returns the position of that anchor on this SVG"""
        a = (anchor.value[0]*self.width, anchor.value[1]*self.height)
        return a

    @abc.abstractmethod
    def draw(self):
        """Method that generates the svg for the structure"""
        pass        
        
class InternalPicture(Picture, metaclass = abc.ABCMeta):
    """Picture classes that contain subpictures that need to be composed into one"""

    def __init__(self, structure, width, height, **kwargs):
        self.pointer_style = kwargs.pop("pointer_style", {})
        super().__init__(structure, width, height, **kwargs)
    
    @abc.abstractmethod
    def _node_generator(self):
        pass
    
    def _draw_node_data(self, pointer_anchor=Anchor.CENTER):
        """Draws/Connects subpictures to the current picture"""
        connections = CompositionEngine(self) #Object used to compose subpictuctures into a single SVG.
        contains_subpictures = False
        for node in self._node_generator():
            if node.data is None:
                continue
            contains_subpictures=True
            if isinstance(node.data, structures.Pointer):
                ref = node.data.referent
                if isinstance(ref, structures.Pointer):
                     raise NotImplementedError("Pointers referring to other pointers is not yet supported.")
                pointerTo = Picture.make_picture(node.data.referent, style=self.style)
                connections.add_connection(node.center, pointerTo, anchor=pointer_anchor, pointer=True, pointer_style=self.pointer_style)
            else:
                #If not a pointer, we scale the subpicture fit into node
                node_data_pic = Picture.make_picture(node.data, style=self.style)
                node_data_pic.scale_down(node.width, node.height)
                anchor = Anchor.BOTTOMRIGHT
                if isinstance(node_data_pic,StringLeaf):
                    anchor = Anchor.BOTTOM #Ideally, this should also be anchored bottom right, but its messed up by the difficult of predicting string length in SVG
                connections.add_connection(node.center, node_data_pic, anchor=anchor, pointer=False)
        if contains_subpictures:
            connections.draw_connections()
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
            for child in childNodes:
                self.add_child(child)

        def get_children(self):
            return self.childNodes

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
        return [structures.TreeNode]
    
    def __init__(self, tree_root, style={}, **kwargs):
        self.root = tree_root
        self.style=style
        self.node_shape = kwargs.pop("node_shape", Shape.CIRCLE)
        self.node_width = kwargs.pop("node_width", 100)
        self.node_height = kwargs.pop("node_height", 100)
        self.edge_length = kwargs.pop("edge_length", 200)
        self.node_sep = kwargs.pop("margin", 10)
        #TODO: better way to assign default values?
        width = self._width_estimate(self.root)
        height = self._height_estimate(self.root)
        super().__init__(tree_root, width, height, **kwargs)

    def _width_estimate(self, root):
        if root is structures.Null:
            return 0
        if root.is_leaf():
            return 2*self.node_width+self.node_sep
        width = 0
        for child in root.children:
            child_width = self._width_estimate(child)
            width += child_width
        return width

    def _determine_height_coef(self, x):
        """expirementally determined function to provide larger trees with smaller relative heights. Cuts off some white space at bottom."""
        x = float(x)
        return (x-0.5)/(2*x**2-x+1)+0.65

    def _height_estimate(self, root):
        #TODO: improve height heuristic for tall trees.
        if root is structures.Null:
            return 0
        tree_height = root.height()
        c = self._determine_height_coef(tree_height)
        return c*tree_height*(2*self.node_width+self.edge_length) - self.edge_length
            
    def _layout_nodes(self, parent, level_roots):
        sub_widths = []
        for subtree in level_roots:
            if subtree is structures.Null:
                sub_widths.append(0)
                continue
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
            if subtree is not structures.Null:
                new_node = TreePicture.TreeNode((x,y), subtree.data,
                                                self.node_width, self.node_height,
                                                self.node_shape, self.style)
                parent.add_child(new_node)
                if not subtree.is_leaf():
                    self._layout_nodes(new_node, subtree.children)

    def _node_generator(self):
        node_queue = [self.root_node]
        while len(node_queue) > 0:
            node = node_queue.pop(0)
            for child_node in node.get_children():
                node_queue.append(child_node)
            yield node
            
    def draw(self):
        if self.is_drawn():
            return
        self.width_dict = {}
        root_x = self.width/2
        root_y = self.node_height/2+self.node_sep
        root_center = (root_x, root_y)
        self.root_node = TreePicture.TreeNode(root_center, self.root.data,
                                         self.node_width, self.node_height,
                                         self.node_shape, self.style)
        svg_engine = SVGEngine(self.width, self.height)
        self._layout_nodes(self.root_node, self.root.children)
        self.root_node.draw(svg_engine)
        self.writeSVG(str(svg_engine))
        self._draw_node_data()

class ArrayPicture(InternalPicture):

    @staticmethod
    def get_structure_type():
        return [structures.Array, list]
        
    def __init__(self, array, style={}, **kwargs):
        self.array = array.data
        self.style = style
        self.cell_width = kwargs.pop("cell_width", 100)
        self.frame_width = kwargs.pop("frame_width", self._width_estimate())
        self.frame_height = kwargs.pop("frame_height", self.cell_width)
        self.margin = kwargs.pop("margin", 25)
        self.nodes = []
        super().__init__(array, self.frame_width+2*self.margin, self.frame_height+2*self.margin, **kwargs)
        if(self.height<50):
            import pdb
            pdb.set_trace()

    def _width_estimate(self):
        return len(self.array)*self.cell_width

    def _layout_nodes(self):
        start_x = self.margin
        for item in self.array:
            end_x = start_x + self.cell_width
            height = self.frame_height
            width = end_x - start_x
            center = (start_x + width/2, self.margin+height/2)
            node = InvisibleNode(center, width, height, shape=Shape.RECT, style=self.style)
            node.data = item
            self.nodes.append(node)
            start_x += self.cell_width

    def _node_generator(self):
        yield from self.nodes

    def _draw_frame(self, svg_engine):
        center = (self.width/2, self.height/2)
        frame = BorderElement(center, self.frame_width, self.frame_height)
        frame.draw(svg_engine, fill_opacity="1", stroke_width = DEFAULTS["stroke_width"])

    def _draw_nodes(self, svg_engine):
        start_height = self.margin
        end_height = self.height - self.margin
        x = self.margin
        for node in self.nodes[:-1]:
            x += node.width
            start = (x,start_height)
            end = (x, end_height)
            svg_engine.draw_line(start, end, **self.style)

    def draw(self):
        self._layout_nodes()
        svg_engine = SVGEngine(self.width, self.height)
        self._draw_frame(svg_engine)
        self._draw_nodes(svg_engine)
        self.writeSVG(str(svg_engine))
        self._draw_node_data()
        
        
class LeafPicture(Picture, metaclass=abc.ABCMeta):
    """Abstract subclass for pictures that do not include subpictures"""
    pass

class StringLeaf(LeafPicture):

    @staticmethod
    def get_structure_type():
        return [structures.String, str, int]

    def __init__(self, text, font_size=DEFAULTS["font_size"], **kwargs):
        self.text = str(text)
        try:
            self.font_size = int(font_size)
        except ValueError:
            self.font_size = int(font_size[:-2]) #removes units (pt,cm,etc.) from font size string
        width = self.font_size*(len(self.text))*0.75 #text width is heuristically determined, will be inexact.
        height = self.font_size*0.9
        super().__init__(text, width, height)
        kwargs["stroke_width"] = kwargs.get("stroke_width", "1")
        kwargs["fill"] = kwargs.get("fill", "black")
        self.properties = kwargs
        super().__init__(text, width, height)

    def draw(self, position = None):
        svg = SVGEngine(self.width, self.height)
        svg.draw_text_default(self.text, (0,4*self.height/5), font_size=self.font_size, **self.properties)
        self.writeSVG(str(svg))

    def text_length(self):
        return len(self.text)


