import svgwrite

#TODO: Expand. Asd in general svgwrite functions.

class Visualizer():
    def __init__(self, svg_doc):
        self.svg_doc = svg_doc

    def __str__(self):
        return self.svg_doc.tostring()

    def save(self):
        self.svg_doc.save()
            
    def getSVG(self):
        return self.svg_doc
                                                            
