import svgutils.transform as svgutils
import os

from algviz.parser import structures
from .anchor import Anchor
from .svg_engine import SVGEngine

"""Tracks connection points and connection pictures to be composed into a single picture"""

class ConnectionMap:
    class Connection:
        def __init__(self, start_point, connect_pic, anchor):
            self.start_point = start_point
            self.connect_pic = connect_pic
            if not connect_pic.is_drawn:
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
        self.connections = []
        self.picture = startPicture
        
    def add_connection(self, point, connect_pic, anchor=None, pointer=True, pointer_style={}):
        if self.picture.width < point[0] or self.picture.height < point[1]:
            raise TypeError("Point not included in picture")
        if pointer:
            self.connections.append(ConnectionMap.PointerConnection(point, connect_pic, anchor, pointer_style))
        else:
            self.connections.append(ConnectionMap.Connection(point, connect_pic, anchor))

    def draw_connections(self):
        #TODO: reimplement with GraphViz?
        cur_pic_width = self.picture.width
        cur_pic_height = self.picture.height
        left_width = 0
        right_width = 0
        left_height = 0
        right_height = 0
        for connection in self.connections:
            if not connection.is_pointer():
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
            subpic.draw()
            anchor = connection.anchor
            anchorPos = connection.connect_pic.get_anchor_position(anchor)
            if not connection.is_pointer():
                shift_x = left_width + connection.start_point[0] - anchorPos[0]/2
                shift_y = connection.start_point[1] - anchorPos[0]/2
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
            subpic_svg = svgutils.fromfile(subpic.filename)
            subpic_root = subpic_svg.getroot()
            subpic_root.moveto(shift_x, shift_y)
            subpics.append(subpic_root)
            if subpic.filename[:4].lower() == "temp":#TODO: clean up leftover svg files better
                os.remove(subpic.filename)
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
        new_svg.save(self.picture.filename)
        self.picture.width = new_width
        self.picture.height = new_height
        self.picture = (self.picture.width, self.picture.height) #TODO: remove
