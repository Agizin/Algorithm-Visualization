def parse(f):
    contents = []
    while line = f.readline():
        line = line[:-1]
        stuff = line.split(maxsplit=2);
        if stuff[0] == "@algviz":
            if stuff[1] == "begin":
                stuff = stuff[2].split(maxsplit=1)
                contents.append({'command': stuff[0],
                                 'arguments': stuff[1],
                                 'contents': parse(f)})
            elif stuff[1] == "end":
                break
            else:
                contents.append({'command': stuff[1],
                                 'arguments': stuff[2]})
        else:
            contents.append(line)
    return contents
        
