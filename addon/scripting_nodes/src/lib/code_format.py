import ast


def _trim_blank_edges(lines):
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return lines


def normalize_indents(code):
    """Remove the common indentation. Leading/trailing blank lines are dropped,
    blank lines in between are kept (they may be part of a string)."""
    lines = _trim_blank_edges(code.split("\n"))
    indents = [len(line) - len(line.lstrip()) for line in lines if line.strip()]
    if not indents:
        return ""
    cut = min(indents)
    return "\n".join(line[cut:] if line.strip() else "" for line in lines)


def indent(code, level=1, keep_first=True):
    """Indent every line by `level` * 4 spaces (except the first one if
    `keep_first`, which is meant to sit right where the placeholder is)."""
    lines = _trim_blank_edges(code.split("\n"))
    if not lines:
        return ""
    prefix = "    " * level
    out = [lines[0] if keep_first else prefix + lines[0]]
    out += [prefix + line if line.strip() else "" for line in lines[1:]]
    return "\n".join(out)


_ATOMIC = (
    ast.Name,
    ast.Constant,
    ast.Call,
    ast.Attribute,
    ast.Subscript,
    ast.List,
    ast.Dict,
    ast.Set,
    ast.ListComp,
    ast.DictComp,
    ast.SetComp,
    ast.GeneratorExp,
)


def is_atomic(expr: str) -> bool:
    """True if `expr` can be embedded in a bigger expression without parens."""
    try:
        node = ast.parse(expr.strip(), mode="eval").body
    except SyntaxError:
        return False
    if isinstance(node, ast.Tuple):
        # only parenthesized tuples are atomic: "(1, 2)" yes, "1, 2" no
        return expr.strip().startswith("(") and expr.strip().endswith(")")
    return isinstance(node, _ATOMIC)


def parenthesize(expr: str) -> str:
    """Wrap `expr` in parentheses unless it is atomic (keeps precedence intact)."""
    if not expr.strip() or is_atomic(expr):
        return expr
    return f"({expr})"


def is_simple(expr: str) -> bool:
    """True for names, constants and attribute chains - cheap and free of side
    effects, so they can be repeated in generated code."""
    try:
        node = ast.parse(expr.strip(), mode="eval").body
    except SyntaxError:
        return False
    while isinstance(node, ast.Attribute):
        node = node.value
    return isinstance(node, (ast.Name, ast.Constant))


def flatten_multiline_strings(code: str) -> str:
    """Rewrite string literals spanning several lines as single-line literals
    with the same value, so the code can be re-indented safely (indenting the
    continuation lines of a multi-line string would change its value)."""
    import io
    import tokenize

    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(code).readline))
    except (tokenize.TokenError, SyntaxError):
        return code
    lines = code.split("\n")
    # replace from the end so earlier positions stay valid
    for tok in reversed(tokens):
        if tok.type != tokenize.STRING or tok.start[0] == tok.end[0]:
            continue
        try:
            value = ast.literal_eval(tok.string)
        except (ValueError, SyntaxError):
            continue  # e.g. f-strings, leave as is
        (srow, scol), (erow, ecol) = tok.start, tok.end
        before = lines[srow - 1][:scol]
        after = lines[erow - 1][ecol:]
        lines[srow - 1 : erow] = [before + repr(value) + after]
    return "\n".join(lines)
