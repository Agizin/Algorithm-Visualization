import contextlib
import json
import sys
from algviz.parser import json_objects

class OutputStateError(Exception):
    """For output operations that don't make sense given the state of the output"""

class _OutputContext:
    """Don't work with this class directly.  Prefer to use OutputManager."""
    def __init__(self, parent=None, outfile=sys.stdout):
        self.parent = parent
        self.indent = 2 if parent is None else parent.indent + 2
        self.comma_needed = False
        self.outfile = outfile
        self.closed = False
        self.cur_child = None

    def write(self, text):
        # if '\n' in text:
        #     print("newline in next line: {!r}".format(text), file=sys.stderr)
        print(text, end="", file=self.outfile)

    def begin(self):
        self.write(self.open_char)

    def end(self):
        if self.parent is not None:
            assert not self.parent.closed, "parent block ended before this one did"
        self.end_child()
        if self.comma_needed:  # we're closing a non-empty empty dict/list, so put a newline
            if self.parent is not None:
                self.parent.do_indent()
            else:
                self.write("\n")
        self.write(self.close_char)
        self.closed = True

    def end_child(self):
        """If there is a child block (a list or dict), make sure it is
        closed before printing anything else at this level.
        """
        if self.cur_child is not None and not self.cur_child.closed:
            self.cur_child.end()
            self.cur_child  = None

    def do_indent(self):
        self.write("\n" + (" " * self.indent))

    def comma_newline(self):
        self.end_child()
        if self.comma_needed:
            # First item in list/dict doesn't need a comma before it
            self.write(",")
        else:
            self.comma_needed = True
        # Indentation is nice
        self.do_indent()

    def write_literal(self, lit):
        """Write a str or int.  Could also do list or dict, I suppose."""
        self.write(json.dumps(lit).strip("\n"))

    def push_child(self, child_cls):
        if self.cur_child is not None:
            assert self.cur_child.closed, "began child block without ending previous child"
        self.cur_child = child_cls(parent=self, outfile=self.outfile)
        self.cur_child.begin()


class _DictOutputContext(_OutputContext):
    open_char = "{"
    close_char = "}"
    def __init__(self, *args, **kwargs):
        self.keys_used = set()
        super().__init__(*args, **kwargs)

    def key_val(self, key, val):
        if key in self.keys_used:
            raise OutputStateError("Key {!r} is a duplicate in this mapping"
                                   .format(key))
        self.keys_used.add(key)
        self.comma_newline()
        self.write_literal(key)
        self.write(": ")
        self.write_literal(val)

    def key_push(self, key, *args, **kwargs):
        self.comma_newline()
        self.write_literal(key)
        self.write(": ")
        self.push_child(*args, **kwargs)

class _ListOutputContext(_OutputContext):
    open_char = "["
    close_char = "]"
    def item(self, val):
        """Add a literal to the list"""
        self.comma_newline()
        self.write_literal(val)

    def item_push(self, *args, **kwargs):
        """Open a dict or list within this list"""
        self.comma_newline()
        self.push_child(*args, **kwargs)


class OutputManager:
    """Useful for outputting valid JSON without maintaining too much state."""

    def __init__(self, outfile=sys.stdout):
        # self._in_dict = False
        # self._in_list = True
        self.outfile = outfile
        self.snapshot_ctx = _ListOutputContext(parent=None, outfile=outfile)
        self.context = self.snapshot_ctx
        self.context.begin()
        self.uids = set()
        self._next_key = None
    # The idea is that the user calls next_item repeatedly if in an array context,
    # or alternates calls to next_key and next_item if in a dict context.
    def next_key(self, key):
        if not isinstance(key, str):
            raise TypeError("JSON keys must be strings, not {}".format(key))
        if self._next_key is not None:
            raise OutputStateError("previous key ({}) not used when new key ({}) added"
                                   .format(self._next_key, key))
        elif not isinstance(self.context, _DictOutputContext):
            raise OutputStateError("cannot set a key ({}) in non-mapping context {}"
                                   .format(key, self.context))
        else:
            self._next_key = key

    def _use_key(self):
        if self._next_key is None:
            raise OutputStateError("Must set a key with `next_key` before adding a key-value pair")
        result = self._next_key
        self._next_key = None
        return result

    def next_val(self, val):
        """Use this to append a literal (or JSON-encodable) value as the next
        item in the current context.
        """
        if isinstance(self.context, _DictOutputContext):
            # sneakily keep track of uids
            if (self._next_key == json_objects.Tokens.UID
                    or json_objects.aliases.get(self._next_key) == json_objects.Tokens.UID):
                if val in self.uids:
                    raise OutputStateError("uid {} is already defined in this snapshot"
                                           .format(val))
                else:
                    self.uids.add(val)
            self.context.key_val(self._use_key(), val)
        else:
            self.context.item(val)

    def _push(self, *args, **kwargs):
        if isinstance(self.context, _DictOutputContext):
            self.context.key_push(self._use_key(), *args, **kwargs)
        else:
            self.context.item_push(*args, **kwargs)
        self.context = self.context.cur_child

    @contextlib.contextmanager
    def push(self, mapping=True):
        """Use this to append a sub-context as the next item in the current
        context.  (The sub-context is for a dictionary by default.)

        After calling `push`, the `OutputManager.context` field will hold the
        new child context.

        When you're done with that context, you should call `pop` to cleanly
        end the context that you pushed and to restore the
        `OutputManager.context` field to its original value.
        """
        if mapping:
            self._push(_DictOutputContext)
        else:
            self._push(_ListOutputContext)
        try:
            yield
        finally:
            self.context.end()
            self.context = self.context.parent

    def start_snapshot(self):
        """Write a snapshot.  Use as a context manager"""
        # if self.context is not self.snapshot_ctx:
        #     self.snapshot_ctx.cur_child.
        self.context = self.snapshot_ctx
        return self.push(mapping=False)

    def end(self):
        self.snapshot_ctx.end()
        self.outfile.flush()
        # print("", file=self.outfile)

    def current_snapshot(self):
        return self.snapshot_ctx.cur_child
