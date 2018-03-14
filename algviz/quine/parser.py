from collections import namedtuple, deque
from . import errors

FileLine = namedtuple("FileLine", ("text", "line_number"))

class LineQueue(deque):
    def __init__(self, file):
        super().__init__(FileLine(line.strip("\n"), i)
                         for i, line in enumerate(file.read().split("\n")))

    def next_line(self):
        return self.popleft()

RawMacro = namedtuple("RawMacro", ("command", "arguments", "contents"))

def parse(file):
    return parse_queue(LineQueue(file))

# _algviz_line = re.compile("@algviz\s+(\S.*)")
# def match_algviz_command(line):
#     return _algviz_line.match(line)

def parse_queue(lines, blockname=None, begin_line=None):
    contents = []
    while lines:
        line, line_num = lines.next_line()
        if line.startswith("@algviz"):
            stuff = line.split(maxsplit=2)
            if stuff[1] == "begin":
                if len(stuff) == 2:
                    raise errors.AlgVizSyntaxError(
                        "`@algviz begin` should be followed by a command name"
                        " at line {}".format(line_num))
                stuff = stuff[2].split(maxsplit=1)
                cmd = stuff[0]
                args = stuff[1] if len(stuff) > 1 else ""
                contents.append(RawMacro(
                    command=cmd,
                    arguments=args,
                    contents=parse_queue(lines, blockname=cmd, begin_line=line_num)))
            elif stuff[1] == "end":
                if blockname is None:
                    raise errors.AlgVizSyntaxError(
                        "`{}` on line {} does not end anything"
                        .format(line, line_num))
                elif blockname is not None and len(stuff) > 2:
                    [endname, *_] = stuff[2].split(maxsplit=1)
                    if endname != blockname:
                        raise errors.AlgVizSyntaxError(
                            "`begin {}` ended with `end {}` at line {}".format(
                                blockname, endname, line_num))
                return contents
            else:
                contents.append(RawMacro(command=stuff[1],
                                         arguments=stuff[2] if len(stuff) > 2 else "",
                                         contents=None))
        else:
            contents.append(line)
    if blockname is not None:
        raise errors.AlgVizSyntaxError(
            "Unmatched `begin {}` on line {} (end-of-file reached)"
            .format(blockname, begin_line))
    return contents
