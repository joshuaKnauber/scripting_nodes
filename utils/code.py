def normalize_indents(code: str) -> str:
    """ Reduces the code block to the minimum number of indents the lines have """
    lines = code.split("\n")
    indents = [len(line) - len(line.lstrip()) for line in lines if line.strip()]
    min_indent = min(indents) if indents else 0
    return "\n".join([line[min_indent:] for line in lines])
