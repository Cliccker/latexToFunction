"""Behavioral regressions for parsing, scalar calculation, and standalone export."""

import contextlib
import importlib.util
import io
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from LatexToFunction import Formula, FormulaEvaluationError, FormulaSyntaxError
from main import LATEX_EXAMPLES, evaluate_interactive, main


class FormulaCalculationTests(unittest.TestCase):
    def test_arithmetic_and_precedence(self):
        cases = [
            ("1+2*3", 7.0),
            ("8/2*2", 8.0),
            ("8/2(2+2)", 16.0),
            ("2^3^2", 512.0),
            ("2**3**2", 512.0),
            ("-2^2", -4.0),
            ("(-2)^2", 4.0),
            ("2^-2", 0.25),
            ("2--3", 5.0),
            (".5+1.+2e-3", 1.502),
            ("[2+{3*4}]/2", 7.0),
        ]
        for expression, expected in cases:
            with self.subTest(expression=expression):
                result = Formula(expression).evaluate({})
                self.assertIsInstance(result, float)
                self.assertAlmostEqual(result, expected)

    def test_short_power_does_not_become_python_xor(self):
        for expression in ("F=x^2", "F=x^{2}", "F=x**2"):
            with self.subTest(expression=expression):
                self.assertEqual(Formula(expression).evaluate({"x": 3}), 9.0)

    def test_implicit_multiplication_and_single_letter_variables(self):
        cases = [
            ("xy", {"x": 2, "y": 3}, 6),
            ("x y", {"x": 2, "y": 3}, 6),
            ("xy(z+1)", {"x": 2, "y": 3, "z": 4}, 30),
            ("xyz(t)", {"x": 2, "y": 3, "z": 4, "t": 5}, 120),
            ("x y(z)", {"x": 2, "y": 3, "z": 4}, 24),
            ("2x(x+1)", {"x": 3}, 24),
            ("(x+1)(x-1)", {"x": 3}, 8),
            (r"x\alpha", {"x": 2, "alpha": 3}, 6),
            (r"x\cdot y", {"x": 2, "y": 3}, 6),
            (r"x\times y", {"x": 2, "y": 3}, 6),
        ]
        for expression, values, expected in cases:
            with self.subTest(expression=expression):
                self.assertEqual(Formula(expression).evaluate(values), expected)

    def test_explicit_multiletter_and_decorated_variables(self):
        formula = Formula(r"F=\mathrm{stress}+\sigma_{ r }^{*}+x_1+x_{1}+y''")
        self.assertEqual(
            formula.parameters, ("stress", "sigma_{r}'", "x_{1}", "y''")
        )
        self.assertEqual(
            formula.evaluate({"stress": 1, "sigma_{r}'": 2, "x_{1}": 3, "y''": 4}),
            13.0,
        )

    def test_prime_and_star_decorations_normalize_consistently(self):
        formula = Formula(r"x'_{i}+x^{*}_{i}+x_{i}'+x_{i}^{*}")
        self.assertEqual(formula.parameters, ("x_{i}'",))
        self.assertEqual(formula.evaluate({"x_{i}'": 3}), 12)
        grouped = Formula("(x')_i")
        self.assertEqual(grouped.parameters, ("(x')_{i}",))
        self.assertEqual(grouped.evaluate({"(x')_{i}": 4}), 4)

    def test_parameter_order_and_expression_metadata(self):
        latex = r"F=y+x+y+\alpha"
        formula = Formula(latex)
        self.assertEqual(formula.latex, latex)
        self.assertEqual(formula.result_name, "F")
        self.assertEqual(formula.parameters, ("y", "x", "alpha"))
        self.assertIsNone(Formula("x+1").result_name)
        self.assertEqual(Formula("x=x+1").parameters, ("x",))

    def test_function_metadata_parameters_follow_source_order(self):
        cases = [
            (r"\log_{b}{x}", {"b": 2, "x": 8}, 3),
            (r"\sqrt[n]{x}", {"n": 3, "x": -8}, -2),
            (r"\sin^{p}{x}", {"p": 2, "x": 0.5}, math.sin(0.5) ** 2),
            (r"\log_{x}{x+y}", {"x": 2, "y": 6}, 3),
        ]
        for expression, values, expected in cases:
            with self.subTest(expression=expression):
                formula = Formula(expression)
                self.assertEqual(formula.parameters, tuple(values))
                self.assertAlmostEqual(formula.evaluate(values), expected)

    def test_constants_and_e_is_a_variable(self):
        formula = Formula(r"\pi+e")
        self.assertEqual(formula.parameters, ("e",))
        self.assertAlmostEqual(formula.evaluate({"e": 2}), math.pi + 2)

    def test_nested_fractions_and_roots(self):
        cases = [
            (r"\frac{\frac{x}{y}}{z}", {"x": 12, "y": 2, "z": 3}, 2),
            (r"\sqrt{x}", {"x": 9}, 3),
            (r"\sqrt[3]{x}", {"x": 8}, 2),
            (r"\sqrt[3]{x}", {"x": -8}, -2),
            (r"\sqrt[5]{x}", {"x": -32}, -2),
            (r"\sqrt[-3]{x}", {"x": -8}, -0.5),
            (r"\sqrt[3]{\frac{64}{8}}", {}, 2),
        ]
        for expression, values, expected in cases:
            with self.subTest(expression=expression, values=values):
                self.assertAlmostEqual(Formula(expression).evaluate(values), expected)

    def test_math_functions(self):
        cases = [
            (r"\sin{x}", 0.5, math.sin(0.5)),
            ("cos(x)", 0.5, math.cos(0.5)),
            (r"\tan[x]", 0.5, math.tan(0.5)),
            (r"\arcsin{x}", 0.5, math.asin(0.5)),
            (r"\arccos{x}", 0.5, math.acos(0.5)),
            (r"\arctan{x}", 0.5, math.atan(0.5)),
            (r"\sinh{x}", 0.5, math.sinh(0.5)),
            (r"\cosh{x}", 0.5, math.cosh(0.5)),
            (r"\tanh{x}", 0.5, math.tanh(0.5)),
            (r"\exp{x}", 0.5, math.exp(0.5)),
            (r"\ln{x}", 2, math.log(2)),
            (r"\log{x}", 100, 2),
            (r"\log_{2}{x}", 8, 3),
            ("log(x,2)", 8, 3),
            ("abs(x)", -3, 3),
            (r"\sin^{2}{x}", 0.5, math.sin(0.5) ** 2),
        ]
        for expression, value, expected in cases:
            with self.subTest(expression=expression):
                self.assertAlmostEqual(Formula(expression).evaluate({"x": value}), expected)

    def test_function_without_brackets_binds_one_power(self):
        cases = [
            (r"\sin x^2", {"x": 2}, math.sin(4)),
            (r"\sin x y", {"x": 1, "y": 2}, math.sin(1) * 2),
            (r"\sin x+1", {"x": 1}, math.sin(1) + 1),
            (r"\sin{x+1}", {"x": 1}, math.sin(2)),
        ]
        for expression, values, expected in cases:
            with self.subTest(expression=expression):
                self.assertAlmostEqual(Formula(expression).evaluate(values), expected)

    def test_absolute_values_and_extrema(self):
        cases = [
            ("|x-3|", {"x": 1}, 2),
            (r"\left|x-3\right|", {"x": 1}, 2),
            ("max(x,2,3)", {"x": 1}, 3),
            (r"\min[x,2,3]", {"x": 1}, 1),
            (r"\left(x+1\right)\left[x-1\right]", {"x": 3}, 8),
        ]
        for expression, values, expected in cases:
            with self.subTest(expression=expression):
                self.assertEqual(Formula(expression).evaluate(values), expected)

    def test_more_than_26_parameters(self):
        names = tuple(f"x_{{{index}}}" for index in range(30))
        formula = Formula("+".join(names))
        self.assertEqual(formula.parameters, names)
        self.assertEqual(formula.evaluate(dict.fromkeys(names, 1)), 30.0)


class EngineeringExampleTests(unittest.TestCase):
    def test_all_original_examples_have_known_parameters_and_results(self):
        cases = [
            ({"a_{12}": 7}, 7),
            ({"E'": 210, "v'": 0.25}, 210 / (2 * 1.25)),
            (
                {"(sigma_{T}')_{a}": 20, "G_{p}'": 8, "G_{d}'": 2,
                 "varepsilon_{i}'": 0.5, "varepsilon_{0}'": 0.1},
                20 - 0.5 * (8 - 2) * (0.5 - 0.1),
            ),
            (
                {"mu'": 2, "K_{x}": 2, "sigma_{x}'": 3, "K_{y}": 4,
                 "sigma_{y}'": 5, "K_{xy}": 6, "tau_{xy}'": 7},
                (2 * 3 + 4 * 5 + 6 * 7) / 2,
            ),
            (
                {"K_{skin}": 2, "E": 100, "alpha": 0.01,
                 "T_{m}": 50, "T_{s}": 20, "v": 0.25},
                2 * (100 * 0.01 * (50 - 20) / (1 - 0.25)),
            ),
            (
                {"mu'": 0.2},
                (9.43983 - 421.179 * 0.2 + 6893.05 * 0.2 ** 2)
                / (1 + 4991.39 * 0.2 + 6032.92 * 0.2 ** 2 - 1466.19 * 0.2 ** 3),
            ),
            (
                {"n": 0.5, "m": 3, "Delta": 2, "S_{n,k}": 6, "S_{PS}": 3},
                1 + ((1 - 0.5) / (0.5 * (3 - 1))) * ((2 * 6 / 3) - 1),
            ),
            (
                {"A_{x}": 1, "B_{x}": 4, "S_{1}": math.e},
                (math.tanh(1) / (1 ** 24 + 2) + 1) / math.sqrt(4 * math.log(math.e)),
            ),
            (
                {"S_{v,k}": 2, "S_{u,k}": 4, "v_{e}": 0.1},
                max(0.5 - 0.2 * (2 / 4), 0.1),
            ),
            ({"sigma_{uts}": 10, "m_{2}": 2}, 10 * math.exp(2) / (2 ** 2)),
            ({"D_{R}": 2, "D_{i}": 6, "r_{k}": 2}, math.asin((2 - 6 / 2 + 2) / 2)),
            (
                {"t": 2, "L_{R}": 10, "alpha": math.pi / 4, "lambda": 10},
                2 * (10 - 2 / (2 * math.tan(math.pi / 4))) * max((10 / 5) ** 0.85, 1),
            ),
            ({"L_{R1}": 3, "L_{R2}": 1, "L_{R3}": 2, "t_{n}": 0.5}, 1.5),
        ]
        self.assertEqual(len(LATEX_EXAMPLES), 13)
        for latex, (values, expected) in zip(LATEX_EXAMPLES, cases):
            with self.subTest(latex=latex):
                formula = Formula(latex)
                self.assertEqual(formula.parameters, tuple(values))
                self.assertAlmostEqual(formula.evaluate(values), expected)


class InvalidInputTests(unittest.TestCase):
    def test_invalid_or_unsupported_syntax_is_rejected_completely(self):
        expressions = [
            "", " ", "x@+1", "x.__class__", "x;1", "1..2", "x+", "(x]",
            "(x", "x)", "=x", "F=", "x+y=2", "1=x", "F=x=2", "x,2",
            r"\unknown{x}", r"\sum_{i=1}^{n}x", r"\int{x}",
            r"\begin{matrix}x\end{matrix}", r"\frac{x}", r"\sqrt{}",
            r"\sin()", "sin(x,y)", "max()", r"\log(x,2,3)",
            r"\mathrm{}", "|x", r"\left(x\right]",
            "__import__('os')", r"\open(x)", r"\operatorname{open}(x)", "math.sin(x)",
        ]
        for expression in expressions:
            with self.subTest(expression=expression):
                with self.assertRaises(FormulaSyntaxError):
                    Formula(expression)

    def test_syntax_errors_identify_original_source_position(self):
        source = r"F=\frac{x}{y}+@"
        with self.assertRaises(FormulaSyntaxError) as raised:
            Formula(source)
        self.assertEqual(raised.exception.position, source.index("@"))
        self.assertEqual(raised.exception.source, source)
        self.assertTrue(str(raised.exception))

    def test_exact_parameters_and_numeric_values_are_required(self):
        formula = Formula("F=x+1")
        invalid = [
            {}, {"x": 1, "y": 2}, {"x": True}, {"x": None}, {"x": "3"},
            {"x": 1 + 2j}, {"x": float("inf")}, {"x": float("nan")},
            {"x": 10 ** 1000},
        ]
        for values in invalid:
            with self.subTest(values=values):
                with self.assertRaises(FormulaEvaluationError):
                    formula.evaluate(values)

    def test_parameter_code_is_rejected_without_execution(self):
        captured = io.StringIO()
        with contextlib.redirect_stdout(captured):
            with self.assertRaises(FormulaEvaluationError):
                Formula("F=x").evaluate({"x": "print('EXECUTION_MARKER') or 7"})
        self.assertEqual(captured.getvalue(), "")

    def test_unknown_plain_words_are_letter_products_never_python_calls(self):
        with patch("builtins.open", side_effect=AssertionError("Python callable was invoked")):
            formula = Formula("open(x)")
            self.assertEqual(formula.parameters, ("o", "p", "e", "n", "x"))
            self.assertEqual(formula.evaluate({"o": 1, "p": 2, "e": 3, "n": 4, "x": 5}), 120)

    def test_domain_errors_and_nonfinite_results_are_explicit(self):
        cases = [
            ("1/x", {"x": 0}),
            (r"\sqrt{x}", {"x": -1}),
            (r"\ln{x}", {"x": 0}),
            (r"\arcsin{x}", {"x": 2}),
            (r"\exp{x}", {"x": 1000}),
            ("x^0.5", {"x": -1}),
            ("x*x", {"x": 1e308}),
            (r"\sqrt[0]{x}", {"x": 8}),
            (r"\sqrt[2.5]{x}", {"x": 8}),
            (r"\log(x,1)", {"x": 8}),
        ]
        for expression, values in cases:
            with self.subTest(expression=expression):
                with self.assertRaises(FormulaEvaluationError) as raised:
                    Formula(expression).evaluate(values)
                self.assertTrue(str(raised.exception))

    def test_nonfinite_literals_are_rejected(self):
        with self.assertRaises((FormulaSyntaxError, FormulaEvaluationError)):
            Formula("1e999").evaluate({})

    def test_input_length_limit(self):
        self.assertEqual(Formula(" " * 9999 + "x").evaluate({"x": 1}), 1)
        with self.assertRaises(FormulaSyntaxError):
            Formula("x" * 10001)

    def test_nested_and_recursive_operator_limits(self):
        expressions = ["(" * 65 + "x" + ")" * 65, "-" * 100 + "x", "^".join(["x"] * 100)]
        for expression in expressions:
            with self.subTest(expression=expression):
                with self.assertRaises(FormulaSyntaxError):
                    Formula(expression)

    def test_exact_nesting_boundary(self):
        expression = "(" * 64 + "x" + ")" * 64
        self.assertEqual(Formula(expression).evaluate({"x": 3}), 3)

    def test_node_limit_and_long_valid_flat_expression(self):
        expression = "+".join(["x"] * 1000)
        self.assertEqual(Formula(expression).evaluate({"x": 1}), 1000)
        self.assertEqual(Formula(f"-({expression})").evaluate({"x": 1}), -1000)
        with self.assertRaises(FormulaSyntaxError):
            Formula("+".join(["x"] * 1001))


class StandaloneExportTests(unittest.TestCase):
    @staticmethod
    def import_export(path):
        spec = importlib.util.spec_from_file_location("exported_formula", path)
        module = importlib.util.module_from_spec(spec)
        captured = io.StringIO()
        with contextlib.redirect_stdout(captured), contextlib.redirect_stderr(captured):
            spec.loader.exec_module(module)
        return module, captured.getvalue()

    def test_source_contains_original_formula_and_parameter_mapping(self):
        formula = Formula(r"F=\frac{x}{y}")
        with tempfile.TemporaryDirectory() as temporary:
            path = formula.export_python(Path(temporary) / "nested" / "formula.py")
            self.assertIsInstance(path, Path)
            self.assertEqual(path.read_text(encoding="utf-8"), formula.to_python())
            module, output = self.import_export(path)
            self.assertEqual(output, "")
            self.assertEqual(module.LATEX, formula.latex)
            self.assertEqual(module.PARAMETERS, {"p0": "x", "p1": "y"})
            self.assertEqual(module.formula(6, 2), 3.0)

    def test_overwrite_requires_explicit_opt_in(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "formula.py"
            path.write_text("original", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                Formula("1").export_python(path)
            self.assertEqual(path.read_text(encoding="utf-8"), "original")
            Formula("1").export_python(path, overwrite=True)
            module, output = self.import_export(path)
            self.assertEqual(output, "")
            self.assertEqual(module.formula(), 1.0)

    def test_export_numerical_parity(self):
        cases = [
            (r"\sqrt[3]{x}+\sin^{2}{y}", {"x": -8, "y": 0.5}),
            (r"\log_{2}{x}+\pi", {"x": 8}),
            (r"\mathrm{stress}+\sigma_{r}^{*}", {"stress": 2, "sigma_{r}'": 3}),
            ("2^3^2-2^-2", {}),
            ("|x|+max(x,y)", {"x": -2, "y": 3}),
        ]
        with tempfile.TemporaryDirectory() as temporary:
            for index, (expression, values) in enumerate(cases):
                with self.subTest(expression=expression):
                    formula = Formula(expression)
                    module, output = self.import_export(
                        formula.export_python(Path(temporary) / f"formula_{index}.py")
                    )
                    arguments = [values[name] for name in formula.parameters]
                    self.assertEqual(output, "")
                    self.assertAlmostEqual(module.formula(*arguments), formula.evaluate(values))

    def test_export_handles_more_than_26_parameters(self):
        formula = Formula("+".join(f"x_{{{index}}}" for index in range(30)))
        with tempfile.TemporaryDirectory() as temporary:
            module, _ = self.import_export(formula.export_python(Path(temporary) / "many.py"))
            self.assertEqual(module.formula(*([1] * 30)), 30.0)
            self.assertEqual(module.PARAMETERS["p29"], "x_{29}")

    def test_export_preserves_source_parameter_order(self):
        cases = [
            (r"\log_{b}{x}", ("b", "x"), (2, 8), 3),
            (r"\sqrt[n]{x}", ("n", "x"), (3, -8), -2),
            (r"\sin^{p}{x}", ("p", "x"), (2, 0.5), math.sin(0.5) ** 2),
            (r"\log_{x}{x+y}", ("x", "y"), (2, 6), 3),
        ]
        with tempfile.TemporaryDirectory() as temporary:
            for index, (expression, names, values, expected) in enumerate(cases):
                with self.subTest(expression=expression):
                    module, _ = self.import_export(
                        Formula(expression).export_python(Path(temporary) / f"order_{index}.py")
                    )
                    self.assertEqual(module.PARAMETERS, {f"p{i}": name for i, name in enumerate(names)})
                    self.assertAlmostEqual(module.formula(*values), expected)

    def test_export_error_parity(self):
        cases = [
            (r"\sqrt{x}", -1), ("1/x", 0), (r"\exp{x}", 1000),
            ("x^0.5", -1), ("x*x", 1e308), ("x", True),
            ("x", "print('EXECUTION_MARKER') or 7"), ("x", float("inf")),
        ]
        with tempfile.TemporaryDirectory() as temporary:
            for index, (expression, value) in enumerate(cases):
                with self.subTest(expression=expression, value=value):
                    formula = Formula(expression)
                    module, _ = self.import_export(
                        formula.export_python(Path(temporary) / f"invalid_{index}.py")
                    )
                    with self.assertRaises(FormulaEvaluationError) as direct:
                        formula.evaluate({"x": value})
                    with self.assertRaises(ValueError) as generated:
                        module.formula(value)
                    self.assertEqual(type(generated.exception).__name__, "FormulaEvaluationError")
                    self.assertEqual(str(generated.exception), str(direct.exception))

    def test_export_of_long_valid_expression(self):
        formula = Formula("+".join(["x"] * 1000))
        with tempfile.TemporaryDirectory() as temporary:
            module, _ = self.import_export(formula.export_python(Path(temporary) / "long.py"))
            self.assertEqual(module.formula(1), 1000)

    def test_export_runs_without_site_packages_or_repository_imports(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Formula(r"\sqrt[3]{x}+\pi").export_python(Path(temporary) / "standalone.py")
            process = subprocess.run(
                [sys.executable, "-I", "-S", "-B", "-c",
                 "import runpy,sys; m=runpy.run_path(sys.argv[1]); print(m['formula'](-8))",
                 str(path)],
                cwd=temporary,
                text=True,
                capture_output=True,
                timeout=10,
                check=True,
            )
            self.assertEqual(process.stderr, "")
            self.assertAlmostEqual(float(process.stdout.strip()), math.pi - 2)


class ExampleEntryPointTests(unittest.TestCase):
    def test_interactive_numeric_input(self):
        captured = io.StringIO()
        with patch("builtins.input", side_effect=["6", "2"]), contextlib.redirect_stdout(captured):
            self.assertEqual(evaluate_interactive(r"F=\frac{x}{y}"), 3.0)
        self.assertIn("3.0", captured.getvalue())

    def test_interactive_expression_and_nonfinite_input_are_rejected(self):
        for value in ("1+2", "print('EXECUTION_MARKER') or 7", "nan", "inf"):
            with self.subTest(value=value):
                captured = io.StringIO()
                with patch("builtins.input", return_value=value), contextlib.redirect_stdout(captured):
                    with self.assertRaises(FormulaEvaluationError):
                        evaluate_interactive("F=2*x")
                self.assertEqual(captured.getvalue(), "")

    def test_sample_entry_point_exports_all_examples(self):
        with tempfile.TemporaryDirectory() as temporary:
            with contextlib.redirect_stdout(io.StringIO()):
                paths = main(temporary)
            self.assertEqual(len(paths), 13)
            self.assertEqual([path.name for path in paths], [f"Formula_{i}.py" for i in range(13)])
            self.assertTrue(all(path.is_file() for path in paths))
            for path in paths:
                _, output = StandaloneExportTests.import_export(path)
                self.assertEqual(output, "")


if __name__ == "__main__":
    unittest.main()
