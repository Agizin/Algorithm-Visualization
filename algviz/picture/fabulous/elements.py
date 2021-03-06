import abc
from enum import Enum

class ShapeException(TypeError):
    def __init__(self, shape):
        message = "{} not a recognized shape".format(str(shape))
        super().__init__(message)

class Shape(Enum):
    """Defines shape constants and how to draw them"""
    
    #TODO: expand
    CIRCLE = 0
    RECT = 1
    ROUNDED_RECT = 2

    def draw(self, center, width, height, svg_engine, **kwargs):
        if self is Shape.CIRCLE:
            radius = min(width/2, height/2)
            svg_engine.draw_circle(center, radius, **kwargs)
        elif self is Shape.RECT:
            upper_left_corner = (center[0]-width/2, center[1]-height/2)
            svg_engine.draw_rect(upper_left_corner, width, height, **kwargs)
        elif self is Shape.ROUNDED_RECT:
            upper_left_corner = (center[0]-width/2, center[1]-height/2)
            rx = kwargs.pop("rx",5)
            ry = kwargs.pop("ry",5)
            svg_engine.draw_rounded_rect(upper_left_corner, width, height, rx, ry, **kwargs)

class PictureElement(metaclass = abc.ABCMeta):
    """Components of a data structure picture"""
    pass

class RectangularElement(PictureElement, metaclass = abc.ABCMeta):
    """Elements of a picture that take up space 
    (as defined by a bounding box)"""
    def __init__(self, center, width, height, **kwargs):
        self.center = center
        self.width = width
        self.height = height

    @abc.abstractmethod
    def draw(self, svg_engine):
        pass

class BorderElement(RectangularElement):
    """Use to define borders around objects"""
    def draw(self, svg_engine, fill_opacity="0", stroke_width="2"):
        Shape.RECT.draw(self.center, self.width, self.height, svg_engine,
                        fill_opacity=fill_opacity, stroke_width =stroke_width)

class NodeElement(RectangularElement):
    def __init__(self, center, width, height, shape = None, style={}, **kwargs):
        if shape != None and not isinstance(shape,Shape):
            for name, member in Shape.__members__.items():
                if name.lower() == shape:
                    self.shape = member
            else:
                raise ShapeException(shape)
        else:
            self.shape = shape
        self.style = style
        if not hasattr(self, 'data'):
            self.data = None
        super().__init__(center, width, height, **kwargs)

    def draw(self, svg_engine):
        self.shape.draw(self.center, self.width, self.height, svg_engine, **self.style)

class InvisibleNode(NodeElement):
    def draw(self, svg_engine):
        raise NotImplementedError("Drawing not supported for invisible nodes")

class DecorationElement(PictureElement, metaclass=abc.ABCMeta):
    """Elements that do not take up blocks of space"""
    pass

class EdgeElement(DecorationElement):
    def __init__(self, source, destination, style, **kwargs):
        self.source = source
        self.destination = destination
        self.style = style

    def draw(self, svg_engine):
        svg_engine.draw_line(self.source, self.destination, **self.style)

class ArrowElement(EdgeElement):
    def draw(self, svg_engine):
        svg_engine.draw_arrow(self.source, self.destination, **self.style)

class PointerElement(EdgeElement):
    def draw(self, svg_engine):
        svg_engine.draw_pointer(self.source, self.destination, **self.style)
        



    
