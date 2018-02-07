import abc

from .picture import Picture
from .svg_engine import DEFAULTS, SVGEngine

class LeafPicture(Picture, metaclass=abc.ABCMeta):
    pass

class StringLeaf(LeafPicture):

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

