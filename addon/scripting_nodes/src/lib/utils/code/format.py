def normalize_indents(code):
    lines = code.split("\n")
    min_indent = 0
    for line in lines:
        stripped = line.lstrip()
        if stripped:
            indent = len(line) - len(stripped)
            min_indent = min(min_indent, indent) if min_indent else indent
    return "\n".join(line[min_indent:] for line in lines)
