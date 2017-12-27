import sys

from . import output, visitors

__output_manager = None

def do_setup():
    global __output_manager
    if __output_manager is None:
        __output_manager = output.OutputManager(sys.stdout)

def show(obj, var=None, api=None, metadata=None):
    global __output_manager
    do_setup()
    if api is None:
        api = visitors.DispatchVisitor
    visitor = api(__output_manager)
    with __output_manager.start_snapshot():
        visitor.traverse(obj, var=var, metadata=metadata)
