"""Export the original engineering examples, or evaluate a formula interactively."""

import argparse
from pathlib import Path

from LatexToFunction import Formula, FormulaEvaluationError


LATEX_EXAMPLES = (
    r"s=a_{12}",
    r"G^{*}=\frac{E^{*}}{2\left(1+v^{*}\right)}",
    (
        r"\left(\sigma_{r}^{*}\right)_{P}=\left(\sigma_{T}^{*}\right)_{a}"
        r"-\frac{1}{2}\left(G_{p}^{*}-G_{d}^{*}\right)"
        r"\left(\varepsilon_{i}^{*}-\varepsilon_{0}^{*}\right)"
    ),
    (
        r"\sigma_{0}=\frac{1}{\mu^{*}}"
        r"\left(K_{x}\sigma_{x}^{*}+K_{y}\sigma_{y}^{*}+K_{xy}\tau_{xy}^{*}\right)"
    ),
    r"\sigma_{p}^{*}=K_{skin}\left[\frac{E\alpha\left(T_{m}-T_{s}\right)}{(1-v)}\right]",
    (
        r"K_{vkin}=\frac{9.43983-421.179\mu^{*}+6893.05\mu^{*2}}"
        r"{1+4991.39\mu^{*}+6032.92\mu^{*2}-1466.19\mu^{*3}}"
    ),
    r"K_{e,k}=1.0+\frac{(1-n)}{n*(m-1)}\left(\frac{\Delta S_{n,k}}{S_{PS}}-1\right)",
    r"F=\frac{\frac{tanh{1}}{A_{x}^{24}+2}+1}{\sqrt{B_{x}\ln{S_{1}}}}",
    r"v_{p}=\max\left[0.5-0.2\left(\frac{S_{v,k}}{S_{u,k}}\right),v_{e}\right]",
    r"A_{2}=\frac{\sigma_{uts}\exp\left[m_{2}\right]}{m_{2}^{m_{2}}}",
    r"\theta=\arcsin\left[\frac{D_{R}-\frac{D_{i}}{2}+r_{k}}{r_{k}}\right]",
    (
        r"A_{1}=t\left(L_{R}-\frac{t}{2\tan[\alpha]}\right)"
        r"\cdot\max\left[\left(\frac{\lambda}{5}\right)^{0.85},{1.0}\right]"
    ),
    r"L_{R}=\min\left[L_{R1},L_{R2},L_{R3}\right]+t_{n}",
)


def main(output_directory: str | Path = "Data") -> list[Path]:
    """Export all 13 examples, explicitly replacing previously generated files."""
    directory = Path(output_directory)
    paths = []
    for index, latex in enumerate(LATEX_EXAMPLES):
        path = Formula(latex).export_python(directory / f"Formula_{index}.py", overwrite=True)
        paths.append(path)
        print(path)
    return paths


def evaluate_interactive(latex: str) -> float:
    """Read numeric parameters; never interpret user input as an expression."""
    formula = Formula(latex)
    values = {}
    for name in formula.parameters:
        try:
            values[name] = float(input(f"{name} = "))
        except ValueError as error:
            raise FormulaEvaluationError(f"parameter {name!r}: expected a number") from error
    result = formula.evaluate(values)
    print(f"{formula.result_name or 'result'} = {result}")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--formula", help="LaTeX formula to evaluate with interactive numeric input")
    parser.add_argument("--output-dir", default="Data", help="destination for the 13 example modules")
    arguments = parser.parse_args()
    try:
        if arguments.formula is None:
            main(arguments.output_dir)
        else:
            evaluate_interactive(arguments.formula)
    except ValueError as error:
        parser.error(str(error))
