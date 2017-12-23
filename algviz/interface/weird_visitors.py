from . import visitors
import math

class BitmapArrayVisitor(visitors.ArrayVisitor):
    """Interpret an `int` as an array of 0s and ones"""

    def __init__(self, output_mngr, *args, data_visitor=None, **kwargs):
        if data_visitor is None:
            data_visitor = visitors.NumberVisitor(output_mngr)
        super().__init__(output_mngr, *args, data_visitor=data_visitor, **kwargs)

    def length(self, x):
        return math.ceil(math.log(x, 2))

    def get_item(self, x, i):
        # Return the i'th bit of x
        return int(bool(x & (2**i)))
