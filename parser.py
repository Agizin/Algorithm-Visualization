def parse(file):
    contents = []
    line = file.readline()
    while line:
        line = line[:-1]
        stuff = line.split(maxsplit=2);
        if line.startswith("@algviz"):
            if stuff[1] == "begin":
                stuff = stuff[2].split(maxsplit=1)
                contents.append({'command': stuff[0],
                                 'arguments': stuff[1],
                                 'contents': parse(file)})
            elif stuff[1] == "end":
                break
            else:
                contents.append({'command': stuff[1],
                                 'arguments': stuff[2]})
        else:
            contents.append(line)
        line = file.readline()
    return contents
        
