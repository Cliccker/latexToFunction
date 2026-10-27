"""Parse, evaluate and export real-valued LaTeX formulas (Python 3.11+)."""

import inspect
import math
from collections.abc import Mapping
from pathlib import Path

from formula_parser import FormulaSyntaxError, parse


class FormulaEvaluationError(ValueError):
    """A parameter or mathematical operation cannot produce a finite real value."""


_FUNCTIONS = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "arcsin": math.asin,
    "arccos": math.acos,
    "arctan": math.atan,
    "sinh": math.sinh,
    "cosh": math.cosh,
    "tanh": math.tanh,
    "exp": math.exp,
    "ln": math.log,
    "abs": abs,
}


def _number(value: object, label: str) -> float:
    if type(value) not in (int, float):
        raise FormulaEvaluationError(f"{label}: expected a finite int or float")
    try:
        number = float(value)
    except (OverflowError, ValueError) as error:
        raise FormulaEvaluationError(f"{label}: value is outside the finite real range") from error
    if not math.isfinite(number):
        raise FormulaEvaluationError(f"{label}: expected a finite real value")
    return number


def _apply(operation: str, *arguments: float) -> float:
    try:
        if operation == "+":
            result = arguments[0] + arguments[1]
        elif operation == "-":
            result = arguments[0] - arguments[1]
        elif operation == "*":
            result = arguments[0] * arguments[1]
        elif operation == "/":
            result = arguments[0] / arguments[1]
        elif operation == "^":
            result = math.pow(arguments[0], arguments[1])
        elif operation == "pos":
            result = arguments[0]
        elif operation == "neg":
            result = -arguments[0]
        elif operation == "root":
            radicand, degree = arguments
            if degree == 0 or not degree.is_integer():
                raise ValueError("root index must be a nonzero integer")
            if radicand < 0:
                if degree % 2 == 0:
                    raise ValueError("even root of a negative number is not real")
                result = -math.pow(-radicand, 1.0 / degree)
            else:
                result = math.pow(radicand, 1.0 / degree)
        elif operation == "log":
            result = math.log10(arguments[0]) if len(arguments) == 1 else math.log(*arguments)
        elif operation == "min":
            result = min(arguments)
        elif operation == "max":
            result = max(arguments)
        elif operation in _FUNCTIONS:
            result = _FUNCTIONS[operation](*arguments)
        else:
            raise FormulaEvaluationError(f"Unsupported operation: {operation}")
    except (ArithmeticError, ValueError, TypeError) as error:
        raise FormulaEvaluationError(f"{operation}: {error}") from error
    return _number(result, f"{operation} result")


def _postorder(root):
    """Visit children before parents without Python recursion."""
    pending = [(root, False)]
    while pending:
        node, visited = pending.pop()
        if visited:
            yield node
        else:
            pending.append((node, True))
            pending.extend((child, False) for child in reversed(node.children))


def _operation(node):
    if node.kind == "unary":
        return "pos" if node.value == "+" else "neg"
    return node.value


class Formula:
    """An entirely parsed formula with deterministic parameter names and order."""

    def __init__(self, latex: str):
        self.result_name, self._root, self.parameters = parse(latex)
        self.latex = latex

    def evaluate(self, values: Mapping[str, int | float]) -> float:
        """Evaluate using exactly the named, finite real numeric parameters."""
        if not isinstance(values, Mapping):
            raise FormulaEvaluationError("parameters: expected a mapping of names to numbers")
        missing = [name for name in self.parameters if name not in values]
        extra = [name for name in values if name not in self.parameters]
        if missing or extra:
            raise FormulaEvaluationError(f"parameters: missing {missing!r}; unexpected {extra!r}")
        numbers = {name: _number(values[name], f"parameter {name!r}") for name in self.parameters}
        results = []
        for node in _postorder(self._root):
            if node.kind == "number":
                result = node.value
            elif node.kind == "constant":
                result = math.pi
            elif node.kind == "symbol":
                result = numbers[node.value]
            else:
                count = len(node.children)
                arguments = results[-count:]
                del results[-count:]
                result = _apply(_operation(node), *arguments)
            results.append(result)
        return _number(results[0], "result")

    def to_python(self) -> str:
        """Return a standalone module; generating it never executes the formula."""
        parameter_names = {name: f"p{index}" for index, name in enumerate(self.parameters)}
        mapping = {argument: name for name, argument in parameter_names.items()}
        function_entries = [
            f"    {name!r}: {'abs' if name == 'abs' else 'math.' + function.__name__},"
            for name, function in _FUNCTIONS.items()
        ]
        sections = [
            '"""Generated scalar formula. Importing this module does not evaluate it."""\n\nimport math',
            f"LATEX = {self.latex!r}\nRESULT_NAME = {self.result_name!r}\nPARAMETERS = {mapping!r}",
            inspect.getsource(FormulaEvaluationError).strip(),
            "_FUNCTIONS = {\n" + "\n".join(function_entries) + "\n}",
            inspect.getsource(_number).strip(),
            inspect.getsource(_apply).strip(),
        ]
        body = [f"def formula({', '.join(parameter_names.values())}):"]
        for name, argument in parameter_names.items():
            body.append(f"    {argument} = _number({argument}, {('parameter ' + repr(name))!r})")
        results = []
        for index, node in enumerate(_postorder(self._root)):
            target = f"v{index}"
            if node.kind == "number":
                expression = repr(node.value)
            elif node.kind == "constant":
                expression = "math.pi"
            elif node.kind == "symbol":
                expression = parameter_names[node.value]
            else:
                count = len(node.children)
                arguments = results[-count:]
                del results[-count:]
                expression = f"_apply({_operation(node)!r}, {', '.join(arguments)})"
            body.append(f"    {target} = {expression}")
            results.append(target)
        body.append(f"    return _number({results[0]}, 'result')")
        sections.append("\n".join(body))
        return "\n\n\n".join(sections) + "\n"

    def export_python(self, path: str | Path, *, overwrite: bool = False) -> Path:
        """Write a module, creating directories and requiring opt-in to overwrite."""
        destination = Path(path)
        source = self.to_python()
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("w" if overwrite else "x", encoding="utf-8", newline="\n") as output:
            output.write(source)
        return destination
