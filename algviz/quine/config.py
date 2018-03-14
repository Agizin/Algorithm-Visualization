
import json
from collections import OrderedDict

def decode_json_ordereddict(string):
    return json.JSONDecoder(object_pairs_hook=OrderedDict).decode(string)



# class Args:
#     picture_dir = "picturedir"
#     tangle_dir = "tangledir"

# def dir_arguments():
#     for obj

_ALL_ARGUMENTS = set()

def parse_args(arg_string, TODO in progress

class _ArgumentModuleHelper(type):
    """This is just so we can list all the arguments defined in this module"""
    def __init__(self, name, bases, namespace):
        super().__init__(name, bases, namespace)
        if not name.startswith("_"):
            _ALL_ARGUMENTS.add(self)

class _LegalMacroArgument(metaclass=_ArgumentModuleHelper):

    def __init__(self, value):
        self.value = value
        try:
            if not self.validate(value):
                # it's encouraged for self.validate to raise a more specific error
                raise errors.MacroArgumentValueError(
                    "{} is not a legal value for {}".format(self.value, self.key))
        except errors.MacroUsageUserError as err:
            if hasattr(self, "usage"):
                err.usage = self.usage
            raise

class _StringMacroArgument(_LegalMacroArgument):
    def validate(self, value):
        return isinstance(value, str)

class _IntMacroArgument(_LegalMacroArgument):
    def validate(self, value):
        try:
            self.value = int(value)
        except ValueError as err:
            raise errors.MacroArgumentValueError(
                "Illegal value {} for integer key {}: {!s}".format(
                    value, self.key, err))


class _EnumStringArgument(_LegalMacroArgument):
    @property
    def usage(self):
        return "valid options for {}: {}".format(self.key, self.options)

    def validate(self, value):
        return value in self.options

class _BoolMacroArgument(_EnumMacroArgument):
    _true_options = ("true", "True", "TRUE", "t")
    _false_options = ("false", "False", "FALSE", "f")
    options = _true_options + _false_options
    def __init__(self, value):
        super().__init__(value)
        self.value = value in self._true_options

class Newline(_EnumStringArgument):
    """Where to put a newline"""
    key = "newline"
    ABOVE = "above"
    BELOW = "below"
    BOTH = "both"
    NEITHER = "none"
    options = (ABOVE, BELOW, BOTH, NEITHER)

class PictureDir(_StringMacroArgument):
    key = "picturedir"
    usage = "Name of directory where SVG files should be written"

class TangleDir(_StringMacroArgument):
    key = "tangledir"
    usage = "Name of directory where code should be written when tangling"

class Interpreter(_StringMacroArgument):
    """An interpreter for the given code.  This is responsible for all
    compilation and linking if necessary.  For most supported languages, the
    default should be sufficient.
    """
    key = "interpreter"
    usage = "Path to a script that can run the given code."

class Language(_StringMacroArgument):
    """Programming language for a code block.

    For supported languages, this is used to expand language-specific macros,
    if any, and to select an interpreter automatically if an interpreter isn't
    specified (see `{}`).
    """.format(Interpreter.key)
    key = "lang"
    usage = """Programming language for a code block."""

class Name(_StringMacroArgument):
    """A name for either a code-block or a config-block"""
    key = "name"
    usage = "See the docs... at the time of writing, any string should work"

class EagerRun(_BoolMacroArgument):
    """If True, the code block will be run even if the output is not needed"""
    key = "eager_run"

class Parent(_StringMacroArgument):
    """The `{}` of the parent code block.

    When a block is tangled, its parent and ancestors are prepended to it in
    the order that makes sense.  Note that it often makes more sense to use the
    include/import/use mechanism provided by your language.

    Language is inherited from the parent.
    """.format(Name.key)
    key = "parent"
    usage = "Name (`{}`) of a parent code block.  See the docs.".format(Name.key)

"""
This is our contract.
# Global-ish options for algviz
picturedir=str

# Options for all macros that have replacement text
## Not legal to set from config:
newline=["both", "after", "before", "none"]

# Options for code blocks

tangledir=str
lang=str
interpreter=str or null
eager_run=bool
## Not legal to set from config:
name
parent

# Options for Python3 macros:
## Not legal to set from config:
api=str
var=str
indent=int
"""
