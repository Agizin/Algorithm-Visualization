class AlgVizSyntaxError(Exception):
    """Errors raised by the parser, e.g. unmatched `begin`"""
    pass

class MacroSyntaxError(Exception):
    pass

class MacroUsageUserError(Exception):
    """Errors caused by improper usage of macros"""
    def __init__(self, *args, **kwargs):
        self.usage = None
        super().__init__(*args, **kwargs)
    def __str__(self):
        result = super().__str__(self)
        if self.usage is not None:
            usage = self.usage
        else:
            usage = "See the documentation"
        return "{}\n{}".format(result, usage)


class MacroNameUserError(MacroUsageUserError):
    """Errors related to macro names (i.e. the `name` parameter for some macros)"""
    pass

class NameUndefinedError(MacroNameUserError):
    # E.g. parent=foo but no macro with name=foo
    pass

class NameAlreadyDefinedError(MacroNameUserError):
    pass

class MacroArgumentError(MacroUsageUserError):
    pass

class UnrecognizedMacroKeywordArgumentError(MacroArgumentError):
    """A macro received an unrecognized keyword argument, e.g. `asdf=3`"""
    pass

class MandatoryArgumentMissingError(MacroArgumentError):
    pass

class MacroArgumentValueError(MacroArgumentError):
    """A macro argument has an illegal value"""
    pass

class NotSupportedError(Exception):
    pass

class AlgVizBug(Exception):
    pass  # for exceptions that indicate bugs in our code
