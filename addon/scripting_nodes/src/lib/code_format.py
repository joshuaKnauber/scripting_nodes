import ast
import string

from .python_format import remove_redundant_parens


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


def literal_set(items) -> str:
    """Python source of a set of strings with a stable order."""
    items = sorted(items)
    if not items:
        return "set()"
    return "{" + ", ".join(repr(item) for item in items) + "}"


def f_string(template: str, values: list[str]) -> str | None:
    """`template.format(*values)` as an f-string, None if it can't be one
    (named or numbered fields, nested specs, values that don't fit in one)."""
    parts = []
    index = 0
    try:
        parsed = list(string.Formatter().parse(template))
    except ValueError:
        return None
    for literal, field, spec, conversion in parsed:
        if any(ord(char) < 32 and char not in "\n\t" for char in literal):
            return None
        literal = (
            literal.replace("\\", "\\\\").replace("\n", "\\n").replace("\t", "\\t")
        )
        parts.append(literal.replace("{", "{{").replace("}", "}}"))
        if field is None:
            continue
        if field != "" or index >= len(values) or "{" in (spec or ""):
            return None
        value = remove_redundant_parens(values[index].strip())
        index += 1
        if "\\" in value or "\n" in value:
            return None
        if (
            value.startswith("{")
            or value.startswith("lambda")
            or ":" in _top_level(value)
        ):
            value = f"({value})"
        conversion = f"!{conversion}" if conversion else ""
        spec = f":{spec}" if spec else ""
        parts.append("{" + value + conversion + spec + "}")
    if index != len(values):
        return None
    body = "".join(parts)
    for quote in ('"', "'"):
        if quote not in body:
            code = f"f{quote}{body}{quote}"
            try:
                ast.parse(code, mode="eval")
            except SyntaxError:
                return None
            return code
    return None


def _top_level(expr: str) -> str:
    """`expr` without what's inside brackets and strings."""
    out, depth, quote = [], 0, None
    for char in expr:
        if quote:
            if char == quote:
                quote = None
            continue
        if char in "'\"":
            quote = char
        elif char in "([{":
            depth += 1
        elif char in ")]}":
            depth -= 1
        elif depth == 0:
            out.append(char)
    return "".join(out)


def sort_imports(imports) -> list[str]:
    """Like isort: standard library, then bpy (third party), then the add-on's
    own modules, a blank line between the groups; one `from` per module."""
    merged, plain = {}, set()
    for line in imports:
        parts = line.split(" import ", 1)
        if line.startswith("from ") and " as " not in line:
            merged.setdefault(parts[0], set()).update(
                name.strip() for name in parts[1].split(",")
            )
        else:
            plain.add(line)
    imports = plain | {
        f"{head} import {', '.join(sorted(names, key=_name_key))}"
        for head, names in merged.items()
    }
    groups = [[], [], []]
    for line in imports:
        module = line.split()[1]
        if module.startswith("."):
            groups[2].append(line)
        elif module.split(".")[0] in ("bpy", "bmesh", "mathutils", "gpu", "blf"):
            groups[1].append(line)
        else:
            groups[0].append(line)
    result = []
    for group in groups:
        if group:
            if result:
                result.append("")
            result += sorted(group, key=_import_key)
    return result


def _name_key(name):
    """isort's order by type: CONSTANTS, Classes, functions."""
    if name.isupper() and len(name) > 1:
        return (0, name)
    return (1 if name[0].isupper() else 2, name)


def _import_key(line):
    """`import x` before `from x import y` (isort's force-sort-within-sections
    off), then by module."""
    parts = line.split()
    return (parts[0] == "from", parts[1].lstrip(".").lower(), line)
