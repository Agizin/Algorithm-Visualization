import svgutils.transform as svgutils

from algviz.parser import structures
from .anchor import Anchor
from .svg_engine import SVGEngine
from .elements import PointerElement, BorderElement

"""This is what composes pictures into a single SVG.

This class is given a base picture and a series of subpictures. Each subpicture is
connected to the base picture at a specific point, which I called the start point for
the connection. An anchor element from anchor.py defines the point that the subpicture 
is placed at, called the connection point. This information is contained in the Connection class.
The Composition Engine class holds this connection information and has methods to compose the
base picture and subpictures into a single SVG, which is then made a property of the base
picture."""

class CompositionEngine:
    class Connection:
        """Default connection: the subpicture is placed directly on the
            base picture at the connection point."""
        def __init__(self, start_point, connect_pic, anchor):

            self.start_point = start_point
            self.connect_pic = connect_pic
            if not connect_pic.is_drawn():
                connect_pic.draw()
            self.anchor = anchor

        def is_pointer(self):
            return isinstance(self, CompositionEngine.PointerConnection)

    class PointerConnection(Connection):
        """Pointer connections are placed outside the base picture. The start point
        of the connection (in the start point) is connected to the anchor point by
        a pointer"""
        def __init__(self, start_point, connect_pic, anchor, pointer_style={}):
            self.pointer_style = pointer_style
            super().__init__(start_point, connect_pic, anchor)
    
    def __init__(self, startPicture):
        self.connections = []
        self.picture = startPicture #base picture
        self.left_shift_y = 0
        self.right_shift_y = 0
        
    def add_connection(self, point, connect_pic, anchor=None, pointer=True, pointer_style={}):
        if self.picture.width < point[0] or self.picture.height < point[1]:
            raise ValueError("Point not included in picture")
        if pointer:
            cxn = CompositionEngine.PointerConnection(point, connect_pic, anchor, pointer_style)
        else:
            cxn = CompositionEngine.Connection(point, connect_pic, anchor)
        self.connections.append(cxn)

    def _connect_on_left(self, connection, mid):
        """Returns True if the (pointer) connection should be placed to the left of main pic.
        Otherwise, return false - connection placed on right"""
        if not connection.is_pointer():
            return TypeError("Must be a pointer connection.")
        if connection.anchor.is_on_right():
            return True
        elif connection.anchor.is_on_left():
            return False #false b/c a left anchor implies we should place on right of main pic
        return connection.start_point[0] <= mid
        

    def _resize_pic(self):
        """If we need to add pointers to our picture, we need to create margins in the canvas
        of the base picture SVG to place the subpicture in. This method computes what
        the size of that new canvas should be. (note: we don't actually change the size
        of the base picture's visual, only the canvas it would be drawn on)."""

        #the variables below define what width/height we should add to each margin
        left_width = 0
        right_width = 0
        left_height = 0
        right_height = 0
        
        for connection in self.connections:
            if not connection.is_pointer():
                #in place connections dont change size of picture
                continue
            connect_width = connection.connect_pic.width
            connect_height = connection.connect_pic.height
            if self._connect_on_left(connection, self.picture.width/2):
                left_width = max(connect_width, left_width)
                left_height += connect_height
            else:
                right_width = max(connect_width, right_width)
                right_height += connect_height
        new_width = left_width + self.picture.width + right_width
        new_height = max(left_height, self.picture.height, right_height)
        self.picture.width = new_width
        self.picture.height = new_height
        return left_width, left_height, right_width, right_height
                    
    def draw_connections(self):
        """Method that draws all defined connections onto the base picture"""
        
        #TODO: reimplement with GraphViz?
        start_pic_height = self.picture.width
        start_pic_width = self.picture.height
        left_width, left_height, right_width, right_width = self._resize_pic() #defines new margin sizes, changes the height and width of self.picture
        main_svg = svgutils.fromstring(self.picture.getSVG())
        main_root = main_svg.getroot()
        main_root.moveto(left_width, 0)
        subpics = [main_root]
        new_elements = []
        for connection in self.connections:
            subpic = connection.connect_pic
            subpic.draw()
            anchor = connection.anchor
            anchorPos = connection.connect_pic.get_anchor_position(anchor)
            #To place the subpicture, we first determine its location relative to the base
            #picture. So, we compute how much to shift it's current coordinates by.
            if not connection.is_pointer():
                shift_x = left_width + connection.start_point[0] - anchorPos[0]/2
                shift_y = connection.start_point[1] - anchorPos[1]/2
            else:
                if self._connect_on_left(connection, start_pic_width/2):
                    shift_x = 0
                    shift_y = self.left_shift_y
                    self.left_shift_y += subpic.height
                else:
                    shift_x = 0.95*(left_width + start_pic_width) #coefficient becasue to decrease unintentional shift right from margins
                    shift_y = self.right_shift_y
                    self.right_shift_y += subpic.height
                newStartPoint = (connection.start_point[0]+left_width, connection.start_point[1])
                endPoint = (anchorPos[0]+shift_x, anchorPos[1]+shift_y)
                new_elements.append(PointerElement(newStartPoint, endPoint, connection.pointer_style))
                subpic.scale_down_percent(0.9)
                new_subpic_center = (subpic.width/2+shift_x, subpic.height/2+shift_y)
                new_elements.append(BorderElement(new_subpic_center, subpic.width, subpic.height))
            subpic_svg = svgutils.fromstring(subpic.getSVG())
            subpic_root = subpic_svg.getroot()
            subpic_root.moveto(shift_x, shift_y)
            subpics.append(subpic_root)
        new_svg = svgutils.SVGFigure("{!s}px".format(self.picture.width), "{!s}px".format(self.picture.height))
        new_svg.append(subpics)

        #Lastly, after composing pioctures, we add pointers, borders, and other new elements if needed
        elems_svg_engine = SVGEngine(self.picture.width, self.picture.height)
        for element in new_elements:
            element.draw(elems_svg_engine)
        elems_svg = svgutils.fromstring(str(elems_svg_engine))
        elems_root = elems_svg.getroot()
        new_svg.append(elems_root)
        self.picture.writeSVG(new_svg.to_str()) #composite SVG saved to the base picture
