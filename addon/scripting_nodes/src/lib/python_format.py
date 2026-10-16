"""Formats Python source the way `ruff format` does (88 columns, double
quotes, magic trailing commas), for the code of exported add-ons.

    format_source(source) -> str

Covers what generated code contains: statements on logical lines are kept
as written and only re-wrapped. A line that is too long is split at its last
bracket (`call(` ... `)`), the contents of a split bracket go on one line or
one item per line, and expressions without brackets of their own are wrapped
in parentheses and split at their operators. Lines with comments inside
brackets are left alone. Pure Python, no Blender.
"""

import ast
import io
import keyword
import tokenize

LINE_LENGTH = 88
INDENT = "    "
OPENING = {"(": ")", "[": "]", "{": "}"}
CLOSING = {")", "]", "}"}

# split priorities (higher splits first), like black's
COMMA = 18
TERNARY = 16
LOGIC = 14
STRING = 12
COMPARE = 10
DOT = 1
COMPREHENSION = 20
OPERATORS = {
    "|": 9,
    "^": 8,
    "&": 7,
    "<<": 6,
    ">>": 6,
    "+": 5,
    "-": 5,
    "*": 4,
    "/": 4,
    "//": 4,
    "%": 4,
    "@": 4,
    "**": 1,
}
COMPARATORS = {"<", ">", "==", "!=", "<=", ">=", "in", "not", "is"}
AUGMENTED = {
    "+=",
    "-=",
    "*=",
    "/=",
    "//=",
    "%=",
    "**=",
    "@=",
    "|=",
    "&=",
    "^=",
    ">>=",
    "<<=",
}
# statements whose expression ruff puts in parentheses when it's split
CLAUSES = {"return", "if", "elif", "while", "del", "assert", "raise"}


class Leaf:
    __slots__ = ("text", "kind", "space")

    def __init__(self, text, kind, space):
        self.text = text
        self.kind = kind  # "name", "number", "string", "op"
        # whitespace before it in the source, None at the start of a line
        self.space = space

    def __repr__(self):
        return f"Leaf({self.text!r})"


def format_source(source: str, line_length: int = LINE_LENGTH) -> str:
    try:
        lines = _Formatter(source, line_length).run()
    except (tokenize.TokenError, SyntaxError, IndentationError):
        return source
    text = "\n".join(lines).rstrip("\n")
    if not text:
        return "\n" if source.strip("\n ") == "" and source else ""
    return text + "\n"


# -- strings --------------------------------------------------------------------


def normalize_string(text: str) -> str:
    """Double quotes unless that needs more escapes than single ones."""
    prefix = ""
    while text and text[0] not in "'\"":
        prefix, text = prefix + text[0], text[1:]
    if text.startswith("'''"):
        body = text[3:-3]
        if '"' in body or body.endswith("\\"):
            return prefix + text
        return f'{prefix}"""{body}"""'
    if text.startswith('"""'):
        return prefix + text
    quote, body = text[0], text[1:-1]
    kind = prefix.lower()
    if "r" in kind or "f" in kind or "t" in kind:
        # escapes mean something else (raw) or the expressions may use quotes
        if quote == "'" and '"' not in body and "\\'" not in body:
            return f'{prefix}"{body}"'
        return prefix + text
    # characters and escape sequences of the body, escaped quotes as quotes
    pieces, i = [], 0
    while i < len(body):
        if body[i] == "\\" and i + 1 < len(body):
            pair = body[i : i + 2]
            pieces.append(pair[1] if pair in ("\\'", '\\"') else pair)
            i += 2
        else:
            pieces.append(body[i])
            i += 1
    doubles, singles = pieces.count('"'), pieces.count("'")
    new = '"' if doubles <= singles else "'"
    out = "".join("\\" + p if p == new else p for p in pieces)
    return f"{prefix}{new}{out}{new}"


# -- reading ----------------------------------------------------------------------


class _Logical:
    """One statement: its leaves, indentation and trailing comment."""

    def __init__(self, indent, leaves, comment, verbatim):
        self.indent = indent
        self.leaves = leaves
        self.comment = comment
        self.verbatim = verbatim  # source lines, kept as they are

    @property
    def first(self):
        return self.leaves[0].text if self.leaves else ""


def _read(source):
    """Logical lines, comment lines ("#...", indent) and blank lines (None)."""
    lines = source.splitlines(keepends=True)
    tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
    items = []
    leaves, start_row, comment, inner_comment = [], None, None, False
    prev_end = None
    depth = 0
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        kind = tok.type
        if kind in (tokenize.INDENT, tokenize.DEDENT, tokenize.ENCODING):
            i += 1
            continue
        if kind == tokenize.ENDMARKER:
            break
        if kind == tokenize.NL and not leaves:
            if tok.line.strip() == "":
                items.append(None)
            i += 1
            continue
        if kind == tokenize.COMMENT and not leaves:
            items.append(("#", tok.line[: tok.start[1]], tok.string))
            i += 1
            continue
        if kind == tokenize.NL:
            i += 1
            continue
        if kind == tokenize.COMMENT:
            following = tokens[i + 1].type if i + 1 < len(tokens) else None
            if following == tokenize.NEWLINE:
                comment = tok.string
            else:
                inner_comment = True
            i += 1
            continue
        if kind == tokenize.NEWLINE:
            first_line = lines[start_row - 1]
            indent = first_line[: len(first_line) - len(first_line.lstrip())]
            verbatim = None
            skip = comment is not None and "fmt: skip" in comment
            if skip or inner_comment or any("\n" in leaf.text for leaf in leaves):
                verbatim = [
                    line.rstrip("\n") for line in lines[start_row - 1 : tok.start[0]]
                ]
                if comment and verbatim and comment not in verbatim[-1]:
                    verbatim = None
            items.append(_Logical(indent, leaves, comment, verbatim))
            leaves, start_row, comment, inner_comment = [], None, None, False
            prev_end = None
            i += 1
            continue
        # f-strings (Python 3.12+) come in parts: take the whole literal
        end = tok.end
        text = tok.string
        leaf_kind = "op"
        if kind == getattr(tokenize, "FSTRING_START", -1) or kind == getattr(
            tokenize, "TSTRING_START", -1
        ):
            nesting, j = 0, i
            while True:
                t = tokens[j]
                if t.type in (
                    tokenize.FSTRING_START,
                    getattr(tokenize, "TSTRING_START", -2),
                ):
                    nesting += 1
                elif t.type in (
                    tokenize.FSTRING_END,
                    getattr(tokenize, "TSTRING_END", -2),
                ):
                    nesting -= 1
                    if nesting == 0:
                        break
                j += 1
            end = tokens[j].end
            text = _slice(lines, tok.start, end)
            leaf_kind = "string"
            i = j
        elif kind == tokenize.STRING:
            leaf_kind = "string"
        elif kind == tokenize.NAME:
            leaf_kind = "name"
        elif kind == tokenize.NUMBER:
            leaf_kind = "number"
        if start_row is None:
            start_row = tok.start[0]
        space = None
        if prev_end is not None and prev_end[0] == tok.start[0]:
            space = tok.line[prev_end[1] : tok.start[1]]
        if leaf_kind == "string":
            text = normalize_string(text)
        if text in OPENING:
            depth += 1
        elif text in CLOSING:
            depth -= 1
        leaves.append(Leaf(text, leaf_kind, space))
        prev_end = end
        i += 1
    return items


def _slice(lines, start, end):
    (srow, scol), (erow, ecol) = start, end
    if srow == erow:
        return lines[srow - 1][scol:ecol]
    parts = [lines[srow - 1][scol:]]
    parts += lines[srow : erow - 1]
    parts.append(lines[erow - 1][:ecol])
    return "".join(parts)


# -- leaves -------------------------------------------------------------------------


def flat(leaves) -> str:
    out = []
    for i, leaf in enumerate(leaves):
        if i:
            out.append(
                leaf.space if leaf.space is not None else _space(leaves[i - 1], leaf)
            )
        out.append(leaf.text)
    return "".join(out)


def _space(prev, leaf):
    """Whitespace between two leaves that were on different lines."""
    if prev.text in OPENING or leaf.text in CLOSING or leaf.text in (",", ":", "."):
        return ""
    return " "


def matching(leaves):
    """{index of an opening bracket: index of its closing one} and back."""
    pairs, stack = {}, []
    for i, leaf in enumerate(leaves):
        if leaf.kind != "op":
            continue
        if leaf.text in OPENING:
            stack.append(i)
        elif leaf.text in CLOSING and stack:
            j = stack.pop()
            pairs[j] = i
            pairs[i] = j
    return pairs


def top_level(leaves):
    """Indices of leaves outside of brackets (brackets themselves included)."""
    depth = 0
    for i, leaf in enumerate(leaves):
        if leaf.kind == "op" and leaf.text in CLOSING:
            depth -= 1
        if depth == 0:
            yield i
        if leaf.kind == "op" and leaf.text in OPENING:
            depth += 1


def is_operand_end(leaf):
    if leaf.kind in ("number", "string"):
        return True
    if leaf.kind == "name":
        return not keyword.iskeyword(leaf.text) or leaf.text in (
            "None",
            "True",
            "False",
        )
    return leaf.text in CLOSING


def bracket_kind(leaves, i):
    """What the bracket at `i` is: "call", "subscript", "def" (parameters) or
    "atom" (a literal or parentheses)."""
    prev = leaves[i - 1] if i else None
    if prev is None or not is_operand_end(prev):
        return "atom"
    if leaves[i].text == "(":
        if i >= 2 and leaves[i - 2].text in ("def", "class"):
            return "def" if leaves[i - 2].text == "def" else "call"
        return "call"
    if leaves[i].text == "[":
        return "subscript"
    return "atom"


def delimiters(leaves):
    """{index: priority} of the leaves at the top level a line splits
    before (or after, for commas)."""
    result = {}
    tops = list(top_level(leaves))
    texts = [leaves[i].text for i in tops]
    has_for = "for" in texts
    in_lambda = False
    seen_for = False
    comprehension_target = False  # between `for` and its `in`
    for n, i in enumerate(tops):
        leaf = leaves[i]
        text = leaf.text
        prev = leaves[tops[n - 1]] if n else None
        if leaf.kind == "name" and text == "lambda":
            in_lambda = True
            continue
        if in_lambda:
            if text == ":":
                in_lambda = False
            continue
        if leaf.kind == "op" and text == ",":
            result[i] = COMMA
        elif leaf.kind == "name" and text in ("for", "async") and has_for:
            if text == "for":
                comprehension_target = True
            if not n or (text == "for" and prev is not None and prev.text == "async"):
                continue
            result[i] = COMPREHENSION
            seen_for = True
        elif leaf.kind == "name" and text == "if" and n:
            result[i] = COMPREHENSION if seen_for else TERNARY
        elif leaf.kind == "name" and text == "else" and n:
            result[i] = TERNARY
        elif leaf.kind == "name" and text in ("and", "or") and n:
            result[i] = LOGIC
        elif leaf.kind == "name" and text in ("in", "is", "not") and n:
            if text == "not" and (prev is None or not is_operand_end(prev)):
                continue  # unary not
            if text == "in" and prev is not None and prev.text == "not":
                continue
            if text == "in" and comprehension_target:
                comprehension_target = False
                continue
            if text == "not" and prev is not None and prev.text == "is":
                continue
            result[i] = COMPARE
        elif leaf.kind == "op" and text in COMPARATORS:
            result[i] = COMPARE
        elif leaf.kind == "op" and text in OPERATORS and prev is not None:
            if is_operand_end(prev):
                result[i] = OPERATORS[text]
        elif leaf.kind == "string" and prev is not None and prev.kind == "string":
            result[i] = STRING
        elif (
            leaf.kind == "op"
            and text == "."
            and prev is not None
            and prev.text in CLOSING
        ):
            result[i] = DOT
    return result


def max_delimiter(leaves):
    found = delimiters(leaves)
    if not found:
        return 0, 0, found
    priority = max(found.values())
    return priority, sum(1 for p in found.values() if p == priority), found


def magic_comma(leaves, start, end):
    """The bracket from `start` to `end` ends with a trailing comma that keeps
    it split."""
    if end - start < 2 or leaves[end - 1].text != ",":
        return False
    kind = bracket_kind(leaves, start)
    commas = [
        i
        for i in top_level(leaves[start + 1 : end])
        if leaves[start + 1 + i].text == ","
    ]
    if len(commas) == 1:
        if leaves[start].text == "(" and kind == "atom":
            return False  # (one,)
        if kind == "subscript":
            return False
    return True


def has_magic_comma(leaves):
    pairs = matching(leaves)
    return any(
        magic_comma(leaves, i, j)
        for i, j in pairs.items()
        if i < j and leaves[i].text in OPENING
    )


# -- formatting ---------------------------------------------------------------------


class _Formatter:
    def __init__(self, source, line_length):
        self.source = source
        self.width = line_length

    def fits(self, indent, text):
        return len(indent) + len(text) <= self.width and "\n" not in text

    # -- lines ------------------------------------------------------------------

    def run(self):
        out = []
        blanks = 0
        comments = []  # (blank lines before, line) before the next statement
        prev = None
        definitions = []  # indents of the defs / classes we're in
        for item in _read(self.source):
            if item is None:
                blanks += 1
                continue
            if isinstance(item, tuple):
                comments.append((blanks, item[1] + item[2]))
                blanks = 0
                continue
            indent = item.indent
            left = False
            while definitions and len(indent) <= len(definitions[-1]):
                definitions.pop()
                left = True
            # comments indented deeper end the previous block
            while comments and _indent_of(comments[0][1]) > len(indent):
                count, text = comments.pop(0)
                out.extend([""] * min(count, 1))
                out.append(text)
            limit = 1 if indent else 2
            if comments and blanks:
                # comments apart from the statement: like other statements
                first = limit if left else min(comments[0][0], limit)
                if prev is None:
                    first = 0
                elif prev.first in ("import", "from") and prev.indent == indent:
                    first = max(first, 1)
                out.extend([""] * first)
                for n, (count, text) in enumerate(comments):
                    if n:
                        out.extend([""] * min(count, limit))
                    out.append(text)
                out.extend([""] * self.blank_lines(blanks, item, comments, False))
            else:
                before = comments[0][0] if comments else blanks
                out.extend([""] * self.blank_lines(before, item, prev, left))
                for n, (count, text) in enumerate(comments):
                    if n:
                        out.extend([""] * min(count, limit))
                    out.append(text)
            comments, blanks = [], 0
            out.extend(self.statement(item))
            if _is_definition(item) and _ends_block(item):
                definitions.append(indent)
            prev = item
        for n, (count, text) in enumerate(comments):
            if prev is not None:
                out.extend([""] * min(count, 2))
            out.append(text)
        return out

    def blank_lines(self, before, item, prev, left):
        """Blank lines before a statement (and its comments); `prev` is a
        list after comments that are apart from the statement."""
        if isinstance(prev, list):
            limit = 1 if item.indent else 2
            if left or _is_definition(item) or item.first == "@":
                return limit
            return min(before, limit)
        if prev is None or prev.first == "@":
            return 0
        if (
            prev.leaves[0].kind == "string"
            and len(prev.leaves) == 1
            and not prev.indent
        ):
            # after the module's docstring
            return 2 if _is_definition(item) or item.first == "@" else 1
        if _ends_block(prev) and len(item.indent) > len(prev.indent):
            return 0  # first in a block
        limit = 1 if item.indent else 2
        if left or _is_definition(item) or item.first == "@":
            return limit
        wanted = min(before, limit)
        if (
            prev.first in ("import", "from")
            and item.first not in ("import", "from")
            and prev.indent == item.indent
        ):
            wanted = max(wanted, 1)
        return wanted

    def statement(self, item):
        if item.verbatim is not None:
            return item.verbatim
        comment = f"  {item.comment}" if item.comment else ""
        leaves = _remove_redundant_parens(item.leaves)
        lines = self.line(leaves, item.indent, statement=True)
        lines[-1] += comment
        return lines

    # -- splitting ----------------------------------------------------------------

    def line(self, leaves, indent, statement=False):
        text = flat(leaves)
        if self.fits(indent, text) and not has_magic_comma(leaves):
            return [indent + text]
        if statement and leaves[0].text in ("def", "async"):
            split = self.left_split(leaves, indent)
            if split:
                return split
        if not statement:
            split = self.delimiter_split(leaves, indent)
            if split:
                return split
        split = self.right_split(leaves, indent, statement)
        return split or [indent + text]

    def left_split(self, leaves, indent):
        opening = next((i for i, leaf in enumerate(leaves) if leaf.text == "("), None)
        pairs = matching(leaves)
        if opening is None or opening not in pairs:
            return None
        return self.bracket_split(leaves, indent, opening, pairs[opening])

    def right_split(self, leaves, indent, statement):
        slot = _slot(leaves) if statement else None
        if slot is not None:
            start, end = slot
            body = leaves[start:end]
            pairs = matching(body)
            atom = not delimiters(body) and not any(
                body[i].text in OPENING and pairs.get(i, i) > i + 1
                for i in top_level(body)
            )
            if atom:
                # a name or text: split what it's assigned to, else wrap it
                # in parentheses if that makes it fit, else leave it long
                if leaves[start - 1].text == "=" and start > 1:
                    split = self.last_bracket_split(
                        leaves, indent, within=(0, start - 1)
                    )
                    if split and all(self.fits("", line) for line in split):
                        return split
                parens = self.parens_split(leaves, indent, start, end)
                if all(self.fits("", line) for line in parens):
                    return parens
                return None
            if self.can_omit_parens(body):
                split = self.last_bracket_split(leaves, indent, within=(start, end))
                if split and all(self.fits("", line) for line in split):
                    return split
                parens = self.parens_split(leaves, indent, start, end)
                if split and not all(self.fits("", line) for line in parens):
                    return split
                return parens
            return self.parens_split(leaves, indent, start, end)
        return self.last_bracket_split(leaves, indent)

    def can_omit_parens(self, body):
        """Split the expression at its own brackets instead of wrapping it in
        parentheses (ruff's can_omit_optional_parentheses)."""
        pairs = matching(body)
        tops = list(top_level(body))
        brackets = [
            i for i in tops if body[i].text in OPENING and pairs.get(i, i) > i + 1
        ]
        if not brackets:
            return False
        priority, count, found = max_delimiter(body)
        if count > 1 and priority != DOT:
            return False
        if priority == 0 or priority == DOT:
            return True
        last = len(body) - 1
        if body[last].text in CLOSING and pairs.get(last, last) < last - 1:
            if bracket_kind(body, pairs[last]) != "subscript":
                return True
        return body[0].text in OPENING and pairs.get(0, 0) > 1

    def last_bracket_split(self, leaves, indent, within=None):
        """Split at the last bracket (or an earlier one if the line before it
        would be too long)."""
        pairs = matching(leaves)
        start, end = within or (0, len(leaves))
        candidates = [
            i
            for i in top_level(leaves)
            if start <= i < end and leaves[i].text in CLOSING and pairs.get(i, i) < i
        ]
        for close in reversed(candidates):
            opening = pairs[close]
            if opening < start or close - opening < 2:
                continue
            split = self.bracket_split(leaves, indent, opening, close)
            if split is None:
                continue
            if self.fits("", split[0]) or close == candidates[0]:
                return split
        return None

    def bracket_split(self, leaves, indent, opening, close):
        head, body, tail = (
            leaves[: opening + 1],
            leaves[opening + 1 : close],
            leaves[close:],
        )
        if not body:
            return None
        kind = bracket_kind(leaves, opening)
        head_text = flat(head)
        lines = [indent + head_text]
        lines += self.body(
            body, indent + INDENT, kind, magic_comma(leaves, opening, close)
        )
        tail_lines = self.line(tail, indent)
        return lines + tail_lines

    def parens_split(self, leaves, indent, start, end):
        """Wrap leaves[start:end] in parentheses and split it."""
        head = flat(leaves[:start])
        lines = [indent + (head + " (" if head else "(")]
        lines += self.body(
            leaves[start:end], indent + INDENT, "atom", False, wrapped=True
        )
        tail = flat(leaves[end:])
        lines.append(indent + ")" + tail)
        return lines

    def body(self, body, indent, kind, magic, wrapped=False):
        text = flat(body)
        priority, count, found = max_delimiter(body)
        explode = magic or (kind == "atom" and priority == COMMA and not wrapped)
        if not explode and self.fits(indent, text) and not has_magic_comma(body):
            return [indent + text]
        if priority == COMMA:
            items, current = [], []
            for i, leaf in enumerate(body):
                if found.get(i) == COMMA:
                    items.append(current)
                    current = []
                else:
                    current.append(leaf)
            if current:
                items.append(current)
            lines = []
            for item in items:
                item_lines = self.line(item, indent)
                item_lines[-1] += ","
                lines += item_lines
            return lines
        split = self.delimiter_split(body, indent, found=found)
        if split:
            return split
        return self.line(body, indent)

    def delimiter_split(self, leaves, indent, found=None):
        if found is None:
            found = delimiters(leaves)
        if not found:
            return None
        priority = max(found.values())
        if priority == COMMA:
            return None
        count = sum(1 for p in found.values() if p == priority)
        if priority == DOT and count < 2:
            return None
        segments, current = [], []
        for i, leaf in enumerate(leaves):
            if found.get(i) == priority and current:
                segments.append(current)
                current = []
            current.append(leaf)
        segments.append(current)
        if len(segments) < 2:
            return None
        lines = []
        for segment in segments:
            lines += self.line(_strip_space(segment), indent)
        return lines


def _strip_space(leaves):
    if leaves and leaves[0].space is not None:
        leaves = [Leaf(leaves[0].text, leaves[0].kind, None), *leaves[1:]]
    return leaves


def _indent_of(line):
    return len(line) - len(line.lstrip())


def _is_definition(item):
    leaves = item.leaves
    if leaves and leaves[0].text == "async" and len(leaves) > 1:
        return leaves[1].text == "def"
    return item.first in ("def", "class")


def _ends_block(item):
    return (
        bool(item.leaves)
        and item.leaves[-1].text == ":"
        and item.first not in ("lambda",)
    )


def _slot(leaves):
    """(start, end) of the expression ruff wraps in parentheses when the
    statement is split: what's returned, assigned or tested."""
    first = leaves[0].text
    end = len(leaves)
    if leaves[-1].text == ":" and first in ("if", "elif", "while", "for", "with"):
        end -= 1
    if first in CLAUSES and leaves[0].kind == "name":
        return (1, end) if end > 1 else None
    if first == "for":
        tops = [i for i in top_level(leaves) if leaves[i].text == "in"]
        return (tops[0] + 1, end) if tops else None
    tops = list(top_level(leaves))
    assign = [
        i
        for i in tops
        if leaves[i].kind == "op"
        and (leaves[i].text == "=" or leaves[i].text in AUGMENTED)
    ]
    if assign and assign[-1] + 1 < end:
        return assign[-1] + 1, end
    return None


def _remove_redundant_parens(leaves):
    """`if (a):` -> `if a:`, `return (a)` -> `return a`."""
    slot = _slot(leaves)
    if slot is None:
        return leaves
    start, end = slot
    if leaves[start].text != "(":
        return leaves
    pairs = matching(leaves)
    if pairs.get(start) != end - 1 or end - start < 3:
        return leaves
    inner = leaves[start + 1 : end - 1]
    if any(leaves[i].text == "," for i in top_level(inner) if True) or any(
        leaf.text in ("yield", "*", "**", ":=") for leaf in inner[:1]
    ):
        return leaves
    if any(inner[i].text in (",", ":=") for i in top_level(inner)):
        return leaves
    if has_magic_comma(leaves[start:end]):
        return leaves
    first = Leaf(inner[0].text, inner[0].kind, leaves[start].space)
    after = leaves[end:]
    if after:
        after = [
            Leaf(
                after[0].text,
                after[0].kind,
                after[0].space if leaves[end - 1].space is None else after[0].space,
            ),
            *after[1:],
        ]
    return leaves[:start] + [first] + inner[1:] + after


# -- parentheses ------------------------------------------------------------------


def remove_redundant_parens(source: str) -> str:
    """Drop parentheses that don't change what the code means, like the ones
    nodes put around values they combine: `(a * b) if (c) else (0.0)` ->
    `a * b if c else 0.0`. A removal is kept only if the syntax tree stays the
    same. Parentheses that help reading stay: around tuples, after `not` and
    unary operators, around `and` inside `or` and the other way around."""
    try:
        expected = ast.dump(ast.parse(source))
        tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
    except (SyntaxError, tokenize.TokenError, IndentationError):
        return source
    lines = source.splitlines(keepends=True)
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))

    def position(point):
        return offsets[point[0] - 1] + point[1]

    candidates = _paren_candidates(tokens)
    if not candidates:
        return source
    pairs = [(position(o.start), position(c.start)) for o, c in candidates]

    def without(removed):
        chars = list(source)
        for opening, closing in removed:
            chars[opening] = ""
            chars[closing] = ""
        return "".join(chars)

    def same(code):
        try:
            return ast.dump(ast.parse(code)) == expected
        except SyntaxError:
            return False

    result = without(pairs)
    if same(result):
        return result
    kept = []
    for pair in pairs:
        if same(without([*kept, pair])):
            kept.append(pair)
    return without(kept) if kept else source


_UNARY = {"not", "-", "+", "~", "await", "*", "**", "lambda"}


def _paren_candidates(tokens):
    """(opening, closing) tokens of parentheses that aren't calls, tuples,
    generators or empty, and don't help reading."""
    # f-strings are one token before Python 3.12: leave their insides alone
    # on newer versions too, so every version gives the same code
    starts = {
        getattr(tokenize, "FSTRING_START", -1),
        getattr(tokenize, "TSTRING_START", -1),
    }
    ends = {getattr(tokenize, "FSTRING_END", -1), getattr(tokenize, "TSTRING_END", -1)}
    code, nesting = [], 0
    for t in tokens:
        if t.type in starts:
            nesting += 1
        elif t.type in ends:
            nesting -= 1
            if not nesting:
                code.append(t)
            continue
        if nesting or t.type in (
            tokenize.NL,
            tokenize.COMMENT,
            tokenize.INDENT,
            tokenize.DEDENT,
        ):
            continue
        code.append(t)
    stack, found = [], []
    for i, tok in enumerate(code):
        if tok.type != tokenize.OP:
            continue
        if tok.string in "([{":
            stack.append(i)
        elif tok.string in ")]}" and stack:
            j = stack.pop()
            if code[j].string == "(" and tok.string == ")":
                found.append((j, i))
    result = []
    for j, i in found:
        if i == j + 1:
            continue  # ()
        before = code[j - 1] if j else None
        after = code[i + 1] if i + 1 < len(code) else None
        if before is not None and _ends_operand(before):
            continue  # a call
        inner = code[j + 1 : i]
        top = _top_tokens(inner)
        texts = {t.string for t in top}
        if "," in texts or "for" in texts or "yield" in texts or ":=" in texts:
            continue
        if before is not None and before.string in _UNARY:
            continue
        if len(inner) == 1 and inner[0].type == tokenize.NUMBER and after is not None:
            if after.string == ".":
                continue  # (1).real
        logic = texts & {"and", "or"}
        if logic and _neighbor_logic(code, j, i) - logic:
            continue  # a or (b and c)
        result.append((code[j], code[i]))
    return result


def _ends_operand(tok):
    if tok.type in (tokenize.NUMBER, tokenize.STRING):
        return True
    if tok.type == tokenize.NAME:
        return not keyword.iskeyword(tok.string) or tok.string in (
            "None",
            "True",
            "False",
        )
    if tok.type == getattr(tokenize, "FSTRING_END", -1):
        return True
    return tok.string in (")", "]", "}")


def _top_tokens(tokens):
    depth, top = 0, []
    for tok in tokens:
        if tok.type == tokenize.OP and tok.string in ")]}":
            depth -= 1
        if depth == 0:
            top.append(tok)
        if tok.type == tokenize.OP and tok.string in "([{":
            depth += 1
    return top


def _neighbor_logic(code, j, i):
    """`and` / `or` right before or after the parentheses at j..i."""
    found = set()
    if j and code[j - 1].string in ("and", "or"):
        found.add(code[j - 1].string)
    if i + 1 < len(code) and code[i + 1].string in ("and", "or"):
        found.add(code[i + 1].string)
    return found
