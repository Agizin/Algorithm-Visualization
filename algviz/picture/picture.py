import abc
import os.path
from time import time
import svgutils.transform as svgutils

class DataStructureException(TypeError):
    """indicates that an instance of structures.DataStructure was expected"""
    pass

class Picture(metaclass=abc.ABCMeta):

    @staticmethod
    def make_picture(structure, *args, **kwargs):
        try:
            picture_class = type(structure).picture_type
        except AttributeError:
            raise DataStructureException("Expected Data Structure, got {}"
                                         .format(type(structure)))
        if picture_class is not None:
            return picture_class(structure, *args, **kwargs)
        else:
            raise NotImplementedError("Data Structure '{}' is not yet supported"
                                      .format(type(structure)))
    
    def __init__(self, structure, filename=None, size=None, **kwargs):
        self.structure = structure #data structure that this picture represents
        self.size = size #a requirement on max bounding box size, if None then no requirement
        
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

    @abc.abstractmethod
    def draw(self):
        pass

    def get_connection_point(self, position):
        """Returns coordinates of a desired connection point between pictures 
        relative to the current picture. Position is where the connection point
        will be relative to this picture, e.g. Left, Right."""
        
        if position == "Left":
            connection_point = (0, self.size[1]/2)
        elif position == "Right":
            connection_point = (self.size[0], self.size[1]/2)
        #TODO: add top, bottom, positions. Anything else?
        elif position is None:
            connection_point = None
        else:
            raise ValueError("Unknown position: {}".format(position))
        return connection_point

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
        
        
