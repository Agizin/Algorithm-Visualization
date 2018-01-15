import abc
from time import time

class Picture(metaclass=abc.ABCMeta):

    class DataStructureException(TypeError):
        """indicates that an instance of structures.DataStructure was expected"""
        pass

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
    
    def __init__(self, structure, filename, size=None, **kwargs):
        self.structure = structure #data structure that this picture represents
        self.filename = filename #name of svg file
        self.size = size #a requirement on max bounding box size, if None then no requirement
        #TODO: scale down pictures after drawing so that they fit the bounding box.
        
    def _tempname(self):
        time_str = str(time()).replace('.','')
        try:
            uid = self.structure.uid
        except AttributeError:
            raise DataStructureException("Expected Data Structure, got {}"
                                         .format(type(self.structure)))
        return "temp_{}_{}.svg".format(uid, time_str)
                    
    @abc.abstractmethod
    def lay_out(self):
        """determines coordinates for picture elements so that it can be drawn"""
        pass

    @abc.abstractmethod
    def draw(self):
        pass

    def get_connection_point(self, position):
        """Returns coordinates of a desired connection point between pictures 
        relative to the current picture. Position is where the connection point
        will be relative to this picture, e.g. Left, Right."""
        
        if self.size is None:
            self.lay_out()
        if position == "Left":
            connection_point = (0, self.size[1]/2)
        elif position == "Right":
            connection_point = (size[0], self.size[1]/2)
        #TODO: add top, bottom, positions. Anything else?
        elif position is None:
            connection_point = None
        else:
            raise ValueError("Unknown position: {}".format(position))

    

    
