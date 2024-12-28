def normalize_indents(code):
    lines = code.split("\n")
    lines = [*filter(lambda l: l.strip(), lines)]
    min_indent = 0
    for line in lines:
        stripped = line.lstrip()
        if stripped:
            indent = len(line) - len(stripped)
            min_indent = min(min_indent, indent) if min_indent else indent
    return "\n".join(line[min_indent:] for line in lines)


def indent(code, level=1):
    lines = code.split("\n")
    if len(lines) == 1:
        return code
    return "\n".join(" " * 4 * level + line for line in lines)
