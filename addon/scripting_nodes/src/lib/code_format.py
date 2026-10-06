def normalize_indents(code):
    lines = code.split("\n")
    lines = [*filter(lambda l: l.strip(), lines)]
    min_indent = None
    for line in lines:
        stripped = line.lstrip()
        if stripped:
            indent = len(line) - len(stripped)
            min_indent = min(min_indent, indent) if min_indent is not None else indent
    if min_indent is None:
        min_indent = 0
    return "\n".join(line[min_indent:] for line in lines)


def indent(code, level=1, keep_first=True):
    lines = code.split("\n")
    lines = [*filter(lambda l: l.strip(), lines)]
    indent = "    " * level
    if not lines:
        return ""
    if keep_first:
        return "\n".join([lines[0]] + [indent + line for line in lines[1:]])
    return "\n".join([indent + line for line in lines])
