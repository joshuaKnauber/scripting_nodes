def minimize_indents(code: str) -> str:
    """Reduces the code block to the minimum number of indents the lines have"""
    lines = code.split("\n")
    indents = [len(line) - len(line.lstrip()) for line in lines if line.strip()]
    min_indent = min(indents) if indents else 0
    return "\n".join([line[min_indent:] for line in lines])


def indent_code(code: str, indents: int, skip_first_line: bool = True) -> str:
    """Indents the code by the given number of indents"""
    lines = code.split("\n")
    for i in range(0, len(lines)):
        if skip_first_line and i == 0:
            continue
        lines[i] = " " * 4 * indents + lines[i]
    return "\n".join(lines)
