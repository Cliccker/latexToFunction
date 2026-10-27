# LaTeX 标量公式引擎

将 LaTeX 数学表达式解析为语法树，安全地计算有限实数结果，或导出仅依赖 Python 标准库的函数。要求 **Python 3.11 及以上**，无需安装第三方运行依赖。

## 转换示例：复杂 LaTeX 最终变成什么函数？

以示例中的这条公式为例，它同时包含嵌套分数、双曲正切、24 次幂、平方根和自然对数：

$$F=\frac{\frac{\tanh(1)}{A_x^{24}+2}+1}{\sqrt{B_x\ln(S_1)}}$$

输入的 LaTeX 文本为：

```latex
F=\frac{\frac{\tanh{1}}{A_{x}^{24}+2}+1}{\sqrt{B_{x}\ln{S_{1}}}}
```

**从数学意义上，转换结果等价于下面这个 Python 函数：**

```python
import math


def formula(A_x, B_x, S_1):
    numerator = math.tanh(1) / (A_x**24 + 2) + 1
    denominator = math.sqrt(B_x * math.log(S_1))
    return numerator / denominator
```

实际导出时，参数会统一命名为 `p0`、`p1`、`p2`，并通过映射保留原变量名：

```python
PARAMETERS = {"p0": "A_{x}", "p1": "B_{x}", "p2": "S_{1}"}
```

下面的代码完成转换、保存和调用。取 `A_x=1`、`B_x=4`、`S_1=e`，结果约为 **0.6269323593**：

```python
import math
from LatexToFunction import Formula

latex = r"F=\frac{\frac{\tanh{1}}{A_{x}^{24}+2}+1}{\sqrt{B_{x}\ln{S_{1}}}}"
converted = Formula(latex)
converted.export_python("Data/complex_formula.py", overwrite=True)

from Data.complex_formula import formula

print(formula(1, 4, math.e))  # 0.6269323593259608
```

<details>
<summary>查看实际导出的函数主体</summary>

导出器按语法树拆分运算步骤。`_number` 校验有限数值，`_apply` 执行受控数学运算，使非法参数、除零或定义域错误得到明确提示。以下是实际生成的函数主体；辅助函数也会写入同一个文件，因此导出文件可以独立运行。

```python
def formula(p0, p1, p2):
    p0 = _number(p0, "parameter 'A_{x}'")
    p1 = _number(p1, "parameter 'B_{x}'")
    p2 = _number(p2, "parameter 'S_{1}'")
    v0 = 1.0
    v1 = _apply('tanh', v0)
    v2 = p0
    v3 = 24.0
    v4 = _apply('^', v2, v3)
    v5 = 2.0
    v6 = _apply('+', v4, v5)
    v7 = _apply('/', v1, v6)
    v8 = 1.0
    v9 = _apply('+', v7, v8)
    v10 = p1
    v11 = p2
    v12 = _apply('ln', v11)
    v13 = _apply('*', v10, v12)
    v14 = 2.0
    v15 = _apply('root', v13, v14)
    v16 = _apply('/', v9, v15)
    return _number(v16, 'result')
```

</details>

## 快速开始

在仓库根目录运行：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m unittest discover -s tests
python main.py
```

`main.py` 转换 13 条工程公式，自动创建 `Data/`，导出 `Formula_0.py` 至 `Formula_12.py`。重复运行会显式覆盖这些示例文件。导入 `main` 不会生成文件或运行示例。

使用 `--output-dir` 指定示例导出目录，或使用 `--formula` 交互计算一条公式；交互参数先转换为数值再参与计算：

```powershell
python main.py --output-dir Data/demo
python main.py --formula 'F=\frac{x}{y}'
```

```python
from LatexToFunction import Formula

formula = Formula(r"F=\frac{x}{y}")
print(formula.result_name)  # F
print(formula.parameters)  # ('x', 'y')
print(formula.evaluate({"x": 6, "y": 2}))  # 3.0
```

使用原始字符串 `r"..."` 保存 LaTeX，避免 Python 将 `\frac`、`\theta` 等命令中的反斜杠解释为转义字符。

## 支持的语法

可以输入单独表达式，也可以输入 `结果变量=表达式`；等号左侧必须是一个合法变量。

| 类型 | 示例与说明 |
| --- | --- |
| 数字 | `12`、`0.5`、`1e-3`，结果限定为有限实数 |
| 基本运算 | `+`、`-`、`*`、`/`、`^`、`**`，支持一元正负号 |
| 分组 | `(x+y)`、`{x+y}`、`[x+y]`，支持 `\left`、`\right` |
| 隐式乘法 | `2x`、`xy`、`xy(z+1)`、`x(y+1)`、`(x+1)(y+1)`、`x\alpha`，也支持 `\cdot`、`\times` |
| 分数、根式 | `\frac{x}{y}`、`\sqrt{x}`、`\sqrt[3]{x}`，允许嵌套；根次数须为非零整数，负数的奇数次根按实数计算 |
| 三角、反三角函数 | `sin`、`cos`、`tan`、`arcsin`、`arccos`、`arctan`，角度使用弧度 |
| 双曲函数 | `sinh`、`cosh`、`tanh` |
| 指数、对数 | `\exp{x}`、`\ln{x}`、`log(x)`、`log(x,b)`、`\log_{b}{x}`；`log` 默认以 10 为底 |
| 其他函数 | `abs(x)`、`min(x,y)`、`max(x,y)`，以及绝对值 `\left|x\right|` 或 `abs(x)` |
| 函数幂 | `\sin^{2}{x}` 表示正弦值的平方 |

函数名可以带 LaTeX 反斜杠，例如 `\sin{x}`，也可以写为 `sin(x)`。参数允许花括号、圆括号和方括号。无括号的一元函数只绑定紧随的一个幂表达式，例如 `\sin x^2` 表示 `sin(x^2)`；多个项组成的参数应显式分组，如 `\sin{2x}`。

幂右结合，且优先级高于一元负号：`2^3^2 = 512`，`-2^2 = -4`。显式乘法、隐式乘法和除法同级，从左到右计算：`6/2x` 表示 `(6/2)*x`。请用分组明确分母，例如 `6/(2x)`。

## 变量与参数名

普通字母采用数学单字母规则：`xy` 是 `x*y`，`stress` 是多个字母相乘。多字母变量须写成 `\mathrm{stress}`。除已知数学函数名外，连续字母后接括号也表示乘法，例如 `xy(z+1)` 是 `x*y*(z+1)`；未知 LaTeX 函数命令会报错。

| 公式中的变量 | `evaluate` 使用的参数键 |
| --- | --- |
| `x` | `"x"` |
| `\alpha` | `"alpha"` |
| `x_{ i , j }` | `"x_{i,j}"` |
| `\mathrm{stress}` | `"stress"` |
| `\sigma_{ r }^{*}` | `"sigma_{r}'"` |

支持希腊变量、下标、撇号，以及现有工程公式中的星号标签和分组变量附加下标。标签内的空白会移除，下标作为变量标识，不参与数值运算。工程星号标签规范为撇号，不表示复共轭。`\pi` 是圆周率常量，普通字母 `e` 是变量；自然指数使用 `\exp`。

`parameters` 按变量在等号右侧首次出现的顺序排列。以该属性为准构造参数字典：

```python
formula = Formula(r"F=\mathrm{stress}\alpha")
assert formula.parameters == ("stress", "alpha")
assert formula.evaluate({"stress": 10, "alpha": 0.5}) == 5.0
```

## API 与错误处理

| 接口 | 行为 |
| --- | --- |
| `Formula(latex)` | 构造时解析并校验整个输入 |
| `.latex` | 原始 LaTeX 字符串 |
| `.result_name` | 规范化后的结果变量名；单独表达式为 `None` |
| `.parameters` | 规范化参数名的元组 |
| `.evaluate(values)` | 根据参数字典计算，返回 `float` |
| `.to_python()` | 返回完整的 Python 模块源码字符串 |
| `.export_python(path, *, overwrite=False)` | 创建父目录并写入源码，返回 `Path` |

参数值只能是有限的 `int` 或 `float`；布尔值、字符串、缺失参数和多余参数均会被拒绝。交互式输入应先转换为数值，例如 `float(input("x="))`，再传入参数字典。

```python
from LatexToFunction import Formula, FormulaEvaluationError, FormulaSyntaxError

try:
    result = Formula(r"F=\sqrt{x}").evaluate({"x": -1})
except FormulaSyntaxError as error:
    print(error)  # 包含原式位置和语法原因
except FormulaEvaluationError as error:
    print(error)  # 包含失败运算和数值原因
```

未知命令、非法字符、残缺表达式和括号不匹配会报语法错误；除零、定义域错误、溢出和非实数结果会报计算错误。默认限制为 10,000 个输入字符、64 层嵌套、2,000 个语法树节点。

## 导出独立函数

```python
from LatexToFunction import Formula

formula = Formula(r"F=\frac{x}{y}")
source = formula.to_python()
path = formula.export_python("Data/example.py")

# 重复写入需要显式授权覆盖：
formula.export_python(path, overwrite=True)
```

导出模块包含原始公式 `LATEX`、参数映射 `PARAMETERS` 和 `formula(p0, p1, ...)` 函数。变量统一映射为安全的 Python 参数名，数量不再限制为 26 个。例如：

```python
from Data.example import PARAMETERS, formula

assert PARAMETERS == {"p0": "x", "p1": "y"}
assert formula(6, 2) == 3.0
```

生成函数与直接计算采用相同的数值校验和数学语义。导出过程不会执行生成代码，导入导出模块也不会运行公式或打印结果。目标文件已存在时默认抛出 `FileExistsError`。

## 支持边界与安全

本项目处理标量实数公式。求和、积分、矩阵、求导、分段函数及不等式暂不支持，遇到相应结构会明确报错。输入不是 Python 代码；属性访问、任意函数调用和未知 LaTeX 命令均不被接受。

计算直接遍历语法树并调用白名单数学函数，不使用 `eval`、`exec` 或参数文本替换。解析必须消费全部输入，不能通过丢弃未知字符继续计算。导出路径由调用方指定，接入服务时应由服务控制保存位置。

## 从旧接口迁移

旧接口不再保留，迁移方式如下：

| 原用法 | 新用法 |
| --- | --- |
| `Formula(...); f.ToFunction()` | `Formula(...)`，构造时即完成解析 |
| `f.ParaValue = ...; f.Calculate()` | `f.evaluate({...})`，返回数值 |
| `f.Result()` | 调用方读取输入、转成数值，再调用 `evaluate` |
| `f.SaveAsPython("Example")` | `f.export_python("Data/Example.py")` |
| 读取 `f.function` | `f.to_python()` 获取完整模块源码 |

多字母变量改用 `\mathrm{...}`，参数键从 `parameters` 获取。导出不再使用 `latexify`，也不自动执行文件。`requirements.txt` 仅说明运行环境，无需安装旧版 `pyparsing`、`latexify-py` 或 `dill`。

## 开发与测试

- `formula_parser.py`：词法、语法树与语法校验。
- `LatexToFunction.py`：公共接口、受控求值和源码导出。
- `main.py`：13 条工程公式示例及运行入口。
- `tests/`：标准库 `unittest` 回归测试。

```powershell
python -m unittest discover -s tests
```

测试覆盖工程公式、数学优先级、参数命名、错误输入、代码注入防护、资源限制，以及直接计算与导出函数的一致性。
