import sys
# import tempfile
import io

from . import output, visitors

__output_manager = None

def do_setup():
    global __output_manager
    if __output_manager is None:
        __output_manager = output.OutputManager(sys.stdout)

def _reset():
    # This is just for test cases that replace sys.stdout
    global __output_manager
    __output_manager = None

def show(obj, var=None, api=None, metadata=None, _out=None):
    if _out is None:
        do_setup()
        _out = __output_manager
    if api is None:
        api = visitors.DispatchVisitor
    visitor = api(_out)
    with _out.start_snapshot():
        visitor.traverse(obj, var=var, metadata=metadata)

def string_snapshot(*args, **kwargs):
    with io.StringIO() as f:
        out = output.OutputManager(f)
        show(*args, _out=out, **kwargs)
        return f.getvalue()
