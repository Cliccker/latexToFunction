# Repository Guidelines

## Project Structure & Module Organization

`LatexToFunction.py` exposes `Formula`, controlled numerical evaluation, and standalone Python export. `formula_parser.py` implements tokenization, recursive descent, source-positioned errors, and the expression tree. `main.py` contains 13 engineering examples behind a main guard. `tests/` holds first-party regression tests. `README.md` documents supported syntax and migration from the old API.

`Data/` and `Files/` are ignored output directories. Virtual environments (`venv/`, `.venv/`), Python caches, and `.idea/` are ignored local artifacts; keep them out of commits.

## Build, Test, and Development Commands

Use Python 3.11 or later from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m unittest discover -s tests
python main.py
```

The core uses only the standard library; `requirements.txt` contains environment notes rather than packages. There is no build step. Tests validate parsing, mathematics, safety, and export parity. The example command creates `Data/` and explicitly overwrites its 13 generated modules. Importing modules must not run examples or print results.

## Coding Style & Naming Conventions

Use four-space indentation, snake_case methods and variables, PascalCase classes, and explicit imports. Write LaTeX literals as raw strings, such as `r"F=\frac{x}{y}"`. Preserve source positions through parser changes. Keep calculation and code generation aligned with the same expression tree. No formatter or linter is configured.

## Testing Guidelines

Use standard-library `unittest`; name files `tests/test_*.py` and cases `test_*`. Add a focused regression for changed syntax or numerical behavior. Check mathematical results independently rather than comparing two implementations of the same mistake. Cover invalid input and exported-function behavior when relevant. Use temporary directories for export tests. There is no numerical coverage threshold; the full suite must pass.

## Commit & Pull Request Guidelines

History uses short English and Chinese summaries without a required prefix. Write specific subjects, for example `Fix unary minus precedence`. Keep commits focused. PRs should explain the behavior change, show representative LaTeX input and expected results, list validation, and link relevant issues.

## Safety & Syntax Boundaries

Never evaluate input with `eval` or `exec`. Accept only finite numeric parameter values and whitelisted mathematical operations. Consume the entire formula or raise a positioned syntax error. Preserve resource limits and default export overwrite protection. Document syntax additions, especially variable naming and precedence; unsupported symbolic structures must fail explicitly.
