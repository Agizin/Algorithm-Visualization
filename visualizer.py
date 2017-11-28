import svgwrite

class Visualizer():
    def __init__(self, svg_doc):
        self.svg_doc = svg_doc

    def __str__(self):
        return self.svg_doc.tostring()

    def save(self):
        self.svg_doc.save()
            
    def getSVG(self):
        return self.svg_doc
                                                            
    #SHAPE CONSTRUCTION
    
    design_defaults = {"stroke_width" : "3", "stroke" : "black",
                           "fill" : "white", "fill_opacity" : "1"} #static dictionary of default design elements

    def _add_defaults(**kwargs):
        #adds design defaults to kwargs of draw methods when not specified
        for (kwarg, default) in design_defaults.iteritems():
            if kwarg not in kwargs:
                kwargs[kwarg] = default
        return kwargs

    def draw_circle(self, center, radius = 50, **kwargs):
        kwargs = self._add_defaults(**kwargs)
        self.svg_doc.circle(center, r = radius, **kwargs)

    def draw_line(self, start, end, **kwargs):
        kwargs = self._add_defaults(**kwargs)
        self.svg_doc.line(start, end, **kwargs)

    def draw_rect(self, left_upper_corner, width=50, height=50, **kwargs):
        kwargs = self._add_defaults(**kwargs)
        self.svg_doc.rect(insert=left_upper_corner, size=(width,height), **kwargs)

    def draw_rounded_rect(self, left_upper_corner, width=50, height=50, rx=5, ry=5, **kwargs):
        kwargs = self._add_defaults(**kwargs)
        self.svg_doc.rect(insert=left_upper_corner,
                          size=(width,height),
                          rx=rx,
                          ry=ry,
                          **kwargs)

    def draw_ellipse(self, center, rx=75, ry=50, **kwargs):
        kwargs = self._add_defaults(**kwargs)
        self.svg_doc.ellipse(center, r=(rx,ry), **kwargs)

    def draw_text_default(self, text, left_upper_corner, **kwargs):
        """text defined by upper left corner point"""
        
        kwargs = self._add_defaults(**kwargs)
        self.svg_doc.text(insert, **kwargs)

    def draw_text_center(self, text, center, **kwargs):
        """text defined by center point"""
        
        kwargs = self._add_defaults(**kwargs)
        self.svg_doc.text(text, center, text_anchor="middle", dominant_baseline="central")
        #note: some image viewers don't recognize the dominant_baseline attribute

    #TODO: arrows, regular polygons, text along a line
