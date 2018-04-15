from enum import Enum

class Anchor(Enum):
    """Identifies points of relative positions on Picture"""
    TOPLEFT = (0,0)
    TOP = (0.5, 0)
    TOPRIGHT = (1,0)
    LEFT = (0, 0.5)
    CENTER = (0.5,0.5)
    RIGHT = (1,0.5)
    BOTTOMLEFT = (0,1)
    BOTTOM = (0.5,1)
    BOTTOMRIGHT = (1,1)

    def is_on_left(self):
        return self.value[0] == 0

    def is_on_right(self):
        return self.value[0] == 1
