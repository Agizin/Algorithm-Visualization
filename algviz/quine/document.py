from collections import OrderedDict, namedtuple
import logging

from . import errors, parser

logger = logging.getLogger(__name__)

Environment = namedtuple("Environment", ("code_blocks", "config_blocks"))

class DocumentChunk:

    def __init__(self, *components, **kwargs):
        self.components = components
        self._tangled_content = None

    def _call_on_components(self, methodname):
        for cpt in self.components:
            if isinstance(cpt, DocumentChunk):
                yield getattr(cpt, methodname)()
            else:
                yield cpt

    def quine(self):
        return "\n".join(self._call_on_components("quine"))
    # cpt.quine() if isinstance(cpt, DocumentChunk) else cpt
    # for cpt in self.components)

    def gussy(self):
        # Sort of like "weave" from Knuth's WEB language.
        # Most macros will override this
        return "\n".join(gus for gus in self._call_on_components("gussy")
                         if gus is not None)

    newline_before_okay = True
    newline_after_okay = True

    def tangle_content(self, **kwargs):
        # this gets called multiple times, so it will pay to save the intermediate work
        if self._tangled_content is None:
            def _tangled_components():
                for cpt in self.components:
                    if isinstance(cpt, str):
                        yield cpt
                    elif isinstance(cpt, DocumentChunk):
                        tngl = cpt.tangle_content()
                        if tngl is not None:
                            yield tngl
                    else:
                        raise Exception("Unexpected component: {}".format(cpt))

            self._tangled_content = "\n".join(_tangled_components())
        return self._tangled_content

# This is an unfortunate hack.
# _consume_next_newline = "@algviz consume-newline forward\n"
# _consume_prev_newline = "\n@algviz consume-newline backward"

class TextChunk(DocumentChunk):
    pass

OutputLine = namedtuple("OutputLine", ("text", "newline_after_okay", "newline_before_okay"))

def join_respecting_newlines(chunks):
    # just a prototype so I remember what newline_before_okay and
    # newline_after_okay were for.
    if not chunks:
        return ""
    text = []
    for cur, nxt in zip(chunks, chunks[1:]):
        text.append(cur.text)
        if cur.newline_after_okay and nxt.newline_before_okay:
            text.append("\n")
    text.append(chunks[-1].text)
    return "".join(text)

_name_to_macro = {}
def _register_macro(cls):
    if cls.macro_name in _name_to_macro:
        raise Exception("Two macros have been assigned the name {}"
                        .format(cls.macro_name))
    _name_to_macro[cls.macro_name] = cls
    return cls

class MacroChunk(DocumentChunk):

    keyword_delim = "="  # separates keyword from value

    @classmethod
    def split_args(cls, arg_str):
        args = arg_str.split()
        positional = []
        keyword = OrderedDict()  # so quine() will put them in the same order
        for arg in args:
            if cls.keyword_delim in arg:
                key, val = arg.split(cls.keyword_delim, maxsplit=1)
                if key in keyword:
                    raise errors.MacroSyntaxError(
                        "Key-value argument {} given twice!".format(key))
                keyword[key] = val
            else:
                if keyword:
                    raise Exception("Positional argument {} should precede keyword arguments"
                                    .format(arg))
                positional.append(arg)
        return positional, keyword

    def format_args(self):
        return " ".join(self.positional +
                        [self.keyword_delim.join((key, val))
                         for key, val in self.keyword.items()])

    def __init__(self, *args, command=None, arguments="", **kwargs):
        super().__init__(*args, **kwargs)
        self.command = command
        self.positional, self.keyword = self.split_args(arguments)

        self.set_newline_mode()

    def set_newline_mode(self):
        both, after, before, none = "both", "after", "before", "none"
        newline_spec = self.keyword.get("newline", none).lower()
        if newline_spec not in [both, after, before, none]:
            raise errors.MacroSyntaxError(
                "Value {} for key `newline` is not one of {}"
                .format(newline_spec, [both, after, before, none]))
        self.newline_before_okay = newline_spec in [before, both]
        self.newline_after_okay = newline_spec in [after, both]

    def quine(self):
        body = super().quine()
        if body:
            skel = ("@algviz begin {command}{args}\n"
                    "{body}\n"
                    "@algviz end {command}")
        else:
            skel = "@algviz {command}{args}"
        args = self.format_args()
        if args:
            args = " " + args
        return skel.format(command=self.command, args=args, body=body)


class NoBodyMacro(MacroChunk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.components:
            raise errors.MacroSyntaxError(
                "Macro {} may only appear in one-line form".format(
                    self.macro_name))

@_register_macro
class VerbatimMacro(NoBodyMacro):
    """This is like an escape-sequence"""
    macro_name = "verbatim"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.arg_string = kwargs.get("arguments", "")

    def gussy(self):
        return self.arg_string

@_register_macro
class HiddenChunk(MacroChunk):
    macro_name = "hidden"
    def gussy(self):
        return None

DocumentNamespace = namedtuple("DocumentNamespace",
                               ("code_blocks",
                                "config_blocks",
                               ))


class FullDocument(DocumentChunk):

    @classmethod
    def from_parsed_text(cls, raw_parsed):
        doc_names = DocumentNamespace({}, {})
        return cls(*cls.parsed_text_to_macros(raw_parsed, doc_names=doc_names),
                   doc_names=doc_names)

    @classmethod
    def parsed_text_to_macros(cls, raw_parsed, doc_names=None):
        if doc_names is None:
            doc_names = DocumentNamespace({}, {})
        results = []
        for elem in raw_parsed:
            if isinstance(elem, str):
                assert not elem.endswith("\n")
                results.append(elem)
            else:
                assert isinstance(elem, parser.RawMacro)
                macro_cls = _name_to_macro.get(elem.command)
                if macro_cls is None:
                    raise errors.NotSupportedError(
                        "`{}` is not the name of any macro".format(elem.command))
                if elem.contents is None:
                    contents = []
                else:
                    contents = cls.parsed_text_to_macros(elem.contents,
                                                     doc_names=doc_names)
                results.append(macro_cls(*contents,
                                         arguments=elem.arguments,
                                         command=elem.command,
                                         doc_names=doc_names))
        return results
