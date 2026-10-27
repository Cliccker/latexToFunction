"""Strict parsing of the supported scalar LaTeX expression language."""

from contextlib import contextmanager
from dataclasses import dataclass
import math
import re


MAX_LENGTH = 10_000
MAX_DEPTH = 64
MAX_NODES = 2_000


class FormulaSyntaxError(ValueError):
    """An invalid or unsupported expression, with its original source offset."""

    def __init__(self, source: str, position: int, reason: str):
        self.source = source
        self.position = position
        self.reason = reason
        start = max(0, position - 30)
        end = min(len(source), position + 30)
        excerpt = source[start:end].replace("\n", " ").replace("\r", " ")
        super().__init__(
            f"{reason} at position {position}\n{excerpt}\n{' ' * (position - start)}^"
        )


@dataclass(frozen=True)
class Node:
    kind: str
    value: str | float
    children: tuple["Node", ...] = ()
    position: int = 0


@dataclass(frozen=True)
class _Token:
    kind: str
    value: str
    position: int


_FUNCTIONS = {
    "sin", "cos", "tan", "arcsin", "arccos", "arctan",
    "sinh", "cosh", "tanh", "exp", "ln", "log", "abs", "min", "max",
}
_GREEK = {
    "alpha", "beta", "gamma", "delta", "epsilon", "varepsilon", "zeta",
    "eta", "theta", "vartheta", "iota", "kappa", "varkappa", "lambda",
    "mu", "nu", "xi", "omicron", "rho", "varrho", "sigma", "varsigma",
    "tau", "upsilon", "phi", "varphi", "chi", "psi", "omega",
    "Gamma", "Delta", "Theta", "Lambda", "Xi", "Pi", "Sigma", "Upsilon",
    "Phi", "Psi", "Omega", "varpi",
}
_NUMBER = re.compile(r"(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?")
_WORD = re.compile(r"[A-Za-z]+")
_LABEL = re.compile(r"[A-Za-z0-9]+(?:,[A-Za-z0-9]+)*\Z")
_DELIMITERS = {"(": ")", "[": "]", "{": "}"}
_STARTS_ATOM = {"number", "symbol", "constant", "function", "frac", "sqrt", "mathrm", "(", "[", "{", "|"}


def _tokenize(source: str) -> list[_Token]:
    tokens = []
    index = 0
    while index < len(source):
        char = source[index]
        if char.isspace():
            index += 1
            continue
        if char == "\\":
            match = _WORD.match(source, index + 1)
            if not match:
                if index + 1 < len(source) and source[index + 1] in ",;:! ":
                    index += 2
                    continue
                if index + 1 < len(source) and source[index + 1] in "{}|":
                    tokens.append(_Token(source[index + 1], source[index + 1], index))
                    index += 2
                    continue
                raise FormulaSyntaxError(source, index, "Invalid LaTeX command")
            command = match.group()
            end = match.end()
            if command in {"left", "right"}:
                following = end
                while following < len(source) and source[following].isspace():
                    following += 1
                allowed = "([{|" if command == "left" else ")]}|"
                escaped = (r"\{", r"\lvert", r"\vert") if command == "left" else (r"\}", r"\rvert", r"\vert")
                if following == len(source) or not (
                    source[following] in allowed or any(source.startswith(item, following) for item in escaped)
                ):
                    raise FormulaSyntaxError(source, index, f"\\{command} must precede a matching delimiter")
                index = end
                continue
            if command in {"quad", "qquad"}:
                index = end
                continue
            if command in {"cdot", "times", "div"}:
                operator = "/" if command == "div" else "*"
                tokens.append(_Token(operator, operator, index))
            elif command in {"vert", "lvert", "rvert"}:
                tokens.append(_Token("|", "|", index))
            elif command in {"frac", "dfrac", "tfrac"}:
                tokens.append(_Token("frac", command, index))
            elif command in {"sqrt", "mathrm"}:
                tokens.append(_Token(command, command, index))
            elif command in _FUNCTIONS:
                tokens.append(_Token("function", command, index))
            elif command == "pi":
                tokens.append(_Token("constant", "pi", index))
            elif command in _GREEK:
                tokens.append(_Token("symbol", command, index))
            else:
                raise FormulaSyntaxError(source, index, f"Unsupported command \\{command}")
            index = end
            continue
        match = _NUMBER.match(source, index)
        if match:
            if tokens and tokens[-1].kind == "number" and index == tokens[-1].position + len(tokens[-1].value):
                raise FormulaSyntaxError(source, index, "Invalid numeric literal")
            tokens.append(_Token("number", match.group(), index))
            index = match.end()
            continue
        match = _WORD.match(source, index)
        if match:
            word = match.group()
            if word in _FUNCTIONS:
                tokens.append(_Token("function", word, index))
            elif word in {"sqrt", "frac"}:
                tokens.append(_Token(word, word, index))
            else:
                tokens.extend(_Token("symbol", letter, index + offset) for offset, letter in enumerate(word))
            index = match.end()
            continue
        if source.startswith("**", index):
            tokens.append(_Token("^", "**", index))
            index += 2
            continue
        if char in "+-*/^_='(),[]{}|":
            tokens.append(_Token(char, char, index))
            index += 1
            continue
        raise FormulaSyntaxError(source, index, f"Invalid character {char!r}")
    tokens.append(_Token("end", "", len(source)))
    return tokens


class _Parser:
    def __init__(self, source: str):
        self.source = source
        self.tokens = _tokenize(source)
        self.index = 0
        self.depth = 0
        self.bars = 0

    @property
    def current(self) -> _Token:
        return self.tokens[self.index]

    def _take(self, kind: str) -> _Token:
        token = self.current
        if token.kind != kind:
            raise FormulaSyntaxError(self.source, token.position, f"Expected {kind!r}, found {token.value or 'end of input'!r}")
        self.index += 1
        return token

    @contextmanager
    def _nested(self):
        self.depth += 1
        try:
            if self.depth > MAX_DEPTH:
                raise FormulaSyntaxError(self.source, self.current.position, f"Expression exceeds maximum nesting depth ({MAX_DEPTH})")
            yield
        finally:
            self.depth -= 1

    def parse(self) -> tuple[str | None, Node, tuple[str, ...]]:
        expression = self._expression()
        result_name = None
        if self.current.kind == "=":
            equal = self._take("=")
            if expression.kind != "symbol":
                raise FormulaSyntaxError(self.source, equal.position, "The left side of '=' must be a single variable")
            result_name = str(expression.value)
            expression = self._expression()
        if self.current.kind != "end":
            raise FormulaSyntaxError(self.source, self.current.position, f"Unexpected token {self.current.value!r}")
        parameter_positions = {}
        pending = [expression]
        count = 0
        while pending:
            node = pending.pop()
            count += 1
            if count > MAX_NODES:
                raise FormulaSyntaxError(self.source, node.position, f"Expression exceeds maximum node count ({MAX_NODES})")
            if node.kind == "symbol":
                name = str(node.value)
                parameter_positions[name] = min(node.position, parameter_positions.get(name, node.position))
            pending.extend(reversed(node.children))
        parameters = tuple(sorted(parameter_positions, key=parameter_positions.get))
        return result_name, expression, parameters

    def _expression(self) -> Node:
        node = self._product()
        while self.current.kind in {"+", "-"}:
            token = self.current
            self.index += 1
            node = Node("binary", token.kind, (node, self._product()), token.position)
        return node

    def _product(self) -> Node:
        node = self._unary()
        while True:
            token = self.current
            if token.kind in {"*", "/"}:
                self.index += 1
                node = Node("binary", token.kind, (node, self._unary()), token.position)
            elif token.kind in _STARTS_ATOM and not (token.kind == "|" and self.bars):
                node = Node("binary", "*", (node, self._unary()), token.position)
            else:
                return node

    def _unary(self) -> Node:
        if self.current.kind in {"+", "-"}:
            token = self.current
            self.index += 1
            with self._nested():
                return Node("unary", token.kind, (self._unary(),), token.position)
        return self._power()

    def _power(self) -> Node:
        node = self._primary()
        if self.current.kind == "^":
            token = self._take("^")
            with self._nested():
                node = Node("binary", "^", (node, self._unary()), token.position)
        return node

    def _number(self, token: _Token) -> Node:
        value = float(token.value)
        if not math.isfinite(value):
            raise FormulaSyntaxError(self.source, token.position, "Numeric literals must be finite")
        return Node("number", value, position=token.position)

    def _primary(self) -> Node:
        token = self.current
        grouped = False
        if token.kind == "number":
            self.index += 1
            node = self._number(token)
        elif token.kind in {"symbol", "constant"}:
            self.index += 1
            node = Node(token.kind, token.value, position=token.position)
        elif token.kind == "mathrm":
            self.index += 1
            name = self._label(require_braces=True)
            if not re.fullmatch(r"[A-Za-z][A-Za-z0-9]*", name):
                raise FormulaSyntaxError(self.source, token.position, "\\mathrm requires an alphanumeric variable name starting with a letter")
            node = Node("symbol", name, position=token.position)
        elif token.kind in _DELIMITERS:
            node = self._group()
            grouped = True
        elif token.kind == "|":
            self.index += 1
            self.bars += 1
            try:
                with self._nested():
                    argument = self._expression()
                    self._take("|")
            finally:
                self.bars -= 1
            node = Node("call", "abs", (argument,), token.position)
        elif token.kind in {"function", "frac", "sqrt"}:
            node = self._function()
        else:
            raise FormulaSyntaxError(self.source, token.position, f"Expected an expression, found {token.value or 'end of input'!r}")
        return self._decorate(node, grouped)

    def _group(self) -> Node:
        opening = self.current.kind
        self.index += 1
        with self._nested():
            node = self._expression()
            self._take(_DELIMITERS[opening])
        return node

    def _label(self, require_braces: bool = False) -> str:
        braced = self.current.kind == "{"
        position = self.current.position
        if require_braces and not braced:
            raise FormulaSyntaxError(self.source, position, "Expected a braced variable name")
        if braced:
            self.index += 1
            parts = []
            while self.current.kind != "}":
                if self.current.kind not in {"symbol", "number", "function", "constant", "sqrt", "frac", ","}:
                    raise FormulaSyntaxError(self.source, self.current.position, "Subscripts must contain alphanumeric labels separated by commas")
                parts.append(self.current.value)
                self.index += 1
            self._take("}")
            label = "".join(parts)
        else:
            if self.current.kind not in {"symbol", "number", "constant"}:
                raise FormulaSyntaxError(self.source, position, "Expected a subscript label")
            label = self.current.value
            self.index += 1
        if not _LABEL.fullmatch(label):
            raise FormulaSyntaxError(self.source, position, "Invalid or empty subscript label")
        return label

    def _star_label(self) -> tuple[bool, _Token | None]:
        """Recognize legacy engineering star labels with an optional integer power."""
        if self.current.kind != "^":
            return False, None
        following = self.tokens[self.index + 1:self.index + 6]
        if len(following) < 3 or following[0].kind != "{" or following[1].kind != "*":
            return False, None
        if following[2].kind == "}":
            self.index += 4
            return True, None
        if len(following) >= 4 and following[2].kind == "number" and following[3].kind == "}":
            exponent = following[2]
            if not exponent.value.isdigit():
                return False, None
            self.index += 5
            return True, exponent
        return False, None

    def _decorate(self, node: Node, grouped: bool) -> Node:
        has_subscript = False
        named_group = False
        while True:
            token = self.current
            if token.kind == "_":
                if node.kind != "symbol" or has_subscript:
                    raise FormulaSyntaxError(self.source, token.position, "Only a variable may have one subscript at each grouping level")
                self.index += 1
                label = self._label()
                if grouped and not named_group:
                    name, primes = f"({node.value})", ""
                else:
                    name = str(node.value).rstrip("'")
                    primes = str(node.value)[len(name):]
                node = Node("symbol", name + "_{" + label + "}" + primes, position=node.position)
                has_subscript = True
                named_group = True
            elif token.kind == "'":
                if node.kind != "symbol":
                    raise FormulaSyntaxError(self.source, token.position, "Only variables may have prime labels")
                self.index += 1
                node = Node("symbol", str(node.value) + "'", position=node.position)
            elif token.kind == "^":
                starred, exponent = self._star_label()
                if not starred:
                    return node
                if node.kind != "symbol":
                    raise FormulaSyntaxError(self.source, token.position, "Only variables may have engineering star labels")
                node = Node("symbol", str(node.value) + "'", position=node.position)
                if exponent is not None:
                    node = Node("binary", "^", (node, self._number(exponent)), token.position)
                    return node
            else:
                return node

    def _arguments(self) -> tuple[Node, ...]:
        opening = self.current.kind
        if opening not in _DELIMITERS:
            with self._nested():
                return (self._unary(),)
        self.index += 1
        with self._nested():
            arguments = [self._expression()]
            while self.current.kind == ",":
                self.index += 1
                arguments.append(self._expression())
            self._take(_DELIMITERS[opening])
        return tuple(arguments)

    def _function(self) -> Node:
        token = self.current
        self.index += 1
        if token.kind == "frac":
            if self.current.kind != "{":
                raise FormulaSyntaxError(self.source, self.current.position, "Fractions require braced numerator and denominator")
            numerator = self._group()
            if self.current.kind != "{":
                raise FormulaSyntaxError(self.source, self.current.position, "Fractions require a braced denominator")
            return Node("binary", "/", (numerator, self._group()), token.position)
        if token.kind == "sqrt":
            index = Node("number", 2.0, position=token.position)
            if self.current.kind == "[":
                index = self._group()
            arguments = self._arguments()
            if len(arguments) != 1:
                raise FormulaSyntaxError(self.source, token.position, "sqrt requires one radicand")
            return Node("call", "root", (arguments[0], index), token.position)
        name = token.value
        base = None
        if self.current.kind == "_":
            if name != "log":
                raise FormulaSyntaxError(self.source, self.current.position, "Only log accepts a base subscript")
            self.index += 1
            with self._nested():
                base = self._group() if self.current.kind in _DELIMITERS else self._primary()
        exponent = None
        if self.current.kind == "^":
            self.index += 1
            with self._nested():
                exponent = self._unary()
        arguments = self._arguments()
        if base is not None:
            if len(arguments) != 1:
                raise FormulaSyntaxError(self.source, token.position, "A logarithm with a base subscript requires one argument")
            arguments += (base,)
        valid_arity = (len(arguments) >= 2 if name in {"min", "max"}
                       else len(arguments) in {1, 2} if name == "log"
                       else len(arguments) == 1)
        if not valid_arity:
            raise FormulaSyntaxError(self.source, token.position, f"Invalid argument count for {name}")
        node = Node("call", name, arguments, token.position)
        if exponent is not None:
            node = Node("binary", "^", (node, exponent), token.position)
        return node


def parse(latex: str) -> tuple[str | None, Node, tuple[str, ...]]:
    """Return the optional result variable, expression tree, and ordered variables."""
    if not isinstance(latex, str):
        raise TypeError("latex must be a string")
    if len(latex) > MAX_LENGTH:
        raise FormulaSyntaxError(latex, MAX_LENGTH, f"Expression exceeds maximum length ({MAX_LENGTH})")
    return _Parser(latex).parse()
