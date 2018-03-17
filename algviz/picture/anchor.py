from enum import Enum

class Anchor(Enum):
    """Relative Positions on Picture"""
    TOPLEFT = (0,0)
    TOP = (0.5, 0)
    LEFT = (0, 0.5)
    CENTER = (0.5,0.5)
    RIGHT = (1,0.5)
    BOTTOM = (0.5,1)
