import svgwrite

DEFAULTS = {"stroke_width" : "3", "stroke" : "black",
            "fill" : "white", "fill_opacity" : "1",
            "font_size" : "24pt"}

class SVGEngine():
    def __init__(self, filename, size):
        self.svg_doc = svgwrite.Drawing(filename,size)

    def __str__(self):
        return self.svg_doc.tostring()

    def save(self):
        self.svg_doc.save()
            
    def getSVG(self):
        return self.svg_doc
                                                            
    #SHAPE CONSTRUCTION
    def _add_defaults(self, **kwargs):
        #adds design defaults to kwargs of draw methods when not specified
        for kwarg, default in DEFAULTS.items():
            if kwarg not in kwargs:
                kwargs[kwarg] = default
        return kwargs

    def draw_circle(self, center, radius = 50, **kwargs):
        kwargs = self._add_defaults(**kwargs)
        circle = self.svg_doc.circle(center, r = radius, **kwargs)
        self.svg_doc.add(circle)

    def draw_line(self, start, end, **kwargs):
        kwargs = self._add_defaults(**kwargs)
        line = self.svg_doc.line(start, end, **kwargs)
        self.svg_doc.add(line)

    def draw_rect(self, left_upper_corner, width=50, height=50, **kwargs):
        kwargs = self._add_defaults(**kwargs)
        rect = self.svg_doc.rect(insert=left_upper_corner, size=(width,height), **kwargs)
        self.svg_doc.add(rect)

    def draw_rect_center(self, center, width=50, height=50, **kwargs):
        left_upper_x = center[0] - width/2
        left_upper_y = center[1] - height/2
        corner = (left_upper_x, left_upper_y)
        rect = self.draw_rect(self, corner, width, height, **kwargs)
        self.svg_doc.add(rect)

    def draw_rounded_rect(self, left_upper_corner, width=50, height=50, rx=5, ry=5, **kwargs):
        kwargs = self._add_defaults(**kwargs)
        rect = self.svg_doc.rect(insert=left_upper_corner,
                                 size=(width,height),
                                 rx=rx,
                                 ry=ry,
                                 **kwargs)
        self.svg_doc.add(rect)

    def draw_ellipse(self, center, rx=75, ry=50, **kwargs):
        kwargs = self._add_defaults(**kwargs)
        ellipse = self.svg_doc.ellipse(center, r=(rx,ry), **kwargs)
        self.svg_doc.add(ellipse)

    def draw_text_default(self, text, left_upper_corner, **kwargs):
        """text defined by upper left corner point"""
        
        kwargs = self._add_defaults(**kwargs)
        text = self.svg_doc.text(text, left_upper_corner, **kwargs)
        self.svg_doc.add(text)

    def draw_text_center(self, text, center, **kwargs):
        """text defined by center point"""
        
        kwargs = self._add_defaults(**kwargs)
        text = self.svg_doc.text(text, center, text_anchor="middle", dominant_obaseline="central")
        #note: some image viewers don't recognize the dominant_baseline attribute
        self.svg_doc.add(text)

    def draw_arrow(self, start, end, **kwargs):
        #Temporary implementation only draws a line, TODO: draw arrows
        kwargs = self._add_defaults(**kwargs)
        self.draw_line(start,end,**kwargs)

#TODO: arrows, regular polygons, text along a line
