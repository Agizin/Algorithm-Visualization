from . import document

import logging
logger = logging.getLogger(__name__)

@document._register_macro
class CodeChunk(document.MacroChunk):
    macro_name = "code"
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = self.keyword["name"]
        doc_names = kwargs["doc_names"]
        if self.name in doc_names.code_blocks:
            raise document.NameAlreadyDefinedError(self.name)
        if "parent" in self.keyword:
            self.parent_name = self.keyword["parent"]
            try:
                self.parent = doc_names.code_blocks[self.parent_name]
            except KeyError:
                # TODO: Allow parent to be defined after child, but use union-
                # find to check for cycles
                raise document.NameUndefinedError(
                    "Could not find {code_macro} block named {parent_name} "
                    "(parent of {code_macro} block {name})"
                    .format(code_macro=self.macro_name,
                            parent_name=self.parent_name,
                            name=self.name))
        else:
            self.parent = None
        doc_names.code_blocks[self.name] = self
        self.language = (self.parent.lang if self.parent
                         else self.keyword.get("lang", None))
        self._tangled_content = None

    def cat_to_file(self):
        if not self.filename:
            raise document.AlgVizBug("cat_to_file called on {}, which has no filename."
                            .format(self.name))
        with open(self.filename, "w") as f:
            print("\n".join(self.cat_list()), file=f)

    def cat_list(self):
        content = [] if self.parent is None else self.parent.cat_list()
        content.append(self.tangle_content())
        return content

    def tangle_content(self, lang=None, **kwargs):
        # We only get the `lang` keyword if this code block is embedded inside
        # another code block.  I can think of few cases where somebody would
        # that, and even fewer where the languages don't match.  But I'd be
        # flattered if somebody made a multi-language quine with AlgViz
        # pictures, so let's make it possible.
        if lang is not None and lang != self.language:
            logger.warn("You have a code block ({my_name}) of language "
                        "{my_lang} inside a code block of language {lang}."
                        " We'll consider the inner code block to have "
                        "language {my_lang} when tangling it.".format(
                            my_name=self.name,
                            my_lang=self.language,
                            lang=lang))
        return super().tangle_content(lang=self.language, **kwargs)


def add_handler_dict(cls):
    # TODO consider using a metaclass for this.  (Refactor this and
    # parser.json_objects.Dispatcher)
    cls.lang_handlers = {}
    def handle_lang(cls, lang):
        def decorate(fn):
            cls.lang_handlers[lang] = fn
            return fn
        return decorate
    cls.handle_lang = classmethod(handle_lang)
    return cls

class LanguageSpecificMacro(document.NoBodyMacro):

    def tangle_content(self, lang=None, **kwargs):
        if lang not in self.lang_handlers:
            raise document.NotSupportedError(
                "Macros are not supported for language {}".format(lang))
        return lang_handlers[lang](self.positional, self.keyword)


@document._register_macro
@add_handler_dict
class SnapshotMacro(LanguageSpecificMacro):
    macro_name = "snapshot"

@document._register_macro
@add_handler_dict
class HeaderMacro(LanguageSpecificMacro):
    macro_name = "header"

# @document._register_macro
# @add_handler_dict
# class SnapshotMacro(document.NoBodyMacro):
#     macro_name = "snapshot"

#     def tangle_content(self, lang=None, **kwargs):
#         if lang not in self.lang_handlers:
#             raise document.NotSupportedError(
#                 "Macros are not supported for language {}".format(lang))
#         return lang_handlers[lang](self.positional, self.keyword)

#     @classmethod
#     def handle_lang(cls, lang):
#         def decorate(fn):
#             cls.lang_handlers[lang] = fn
#             return fn
#         return decorate

# @document._register_macro
# @add_handler_dict
# class HeaderMacro(document.NoBodyMacro):

    

@SnapshotMacro.handle_lang("python3")
def python3_snapshot(positional, keyword):
    parameters = [positional[0]]
    if "api" in keyword:
        parameters.append("api=" + keyword["api"])
    if "var" in keyword:
        parameters.append("var=" + repr(keyword["var"]))
    return "{indent}algviz.high_level.show({param})".format(
        indent=" " * int(keyword.get("indent", 0)),
        param=", ".join(parameters))

